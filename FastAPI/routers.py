from fastapi import APIRouter, Depends, HTTPException
from schema import *
from database import UserRepository as ur, QuizRepository, QuestionRepository

user_router = APIRouter(
    prefix="/users", # слэш оставляем открытыми
    tags=['Пользователи']
)

default_router = APIRouter(
    prefix="/quiz", # слэш оставляем открытыми
    tags=['Квизы']
)



@default_router.get('/', tags=['api'])
async def index():
    return {'data':'ok'}


@user_router.get('')
async def get_users() -> list[User]:
    users = await ur.get_users()
    return users

@user_router.get('/{id}')
async def get_user(id) -> User:
    user = await ur.get_user(id=id)
    if user:
        return user
    # return {'err':"User not found"} # но тогда get_user(id) -> User | dict[str,str]
    raise HTTPException(status_code=404, detail="User not found")

@user_router.post('')
async def get_user(user:UserAdd = Depends()) -> UserId:
    id = await ur.add_user(user)
    return {'id':id}


class QuizCreate(BaseModel):
    title: str
    description: str | None

class QuestionCreate(BaseModel):
    quiz_id: int
    question_text: str

@default_router.post("/quizes", response_model=int)
async def create_quiz(quiz: QuizCreate):
    quiz_id = await QuizRepository.add_quiz(title=quiz.title, description=quiz.description)
    return quiz_id

@default_router.get("/quizes", response_model=list[QuizCreate])
async def read_quizzes():
    quizzes = await QuizRepository.get_quizzes()
    return quizzes

@default_router.get("/quizes/{id}", response_model=QuizCreate)
async def read_quiz(id: int):
    quiz = await QuizRepository.get_quiz(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@default_router.post("/questions", response_model=int)
async def create_question(question: QuestionCreate):
    question_id = await QuestionRepository.add_question(quiz_id=question.quiz_id, question_text=question.question_text)
    return question_id

@default_router.get("/questions", response_model=list[QuestionCreate])
async def read_questions():
    questions = await QuestionRepository.get_questions()
    return questions

@default_router.get("/questions/{id}", response_model=QuestionCreate)
async def read_question(id: int):
    question = await QuestionRepository.get_question(id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question




