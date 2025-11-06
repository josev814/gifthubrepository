from datetime import datetime, timedelta
import asyncio, os

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select

from ..database import get_session
from ..models import GiftItem, Reservation
from ..schemas import ReservationCreate, ReservationRead
from ..auth import get_current_user
from ..tasks import send_reminder_email
from ..pubsub import pubsub

router = APIRouter(prefix='/api/reservations', tags=['reservations'])
REMINDER_OFFSET_MINUTES = int(os.environ.get('REMINDER_BEFORE_MINUTES', '10'))

class ReservationCreateModel:
    duration_minutes: int

@router.post('/{gift_id}', response_model=ReservationRead)
def reserve_gift(gift_id: int, data: ReservationCreate, session: Session = Depends(get_session), user = Depends(get_current_user)):
    gift = session.get(GiftItem, gift_id)
    if not gift:
        raise HTTPException(status_code=404, detail='Gift not found')
    if gift.bought:
        raise HTTPException(status_code=400, detail='Already bought')
    current_utc_time=datetime.now(datetime.timezone.utc)
    active_reservations = select(Reservation).where(
        Reservation.gift_id==gift_id, 
        Reservation.expires_at>current_utc_time, 
        Reservation.confirmed==False
    )
    existing = session.exec(active_reservations).first()
    if existing:
        raise HTTPException(
            status_code=409, 
            detail='Gift already reserved'
        )
    expires = current_utc_time + timedelta(minutes=int(data.get('duration_minutes', 60)))
    res = Reservation(gift_id=gift_id, user_id=user.id, reserved_at=current_utc_time, expires_at=expires, confirmed=False)
    session.add(res); session.commit(); session.refresh(res)
    # publish event
    expires_at_iso = res.expires_at.isoformat()
    asyncio.create_task(
        pubsub.publish({
            'type':'reservation',
            'action':'reserved',
            'gift_id':gift_id,
            'expires_at':expires_at_iso,
            'user_id': user.id
        })
    )
    # schedule reminder
    reminder_time = res.expires_at - timedelta(minutes=REMINDER_OFFSET_MINUTES)
    if reminder_time > current_utc_time:
        send_reminder_email.apply_async(
            args=[
                user.email,
                'Reservation expiring soon',
                f'Your reservation for gift {gift_id} will expire at {expires_at_iso} UTC'
            ],
            eta=reminder_time
        )
    return {'id': res.id, 'gift_id': gift_id, 'expires_at': expires_at_iso}

@router.post('/{gift_id}/confirm')
def confirm_purchase(gift_id: int, session: Session = Depends(get_session), user = Depends(get_current_user)):
    current_utc_time=datetime.now(datetime.timezone.utc)
    my_gift_reservation = select(Reservation).where(
        Reservation.gift_id==gift_id,
        Reservation.user_id==user.id,
        Reservation.expires_at>current_utc_time,
        Reservation.confirmed==False
    )
    res = session.exec(my_gift_reservation).first()
    if not res:
        raise HTTPException(status_code=400, detail='Reservation missing or expired')
    
    gift = session.get(GiftItem, gift_id)
    gift.bought = True
    res.confirmed = True
    session.add(gift)
    session.add(res)
    session.commit()

    asyncio.create_task(
        pubsub.publish({
            'type':'reservation',
            'action':'confirmed',
            'gift_id':gift_id,
            'user_id':user.id
        })
    )
    return {'message':'confirmed'}
