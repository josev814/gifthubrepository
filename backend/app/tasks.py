from datetime import datetime

from sqlmodel import Session, select
import asyncio

from .celery_app import celery
from .email_sendgrid import send_email_sync
from .database import engine, Session
from .models import Reservation, GiftItem
from .pubsub import pubsub

@celery.task
def send_reminder_email(to_email: str, subject: str, body: str):
    return send_email_sync(to_email, subject, body)

@celery.task
def cleanup_expired_reservations():
    # placeholder: production should implement DB cleanup
    cur_utc_time = datetime.now(datetime.timezone.utc)
    with Session(engine) as session:
        stmt = select(Reservation).where(Reservation.expires_at < cur_utc_time, Reservation.confirmed == False)
        expired = session.exec(stmt).all()
        for r in expired:
            # delete reservation (make gift available again)
            session.delete(r)
            session.commit()
            # broadcast expiry
            asyncio.create_task(
                pubsub.publish({
                    'type':'reservation',
                    'action':'expired',
                    'gift_id': r.gift_id
                })
            )