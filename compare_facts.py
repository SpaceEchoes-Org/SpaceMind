
import json
from pathlib import Path

def load_docs(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, list) else data.get("documents", [])

old = load_docs("data/processed/knowledge_base.json")
new = load_docs("data/processed/knowledge_base_v2.json")

def get_fact(doc):
    return (
        doc.get("entity"),
        doc.get("attribute"),
        str(doc.get("value", "")).strip()
    )

old_facts = {get_fact(d) for d in old if isinstance(d, dict)}
new_facts = {get_fact(d) for d in new if isinstance(d, dict)}

print("=" * 60)
print("FACT COMPARISON")
print("=" * 60)

print("OLD FACTS:", len(old_facts))
print("V2 FACTS:", len(new_facts))

print("\nFACTS ONLY IN OLD:")
for fact in sorted(old_facts - new_facts):
    print(fact)

print("\nFACTS ONLY IN V2:")
for fact in sorted(new_facts - old_facts):
    print(fact)

print("\nCOMMON FACTS:", len(old_facts & new_facts))

print("\nDOCUMENT FIELDS:")
for name, docs in [("OLD", old), ("V2", new)]:
    print("\n", name)
    if docs and isinstance(docs[0], dict):
        print(sorted(docs[0].keys()))
        print("SAMPLE:", docs[0])

print("\nCOMPARISON COMPLETE")
