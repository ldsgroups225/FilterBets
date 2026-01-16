"""League schemas for API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class LeagueResponse(BaseModel):
    """League response schema."""

    id: int = Field(..., description="League database ID")
    season_type: int = Field(..., description="Season type identifier")
    year: int = Field(..., description="Season year")
    season_name: str = Field(..., description="Full season name")
    season_slug: str | None = Field(None, description="Season URL slug")
    league_id: int = Field(..., description="ESPN league ID")
    midsize_name: str | None = Field(None, description="Medium-length league name")
    league_name: str = Field(..., description="Full league name")
    league_short_name: str | None = Field(None, description="Short league name")
    logo_url: str | None = Field(None, description="League logo URL")
    created_at: datetime = Field(..., description="Record creation timestamp")

    class Config:
        from_attributes = True
