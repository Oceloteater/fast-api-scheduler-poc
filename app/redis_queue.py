from redis import Redis
from rq import Queue, Worker, Connection

redis_client = Redis(host="redis_container", port=6379)
queue = Queue(connection=redis_client)
