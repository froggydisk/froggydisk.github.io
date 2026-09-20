#!/usr/bin/env python3
"""references/korean.md의 ✕ 열을 그대로 검사로 돌린다.

    python3 .claude/skills/book-chapter/scripts/check-rules.py [원고...]

korean.md의 ✕ 표는 **첫 열이 ✕**다. 다만 첫 열이 ✕가 아닌 표도 있어서(§14의 `건너뛴 자리`)
**머리글로 가려 읽는다**(BAD_HEAD). 그 열의 백틱 문구와 코드블록의 `✕ ` 줄을 뽑아 원고에서 찾는다.
규칙을 새로 적으면 검사도 같이 늘어나므로 **문서와 검사가 어긋날 수 없다.**

**✕가 ✓의 부분 문자열인 자리는 건너뛴다.** `나흘 사이에 일어난 일이다` ✕ →
`고작 나흘 사이에 일어난 일이다` ✓처럼 부사 하나를 얹는 교정이 많아서, 그냥 찾으면
고쳐 놓은 문장이 다시 걸린다.

**낱말이 아니라 꼴을 적고 싶으면 백틱 안을 `re:`로 시작한다.** 그 뒤는 정규식으로 읽는다.
2026-09-19에 `네 번의 실패`가 §7을 통과해서 넣었다 — 그 절의 원리(`A의 N 가지 B`)는 산문에
있었는데 검사가 읽는 것은 ✕ 열의 낱말(`데모의 네 가지 실패`)뿐이라, 같은 부류의 새 문장은
영영 안 걸렸다. **원리를 적었으면 그 절에 `re:` 한 줄을 같이 둔다.**

`~`는 아무 말이나 오는 자리로 본다. `·`로 나열된 문구는 각각 따로 본다.
정상 용례는 ALLOW에 이유와 함께 적는다 — 빼는 것이 아니라 왜 남기는지를 적는 자리다.
"""
import re
import sys
import pathlib

SKILL = pathlib.Path(__file__).resolve().parent.parent
KOREAN = SKILL / "references" / "korean.md"

# 원고에 그대로 있어도 맞는 것. (검사에서 뺀 이유를 반드시 적는다)
# 규칙 이름이 그대로 여기 있으면 그 규칙을 통째로 빼고, `re:` 꼴 규칙에서는
# **일치한 문구 안에 이 말이 들어 있으면 그 자리만** 넘어간다
ALLOW = {
    "붙는다": "부품이 기판에 실장된다는 뜻이면 맞다 (§3)",
    "붙이기도 한다": "프롬프트·질문 뒤에 붙이는 것은 맞다 (§8)",
    "정확했다": "§8이 `틀린 데가 없었다`의 고침으로 정한 말",
    "문제가 발생했다": "굳은 연어라 그냥 쓴다 (§10)",
    "셈이다": "숫자를 흐리면 ✕, 화자의 짐작이면 ✓ (§18)",
    "편이다": "위와 같다 (§18)",
    "남는다": "사람이 기록을 남기거나 구체물이 남으면 맞다 (§7)",
    "다만 ": "역접 접속사로 정상. §1이 막는 것은 `다만 이 다섯은 ~ 센 것이다` 꼴이다",
    "대체로": "§18의 얼버무리기 검사와 겹친다. check-prose 쪽에서 본다",
    "세 요소": "『컴퓨터 구성요소』 전용 항목",
    "한 번의": "굳은 짝이라 둔다 — `한 번의 처리` · `한 번의 요청` (§2)",
    "다섯 장치": "『컴퓨터 구성요소』 전용 항목",
}


# 첫 열이 ✕인 표의 머리글. 이 목록에 없는 표는 읽지 않는다
BAD_HEAD = ("✕", "쓴 말", "만든 말", "사실만")


def rules():
    """(절 제목, ✕ 문구, ✓ 문구들) 목록."""
    out, sec, read = [], "(머리말)", False
    for line in KOREAN.read_text(encoding="utf-8").split("\n"):
        if line.startswith("## "):
            sec, read = line[3:].strip(), False
        elif re.fullmatch(r"\|[\s\-:|]+\|", line or " "):
            continue
        elif line.startswith("|"):
            cells = line.split("|")[1:-1]
            head = cells[0].strip()
            if any(head.startswith(h) for h in BAD_HEAD):
                read = True
                continue
            if not read:
                continue
            # ✓ 열이 `X → Y` 꼴이면 화살표 왼쪽은 ✓가 아니라 ✕다
            good = re.sub(r"`[^`]+`\s*→", "", " ".join(cells[1:]))
            for m in re.findall(r"`([^`]+)`", cells[0]):
                out.append((sec, m, good))
        elif line.startswith("✕"):
            read = True
            for m in re.findall(r"`([^`]+)`", line) or [line[1:].strip()]:
                out.append((sec, m, ""))
    seen, uniq = set(), []
    for sec, lit, good in out:
        for part in re.split(r"\s+·\s+", lit):
            part = part.strip().strip("`")
            if len(part) < 3 or part in ALLOW:
                continue
            if part in good:          # ✓가 ✕를 품고 있으면 찾을 수 없다
                continue
            if (sec, part) in seen:
                continue
            seen.add((sec, part))
            uniq.append((sec, part))
    return uniq


def pattern(lit):
    """`re:`로 시작하면 정규식, 아니면 `~`만 아무 말이나 오는 자리로 본다."""
    if lit.startswith("re:"):
        return re.compile(lit[3:])
    parts = [re.escape(p) for p in lit.split("~")]
    return re.compile(r"[가-힣A-Za-z0-9]{0,14}".join(parts))


def main(paths):
    rs = [(s, l, pattern(l)) for s, l in rules()]
    hits = 0
    for path in paths:
        p = pathlib.Path(path)
        text = p.read_text(encoding="utf-8")
        for sec, lit, pat in rs:
            for m in pat.finditer(text):
                if any(k in m.group() for k in ALLOW):
                    continue
                line = text[: m.start()].count("\n") + 1
                a = max(0, m.start() - 30)
                hits += 1
                print(f"{p.name}:{line}  [{sec[:22]}] {lit}")
                print(f"    …{text[a:m.end() + 24]}…".replace("\n", " "))
    print(f"\n규칙 {len(rs)}개 · 걸린 곳 {hits}곳")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(
        str(x) for x in pathlib.Path("src/content/book").rglob("*.md*")))
