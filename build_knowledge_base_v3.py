
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path("data/processed")

OLD_FILE = BASE / "knowledge_base.json"
V2_FILE = BASE / "knowledge_base_v2.json"

BACKUP_DIR = BASE / "backups"
OUTPUT_FILE = BASE / "knowledge_base_v3_candidate.json"

# 1. Verify input files
for path in [OLD_FILE, V2_FILE]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

# 2. Never overwrite an existing candidate
if OUTPUT_FILE.exists():
    raise FileExistsError(
        f"{OUTPUT_FILE} already exists. "
        "Preserve it and choose another output filename."
    )

# 3. Read original databases
with open(OLD_FILE, encoding="utf-8") as f:
    old_data = json.load(f)

with open(V2_FILE, encoding="utf-8") as f:
    v2_data = json.load(f)

old_docs = (
    old_data if isinstance(old_data, list)
    else old_data.get("documents", [])
)

v2_docs = (
    v2_data if isinstance(v2_data, list)
    else v2_data.get("documents", [])
)

if not all(isinstance(x, dict) for x in old_docs + v2_docs):
    raise ValueError("Invalid document structure detected")

# 4. Create timestamped backups
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

shutil.copy2(
    OLD_FILE,
    BACKUP_DIR / f"knowledge_base_{timestamp}.json"
)

shutil.copy2(
    V2_FILE,
    BACKUP_DIR / f"knowledge_base_v2_{timestamp}.json"
)

# 5. Preserve old descriptive documents
documents = []

for doc in old_docs:
    record = dict(doc)
    record["record_id"] = doc.get("id")
    record["record_type"] = "overview"
    record["origin_file"] = OLD_FILE.name
    documents.append(record)

# 6. Preserve V2 structured facts
for doc in v2_docs:
    record = dict(doc)
    record["record_id"] = doc.get("fact_id")
    record["record_type"] = "fact"
    record["origin_file"] = V2_FILE.name
    documents.append(record)

# 7. Validate record IDs
record_ids = [doc["record_id"] for doc in documents]

if len(record_ids) != len(set(record_ids)):
    raise ValueError("Duplicate record IDs detected")

# 8. Build candidate database
knowledge_base = {
    "schema_version": "3.0-candidate",
    "total_documents": len(documents),
    "sources": [
        OLD_FILE.name,
        V2_FILE.name
    ],
    "documents": documents
}

# 9. Save without modifying original databases
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        knowledge_base,
        f,
        ensure_ascii=False,
        indent=2
    )

# 10. Verify output
with open(OUTPUT_FILE, encoding="utf-8") as f:
    check = json.load(f)

print("=" * 50)
print("KNOWLEDGE BASE V3 CANDIDATE CREATED")
print("=" * 50)
print("Overview records:",
      sum(d["record_type"] == "overview" for d in check["documents"]))
print("Fact records:",
      sum(d["record_type"] == "fact" for d in check["documents"]))
print("Total records:", len(check["documents"]))
print("Backup directory:", BACKUP_DIR)
print("Output:", OUTPUT_FILE)
print("Original files preserved: YES")
