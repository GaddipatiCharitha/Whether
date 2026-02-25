import asyncio
from app.db.session import AsyncSessionLocal
from app.repositories.weather_repository import WeatherRepository


async def main():
    async with AsyncSessionLocal() as session:
        repo = WeatherRepository(session)
        try:
            items, total = await repo.get_by_location('Hyderabad')
            print('TOTAL', total)
            for it in items[:5]:
                print(it.location_name, it.latitude, it.longitude)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
