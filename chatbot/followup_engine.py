
class FollowUpEngine:

    def __init__(self, retriever):
        self.retriever = retriever

    def generate(self, entity, current_fact_id, limit=3):

        if not entity or not isinstance(entity, str):
            return []

        if not isinstance(limit, int) or limit <= 0:
            return []

        documents = getattr(self.retriever, "documents", [])

        if not isinstance(documents, list):
            return []

        entity_name = entity.strip().casefold()
        current_id = str(current_fact_id or "")

        templates = {
            "landing_date": "When did {entity} land?",
            "scientific_objective": "What was the scientific objective of {entity}?",
            "marsquakes_recorded": "How many marsquakes did {entity} record?",
            "mission_end": "When did the {entity} mission end?",
            "wheel_count": "How many wheels did {entity} have?",
            "first_use": "When was {entity} first used?",
            "research_topics": "What research topics did {entity} study?",
            "components": "What were the main components of {entity}?",
            "deployment": "How was {entity} deployed?",
            "mission_objective": "What was the mission objective of {entity}?",
            "missions_used": "Which missions used {entity}?",
            "purpose": "What was the purpose of {entity}?"
        }

        related_facts = []

        for doc in documents:

            if not isinstance(doc, dict):
                continue

            doc_entity = str(
                doc.get("entity") or ""
            ).strip().casefold()

            fact_id = str(
                doc.get("fact_id", doc.get("id")) or ""
            )

            attribute = str(
                doc.get("attribute") or ""
            ).strip().casefold().replace("-", "_").replace(" ", "_")

            value = doc.get("value") or doc.get("content")

            if doc_entity != entity_name:
                continue

            if fact_id == current_id:
                continue

            if not value or not str(value).strip():
                continue

            if attribute not in templates:
                continue

            related_facts.append(attribute)

        questions = []
        seen = set()

        for attribute in related_facts:

            question = templates[attribute].format(
                entity=entity.strip()
            )

            normalized = question.casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            questions.append(question)

            if len(questions) >= limit:
                break

        return questions

