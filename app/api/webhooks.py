import asyncio
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from maxapi.methods.types.getted_updates import process_update_webhook

from app.database.db_init import get_db
from app.routers.payment_notify import payment_notify

from app.bot_init import dp, bot






router = APIRouter()



@router.post('/webhook')
async def max_webhook(request: Request) -> JSONResponse:
    event_json = await request.json()
    event_object = await process_update_webhook(event_json=event_json, bot=bot)

    if event_object is None:
        return JSONResponse(content={'ok': True}, status_code=200)

    if dp.use_create_task:
        asyncio.create_task(dp.handle(event_object))
    else:
        await dp.handle(event_object)

    return JSONResponse(content={'ok': True}, status_code=200)




@router.post('/yookassa/webhook', status_code=status.HTTP_200_OK)
async def ykassa_webhook(request: Request, task: BackgroundTasks, session: AsyncSession = Depends(get_db)):
    payload = await request.json()
    
    if payload.get('event') == 'payment.succeeded':
        task.add_task(payment_notify, session, payload)

    return {'ok': True}    