import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "knowledge_base_v2.json"


class QuizEngine:

    def __init__(self, data_path=DATA_PATH):
        self.data_path = Path(data_path)
        self.documents = self._load_data()

    def _load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("documents", [])

    @staticmethod
    def format_value(value):
        if isinstance(value, list):
            return ", ".join(str(x) for x in value)
        return str(value)

    def generate_quiz(self, quiz_type="mixed", num_questions=5):
        if quiz_type not in ("mcq", "true_false", "mixed"):
            raise ValueError("Invalid quiz type")

        questions = []

        for doc in self.documents:
            value = doc.get("value")
            if value is None:
                continue

            if quiz_type in ("mcq", "mixed"):
                q = self._make_mcq(doc)
                if q:
                    questions.append(q)

            if quiz_type in ("true_false", "mixed"):
                q = self._make_true_false(doc)
                if q:
                    questions.append(q)

        random.shuffle(questions)
        return questions[:max(1, num_questions)]

    def _make_mcq(self, doc):
        correct = self.format_value(doc["value"])
        candidates = []

        for item in self.documents:
            if item["fact_id"] == doc["fact_id"]:
                continue

            candidate = self.format_value(item.get("value"))

            if candidate != correct and candidate not in candidates:
                candidates.append(candidate)

        if len(candidates) < 3:
            return None

        options = random.sample(candidates, 3) + [correct]
        random.shuffle(options)

        return {
            "question_id": doc["fact_id"] + "_MCQ",
            "type": "mcq",
            "question": (
                f"What is the {doc['attribute'].replace('_', ' ')} "
                f"of {doc['entity']}?"
            ),
            "options": options,
            "correct_answer": correct,
            "explanation": doc.get("content", ""),
            "fact_id": doc["fact_id"]
        }

    def _make_true_false(self, doc):
        correct = self.format_value(doc["value"])
        candidates = []

        for item in self.documents:
            if item["fact_id"] == doc["fact_id"]:
                continue

            candidate = self.format_value(item.get("value"))

            if candidate != correct:
                candidates.append(candidate)

        if not candidates:
            return None

        is_true = random.choice([True, False])
        displayed = correct if is_true else random.choice(candidates)

        return {
            "question_id": doc["fact_id"] + "_TF",
            "type": "true_false",
            "question": (
                f"True or False: The {doc['attribute'].replace('_', ' ')} "
                f"of {doc['entity']} is {displayed}."
            ),
            "options": ["True", "False"],
            "correct_answer": "True" if is_true else "False",
            "explanation": doc.get("content", ""),
            "fact_id": doc["fact_id"]
        }

    @staticmethod
    def score_quiz(questions, answers):
        total = len(questions)
        results = []
        correct = 0

        for q in questions:
            answer = answers.get(q["question_id"])
            is_correct = (
                answer is not None
                and str(answer).strip().lower()
                == str(q["correct_answer"]).strip().lower()
            )

            if is_correct:
                correct += 1

            results.append({
                "question_id": q["question_id"],
                "user_answer": answer,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

        return {
            "total_questions": total,
            "correct_answers": correct,
            "wrong_answers": total - correct,
            "score_percentage": round(correct / total * 100, 2) if total else 0,
            "results": results
        }
