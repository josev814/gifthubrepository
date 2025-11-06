from .celery_app import celery
from .email_sendgrid import send_email_sync
from .database import engine, get_engine, Session
from .models import Reservation, GiftItem
from datetime import datetime

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
            import asyncio
            from .broadcast import broadcast_message
            asyncio.get_event_loop().create_task(broadcast_message({
                "type": "reservation",
                "action": "expired",
                "gift_id": r.gift_id
            }))