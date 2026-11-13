from typing import Any


VALID_QUESTION_TYPES = {"mcq", "true_false"}


def validate_question_type(question_type: str) -> bool:
    """Check whether the requested question type is supported."""
    return question_type in VALID_QUESTION_TYPES


def validate_num_questions(num_questions: int) -> bool:
    """Check whether the requested number of questions is valid."""
    return isinstance(num_questions, int) and not isinstance(num_questions, bool) and 1 <= num_questions <= 14


def validate_answer(question: dict[str, Any], answer: Any) -> bool:
    """Check whether an answer is valid for a question."""
    question_type = question.get("type")

    if question_type == "mcq":
        choices = question.get("choices", [])
        return isinstance(answer, str) and answer in choices

    if question_type == "true_false":
        return isinstance(answer, bool)

    return False