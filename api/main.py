
from contextlib import asynccontextmanager
from uuid import uuid4
from typing import Any, Optional
import re

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from quiz.quiz_generator import generate_quiz
from quiz.quiz_scorer import score_quiz
from chatbot.assistant import build_assistant

from images.nasa_image_search import (
    search_nasa_images,
    NASAImageSearchError
)


# Global chatbot instance
assistant = None

# Conversation memory
chat_sessions: dict[str, dict] = {}

# Temporary quiz storage
quiz_sessions: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global assistant

    assistant = build_assistant()

    yield

    assistant = None
    chat_sessions.clear()
    quiz_sessions.clear()


app = FastAPI(
    title="SpaceMind API",
    description="NASA Space Exploration Educational Chatbot",
    version="1.4.0",
    lifespan=lifespan
)


# =========================
# Request Models
# =========================

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: Optional[str] = None


class QuizRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=14)
    question_type: str = "mcq"


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: dict[str, Any]


# =========================
# Follow-up Question Engine
# =========================

def resolve_followup(
    question: str,
    previous_entity: Optional[str]
):
    if not previous_entity:
        return question

    q = question.strip()

    pronouns = (
        r"\bit\b",
        r"\bits\b",
        r"\bthey\b",
        r"\bthem\b",
        r"\bthis mission\b",
        r"\bthat mission\b",
        r"\bthere\b"
    )

    if any(
        re.search(pattern, q, re.IGNORECASE)
        for pattern in pronouns
    ):

        q = re.sub(
            r"\bit\b|\bits\b|\bthey\b|\bthem\b|"
            r"\bthis mission\b|\bthat mission\b|\bthere\b",
            previous_entity,
            q,
            flags=re.IGNORECASE
        )

    return q


# =========================
# Home Endpoint
# =========================

@app.get("/")
def home():

    return {
        "message": "Welcome to SpaceMind!",
        "status": "running",
        "version": "1.4.0"
    }


# =========================
# Chat Endpoint
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not initialized."
        )

    try:

        session_id = request.session_id or str(uuid4())

        session = chat_sessions.setdefault(
            session_id,
            {"entity": None}
        )

        original_question = request.question

        resolved_question = resolve_followup(
            original_question,
            session.get("entity")
        )

        response = assistant.answer_question(
            resolved_question
        )

        if response["status"] == "invalid_request":
            raise HTTPException(
                status_code=400,
                detail=response["answer"]
            )

        current_entity = response.get("entity")

        if current_entity:
            session["entity"] = current_entity

        response["question"] = original_question
        response["session_id"] = session_id

        return response

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(error)}"
        )


# =========================
# NASA Real Images Search
# =========================

@app.get("/images/search")
def nasa_images_search(

    query: str = Query(
        min_length=1,
        max_length=200,
        description="NASA image search query"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=5,
        ge=1,
        le=30
    )

):

    try:

        result = search_nasa_images(
            query=query,
            page=page,
            page_size=page_size
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except NASAImageSearchError as error:

        raise HTTPException(
            status_code=502,
            detail=f"NASA image service error: {str(error)}"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Image search error: {str(error)}"
        )


# =========================
# Start Quiz
# =========================

@app.post("/quiz/start")
def start_quiz(request: QuizRequest):

    if request.question_type not in {
        "mcq", "true_false", "mixed"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid question type."
        )

    try:

        quiz = generate_quiz(
            request.num_questions,
            request.question_type
        )

        if not quiz["questions"]:

            raise HTTPException(
                status_code=404,
                detail="No questions could be generated."
            )

        quiz_id = str(uuid4())

        quiz_sessions[quiz_id] = quiz["questions"]

        public_questions = [
            {
                key: value
                for key, value in question.items()
                if key != "correct_answer"
            }
            for question in quiz["questions"]
        ]

        return {
            "quiz_id": quiz_id,
            "total_questions": len(public_questions),
            "question_type": request.question_type,
            "questions": public_questions
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Submit Quiz
# =========================

@app.post("/quiz/submit")
def submit_quiz(submission: QuizSubmission):

    questions = quiz_sessions.get(submission.quiz_id)

    if questions is None:

        raise HTTPException(
            status_code=404,
            detail="Quiz not found or already submitted."
        )

    try:

        result = score_quiz(
            questions,
            submission.answers
        )

        del quiz_sessions[submission.quiz_id]

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


from contextlib import asynccontextmanager
from uuid import uuid4
from typing import Any, Optional
import re

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from quiz.quiz_generator import generate_quiz
from quiz.quiz_scorer import score_quiz
from chatbot.assistant import build_assistant

from images.nasa_image_search import (
    search_nasa_images,
    NASAImageSearchError
)


# Global chatbot instance
assistant = None

# Conversation memory
chat_sessions: dict[str, dict] = {}

# Temporary quiz storage
quiz_sessions: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global assistant

    assistant = build_assistant()

    yield

    assistant = None
    chat_sessions.clear()
    quiz_sessions.clear()


app = FastAPI(
    title="SpaceMind API",
    description="NASA Space Exploration Educational Chatbot",
    version="1.4.0",
    lifespan=lifespan
)


# =========================
# Request Models
# =========================

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: Optional[str] = None


class QuizRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=14)
    question_type: str = "mcq"


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: dict[str, Any]


# =========================
# Follow-up Question Engine
# =========================

def resolve_followup(
    question: str,
    previous_entity: Optional[str]
):
    if not previous_entity:
        return question

    q = question.strip()

    pronouns = (
        r"\bit\b",
        r"\bits\b",
        r"\bthey\b",
        r"\bthem\b",
        r"\bthis mission\b",
        r"\bthat mission\b",
        r"\bthere\b"
    )

    if any(
        re.search(pattern, q, re.IGNORECASE)
        for pattern in pronouns
    ):

        q = re.sub(
            r"\bit\b|\bits\b|\bthey\b|\bthem\b|"
            r"\bthis mission\b|\bthat mission\b|\bthere\b",
            previous_entity,
            q,
            flags=re.IGNORECASE
        )

    return q


# =========================
# Home Endpoint
# =========================

@app.get("/")
def home():

    return {
        "message": "Welcome to SpaceMind!",
        "status": "running",
        "version": "1.4.0"
    }


# =========================
# Chat Endpoint
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not initialized."
        )

    try:

        session_id = request.session_id or str(uuid4())

        session = chat_sessions.setdefault(
            session_id,
            {"entity": None}
        )

        original_question = request.question

        resolved_question = resolve_followup(
            original_question,
            session.get("entity")
        )

        response = assistant.answer_question(
            resolved_question
        )

        if response["status"] == "invalid_request":
            raise HTTPException(
                status_code=400,
                detail=response["answer"]
            )

        current_entity = response.get("entity")

        if current_entity:
            session["entity"] = current_entity

        response["question"] = original_question
        response["session_id"] = session_id

        return response

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(error)}"
        )


# =========================
# NASA Real Images Search
# =========================

@app.get("/images/search")
def nasa_images_search(

    query: str = Query(
        min_length=1,
        max_length=200,
        description="NASA image search query"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=5,
        ge=1,
        le=30
    )

):

    try:

        result = search_nasa_images(
            query=query,
            page=page,
            page_size=page_size
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except NASAImageSearchError as error:

        raise HTTPException(
            status_code=502,
            detail=f"NASA image service error: {str(error)}"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Image search error: {str(error)}"
        )


# =========================
# Start Quiz
# =========================

@app.post("/quiz/start")
def start_quiz(request: QuizRequest):

    if request.question_type not in {
        "mcq", "true_false", "mixed"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid question type."
        )

    try:

        quiz = generate_quiz(
            request.num_questions,
            request.question_type
        )

        if not quiz["questions"]:

            raise HTTPException(
                status_code=404,
                detail="No questions could be generated."
            )

        quiz_id = str(uuid4())

        quiz_sessions[quiz_id] = quiz["questions"]

        public_questions = [
            {
                key: value
                for key, value in question.items()
                if key != "correct_answer"
            }
            for question in quiz["questions"]
        ]

        return {
            "quiz_id": quiz_id,
            "total_questions": len(public_questions),
            "question_type": request.question_type,
            "questions": public_questions
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Submit Quiz
# =========================

@app.post("/quiz/submit")
def submit_quiz(submission: QuizSubmission):

    questions = quiz_sessions.get(submission.quiz_id)

    if questions is None:

        raise HTTPException(
            status_code=404,
            detail="Quiz not found or already submitted."
        )

    try:

        result = score_quiz(
            questions,
            submission.answers
        )

        del quiz_sessions[submission.quiz_id]

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

from contextlib import asynccontextmanager
from uuid import uuid4
from typing import Any, Optional
import re

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from quiz.quiz_generator import generate_quiz
from quiz.quiz_scorer import score_quiz
from chatbot.assistant import build_assistant

from images.nasa_image_search import (
    search_nasa_images,
    NASAImageSearchError
)


# Global chatbot instance
assistant = None

# Conversation memory
chat_sessions: dict[str, dict] = {}

# Temporary quiz storage
quiz_sessions: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global assistant

    assistant = build_assistant()

    yield

    assistant = None
    chat_sessions.clear()
    quiz_sessions.clear()


app = FastAPI(
    title="SpaceMind API",
    description="NASA Space Exploration Educational Chatbot",
    version="1.4.0",
    lifespan=lifespan
)


# =========================
# Request Models
# =========================

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: Optional[str] = None


class QuizRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=14)
    question_type: str = "mcq"


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: dict[str, Any]


# =========================
# Follow-up Question Engine
# =========================

def resolve_followup(
    question: str,
    previous_entity: Optional[str]
):
    if not previous_entity:
        return question

    q = question.strip()

    pronouns = (
        r"\bit\b",
        r"\bits\b",
        r"\bthey\b",
        r"\bthem\b",
        r"\bthis mission\b",
        r"\bthat mission\b",
        r"\bthere\b"
    )

    if any(
        re.search(pattern, q, re.IGNORECASE)
        for pattern in pronouns
    ):

        q = re.sub(
            r"\bit\b|\bits\b|\bthey\b|\bthem\b|"
            r"\bthis mission\b|\bthat mission\b|\bthere\b",
            previous_entity,
            q,
            flags=re.IGNORECASE
        )

    return q


# =========================
# Home Endpoint
# =========================

@app.get("/")
def home():

    return {
        "message": "Welcome to SpaceMind!",
        "status": "running",
        "version": "1.4.0"
    }


# =========================
# Chat Endpoint
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    if assistant is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not initialized."
        )

    try:

        session_id = request.session_id or str(uuid4())

        session = chat_sessions.setdefault(
            session_id,
            {"entity": None}
        )

        original_question = request.question

        resolved_question = resolve_followup(
            original_question,
            session.get("entity")
        )

        response = assistant.answer_question(
            resolved_question
        )

        if response["status"] == "invalid_request":
            raise HTTPException(
                status_code=400,
                detail=response["answer"]
            )

        current_entity = response.get("entity")

        if current_entity:
            session["entity"] = current_entity

        response["question"] = original_question
        response["session_id"] = session_id

        return response

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(error)}"
        )


# =========================
# NASA Real Images Search
# =========================

@app.get("/images/search")
def nasa_images_search(

    query: str = Query(
        min_length=1,
        max_length=200,
        description="NASA image search query"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=5,
        ge=1,
        le=30
    )

):

    try:

        result = search_nasa_images(
            query=query,
            page=page,
            page_size=page_size
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except NASAImageSearchError as error:

        raise HTTPException(
            status_code=502,
            detail=f"NASA image service error: {str(error)}"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Image search error: {str(error)}"
        )


# =========================
# Start Quiz
# =========================

@app.post("/quiz/start")
def start_quiz(request: QuizRequest):

    if request.question_type not in {
        "mcq", "true_false", "mixed"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid question type."
        )

    try:

        quiz = generate_quiz(
            request.num_questions,
            request.question_type
        )

        if not quiz["questions"]:

            raise HTTPException(
                status_code=404,
                detail="No questions could be generated."
            )

        quiz_id = str(uuid4())

        quiz_sessions[quiz_id] = quiz["questions"]

        public_questions = [
            {
                key: value
                for key, value in question.items()
                if key != "correct_answer"
            }
            for question in quiz["questions"]
        ]

        return {
            "quiz_id": quiz_id,
            "total_questions": len(public_questions),
            "question_type": request.question_type,
            "questions": public_questions
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Submit Quiz
# =========================

@app.post("/quiz/submit")
def submit_quiz(submission: QuizSubmission):

    questions = quiz_sessions.get(submission.quiz_id)

    if questions is None:

        raise HTTPException(
            status_code=404,
            detail="Quiz not found or already submitted."
        )

    try:

        result = score_quiz(
            questions,
            submission.answers
        )

        del quiz_sessions[submission.quiz_id]

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
