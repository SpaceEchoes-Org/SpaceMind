
import sys
from pathlib import Path


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from retrieval.retriever import build_retriever
from chatbot.followup_engine import FollowUpEngine


NOT_FOUND_MESSAGE = (
    "I don't have enough information in my NASA knowledge base "
    "to answer this question. Please try asking about a NASA "
    "mission or a topic covered by the available sources."
)


class NASAChatAssistant:

    def __init__(self, retriever):

        if retriever is None or not hasattr(retriever, "search"):
            raise TypeError("Invalid retriever.")

        self.retriever = retriever

        # Initialize Follow-up Questions Engine
        self.followup_engine = FollowUpEngine(retriever)

    @staticmethod
    def to_text(value):

        if value is None:
            return ""

        if isinstance(value, list):
            return ", ".join(str(item) for item in value)

        return str(value).strip()

    # Main chatbot function
    def answer_question(self, question):

        if not isinstance(question, str):
            return self.error_response(
                "Question must be a string."
            )

        question = question.strip()

        if not question:
            return self.error_response(
                "Question cannot be empty."
            )

        # Search knowledge base using BM25
        results = self.retriever.search(
            question,
            top_k=1
        )

        # No relevant information found
        if not results:
            return self.not_found_response(question)

        # Get best matching fact
        fact = results[0]

        evidence = self.to_text(
            fact.get("content")
        )

        value = self.to_text(
            fact.get("value")
        )

        entity = self.to_text(
            fact.get("entity")
        ) or None

        fact_id = self.to_text(
            fact.get("fact_id")
        ) or None

        # Build answer from retrieved information
        if evidence:

            answer = evidence

        elif value and entity:

            answer = f"{entity}: {value}."

        elif value:

            answer = value

        else:

            return self.not_found_response(question)

        # Generate related follow-up questions
        follow_up_questions = self.followup_engine.generate(
            entity=entity,
            current_fact_id=fact_id,
            limit=3
        )

        # Return structured chatbot response
        return {

            "success": True,

            "status": "answered",

            "question": question,

            "answer": answer,

            "entity": entity,

            "fact_id": fact_id,

            "attribute": self.to_text(
                fact.get("attribute")
            ) or None,

            "evidence": evidence or None,

            "source": self.to_text(
                fact.get("source")
            ) or None,

            "source_url": self.to_text(
                fact.get("source_url")
            ) or None,

            "verification_status": self.to_text(
                fact.get("verification_status")
            ) or "unknown",

            "follow_up_questions": follow_up_questions

        }

    # Out of knowledge base response
    @staticmethod
    def not_found_response(question):

        return {

            "success": False,

            "status": "not_found",

            "question": question,

            "answer": NOT_FOUND_MESSAGE,

            "entity": None,

            "fact_id": None,

            "attribute": None,

            "evidence": None,

            "source": None,

            "source_url": None,

            "verification_status": None,

            "follow_up_questions": []

        }

    # Invalid question response
    @staticmethod
    def error_response(message):

        return {

            "success": False,

            "status": "invalid_request",

            "question": None,

            "answer": message,

            "entity": None,

            "fact_id": None,

            "attribute": None,

            "evidence": None,

            "source": None,

            "source_url": None,

            "verification_status": None,

            "follow_up_questions": []

        }


# Create chatbot
def build_assistant():

    retriever = build_retriever()

    return NASAChatAssistant(retriever)


# Terminal interface
def main():

    try:

        assistant = build_assistant()

    except (FileNotFoundError, ValueError, OSError) as error:

        print(f"Could not start NASA SpaceMind: {error}")
        return

    print("=" * 58)

    print("NASA SpaceMind - Local Chatbot")

    print("Type 'exit' to stop.")

    print("=" * 58)

    while True:

        try:

            question = input("\nYou: ").strip()

        except (EOFError, KeyboardInterrupt):

            print("\nChat session ended.")
            break

        if question.lower() in {"exit", "quit"}:

            print("Chat session ended.")
            break

        if not question:
            continue

        response = assistant.answer_question(question)

        print("\nNASA SpaceMind:")
        print(response["answer"])

        if response["success"]:

            print("\nFact ID:", response["fact_id"])

            print("Source:", response["source"] or "Not supplied")

            print(
                "Source URL:",
                response["source_url"] or "Not supplied"
            )

            print(
                "Verification:",
                response["verification_status"]
            )

            print("\nFollow-up Questions:")

            for index, follow_up in enumerate(
                response["follow_up_questions"],
                start=1
            ):
                print(f"{index}. {follow_up}")


if __name__ == "__main__":

    main()
