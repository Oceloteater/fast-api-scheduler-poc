from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def background_task():
    print("Testing running background task!")
    # actual logic to go here


def schedule_tasks():
    scheduler.add_job(background_task, "interval", seconds=5)
