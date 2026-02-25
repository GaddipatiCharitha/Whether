import asyncio
from app.db.session import AsyncSessionLocal
from app.services.weather_application_service import WeatherApplicationService


async def main():
    async with AsyncSessionLocal() as session:
        service = WeatherApplicationService(session)
        try:
            items, total = await service.get_all_weather_requests(0, 5)
            print('TOTAL', total)
            for it in items:
                print(type(it), it.model_dump() if hasattr(it, 'model_dump') else it)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
