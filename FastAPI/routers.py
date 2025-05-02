from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_filter import FilterDepends

from models import UserFilter
from schema import *
from database import UserRepository as ur, QuizRepository as qr
from database import QuestionRepository as questr



default_router = APIRouter()

user_router = APIRouter(
    prefix="/users",
    tags=['Пользователи']
)

quiz_router = APIRouter(
    prefix="/quizes",
    tags=['Квизы']
)

question_router = APIRouter(
    prefix="/questions",
    tags=['Вопросы']
)


@default_router.get('/', tags=['api'])
async def index():
    return {'data': 'ok'}


# USER ------------------------
@user_router.get('')
async def get_users(
        limit: int = Query(ge=1, lt=10, default=3),
        offset: int = Query(ge=0, default=0),
        user_filter: UserFilter = FilterDepends(UserFilter)
) -> dict[str, int | list[User]]:
    users = await ur.get_users(limit, offset, user_filter)
    return {"data": users, "limit": limit, "offset": offset}



@user_router.get('/{id}')
async def get_user(id: int) -> User:
    user = await ur.get_user(id=id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@user_router.post('')
async def add_user(user: UserAdd = Depends()) -> UserId:
    id = await ur.add_user(user)
    return {'id': id}


# QUIZES ----------------------
@quiz_router.get('')
async def get_quizes() -> list[Quiz]:
    quizes = await qr.get_quizes()
    return quizes


@quiz_router.get('/{id}')
async def quiz(id: int) -> QuizWithQuestions:
    quiz = await qr.get_quiz(id=id)
    if quiz:
        return quiz
    raise HTTPException(status_code=404, detail="Quiz not found")


@quiz_router.get('/{id}/questions')
async def quiz_questions(id: int) -> list[Question]:
    quiz = await qr.get_quiz(id=id)
    if quiz:
        return quiz.question
    raise HTTPException(status_code=404, detail="Quiz not found")


@quiz_router.post('')
async def add_quiz(quiz: QuizAdd = Depends()):
    id = await qr.add_quiz(quiz)
    return {'id': id}


@quiz_router.post('/{quiz_id}/link')
async def link_quiz(quiz_id: int, question_id: int) -> dict[str, bool]:
    try:
        res = await qr.link_quiz(quiz_id, question_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {'res': bool(res)}

# QUESTIONS ----------------------

@question_router.get('')
async def get_questions(
    limit: int = Query(ge=1, lt=10, default=3),
    offset: int = Query(ge=0, default=0)
) -> dict[str, int | list[Question]]:
    questions = await questr.get_questions(limit, offset)
    return {"data": questions, "limit": limit, "offset": offset}


@question_router.get('/{id}')
async def get_question(id: int) -> Question:
    question = await questr.get_question(id=id)
    if question:
        return question
    raise HTTPException(status_code=404, detail="Question not found")


@question_router.post('')
async def add_question(question: QuestionAdd = Depends()) -> QuestionId:
    id = await questr.add_question(question)
    return {'id': id}







