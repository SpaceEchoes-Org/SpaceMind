from quiz.validators import validate_answer


def score_quiz(questions: list, answers: dict) -> dict:
    """Evaluate submitted answers and calculate the quiz score."""

    if not isinstance(answers, dict):
        raise ValueError("Answers must be a dictionary.")

    question_ids = {
        question["question_id"]
        for question in questions
    }

    unknown_ids = set(answers.keys()) - question_ids

    if unknown_ids:
        raise ValueError(f"Unknown question IDs: {unknown_ids}")

    results = []
    correct_count = 0

    for question in questions:
        question_id = question["question_id"]
        user_answer = answers.get(question_id)

        if user_answer is None:
            is_correct = False
            status = "unanswered"
        else:
            if not validate_answer(question, user_answer):
                raise ValueError(
                    f"Invalid answer for {question_id}"
                )

            is_correct = (
                user_answer == question["correct_answer"]
            )

            status = "correct" if is_correct else "incorrect"

        if is_correct:
            correct_count += 1

        results.append({
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "status": status
        })

    total = len(questions)

    percentage = (
        round((correct_count / total) * 100, 2)
        if total else 0
    )

    return {
        "total_questions": total,
        "correct_answers": correct_count,
        "wrong_answers": total - correct_count,
        "score_percentage": percentage,
        "results": results
    }