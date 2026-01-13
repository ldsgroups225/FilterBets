#!/usr/bin/env python3
"""
FilterBets - Agent-Driven Git Development Workflow Orchestrator
Reads workflow configuration from CLAUDE.md and executes it.

Supports both Python (FastAPI) backend and React (TypeScript) frontend.
"""

import subprocess
import sys
import time
import re
import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Union
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML package not found.", file=sys.stderr)
    print("Please install it by running: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

from enum import Enum


class WorkflowState(Enum):
    INIT = "init"
    GIT_STATUS_CHECK = "git_status_check"
    BACKEND_TYPECHECK = "backend_typecheck"
    BACKEND_LINT = "backend_lint"
    BACKEND_TEST = "backend_test"
    FRONTEND_TYPECHECK = "frontend_typecheck"
    FRONTEND_LINT = "frontend_lint"
    FRONTEND_TEST = "frontend_test"
    NOTEBOOK_VALIDATION = "notebook_validation"
    FINAL_STATUS = "final_status"
    COMMIT_MESSAGE = "commit_message"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowContext:
    current_state: WorkflowState
    request_type: str
    initial_git_status: str = ""
    last_commit: str = ""
    attempts: Dict[str, int] = field(default_factory=lambda: {
        "backend_typecheck": 0,
        "backend_lint": 0,
        "backend_test": 0,
        "frontend_typecheck": 0,
        "frontend_lint": 0,
        "frontend_test": 0,
        "notebook": 0,
    })
    max_attempts: int = 3
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AgentWorkflowOrchestrator:
    """Orchestrates development workflows for FilterBets project."""

    # Project paths
    BACKEND_DIR = "backend"
    FRONTEND_DIR = "frontend"
    NOTEBOOKS_DIR = "notebooks"

    def __init__(self, request_type: str, config_file: str = "CLAUDE.md", max_fix_attempts: int = 3):
        self.context = WorkflowContext(
            current_state=WorkflowState.INIT,
            request_type=request_type,
            max_attempts=max_fix_attempts
        )
        self.project_root = Path.cwd()
        self.workflow_steps = self._load_workflow_from_config(config_file)

    def _load_workflow_from_config(self, config_file: str) -> List[Tuple[Callable, str]]:
        print(f"📄 Loading workflows from {config_file}...")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.search(
                r'<!--AGENT_WORKFLOWS_START-->(.*)<!--AGENT_WORKFLOWS_END-->',
                content,
                re.DOTALL
            )
            if not match:
                print(f"Error: Could not find workflow block in {config_file}", file=sys.stderr)
                sys.exit(1)

            yaml_content = re.sub(r'```yaml|```', '', match.group(1)).strip()
            config = yaml.safe_load(yaml_content)

            agent_config = next(
                (agent for agent in config.get('agents', [])
                 if agent['name'] == self.context.request_type
                 or agent.get('alias') == self.context.request_type),
                None
            )

            if not agent_config:
                print(f"⚠️ Agent '{self.context.request_type}' not found. Defaulting to 'review'.")
                self.context.request_type = 'review'
                return self._load_workflow_from_config(config_file)

            print(f"🤖 Initializing '{agent_config['name']}' agent: {agent_config['description']}")

            steps = []
            for step in agent_config.get('steps', []):
                func = getattr(self, step['function'], None)
                if callable(func):
                    steps.append((func, step['name']))
                else:
                    print(f"Error: Function '{step['function']}' not found.", file=sys.stderr)
                    sys.exit(1)
            return steps

        except FileNotFoundError:
            print(f"Error: Config file '{config_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error parsing workflow config: {e}", file=sys.stderr)
            sys.exit(1)

    def run_command(
        self,
        cmd: List[str],
        cwd: str = None,
        timeout: int = 600
    ) -> Tuple[int, str, str]:
        """Execute a shell command and return (returncode, stdout, stderr)."""
        work_dir = cwd or self.project_root
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                cwd=work_dir
            )
            return process.returncode, process.stdout, process.stderr
        except FileNotFoundError:
            return -2, "", f"Command not found: {cmd[0]}"
        except subprocess.TimeoutExpired:
            return -3, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return -1, "", str(e)

    def _dir_exists(self, dirname: str) -> bool:
        """Check if a project directory exists."""
        return (self.project_root / dirname).is_dir()

    # =========================================================================
    # Git Operations
    # =========================================================================

    def check_git_status(self) -> bool:
        self.context.current_state = WorkflowState.GIT_STATUS_CHECK
        print("\n🔍 Checking Git Status...")
        code, status, err = self.run_command(["git", "status", "--short"])
        if code != 0:
            self.context.errors.append(f"Git status failed: {err}")
            return False
        self.context.initial_git_status = status
        print(f"📊 Git Status:\n{status or 'Working tree clean'}")
        return True

    def check_final_status(self) -> Union[bool, str]:
        self.context.current_state = WorkflowState.FINAL_STATUS
        print("\n🔍 Checking Final Git Status...")
        code, status, _ = self.run_command(["git", "status", "--short"])
        if not status:
            print("✅ No changes to commit after fixes.")
            self.context.current_state = WorkflowState.COMPLETED
            return "SKIP_WORKFLOW"
        print(f"📊 Final Git Status:\n{status}")
        return True

    def suggest_commit_message(self) -> bool:
        self.context.current_state = WorkflowState.COMMIT_MESSAGE
        print("\n💬 Generating Commit Message...")
        _, diff_summary, _ = self.run_command(["git", "diff", "--shortstat"])

        prefix_map = {
            'feat': 'feat',
            'bug': 'fix',
            'fix': 'fix',
            'data': 'chore(data)',
            'review': 'chore',
        }
        prefix = prefix_map.get(self.context.request_type, 'chore')
        subject = f"{prefix}: apply automated fixes and pass checks"
        body = f"{diff_summary.strip()}\n\nAutomated workflow run for '{self.context.request_type}' request."

        print("\n" + "=" * 60)
        print("📋 Suggested Commit Message:")
        print(f"\n{subject}\n\n{body}")
        print("=" * 60)
        return True

    # =========================================================================
    # Backend (Python/FastAPI) Operations
    # =========================================================================

    def run_backend_typecheck_readonly(self) -> bool:
        if not self._dir_exists(self.BACKEND_DIR):
            print(f"⏭️  Skipping backend typecheck: '{self.BACKEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.BACKEND_TYPECHECK
        print("\n🔎 Running Backend Type Check (mypy - Read-only)...")
        self.context.attempts['backend_typecheck'] += 1

        code, stdout, stderr = self.run_command(
            ["mypy", "."],
            cwd=self.BACKEND_DIR
        )
        if code == 0:
            print("✅ Backend type check passed.")
            return True

        output = (stdout + stderr)[:2000]
        print(f"❌ Backend type errors found:\n{output}")
        self.context.errors.append("Backend type checking failed.")
        return True  # Read-only mode continues

    def run_backend_typecheck_fix(self) -> bool:
        # mypy doesn't auto-fix, so same as readonly
        return self.run_backend_typecheck_readonly()

    def run_backend_lint_readonly(self) -> bool:
        if not self._dir_exists(self.BACKEND_DIR):
            print(f"⏭️  Skipping backend lint: '{self.BACKEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.BACKEND_LINT
        print("\n🧹 Running Backend Linter (ruff - Read-only)...")
        self.context.attempts['backend_lint'] += 1

        code, stdout, stderr = self.run_command(
            ["ruff", "check", "."],
            cwd=self.BACKEND_DIR
        )
        if code == 0:
            print("✅ Backend linting passed.")
            return True

        output = (stdout + stderr)[:2000]
        print(f"❌ Backend lint issues found:\n{output}")
        self.context.errors.append("Backend linting issues found.")
        return True

    def run_backend_lint_fix(self) -> bool:
        if not self._dir_exists(self.BACKEND_DIR):
            print(f"⏭️  Skipping backend lint: '{self.BACKEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.BACKEND_LINT
        print("\n🧹 Running Backend Linter (ruff - with Fixes)...")
        self.context.attempts['backend_lint'] += 1

        # Run ruff with --fix flag
        code, stdout, stderr = self.run_command(
            ["ruff", "check", ".", "--fix"],
            cwd=self.BACKEND_DIR
        )

        # Also run ruff format
        self.run_command(["ruff", "format", "."], cwd=self.BACKEND_DIR)

        if code == 0:
            print("✅ Backend linting passed and/or auto-fixed.")
            return True

        if self.context.attempts['backend_lint'] >= self.context.max_attempts:
            self.context.errors.append("Backend linting failed after max attempts.")
            return False

        print("⚠️ Backend lint issues remain, retrying...")
        time.sleep(1)
        return self.run_backend_lint_fix()

    def run_backend_tests_readonly(self) -> bool:
        return self._run_backend_tests(retry=False)

    def run_backend_tests_with_retry(self) -> bool:
        return self._run_backend_tests(retry=True)

    def _run_backend_tests(self, retry: bool) -> bool:
        if not self._dir_exists(self.BACKEND_DIR):
            print(f"⏭️  Skipping backend tests: '{self.BACKEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.BACKEND_TEST
        self.context.attempts['backend_test'] += 1
        print(f"\n🧪 Running Backend Tests (pytest - Attempt {self.context.attempts['backend_test']})...")

        code, stdout, stderr = self.run_command(
            ["pytest", "tests/", "-v", "--tb=short"],
            cwd=self.BACKEND_DIR
        )

        if code == 0:
            print("✅ Backend tests passed.")
            return True

        output = (stdout + stderr)[:3000]
        print(f"❌ Backend tests failed:\n{output}")

        if retry and self.context.attempts['backend_test'] < self.context.max_attempts:
            print("\n🔄 Retrying backend tests...")
            time.sleep(1)
            return self._run_backend_tests(retry=True)

        self.context.errors.append("Backend tests failed.")
        return not retry

    # =========================================================================
    # Frontend (React/TypeScript) Operations
    # =========================================================================

    def run_frontend_typecheck_readonly(self) -> bool:
        if not self._dir_exists(self.FRONTEND_DIR):
            print(f"⏭️  Skipping frontend typecheck: '{self.FRONTEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.FRONTEND_TYPECHECK
        print("\n🔎 Running Frontend Type Check (tsc - Read-only)...")
        self.context.attempts['frontend_typecheck'] += 1

        code, stdout, stderr = self.run_command(
            ["pnpm", "run", "typecheck"],
            cwd=self.FRONTEND_DIR
        )

        if code == 0:
            print("✅ Frontend type check passed.")
            return True

        output = (stdout + stderr)[:2000]
        print(f"❌ Frontend type errors found:\n{output}")
        self.context.errors.append("Frontend type checking failed.")
        return True

    def run_frontend_typecheck_fix(self) -> bool:
        # TypeScript doesn't auto-fix type errors
        return self.run_frontend_typecheck_readonly()

    def run_frontend_lint_readonly(self) -> bool:
        if not self._dir_exists(self.FRONTEND_DIR):
            print(f"⏭️  Skipping frontend lint: '{self.FRONTEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.FRONTEND_LINT
        print("\n🧹 Running Frontend Linter (eslint - Read-only)...")
        self.context.attempts['frontend_lint'] += 1

        code, stdout, stderr = self.run_command(
            ["pnpm", "run", "lint"],
            cwd=self.FRONTEND_DIR
        )

        if code == 0:
            print("✅ Frontend linting passed.")
            return True

        output = (stdout + stderr)[:2000]
        print(f"❌ Frontend lint issues found:\n{output}")
        self.context.errors.append("Frontend linting issues found.")
        return True

    def run_frontend_lint_fix(self) -> bool:
        if not self._dir_exists(self.FRONTEND_DIR):
            print(f"⏭️  Skipping frontend lint: '{self.FRONTEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.FRONTEND_LINT
        print("\n🧹 Running Frontend Linter (eslint - with Fixes)...")
        self.context.attempts['frontend_lint'] += 1

        # Try lint:fix first, fall back to lint --fix
        code, stdout, stderr = self.run_command(
            ["pnpm", "run", "lint:fix"],
            cwd=self.FRONTEND_DIR
        )

        if code == -2:  # Command not found, try alternative
            code, stdout, stderr = self.run_command(
                ["pnpm", "run", "lint", "--", "--fix"],
                cwd=self.FRONTEND_DIR
            )

        if code == 0:
            print("✅ Frontend linting passed and/or auto-fixed.")
            return True

        if self.context.attempts['frontend_lint'] >= self.context.max_attempts:
            self.context.errors.append("Frontend linting failed after max attempts.")
            return False

        print("⚠️ Frontend lint issues remain, retrying...")
        time.sleep(1)
        return self.run_frontend_lint_fix()

    def run_frontend_tests_readonly(self) -> bool:
        return self._run_frontend_tests(retry=False)

    def run_frontend_tests_with_retry(self) -> bool:
        return self._run_frontend_tests(retry=True)

    def _run_frontend_tests(self, retry: bool) -> bool:
        if not self._dir_exists(self.FRONTEND_DIR):
            print(f"⏭️  Skipping frontend tests: '{self.FRONTEND_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.FRONTEND_TEST
        self.context.attempts['frontend_test'] += 1
        print(f"\n🧪 Running Frontend Tests (Attempt {self.context.attempts['frontend_test']})...")

        # Use --run flag to avoid watch mode
        code, stdout, stderr = self.run_command(
            ["pnpm", "run", "test", "--", "--run"],
            cwd=self.FRONTEND_DIR
        )

        if code == 0:
            print("✅ Frontend tests passed.")
            return True

        output = (stdout + stderr)[:3000]
        print(f"❌ Frontend tests failed:\n{output}")

        if retry and self.context.attempts['frontend_test'] < self.context.max_attempts:
            print("\n🔄 Retrying frontend tests...")
            time.sleep(1)
            return self._run_frontend_tests(retry=True)

        self.context.errors.append("Frontend tests failed.")
        return not retry

    # =========================================================================
    # Notebook Operations
    # =========================================================================

    def run_notebook_validation(self) -> bool:
        if not self._dir_exists(self.NOTEBOOKS_DIR):
            print(f"⏭️  Skipping notebook validation: '{self.NOTEBOOKS_DIR}/' not found")
            return True

        self.context.current_state = WorkflowState.NOTEBOOK_VALIDATION
        print("\n📓 Validating Jupyter Notebooks...")
        self.context.attempts['notebook'] += 1

        # Check if nbstripout is available for cleaning outputs
        code, _, _ = self.run_command(["which", "nbstripout"])
        if code == 0:
            print("  Running nbstripout to clean notebook outputs...")
            self.run_command(
                ["nbstripout", "--extra-keys", "metadata.kernelspec", "*.ipynb"],
                cwd=self.NOTEBOOKS_DIR
            )

        # Validate notebook JSON structure
        code, stdout, stderr = self.run_command(
            ["python", "-c", """
import json
import sys
from pathlib import Path

notebooks = list(Path('.').glob('*.ipynb'))
errors = []
for nb in notebooks:
    try:
        with open(nb) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f'{nb}: {e}')

if errors:
    print('\\n'.join(errors))
    sys.exit(1)
print(f'Validated {len(notebooks)} notebook(s)')
"""],
            cwd=self.NOTEBOOKS_DIR
        )

        if code == 0:
            print(f"✅ Notebook validation passed. {stdout.strip()}")
            return True

        print(f"❌ Notebook validation failed:\n{stdout + stderr}")
        self.context.errors.append("Notebook validation failed.")
        return False

    # =========================================================================
    # Workflow Execution
    # =========================================================================

    def execute(self) -> bool:
        if not self.workflow_steps:
            print("No workflow steps loaded. Exiting.", file=sys.stderr)
            return False

        print("=" * 60)
        print(f"🚀 FilterBets Workflow Orchestrator")
        print(f"   Request Type: {self.context.request_type}")
        print("=" * 60)
        start_time = time.time()

        for step_func, step_name in self.workflow_steps:
            print(f"\n▶️  Executing Step: {step_name}")
            result = step_func()
            if result is False:
                self.context.current_state = WorkflowState.FAILED
                break
            if result == "SKIP_WORKFLOW":
                break

        duration = time.time() - start_time
        print("\n" + "=" * 60)

        final_status = WorkflowState.COMPLETED if not self.context.errors else WorkflowState.FAILED
        if final_status == WorkflowState.COMPLETED:
            print(f"✅ Workflow Completed Successfully in {duration:.2f}s")
        else:
            print(f"❌ Workflow Failed in {duration:.2f}s")
            print(f"   Errors: {', '.join(set(self.context.errors))}")

        if self.context.warnings:
            print(f"   Warnings: {', '.join(set(self.context.warnings))}")

        return final_status == WorkflowState.COMPLETED


def main():
    if len(sys.argv) < 2:
        print("Usage: ./git_workflow_orchestrator.py <request_type>", file=sys.stderr)
        print("\nAvailable types (defined in CLAUDE.md):", file=sys.stderr)
        print("  feat   - Full workflow for new features", file=sys.stderr)
        print("  bug    - Full workflow for bug fixes (alias: fix)", file=sys.stderr)
        print("  review - Read-only code review checks", file=sys.stderr)
        print("  data   - Data pipeline and notebook work", file=sys.stderr)
        sys.exit(1)

    orchestrator = AgentWorkflowOrchestrator(request_type=sys.argv[1].lower())

    if not orchestrator.execute():
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
