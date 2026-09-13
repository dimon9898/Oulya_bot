from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, BigInteger, ForeignKey, Numeric
from datetime import datetime

from app.database.base import Base


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID записи в БД
    user_id = mapped_column(BigInteger)  # ID пользователя в MAX (внешний идентификатор)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)  # Дата и время регистрации пользователя
    came_from: Mapped[str] = mapped_column(String(50), nullable=True)  # Источник прихода (deeplink/метка), откуда пришёл пользователь
    is_active: Mapped[bool] = mapped_column(default=True)  # Активен ли пользователь (не заблокировал бота и т.п.)
    
    purchases: Mapped[list['Purchase']] = relationship(back_populates='user')  # Список покупок пользователя



class Contest(Base):
    __tablename__ = 'contests'

    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID конкурса
    enabled: Mapped[bool] = mapped_column(default=False)  # Включён ли конкурс (виден ли пользователям)
    description: Mapped[str] = mapped_column(String(512), nullable=True)  # Описание конкурса
    title: Mapped[str] = mapped_column(String(128), nullable=True)  # Название конкурса
    rules: Mapped[str] = mapped_column(String(2048), nullable=True)  # Правила участия в конкурсе
    submission_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата/время начала приёма работ
    submission_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата/время окончания приёма работ
    voting_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата/время начала голосования
    voting_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата/время окончания голосования
    voting_open: Mapped[bool] = mapped_column(default=False)  # Открыто ли голосование вручную (флаг админа)
    results_published: Mapped[bool] = mapped_column(default=False)  # Опубликованы ли результаты конкурса

    works: Mapped[list['ContestWork']] = relationship(back_populates='contest')  # Список работ, поданных на конкурс


class ContestWork(Base):
    __tablename__ = 'contest_works'

    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID работы
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))  # ID конкурса, к которому относится работа
    number: Mapped[int] = mapped_column()  # Порядковый номер работы в рамках конкурса
    author_name: Mapped[str] = mapped_column(String(128))  # Имя автора работы
    author_age: Mapped[int] = mapped_column()  # Возраст автора (используется для определения категории)
    author_username: Mapped[str] = mapped_column(String(128), nullable=True)  # Username автора в MAX (если указан)
    user_id: Mapped[int] = mapped_column(BigInteger)  # ID пользователя MAX, отправившего работу
    category: Mapped[str] = mapped_column(String(16))  # Возрастная категория работы (определяется по возрасту)
    title: Mapped[str] = mapped_column(String(256))  # Название работы
    description: Mapped[str] = mapped_column(String(1024), nullable=True)  # Описание работы
    final_photo: Mapped[str] = mapped_column(String(512))  # Ссылка/ID финального фото работы
    process_photo: Mapped[str] = mapped_column(String(512))  # Ссылка/ID фото процесса создания
    extra_photo: Mapped[str] = mapped_column(String(512), nullable=True)  # Дополнительное фото (опционально)
    status: Mapped[str] = mapped_column(String(32), default='pending')  # Статус модерации: pending/approved/rejected
    moderation_comment: Mapped[str] = mapped_column(String(512), nullable=True)  # Комментарий модератора (при отклонении)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)  # Дата/время подачи работы

    contest: Mapped['Contest'] = relationship(back_populates='works')  # Конкурс, к которому относится работа
    votes: Mapped[list['ContestVote']] = relationship(back_populates='work')  # Голоса, отданные за эту работу


class ContestVoteSession(Base):
    __tablename__ = 'contest_vote_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID сессии голосования
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))  # ID конкурса, в котором голосует пользователь
    user_id: Mapped[int] = mapped_column(BigInteger)  # ID пользователя MAX, проходящего голосование
    order_json: Mapped[str] = mapped_column(String(8192))  # JSON-список ID работ в порядке показа пользователю
    current_index: Mapped[int] = mapped_column(default=0)  # Индекс текущей показываемой работы в order_json
    selected_json: Mapped[str] = mapped_column(String(4096), default='[]')  # JSON-список ID выбранных работ
    is_finished: Mapped[bool] = mapped_column(default=False)  # Завершена ли сессия голосования
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)  # Дата/время создания сессии
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)  # Дата/время последнего обновления сессии


class ContestVote(Base):
    __tablename__ = 'contest_votes'

    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID голоса
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))  # ID конкурса, в рамках которого отдан голос
    work_id: Mapped[int] = mapped_column(ForeignKey('contest_works.id'))  # ID работы, за которую отдан голос
    user_id: Mapped[int] = mapped_column(BigInteger)  # ID пользователя MAX, отдавшего голос
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)  # Дата/время голосования

    work: Mapped['ContestWork'] = relationship(back_populates='votes')  # Работа, за которую отдан голос
    


class Course(Base):
    __tablename__ = 'courses'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID курса
    title: Mapped[str] = mapped_column(String(50), nullable=False)  # Название курса
    description: Mapped[str] = mapped_column(String(1024), nullable=False)  # Описание курса
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Цена курса (0 — бесплатный)
    is_active: Mapped[bool] = mapped_column(default=True)  # Доступен ли курс для покупки/просмотра
    photo_type: Mapped[str] = mapped_column(String(3))  # Тип обложки: 'url' или 'id' (фото в MAX)
    photo_url: Mapped[str] = mapped_column(String(1024))  # Ссылка или ID обложки курса

    course_items: Mapped[list['CourseItem']] = relationship(back_populates='course')  # Уроки/материалы курса
    purchases: Mapped[list['Purchase']] = relationship(back_populates='course')  # Покупки этого курса
    

class CourseItem(Base):
    __tablename__ = 'course_items'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID элемента курса
    name: Mapped[str] = mapped_column(String(50), nullable=True)  # Название урока/материала
    description: Mapped[str] = mapped_column(String(768), nullable=True)  # Описание урока/материала
    category_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))  # ID курса, к которому относится элемент
    is_active: Mapped[bool] = mapped_column(default=1)  # Доступен ли элемент пользователям
    url: Mapped[str] = mapped_column(String(512), nullable=False)  # Ссылка на материал/урок
    template_url: Mapped[str] = mapped_column(String(512), nullable=False)  # Ссылка на шаблон/доп. материал
    
    course: Mapped['Course'] = relationship(back_populates='course_items')  # Курс, к которому относится элемент




class Purchase(Base):
    __tablename__ = 'purchases'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # Внутренний ID покупки
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))  # ID пользователя, совершившего покупку
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))  # ID купленного курса
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Стоимость покупки на момент оплаты
    payment_id: Mapped[str] = mapped_column(String(128), nullable=True)  # ID платежа в платёжной системе (ЮKassa)
    payment_status: Mapped[str] = mapped_column(String(20), default='pending')  # Статус платежа: pending/succeeded/canceled
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)  # Дата/время создания заказа
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)  # Дата/время последнего обновления записи
    paid_at: Mapped[bool] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата/время фактической оплаты
    
    user: Mapped['User'] = relationship(back_populates='purchases')  # Пользователь, совершивший покупку
    course: Mapped['Course'] = relationship(back_populates='purchases')  # Купленный курс
    
