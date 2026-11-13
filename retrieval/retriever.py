
from pathlib import Path
from importlib.machinery import SourcelessFileLoader
from importlib.util import spec_from_loader, module_from_spec

# Load original compiled retriever
backup_path = Path(__file__).with_name("retriever_backup.pyc")

if not backup_path.exists():
    raise FileNotFoundError(f"Backup not found: {backup_path}")

loader = SourcelessFileLoader(
    "retrieval._retriever_backup",
    str(backup_path)
)

spec = spec_from_loader(
    "retrieval._retriever_backup",
    loader
)

_backup = module_from_spec(spec)
loader.exec_module(_backup)

# Explicit declarations for Pylance
BM25Retriever = getattr(_backup, "BM25Retriever")
main = getattr(_backup, "main")

# Restore original module functions
globals().update({
    name: value
    for name, value in vars(_backup).items()
    if not name.startswith("__")
})

# Preserve original intent detector
_original_detect_intent = BM25Retriever._detect_intent


# Fix mission end detection
def _detect_intent_fixed(self, question):
    q = self._clean_question(question).lower()

    mission_end_terms = (
        "mission end",
        "mission ended",
        "mission end date",
        "end of the mission",
        "when did the mission end",
        "when did insight end",
        "when did the insight lander mission end",
        "mission termination",
        "mission concluded",
        "when was the mission over",
        "when did insight stop operating",
    )

    if any(term in q for term in mission_end_terms):
        return "mission_end"

    return _original_detect_intent(self, question)


BM25Retriever._detect_intent = _detect_intent_fixed


if __name__ == "__main__":
    main()
