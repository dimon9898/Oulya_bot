def build_rules_text(contest_obj) -> str:
    """Возвращает текст правил конкурса.

    Если конкурс не передан или правила не заданы — возвращает
    заглушку по умолчанию.
    """
    return (
        contest_obj.rules
        if contest_obj and contest_obj.rules
        else 'Правила конкурса пока не заданы.'
    )
