import logging
from datetime import datetime
from rq import Queue, Worker, Connection
from apscheduler.schedulers.background import BackgroundScheduler

from app.main import get_announcement_by_id, update_announcement_status
from app.models import AnnouncementStatus
from app.redis_queue import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_worker():
    # Create a worker and specify the Redis queue
    with Connection(queue.connection):
        worker = Worker([queue])
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_queue, 'interval', seconds=5)  # Should be process_announcements()
        scheduler.start()
        worker.work()


# def process_announcements():
#     for job in queue.jobs:
#         # Get the announcement details from the job
#         task_kwargs = job.kwargs
#         announcement_id = task_kwargs.get('announcement_id')
#         send_at = task_kwargs.get('send_at')
#
#         # Check if it's time to send the announcement
#         if datetime.now() >= send_at:
#             # Retrieve the announcement from the database based on the announcement_id
#             announcement = get_announcement_by_id(announcement_id)
#             if announcement.status == "pending":
#                 # Send the announcement
#                 #  send_announcement(announcement.message) #  This should have been the WhatsApp API call
#                 print(f"Announcement sent: {announcement}")
#                 update_announcement_status(announcement_id, AnnouncementStatus.sent)
#                 job.delete()  # Remove the job from the queue after processing
#             else:
#                 print(f"Announcement status not suitable for sending: {announcement.status}")
#         else:
#             print(f"Not time to send announcement yet: {announcement_id}")


def check_queue():
    """
    Just for sanity checking the job queue while debugging
    """
    logger.info("Checking job queue for pending tasks...")

    logger.info(f"Jobs: {queue.jobs}")

    for job in queue.jobs:
        logger.info(f"----- Job {job}")

        # Extract task keyword arguments
        task_kwargs = job.kwargs
        announcement_id = task_kwargs.get('announcement_id')
        send_at = task_kwargs.get('send_at')

        print(f"Announcement ID: {announcement_id}")
        print(f"Send At: {send_at}")


if __name__ == '__main__':
    start_worker()
