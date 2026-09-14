import json
from datetime import datetime, timezone
from pathlib import Path

p = Path(r"E:\LIQA\packaging\industry\agency-catalog.json")
data = json.loads(p.read_text(encoding="utf-8"))
for s in data.get("specialists") or []:
    sid = s.get("id") or ""
    s["path"] = f"agency-agents/.cursor/rules/{sid}.mdc" if sid else ""
data["agency_root"] = "agency-agents (set LIQA_AGENCY_HOME) or bundled"
data["exportedAt"] = datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("catalog portable", data["count"])
