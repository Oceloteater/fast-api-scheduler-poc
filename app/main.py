from fastapi import FastAPI
from typing import Union
from app.tasks import scheduler, schedule_tasks

app = FastAPI()


@app.on_event("startup")
def startup_event():
    schedule_tasks()
    scheduler.start()
    print(f"Scheduler started: {scheduler}")


@app.get("/")
async def root():
    return {"message": "FastAPI app with background task!"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
