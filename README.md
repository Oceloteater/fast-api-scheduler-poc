# Announcement Scheduler

### Running on macOS:

1. Pull down the repo: `git clone https://github.com/Oceloteater/fast-api-scheduler-poc.git`
2. Ensure you have Docker Desktop installed and running - https://docs.docker.com/desktop/install/mac-install/
3. Navigate to the root dir and run `docker-compose up -d --build`
4. Hit http://localhost:8000/docs#/ to view the swagger docs
5. Add announcements to the queue via POST `/api/v1/announcements`
6. Worthwhile logging can be found in the `app-1` and `worker-1` containers

### Notes:

- Db container looks unstable because previously supported docker image of sqlite not longer available so had to use community edition which doesn't support M2 chip. Despite that, db behaves as normal - no loss of data.
- This project is not complete due to time constraints, however next steps are to implement the following scheduling component for Redis Queue - https://python-rq.org/docs/scheduling/

### Technologies used in this project:
- https://fastapi.tiangolo.com/
- https://www.uvicorn.org/
- https://apscheduler.readthedocs.io/
- https://www.sqlalchemy.org/
- https://redis.io/docs/get-started/
- https://python-rq.org/

