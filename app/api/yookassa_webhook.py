from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_init import get_db
from app.routers.payment_notify import payment_notify

router = APIRouter(prefix='/yookassa')


@router.post('/webhook', status_code=status.HTTP_200_OK)
async def ykassa_webhook(request: Request, task: BackgroundTasks, session: AsyncSession = Depends(get_db)):
    payload = request.json()
    
    if payload.get('event') == 'payment.succeeded':
        task.add_task(payment_notify, session, payload)

    return {'ok': True}    