from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, BigInteger, ForeignKey, Numeric
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime



class Base(AsyncAttrs, DeclarativeBase):
    pass



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
    