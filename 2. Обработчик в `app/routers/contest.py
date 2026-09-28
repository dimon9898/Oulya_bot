@contest.message_callback(F.callback.payload.startswith('contest_my_votes_'))
async def contest_my_votes(event: MessageCallback, session: AsyncSession):
    await event.message.delete()
    contest_id = int(event.callback.payload.split('_')[3])
    contest_obj = await crq.get_active_contest(session, contest_id)
    if not contest_obj:
        await event.message.answer('Конкурс не найден.')
        return
    ...
