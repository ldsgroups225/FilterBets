"""CLI script to ingest CSV data into the database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import async_session_maker
from app.services.data_ingestion import DataIngestionService


async def main() -> None:
    """Run data ingestion."""
    print("Starting data ingestion...")
    print("-" * 50)

    # Check data directory
    data_dir = Path(__file__).parent.parent.parent / "data" / "base_data"
    print(f"Data directory: {data_dir}")
    print(f"Data directory exists: {data_dir.exists()}")
    if data_dir.exists():
        csv_files = list(data_dir.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files")

    async with async_session_maker() as session:
        service = DataIngestionService(session, data_dir)
        results = await service.ingest_all()

    print("\nData ingestion completed!")
    print("-" * 50)
    print("Results:")
    for entity, count in results.items():
        print(f"  {entity}: {count} records inserted")
    print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
