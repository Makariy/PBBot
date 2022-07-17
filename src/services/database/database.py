from tortoise import Tortoise


async def init_database():
    await Tortoise.init(
        db_url='sqlite://www/db.sqlite3',
        modules={
            'models': ['services.database.models']
        }
    )
    await Tortoise.generate_schemas()


async def stop_database():
    await Tortoise.close_connections()

