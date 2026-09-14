"""Mark completed ids in docs/TODO.md. Does not invent done work."""
from pathlib import Path

DONE = {
    "T004", "T005", "T006", "T020", "T023", "T024",
    "T030",
    "T033", "T034", "T035", "T036", "T037", "T038",
    "T039", "T040", "T041", "T042", "T043", "T044", "T045", "T046", "T047", "T048",
    "T049", "T052", "T053",
    "T058", "T059", "T060", "T061", "T062", "T063", "T064", "T065",
    "T067", "T068", "T069", "T070", "T071", "T072", "T073", "T074",
    "T080", "T081", "T082", "T084", "T085", "T086", "T087",
    "T185", "T186", "T187", "T194",
    "T197", "T198", "T200",
}

p = Path(__file__).resolve().parents[1] / "docs" / "TODO.md"
out = []
for line in p.read_text(encoding="utf-8").splitlines():
    for tid in DONE:
        needle = f"- [ ] **{tid}**"
        if needle in line:
            line = line.replace(needle, f"- [x] **{tid}**", 1)
    out.append(line)
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("updated", p)
