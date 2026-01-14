"""Tests for async backtest job management."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.models.backtest_job import BacktestJob
from app.models.filter import Filter
from app.models.fixture import Fixture
from app.models.league import League
from app.models.team import Team


class TestBacktestJobs:
    """Test async backtest job management."""

    @pytest.fixture
    async def setup_filter(self, db_session, test_user):
        """Set up test filter with data."""
        # Create league
        league = League(
            league_id=1,
            season_type=2024,
            year=2024,
            season_name="2024",
            league_name="Test League",
        )
        db_session.add(league)

        # Create teams
        team1 = Team(team_id=1, name="Team1", display_name="Team One")
        team2 = Team(team_id=2, name="Team2", display_name="Team Two")
        db_session.add_all([team1, team2])

        # Create filter
        filter_obj = Filter(
            user_id=test_user.id,
            name="Test Filter",
            description="Test filter for backtest",
            rules=[
                {
                    "field": "home_win_odds",
                    "operator": ">=",
                    "value": 1.5,
                }
            ],
            is_active=True,
        )
        db_session.add(filter_obj)

        # Create fixtures
        base_date = datetime(2024, 1, 1)
        fixtures = [
            Fixture(
                event_id=1,
                league_id=1,
                season_type=2024,
                match_date=base_date,
                home_team_id=1,
                away_team_id=2,
                home_team_score=2,
                away_team_score=1,
                status_id=3,
            ),
            Fixture(
                event_id=2,
                league_id=1,
                season_type=2024,
                match_date=base_date + timedelta(days=7),
                home_team_id=1,
                away_team_id=2,
                home_team_score=1,
                away_team_score=0,
                status_id=3,
            ),
        ]
        db_session.add_all(fixtures)
        await db_session.commit()
        await db_session.refresh(filter_obj)

        return filter_obj

    async def test_create_async_backtest_job(
        self, client, auth_headers, setup_filter
    ):
        """Test creating an async backtest job."""
        filter_obj = setup_filter

        response = await client.post(
            f"/api/v1/filters/{filter_obj.id}/backtest?async_mode=true",
            json={
                "bet_type": "home_win",
                "seasons": [2024],
                "stake": 10.0,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["progress"] == 0
        assert data["filter_id"] == filter_obj.id
        assert data["bet_type"] == "home_win"

    async def test_sync_backtest_still_works(
        self, client, auth_headers, setup_filter
    ):
        """Test that synchronous backtest still works (default behavior)."""
        filter_obj = setup_filter

        response = await client.post(
            f"/api/v1/filters/{filter_obj.id}/backtest",
            json={
                "bet_type": "home_win",
                "seasons": [2024],
                "stake": 10.0,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Sync response has backtest results, not job info
        assert "total_matches" in data
        assert "win_rate" in data
        assert "roi_percentage" in data
        assert "job_id" not in data

    async def test_list_backtest_jobs(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test listing backtest jobs."""
        filter_obj = setup_filter

        # Create some jobs
        jobs = [
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="completed",
                progress=100,
                bet_type="home_win",
                seasons="2024",
                result={"total_matches": 10, "win_rate": 60.0},
            ),
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="pending",
                progress=0,
                bet_type="away_win",
                seasons="2024",
            ),
        ]
        db_session.add_all(jobs)
        await db_session.commit()

        response = await client.get(
            "/api/v1/backtest/jobs",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["jobs"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 20

    async def test_list_backtest_jobs_with_status_filter(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test filtering backtest jobs by status."""
        filter_obj = setup_filter

        # Create jobs with different statuses
        jobs = [
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="completed",
                progress=100,
                bet_type="home_win",
                seasons="2024",
            ),
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="pending",
                progress=0,
                bet_type="away_win",
                seasons="2024",
            ),
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="failed",
                progress=50,
                bet_type="draw",
                seasons="2024",
                error_message="Test error",
            ),
        ]
        db_session.add_all(jobs)
        await db_session.commit()

        # Filter by completed
        response = await client.get(
            "/api/v1/backtest/jobs?status=completed",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["jobs"][0]["status"] == "completed"

    async def test_list_backtest_jobs_pagination(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test pagination of backtest jobs."""
        filter_obj = setup_filter

        # Create 25 jobs
        jobs = [
            BacktestJob(
                job_id=uuid4(),
                user_id=test_user.id,
                filter_id=filter_obj.id,
                status="completed",
                progress=100,
                bet_type="home_win",
                seasons="2024",
            )
            for _ in range(25)
        ]
        db_session.add_all(jobs)
        await db_session.commit()

        # Get first page
        response = await client.get(
            "/api/v1/backtest/jobs?page=1&page_size=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["jobs"]) == 10
        assert data["page"] == 1

        # Get second page
        response = await client.get(
            "/api/v1/backtest/jobs?page=2&page_size=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["jobs"]) == 10
        assert data["page"] == 2

    async def test_get_backtest_job_status(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test getting status of a specific backtest job."""
        filter_obj = setup_filter

        # Create a job
        job = BacktestJob(
            job_id=uuid4(),
            user_id=test_user.id,
            filter_id=filter_obj.id,
            status="running",
            progress=50,
            bet_type="home_win",
            seasons="2024",
            started_at=datetime.utcnow(),
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(job.job_id)
        assert data["status"] == "running"
        assert data["progress"] == 50

    async def test_get_backtest_job_not_found(self, client, auth_headers):
        """Test getting non-existent job returns 404."""
        fake_job_id = uuid4()

        response = await client.get(
            f"/api/v1/backtest/jobs/{fake_job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_backtest_job_other_user(
        self, client, auth_headers, db_session, setup_filter
    ):
        """Test that users cannot access other users' jobs."""
        filter_obj = setup_filter

        # Create a job for a different user
        from app.models.user import User

        other_user = User(
            email="other@example.com",
            password_hash="hashed",
        )
        db_session.add(other_user)
        await db_session.commit()

        job = BacktestJob(
            job_id=uuid4(),
            user_id=other_user.id,
            filter_id=filter_obj.id,
            status="completed",
            progress=100,
            bet_type="home_win",
            seasons="2024",
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_cancel_backtest_job(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test cancelling a pending backtest job."""
        filter_obj = setup_filter

        # Create a pending job
        job = BacktestJob(
            job_id=uuid4(),
            user_id=test_user.id,
            filter_id=filter_obj.id,
            status="pending",
            progress=0,
            bet_type="home_win",
            seasons="2024",
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.delete(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "cancelled" in response.json()["message"].lower()

        # Verify job status updated
        await db_session.refresh(job)
        assert job.status == "cancelled"

    async def test_cancel_completed_job_fails(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test that completed jobs cannot be cancelled."""
        filter_obj = setup_filter

        # Create a completed job
        job = BacktestJob(
            job_id=uuid4(),
            user_id=test_user.id,
            filter_id=filter_obj.id,
            status="completed",
            progress=100,
            bet_type="home_win",
            seasons="2024",
            result={"total_matches": 10},
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.delete(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "cannot cancel" in response.json()["detail"].lower()

    async def test_backtest_job_with_result(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test getting a completed job with results."""
        filter_obj = setup_filter

        # Create a completed job with results
        result_data = {
            "total_matches": 20,
            "winning_bets": 12,
            "losing_bets": 6,
            "push_bets": 2,
            "win_rate": 60.0,
            "roi_percentage": 15.5,
            "total_profit": 31.0,
        }

        job = BacktestJob(
            job_id=uuid4(),
            user_id=test_user.id,
            filter_id=filter_obj.id,
            status="completed",
            progress=100,
            bet_type="home_win",
            seasons="2024",
            result=result_data,
            started_at=datetime.utcnow() - timedelta(minutes=5),
            completed_at=datetime.utcnow(),
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["result"] is not None
        assert data["result"]["total_matches"] == 20
        assert data["result"]["win_rate"] == 60.0

    async def test_backtest_job_with_error(
        self, client, auth_headers, db_session, test_user, setup_filter
    ):
        """Test getting a failed job with error message."""
        filter_obj = setup_filter

        # Create a failed job
        job = BacktestJob(
            job_id=uuid4(),
            user_id=test_user.id,
            filter_id=filter_obj.id,
            status="failed",
            progress=30,
            bet_type="home_win",
            seasons="2024",
            error_message="Database connection timeout",
            started_at=datetime.utcnow() - timedelta(minutes=2),
            completed_at=datetime.utcnow(),
        )
        db_session.add(job)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/backtest/jobs/{job.job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "Database connection timeout"
        assert data["result"] is None
