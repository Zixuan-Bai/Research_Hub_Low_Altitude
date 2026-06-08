"""Extract conservative typed research atoms from item notes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import research_hub_lib as hub


ATOMS_PATH = Path("data/research_atoms.jsonl")
EVIDENCE_LABELS = {"paper-supported", "inferred", "proposal", "unsupported", "needs-review"}
SECTION_DEFAULT_TYPES = {
    "收录原因": "scenario",
    "核心内容": "problem",
    "方法 / 系统 / 政策细节": "method",
    "关键证据": "evidence",
    "图表与可视证据": "evidence",
    "局限性": "limitation",
    "与低空研究的关联": "scenario",
    "可复用参数 / 模型 / 基线": "parameter",
}
TYPE_KEYWORDS = [
    ("standard_constraint", ["policy", "regulation", "remote id", "u-space", "faa", "easa", "caac", "标准编号", "技术标准", "政策", "法规", "监管"]),
    ("assumption", ["assumption", "assume", "假设", "前提"]),
    ("limitation", ["limitation", "limit", "缺陷", "局限", "不足", "未考虑"]),
    ("metric", ["metric", "pdr", "latency", "throughput", "delay", "coverage", "指标", "时延", "吞吐", "覆盖率"]),
    ("baseline", ["baseline", "benchmark", "对比", "基线"]),
    ("model", ["model", "模型", "建模"]),
    ("parameter", ["parameter", "period", "frequency", "density", "range", "参数", "周期", "频率", "密度", "范围"]),
    ("open_question", ["open question", "future work", "needs-review", "问题", "待复核", "尚未"]),
]


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def split_note_sections(note: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(?P<title>.+?)\s*$", note, flags=re.MULTILINE))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(note)
        sections.append((match.group("title").strip(), note[match.end() : end].strip()))
    return sections


def evidence_and_text(line: str) -> tuple[str, str]:
    text = hub.markdown_plain(line.lstrip("-* "))
    match = re.match(r"^(paper-supported|inferred|proposal|unsupported|needs-review)\s*[:：]\s*(?P<body>.+)$", text)
    if not match:
        return "", ""
    return match.group(1), hub.normalize_space(match.group("body"))


def atom_type_for(section_title: str, text: str) -> str:
    lowered = text.lower()
    for atom_type, keywords in TYPE_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            return atom_type
    return SECTION_DEFAULT_TYPES.get(section_title, "evidence")


def confidence_for(evidence_label: str) -> str:
    if evidence_label == "paper-supported":
        return "medium"
    if evidence_label in {"inferred", "proposal"}:
        return "low"
    return "low"


def item_for_note(note_path: Path, items: list[dict]) -> dict:
    target = str(note_path)
    for item in items:
        if str(item.get("note_path") or "") == target:
            return item
    fallback = hub.make_item(title=note_path.stem, url="", source="local_note", source_type="paper", topic=hub.NEEDS_TOPIC_REVIEW)
    fallback["id"] = hub.stable_id("note", note_path.as_posix())
    fallback["note_path"] = target
    return fallback


def extract_atoms_from_item(item: dict) -> list[dict]:
    note_path = Path(str(item.get("note_path") or ""))
    if not note_path.exists():
        return []
    note = re.sub(r"<!-- item_reading_metadata.*?-->", "", note_path.read_text(encoding="utf-8", errors="replace"), flags=re.DOTALL)
    atoms: list[dict] = []
    for section_title, section in split_note_sections(note):
        if section_title in {"元数据", "推荐入库条目", "可靠性说明"}:
            continue
        for raw_line in section.splitlines():
            line = raw_line.strip()
            if not line.startswith(("-", "*")):
                continue
            evidence_label, text = evidence_and_text(line)
            if evidence_label not in EVIDENCE_LABELS or not text:
                continue
            if len(text) < 12:
                continue
            atom_type = atom_type_for(section_title, text)
            atoms.append(
                {
                    "atom_id": hub.stable_id(str(item.get("id") or ""), atom_type, evidence_label, text),
                    "item_id": str(item.get("id") or ""),
                    "topic": str(item.get("topic") or hub.NEEDS_TOPIC_REVIEW),
                    "atom_type": atom_type,
                    "text": text,
                    "evidence_label": evidence_label,
                    "source_note": note_path.as_posix(),
                    "confidence": confidence_for(evidence_label),
                    "created_at": hub.now_iso(),
                }
            )
    return atoms


def selected_items(items: list[dict], topic: str, note_path: Path | None) -> list[dict]:
    if note_path is not None:
        return [item_for_note(note_path, items)]
    if topic == "all":
        return [item for item in items if item.get("note_path")]
    return [item for item in hub.topic_items(items, topic) if item.get("note_path")]


def merge_atoms(existing: list[dict], extracted: list[dict], topic: str, note_path: Path | None) -> list[dict]:
    if note_path is not None:
        replaced_notes = {note_path.as_posix()}
        kept = [atom for atom in existing if atom.get("source_note") not in replaced_notes]
    elif topic == "all":
        kept = []
    else:
        kept = [atom for atom in existing if atom.get("topic") != hub.slugify(topic)]
    by_id = {atom["atom_id"]: atom for atom in kept if atom.get("atom_id")}
    for atom in extracted:
        by_id[atom["atom_id"]] = atom
    return sorted(by_id.values(), key=lambda row: (row.get("topic", ""), row.get("item_id", ""), row.get("atom_type", ""), row.get("text", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract typed research atoms from item notes.")
    parser.add_argument("--topic", default="all", help="Topic slug, or all.")
    parser.add_argument("--note", default="", help="Extract from one note path.")
    parser.add_argument("--dry-run", action="store_true", help="Print atoms without writing data/research_atoms.jsonl.")
    args = parser.parse_args()

    note_path = Path(args.note) if args.note else None
    if note_path is not None and not note_path.exists():
        print(f"Note not found: {note_path}")
        return 1

    items = hub.load_items()
    atoms: list[dict] = []
    for item in selected_items(items, args.topic, note_path):
        atoms.extend(extract_atoms_from_item(item))

    print(f"Extracted research atoms: {len(atoms)}")
    for atom in atoms[:50]:
        print(f"- {atom['topic']} | {atom['atom_type']} | {atom['evidence_label']} | {atom['text'][:120]}")
    if len(atoms) > 50:
        print(f"... {len(atoms) - 50} more")

    if args.dry_run:
        return 0

    merged = merge_atoms(read_jsonl(ATOMS_PATH), atoms, args.topic, note_path)
    write_jsonl(ATOMS_PATH, merged)
    print(f"Wrote: {ATOMS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
