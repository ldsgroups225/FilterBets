#!/usr/bin/env python3
"""Data Preparation Pipeline Runner - executes notebooks sequentially."""
import sys
import json
from pathlib import Path

def load_notebook(notebook_path: Path) -> dict:
    """Load a Jupyter notebook as JSON."""
    with open(notebook_path, 'r') as f:
        return json.load(f)

def extract_code_cells(notebook: dict) -> list:
    """Extract all code cells from a notebook."""
    code_cells = []
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            code = ''.join(source) if isinstance(source, list) else source
            if code.strip():
                code_cells.append(code)
    return code_cells

def run_notebook(notebook_path: Path) -> bool:
    """Run a notebook by executing its code cells."""
    print(f"\n{'='*60}\nRunning: {notebook_path.name}\n{'='*60}\n")
    try:
        notebook = load_notebook(notebook_path)
        code_cells = extract_code_cells(notebook)
        exec_globals = {'__name__': '__main__', '__file__': str(notebook_path)}
        exec("\n\n".join(code_cells), exec_globals)
        print(f"\n✅ {notebook_path.name} completed successfully")
        return True
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    notebooks_dir = Path(__file__).parent
    notebooks = [
        notebooks_dir / '01_data_exploration.ipynb',
        notebooks_dir / '02_data_cleaning.ipynb',
        notebooks_dir / '03_feature_engineering.ipynb',
        notebooks_dir / '04_data_export.ipynb'
    ]
    
    notebook_arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if notebook_arg != 'all':
        try:
            idx = int(notebook_arg) - 1
            notebooks = [notebooks[idx]] if 0 <= idx < len(notebooks) else notebooks
        except ValueError:
            pass
    
    results = [(nb.name, run_notebook(nb)) for nb in notebooks if nb.exists()]
    
    print(f"\n{'='*60}\nPIPELINE SUMMARY\n{'='*60}")
    for name, success in results:
        print(f"{'✅ PASS' if success else '❌ FAIL'}: {name}")
    
    return 0 if all(s for _, s in results) else 1

if __name__ == '__main__':
    sys.exit(main())
