from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, func
from fastapi_filter.contrib.sqlalchemy import Filter


class Model(DeclarativeBase):
    pass

class UserOrm(Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    phone: Mapped[str|None]
    quiz = relationship('QuizOrm', backref='user')



quiz_question = Table('quiz_question', 
                      Model.metadata,
                      Column('quiz_id', ForeignKey('quiz.id'), primary_key=True),
                      Column('question_id', ForeignKey('question.id'), primary_key=True)
                      )


class QuizOrm(Model):
    __tablename__ = 'quiz'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    question = relationship("QuestionOrm", 
                                secondary="quiz_question", 
                                backref='quiz',
                                lazy='joined')


class QuestionOrm(Model):
    __tablename__ = 'question'
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(String(100))
    wrong1: Mapped[str] = mapped_column(String(100))
    wrong2: Mapped[str] = mapped_column(String(100))
    wrong3: Mapped[str] = mapped_column(String(100))


        
class UserFilter(Filter):
    name: str | None = None
    name__like: str | None = None
    name__startswith: str | None = None
    phone__in: list[str] | None = None
    

    order_by: list[str] = ['age']
    
    class Constants(Filter.Constants):
        model = UserOrm

