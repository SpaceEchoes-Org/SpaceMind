import random


def generate_mcq(fact: dict, all_facts: list) -> dict:
    """Generate an entity-identification MCQ from a NASA fact."""

    correct_answer = fact["entity"]

    # Use distinct NASA entities as answer choices
    entities = list({
        item["entity"]
        for item in all_facts
        if item.get("entity") and item["entity"] != correct_answer
    })

    if len(entities) < 3:
        return None

    distractors = random.sample(entities, 3)
    choices = distractors + [correct_answer]
    random.shuffle(choices)

    question_text = (
        f"Which NASA mission or object is associated with "
        f"{fact['attribute'].replace('_', ' ')}: {fact['value']}?"
    )

    return {
        "question": question_text,
        "type": "mcq",
        "choices": choices,
        "correct_answer": correct_answer,
        "fact_id": fact["fact_id"]
    }


def generate_true_false(fact: dict) -> dict:
    """Generate a true/false question from a NASA fact."""

    return {
        "question": fact["content"],
        "type": "true_false",
        "correct_answer": True,
        "fact_id": fact["fact_id"]
    }