#!/usr/bin/env python3
"""문단이 단문 나열로 끊겨 있는지, 번역투 표현이 남아 있는지 본다.

    python3 .claude/skills/book-chapter/scripts/check-prose.py <파일...>

결과가 0이어야 하는 검사가 아니다. 한 줄씩 눈으로 보는 목록이다.
짧은 문장 자체는 문제가 아니고, **한 문단이 통째로 짧은 문장의 나열**일 때가 문제다.
"""
import re
import sys
import pathlib

# 문장을 이어 주는 표지. 하나도 없는 문단은 끊겨 읽힌다.
CONNECTIVES = re.compile(
    r"(그런데|그래서|그러나|하지만|그리고|결국|다만|반면|따라서|대신|게다가|오히려|그러면|그때|이때|그렇다고|막상|정작|고작|벌써"
    r"|[가-힣]는데[\s,]|[가-힣]은데[\s,]|[가-힣][아어]서[\s,]|[가-힣]으니|[가-힣]니까"
    r"|[가-힣]지만|[가-힣]면서|[가-힣]다가|[가-힣]자[\s,]|[가-힣]려면|[가-힣]도록"
    r"|[가-힣]고[\s,]|[가-힣]며[\s,]|[가-힣]라서|[가-힣]인데|때문이다|때문에|위해서)"
)

# 이번 교정에서 실제로 걸린 번역투
ARTIFACTS = [
    (r"[0-9일이삼사오육칠팔구십한두세네다섯여섯일곱여덟아홉열]+\s*번\s+[가-힣]+했다", "N번 V했다 → N번째다"),
    (r"링크를\s*붙[여이]", "링크를 붙이다 → 보내다"),
    (r"(정해진다|만들어진다|여겨진다|보여진다|되어진)", "피동 남용 → 능동으로"),
    # `이것을 ~라고 부른다`는 이름을 붙이는 표준 구문이라 뺀다
    (r"(이것을|그것을|이것이|그것이)\s(?!.{0,30}(라고 부|이라고|라고 한))", "흐린 지시 → 이름으로 부른다"),
    (r"[가-힣]+하는 사람, [가-힣]+하는 사람", "명사구 나열 → 동사로 잇는다"),
    (r"것이다\.[^\n]*것이다\.", "~것이다 반복 → 서술어로 끝낸다"),
    (r"(답|결과|값|수치)[이가]\s*맞[다았]", "be동사 직역 → 동사 중심 (제대로 답한다)"),
    (r"[0-9한두세네다섯여섯일곱여덟아홉열]+\s*번\s*깨[진지]", "N번 깨진다 → N가지 문제가 드러난다"),
    # `문제가 발생하다`는 굳은 연어라 뺀다. `드러나다·나타나다`만 번역투로 본다
    (r"(문제|오류|실패|차이|결과)[가이]\s*(드러나|나타나)", "무생물 주어 + 자동사 → 사람·상황을 주어로"),
    (r"(문제|오류|실패)[가이]\s*[0-9한두세네다섯여섯]+\s*가지\s*나왔", "사건을 미리 세지 않는다 → 문제가 터져 나왔다"),
    (r"맞는 답이다|답이 맞다", "be동사 직역 → 틀린 데가 없다"),
    (r"(제대로|잘) (동작|작동|수행)했다", "기계 용어로 서사 처리 → 그 사물이 하는 일의 동사로"),
    (r"[^\n]{0,20}마찬가지였다", "대용 표현 → 무엇이 어떠했는지 적는다"),
    (r"덩어리", "형체 없는 것에 물건 가리키는 말 → 모양 · 하나로"),
    # 아래는 im-not-ai / k-skill 분류 체계의 S1 (references/korean.md §3-4)
    (r"에 대해서?\s", "A-1 ~에 대해 → 목적격 조사로"),
    (r"(을|를) 통하?[여어]", "A-2 ~를 통해 → ~로 · ~해서"),
    # A-3 `~에 있어(서)`는 `있다 + -어서`(DB에 있어서 …)와 정규식으로 안 갈린다.
    # 조사 뒤 주제가 오는 꼴만 잡는다.
    (r"에 있어서는|에 있어 [가-힣]+[은는이가]", "A-3 ~에 있어 → ~에서"),
    (r"(가지고|갖고) 있", "A-7 가지고 있다 → 형용사·동사로"),
    (r"(되어진|보여진|여겨진)", "A-8 이중 피동 → 능동 또는 단일 피동"),
    (r"(결론적으로|본질적으로|핵심적으로|시사하는 바)", "D-1~D-3 AI 상투구 → 삭제"),
    (r"[^\n]—", "J-2 줄표 → 마침표·쉼표·괄호로"),
]

SKIP = ("#", "|", "-", "<", "import", "*", "!", ">", "{", "`", "$", "```")


def paragraphs(text: str):
    body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
    body = re.sub(r"```.*?```", "", body, flags=re.S)  # 코드블록 제거
    for block in body.split("\n\n"):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        prose = [l for l in lines if not l.startswith(SKIP)]
        if prose:
            yield " ".join(prose)


def sentences(para: str):
    para = re.sub(r"\*\*|`|\[.*?\]\(.*?\)|\$[^$]*\$", "", para)
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", para) if s.strip()]


def main(paths):
    for path in paths:
        p = pathlib.Path(path)
        text = p.read_text(encoding="utf-8")
        hits = []

        for para in paragraphs(text):
            sents = sentences(para)
            if len(sents) < 4:
                continue
            avg = sum(len(s) for s in sents) / len(sents)
            linked = sum(1 for s in sents if CONNECTIVES.search(s))
            # 문단 전체가 짧은 문장인데 이어 주는 말이 거의 없으면 끊겨 읽힌다
            if avg < 42 and linked <= len(sents) // 3:
                hits.append(
                    f"  끊긴 문단 ({len(sents)}문장 · 평균 {avg:.0f}자 · 연결 {linked})\n"
                    f"    {para[:150]}…"
                )

        # 한 문장에 부정이 셋 이상이면 읽는 쪽이 셈을 해야 한다
        for para in paragraphs(text):
            for sent in sentences(para):
                n = len(re.findall(r"(없|않|못하|아니)", sent))
                if n >= 3:
                    hits.append(f"  부정 {n}겹 → 긍정으로 바꿀 자리를 찾는다\n    {sent[:110]}")

        for pattern, why in ARTIFACTS:
            for m in re.finditer(pattern, text):
                a = max(0, m.start() - 28)
                hits.append(f"  번역투 [{why}]\n    …{text[a:m.end() + 22]}…".replace("\n    …", "\n    …"))

        print(f"══ {p}")
        print("\n".join(hits) if hits else "  (깨끗함)")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(str(x) for x in pathlib.Path(".").glob("*/*.mdx")))
