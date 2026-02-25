import asyncio
import csv
from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.models.weather import WeatherRequest


async def seed():
    path = "data/india_cities.csv"
    async with AsyncSessionLocal() as session:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = row['name'].strip()
                lat = float(row['lat'])
                lon = float(row['lon'])
                # check exists
                exists = await session.execute(
                    WeatherRequest.__table__.select().where(WeatherRequest.location_name == name)
                )
                if exists.first():
                    continue

                req = WeatherRequest(
                    location_name=name,
                    latitude=lat,
                    longitude=lon,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow(),
                    weather_data=None,
                    aqi=None,
                    youtube_videos=None,
                    extra_metadata={"seeded": True},
                )
                session.add(req)
                await session.flush()
                count += 1
            await session.commit()
    print(f"Seeded {count} locations.")


if __name__ == '__main__':
    asyncio.run(seed())
