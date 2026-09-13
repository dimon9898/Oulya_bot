from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, BigInteger, ForeignKey, Numeric
from datetime import datetime

from app.database.base import Base


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    came_from: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    purchases: Mapped[list['Purchase']] = relationship(back_populates='user')



class Contest(Base):
    __tablename__ = 'contests'

    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    title: Mapped[str] = mapped_column(String(128), nullable=True)
    rules: Mapped[str] = mapped_column(String(2048), nullable=True)
    submission_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    voting_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    voting_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    voting_open: Mapped[bool] = mapped_column(default=False)
    results_published: Mapped[bool] = mapped_column(default=False)

    works: Mapped[list['ContestWork']] = relationship(back_populates='contest')


class ContestWork(Base):
    __tablename__ = 'contest_works'

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))
    number: Mapped[int] = mapped_column()
    author_name: Mapped[str] = mapped_column(String(128))
    author_age: Mapped[int] = mapped_column()
    author_username: Mapped[str] = mapped_column(String(128), nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    category: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    final_photo: Mapped[str] = mapped_column(String(512))
    process_photo: Mapped[str] = mapped_column(String(512))
    extra_photo: Mapped[str] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default='pending')
    moderation_comment: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    contest: Mapped['Contest'] = relationship(back_populates='works')
    votes: Mapped[list['ContestVote']] = relationship(back_populates='work')


class ContestVoteSession(Base):
    __tablename__ = 'contest_vote_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))
    user_id: Mapped[int] = mapped_column(BigInteger)
    order_json: Mapped[str] = mapped_column(String(8192))
    current_index: Mapped[int] = mapped_column(default=0)
    selected_json: Mapped[str] = mapped_column(String(4096), default='[]')
    is_finished: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)


class ContestVote(Base):
    __tablename__ = 'contest_votes'

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.id'))
    work_id: Mapped[int] = mapped_column(ForeignKey('contest_works.id'))
    user_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    work: Mapped['ContestWork'] = relationship(back_populates='votes')
    


class Course(Base):
    __tablename__ = 'courses'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    photo_type: Mapped[str] = mapped_column(String(3))
    photo_url: Mapped[str] = mapped_column(String(1024))

    course_items: Mapped[list['CourseItem']] = relationship(back_populates='course')
    purchases: Mapped[list['Purchase']] = relationship(back_populates='course')
    

class CourseItem(Base):
    __tablename__ = 'course_items'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(768), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    is_active: Mapped[bool] = mapped_column(default=1)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    template_url: Mapped[str] = mapped_column(String(512), nullable=False)
    
    course: Mapped['Course'] = relationship(back_populates='course_items')   




class Purchase(Base):
    __tablename__ = 'purchases'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(128), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(20), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    paid_at: Mapped[bool] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped['User'] = relationship(back_populates='purchases')
    course: Mapped['Course'] = relationship(back_populates='purchases')    
    
