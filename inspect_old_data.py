
import json

files = {
    "OLD": "data/processed/knowledge_base.json",
    "V2": "data/processed/knowledge_base_v2.json"
}

data = {}

for name, path in files.items():
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)

    data[name] = (
        obj if isinstance(obj, list)
        else obj.get("documents", [])
    )

print("\n========== OLD DOCUMENTS ==========")

for doc in data["OLD"]:
    print("\nENTITY:", doc.get("entity"))
    print("CATEGORY:", doc.get("category"))
    print("CONTENT:", doc.get("content"))
    print("SOURCE:", doc.get("source"))
    print("SOURCE URL:", doc.get("source_url"))

print("\n========== V2 FACTS BY ENTITY ==========")

for entity in sorted({
    d.get("entity") for d in data["V2"]
}):
    print("\nENTITY:", entity)

    for doc in data["V2"]:
        if doc.get("entity") == entity:
            print(
                "-",
                doc.get("attribute"),
                ":",
                doc.get("value")
            )
