from maxapi.types import ButtonsPayload, Attachment
from maxapi.enums.attachment import AttachmentType

class InlineKeyboardBuilder:
    def __init__(self):
        self._buttons = []

    def add(self, *buttons):
        self._buttons.extend(buttons)
        return self

    def adjust(self, *row_sizes):
        rows = []
        btn_iter = iter(self._buttons)
        for size in row_sizes:
            row = []
            for _ in range(size):
                try:
                    row.append(next(btn_iter))
                except StopIteration:
                    break
            if row:
                rows.append(row)
        # если кнопки остались — добавляем по одной
        for btn in btn_iter:
            rows.append([btn])
        self._rows = rows
        return self

    def as_markup(self):
        return Attachment(
            type=AttachmentType.INLINE_KEYBOARD,
            payload=ButtonsPayload(buttons=self._rows)
        )