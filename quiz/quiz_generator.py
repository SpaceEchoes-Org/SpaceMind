import json
import random
from pathlib import Path

from quiz.question_generator import generate_mcq, generate_true_false
from quiz.validators import validate_num_questions, validate_question_type


DEFAULT_DATA_PATH = Path("data/processed/knowledge_base_v2.json")


def load_facts(data_path=DEFAULT_DATA_PATH):
    """Load NASA facts from the knowledge base."""

    with open(data_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    facts = data.get("documents", [])

    if not facts:
        raise ValueError("No facts found in the knowledge base.")

    return facts


def generate_quiz(num_questions=5, question_type="mixed"):
    """Generate a quiz using facts from the NASA knowledge base."""

    if not validate_num_questions(num_questions):
        raise ValueError("Number of questions must be between 1 and 14.")

    if question_type not in {"mixed", "mcq", "true_false"}:
        raise ValueError("Invalid question type.")

    facts = load_facts()
    random.shuffle(facts)

    questions = []

    for fact in facts:
        if len(questions) >= num_questions:
            break

        selected_type = question_type

        if selected_type == "mixed":
            selected_type = random.choice(["mcq", "true_false"])

        if selected_type == "mcq":
            question = generate_mcq(fact, facts)

            # Skip MCQs that do not have enough choices
            if len(question["choices"]) < 2:
                continue

        else:
            question = generate_true_false(fact)

        question["question_id"] = f"Q{len(questions) + 1:03d}"
        questions.append(question)

    return {
        "total_questions": len(questions),
        "questions": questions
    }