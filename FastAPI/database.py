from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import select, Integer, ForeignKey, String, Table, Column, func

from schema import UserAdd
from datetime import datetime

import os

BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, 'fastapi.db')

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
# engine = create_async_engine("sqlite+aiosqlite:///example//fastapi//db//fastapi.db")
# engine = create_async_engine("sqlite+aiosqlite:///db//fastapi.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass

class UserOrm(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    phone: Mapped[str | None]
    # quiz = relationship('QuizOrm', backref='user')


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


async def add_test_data():
    async with new_session() as session:
        users = [
            UserOrm(name='user1', age=20),
            UserOrm(name='user2', age=30, phone='123456789')
        ]

        session.add_all(users)
        await session.flush()
        await session.commit()


class UserRepository:

    @classmethod
    async def add_user(cls, user: UserAdd) -> int:
        async with new_session() as session:
            data = user.model_dump()
            print(data)
            user = UserOrm(**data)
            session.add(user)
            await session.flush()
            await session.commit()
            return user.id

    @classmethod
    async def get_users(cls) -> list[UserOrm]:
        async with new_session() as session:
            query = select(UserOrm)
            res = await session.execute(query)
            users = res.scalars().all()
            return users

    @classmethod
    async def get_user(cls, id) -> UserOrm:
        async with new_session() as session:
            query = select(UserOrm).filter(UserOrm.id == id)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            res = await session.execute(query)
            user = res.scalars().first()
            return user



class QuizOrm(Model):
    __tablename__ = 'quizzes'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None]

class QuestionOrm(Model):
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'))
    question_text: Mapped[str]
    quiz: Mapped[QuizOrm] = relationship("QuizOrm", back_populates="questions")

QuizOrm.questions = relationship("QuestionOrm", order_by=QuestionOrm.id, back_populates="quiz")

class QuizRepository:

    @classmethod
    async def add_quiz(cls, title: str, description: str) -> int:
        async with new_session() as session:
            quiz = QuizOrm(title=title, description=description)
            session.add(quiz)
            await session.commit()
            return quiz.id

    @classmethod
    async def get_quizzes(cls) -> list[QuizOrm]:
        async with new_session() as session:
            query = select(QuizOrm)
            res = await session.execute(query)
            quizzes = res.scalars().all()
            return quizzes

    @classmethod
    async def get_quiz(cls, id: int) -> QuizOrm:
        async with new_session() as session:
            query = select(QuizOrm).filter(QuizOrm.id == id)
            res = await session.execute(query)
            quiz = res.scalars().first()
            return quiz


class QuestionRepository:

    @classmethod
    async def add_question(cls, quiz_id: int, question_text: str) -> int:
        async with new_session() as session:
            question = QuestionOrm(quiz_id=quiz_id, question_text=question_text)
            session.add(question)
            await session.commit()
            return question.id

    @classmethod
    async def get_questions(cls) -> list[QuestionOrm]:
        async with new_session() as session:
            query = select(QuestionOrm)
            res = await session.execute(query)
            questions = res.scalars().all()
            return questions

    @classmethod
    async def get_question(cls, id: int) -> QuestionOrm:
        async with new_session() as session:
            query = select(QuestionOrm).filter(QuestionOrm.id == id)
            res = await session.execute(query)
            question = res.scalars().first()
            return question
