#!/usr/bin/env python3
"""Parse questions-source.txt and emit practice-questions.js"""
import re
import json
from pathlib import Path

SRC = Path(__file__).parent / "questions-source.txt"
OUT = Path(__file__).parent / "practice-questions.js"

MCQ_KEYS = {
    1: [1, 2, 0, 3, 2],
    2: [0, 1, 2, 1, 1],
    3: [1, 0, 2, 2],
    4: [1, 1, 2, 1, 1],
    5: [0, 1, 1, 0],
    6: [1, 2, 0, 2],
    7: [1, 2, 2],
    8: [1, 3, 2, 1, 3],
}

ORD = {
    "الأول": 1, "الثاني": 2, "الثالث": 3, "الرابع": 4,
    "الخامس": 5, "السادس": 6, "السابع": 7, "الثامن": 8,
}


def parse(text: str):
    lines = text.splitlines()
    sections, current, mode = [], None, None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("القسم"):
            if current:
                sections.append(current)
            lid = next((v for k, v in ORD.items() if k in line), None)
            title = line.split(":", 1)[-1].strip() if ":" in line else line
            current = {"id": lid, "title": title, "tf": [], "mcq": []}
            mode = None
            i += 1
            continue
        if not line:
            i += 1
            continue
        if "أسئلة الصواب" in line:
            mode, i = "tf", i + 1
            continue
        if "أسئلة الاختيار" in line:
            mode, i = "mcq", i + 1
            continue
        if not current:
            i += 1
            continue
        if mode == "tf":
            m = re.match(r"^\((صح|خطأ)\)\s*(.+)$", line)
            if m:
                current["tf"].append({"q": m.group(2).strip(), "a": m.group(1) == "صح"})
            i += 1
            continue
        if mode == "mcq":
            if re.match(r"^[أجبد]\)", line):
                i += 1
                continue
            q, opts = line, []
            i += 1
            while i < len(lines):
                ol = lines[i].strip()
                if not ol:
                    break
                om = re.match(r"^([أجبد])\)\s*(.+)$", ol)
                if om:
                    opts.append(om.group(2).strip())
                    i += 1
                else:
                    break
            if opts:
                idx = len(current["mcq"])
                keys = MCQ_KEYS.get(current["id"], [])
                ans = keys[idx] if idx < len(keys) else None
                current["mcq"].append({"q": q, "opts": opts, "a": ans})
            continue
        i += 1
    if current:
        sections.append(current)
    sections.append({
        "id": 9,
        "title": "أسئلة استرشادية — نفس أسئلة الدرس التاسع في المراجعة",
        "tf": [],
        "mcq": [],
        "useReviewQuiz": True,
    })
    return sections


def load_text():
    for p in (SRC, Path(__file__).parent / "اسئلة.txt"):
        if p.exists() and p.stat().st_size > 50:
            return p.read_text(encoding="utf-8")
    try:
        from questions_embed import QUESTIONS  # type: ignore
        return QUESTIONS
    except ImportError:
        raise SystemExit("Save اسئلة.txt or add questions_embed.py")


def main():
    text = load_text()
    SRC.write_text(text, encoding="utf-8")
    bank = parse(text)
    OUT.write_text(
        "const PRACTICE_BANK = " + json.dumps(bank, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    for s in bank:
        print(f"Lesson {s['id']}: {len(s['tf'])} TF, {len(s['mcq'])} MCQ")


if __name__ == "__main__":
    main()
