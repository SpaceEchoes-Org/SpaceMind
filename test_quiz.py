from chatbot.quiz_engine import QuizEngine

engine = QuizEngine()

questions = engine.generate_quiz("mixed", 5)

answers = {}

for i, q in enumerate(questions):
    answers[q["question_id"]] = (
        q["correct_answer"] if i % 2 == 0
        else "WRONG_ANSWER"
    )

result = engine.score_quiz(questions, answers)

print("\nSCORING TEST")
print(result)