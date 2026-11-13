
import json
from pathlib import Path

files = [
    "data/processed/knowledge_base.json",
    "data/processed/knowledge_base_v2.json"
]

for file in files:
    path = Path(file)

    print("\n" + "=" * 60)
    print("FILE:", file)

    if not path.exists():
        print("NOT FOUND")
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = (
        data if isinstance(data, list)
        else data.get("documents", [])
    )

    print("TYPE:", type(data).__name__)
    print("TOTAL:", len(documents))

    entities = sorted({
        str(doc.get("entity"))
        for doc in documents
        if isinstance(doc, dict)
    })

    print("ENTITIES:")
    for entity in entities:
        print("-", entity)

    categories = sorted({
        str(doc.get("category"))
        for doc in documents
        if isinstance(doc, dict)
    })

    print("CATEGORIES:", categories)

print("\nCOMPARISON FINISHED")
