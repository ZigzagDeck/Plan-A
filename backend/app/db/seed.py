"""Database seed script for Plan-A.

Populates initial risk cells and exposure assets for the North-Eastern Region (NER)
corridor in Arunachal Pradesh, enabling real-time risk simulation, alert policy testing,
and GIS visualization.
"""

import asyncio
import logging
from uuid import uuid4

from sqlalchemy import text

from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

SAMPLE_CELLS = [
    {
        "id": uuid4(),
        "cell_code": "NER-CELL-A17",
        "name": "Papum Pare Hill Section",
        "elevation_m": 820.0,
        "slope_deg": 42.5,
        "aspect_deg": 145.0,
        "geometry": "POLYGON((93.70 27.10, 93.80 27.10, 93.80 27.20, 93.70 27.20, 93.70 27.10))",
        "baseline_rainfall": 45.0,
    },
    {
        "id": uuid4(),
        "cell_code": "NER-CELL-B04",
        "name": "Lower Subansiri Escarpment",
        "elevation_m": 1150.0,
        "slope_deg": 48.0,
        "aspect_deg": 210.0,
        "geometry": "POLYGON((93.85 27.25, 93.95 27.25, 93.95 27.35, 93.85 27.35, 93.85 27.25))",
        "baseline_rainfall": 85.0,
    },
    {
        "id": uuid4(),
        "cell_code": "NER-CELL-C12",
        "name": "Kameng Valley Slope",
        "elevation_m": 450.0,
        "slope_deg": 24.0,
        "aspect_deg": 85.0,
        "geometry": "POLYGON((93.50 27.00, 93.60 27.00, 93.60 27.10, 93.50 27.10, 93.50 27.00))",
        "baseline_rainfall": 20.0,
    },
    {
        "id": uuid4(),
        "cell_code": "NER-CELL-D08",
        "name": "Itanagar Urban Ridge",
        "elevation_m": 720.0,
        "slope_deg": 36.5,
        "aspect_deg": 175.0,
        "geometry": "POLYGON((93.60 27.05, 93.70 27.05, 93.70 27.15, 93.60 27.15, 93.60 27.05))",
        "baseline_rainfall": 60.0,
    },
]

SAMPLE_ASSETS = [
    {
        "id": uuid4(),
        "asset_code": "AST-SCH-01",
        "asset_type": "SCHOOL",
        "name": "Papum Pare District High School",
        "geometry": "POINT(93.74 27.14)",
    },
    {
        "id": uuid4(),
        "asset_code": "AST-HSP-01",
        "asset_type": "HOSPITAL",
        "name": "Sub-divisional Medical Center",
        "geometry": "POINT(93.76 27.16)",
    },
    {
        "id": uuid4(),
        "asset_code": "AST-RD-NH13",
        "asset_type": "ROAD",
        "name": "National Highway NH-13 Corridor",
        "geometry": "POINT(93.75 27.15)",
    },
    {
        "id": uuid4(),
        "asset_code": "AST-BRG-03",
        "asset_type": "BRIDGE",
        "name": "Dikrong River Bridge",
        "geometry": "POINT(93.72 27.12)",
    },
    {
        "id": uuid4(),
        "asset_code": "AST-PWR-02",
        "asset_type": "POWER",
        "name": "Itanagar Main Substation",
        "geometry": "POINT(93.65 27.09)",
    },
    {
        "id": uuid4(),
        "asset_code": "AST-COM-01",
        "asset_type": "COMMUNICATION",
        "name": "Doordarshan Microwave Tower",
        "geometry": "POINT(93.88 27.29)",
    },
]


async def seed() -> None:
    logger.info("Connecting to database...")
    try:
        async with engine.begin() as connection:
            logger.info("Creating PostGIS extension if missing...")
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

            logger.info("Seeding risk cells...")
            for cell in SAMPLE_CELLS:
                await connection.execute(
                    text(
                        """
                        INSERT INTO risk_cells (
                            id, cell_code, geometry, elevation_m, slope_deg, aspect_deg
                        )
                        VALUES (
                            :id, :cell_code, ST_GeomFromText(:geometry, 4326),
                            :elevation_m, :slope_deg, :aspect_deg
                        )
                        ON CONFLICT (cell_code) DO UPDATE SET
                            elevation_m = EXCLUDED.elevation_m,
                            slope_deg = EXCLUDED.slope_deg,
                            aspect_deg = EXCLUDED.aspect_deg,
                            geometry = EXCLUDED.geometry;
                        """
                    ),
                    {
                        "id": cell["id"],
                        "cell_code": cell["cell_code"],
                        "geometry": cell["geometry"],
                        "elevation_m": cell["elevation_m"],
                        "slope_deg": cell["slope_deg"],
                        "aspect_deg": cell["aspect_deg"],
                    },
                )

            logger.info("Seeding exposure assets...")
            for asset in SAMPLE_ASSETS:
                await connection.execute(
                    text(
                        """
                        INSERT INTO assets (id, asset_code, asset_type, name, geometry)
                        VALUES (:id, :asset_code, :asset_type, :name, ST_GeogFromText(:geometry))
                        ON CONFLICT (asset_code) DO UPDATE SET
                            name = EXCLUDED.name,
                            asset_type = EXCLUDED.asset_type,
                            geometry = EXCLUDED.geometry;
                        """
                    ),
                    {
                        "id": asset["id"],
                        "asset_code": asset["asset_code"],
                        "asset_type": asset["asset_type"],
                        "name": asset["name"],
                        "geometry": asset["geometry"],
                    },
                )

        logger.info("Database seeding successfully completed!")
    except Exception as exc:
        logger.error(f"Seeding failed or database unreachable: {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(seed())
