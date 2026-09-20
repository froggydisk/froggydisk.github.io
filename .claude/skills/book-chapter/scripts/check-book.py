#!/usr/bin/env python3
"""SKILL.md §5 · §7의 기계 검사를 한 번에 돌린다.

    python3 .claude/skills/book-chapter/scripts/check-book.py [책 디렉터리]

§5와 §7에 bash 조각으로 흩어져 있던 검사를 모았다. 조각으로 두면 아무도 전부 돌리지
않고, 셸에 따라 파일 여러 개를 한 번에 못 넘기는 문제도 있었다(ugrep은 줄바꿈으로 이은
파일 목록을 파일명 하나로 읽는다).

**0이어야 하는 검사와 눈으로 보는 검사를 나눠 찍는다.** 낱말 목록 검사는 check-rules.py,
문단 리듬은 check-prose.py가 맡고 여기는 구조와 밀도를 본다.

**평균 문장 길이는 합격선으로 쓰지 않는다.** SKILL.md §5의 31~42자는 『컴퓨터 구성요소』의
실측치다(평균 42 · 중간값 36). 2026-09-19에 재 보니 『AI 엔지니어링』은 평균 47 · 중간값 44라
이 선으로는 18개 장이 전부 걸리는데, 걸린 문장은 대부분 연결어미로 제대로 이은 문장이었다.

**명사구 쌓기도 막는 검사가 못 된다.** 대신 `긴데 절을 잇는 어미가 없는 문장`을 세어 봤더니
16곳이 나왔는데 **전부 `A, B, C를 ~한다` 꼴의 정상 나열**이었다. §1이 오히려 권하는 형태다.
그래서 눈으로 보는 목록으로만 찍는다. 진짜 명사구 쌓기는 `~의 존재를, ~의 금지를 뜻한다`처럼
같은 꼴의 속격을 겹쳐 쌓은 자리이고, 그건 사람이 읽어야 갈린다.
"""
import re
import sys
import pathlib

# (이름, 정규식, 0이어야 하는가)
# 좁힌 자리는 이유를 옆에 적는다. 넓은 채로 두면 오탐에 묻혀 아무도 안 본다
GREPS = [
    # `점수`를 뺐다 — 로짓 점수·벤치마크 점수·부분 점수가 이 책의 정상 용어다.
    # `한 장에`도 좁혔다 — 답안지 분량을 겨눈 말인데 `이미지 한 장에서`를 잡았다
    ("문제집 목소리", r"답안|문항|[0-9]항[^목]|채워 넣|한 장에 다|한 장을 채우|한 면을 채우", True),
    # `확인했다`는 서사에도 쓰인다(`개발팀은 …부터 확인했다`). 날짜가 붙은 집필 로그만 본다.
    # `실측`도 `## 다섯 질문의 실측`처럼 절 제목으로 정상이라 `실측하지 않았`만 본다
    ("장 사이 안내·검증 로그", r"[0-9]+장에서|뒤에서 (다룬|추가|확장)|앞 장|다음 장|이 장에서는"
                          r"|20[0-9]{2}-[0-9]{2}-[0-9]{2}에 확인|실측하지 않았|주장하지", True),
    # `경계` 목록에 서버·데이터·구현·결과·교체를 더했다 — 2026-09-20 전수 조사에서
    # `서버 경계 테스트` · `데이터 경계 수정` · `결과 경계` · `교체 경계`가 이 그물을 빠져나갔다
    ("만든 복합어", r"(출력|결과|입력|응답|인용|반환|업무) 계약"
                r"|(책임|신뢰|호출|생성|시스템|접근|실행|서비스|서버|데이터|구현|결과|교체) 경계", True),
    # 개발자가 자기 CLI에 넣는 인자는 예외다(SKILL.md §7) — 코드블록은 아래에서 걷어낸다
    # 평서형 반말을 더했다 — `…50만 원까지 지원한다고 들었어`가 명령형 목록을 빠져나갔다.
    # SKILL.md §7은 직원이 봇에게 모두 존댓말이라고 못 박았다 (2026-09-20)
    ("봇 반말", r"(올려 줘|해 줘|알려 줘|보여 줘|찾아 줘)[”\"]"
             r"|[가-힣](했어|들었어|맞아|같아|거든|잖아)[”\"]", True),
    ("실습 절", r"^## 실습", True),
    ("절 번호", r"^## [0-9]+[.장절]", True),
    # 절 제목이 개수를 세지 않는다 (2026-09-20 저자 지시).
    # 「애초에 몇 가지인지 꼭 말을 해야하는거야? 일반적인 책에서는 이런식으로 몇 가지인지는
    # 잘 말 안할텐데」 — §10 「사건을 미리 세지 않는다」를 산문에만 걸고 제목에는 안 걸고 있었다.
    # 한 번에 19개를 고쳤다. `한 `은 뺐다 — `한 단계의 순서`는 낱개를 가리키지 개수가 아니다
    ("제목이 개수를 센다", r"^#{2,3} .*(두|세|네|다섯|여섯|일곱|여덟|아홉|열|[0-9]+)\s*"
                    r"(가지|개|단계|상태|유형|갈래|요소|출처|겹|줄|질문|한도|캐시|조건)", True),
    # `갖는다`·`갖고 있`를 더했다 — `가진다`만 보고 있어 `각 행은 …을 갖는다` ·
    # `시작·종료와 관계를 갖는 작업 구간` 두 곳이 살아남았다 (2026-09-20)
    ("영어 구조 직역", r"가진다|가지는데|[을를]\s*갖는|[을를]\s*갖고 있|위치한|위치하고"
                  r"|를 통하?[여어]|도출|에 대해서?\s|가지고 있|되어진|보여진|여겨진"
                  r"|결론적으로|본질적으로|에 대한 |에 대하여"
                  r"|(관점|출발점|근거)을 제공|전자는|후자는", True),
    ("에두른 부정·명사", r"지도 않았|[가-힣] 것도 없|[가-힣] 차례다|의 시작이다|대기가 어려", True),
    # 2026-09-20 저자 지시: 「깨진다. 갈린다. 열다. → 전부 웬만하면 번역투야」
    #   깨다  — 규칙·조건·통제를 깨는 것은 break 직역이다. 어긴다·뚫린다·흐트러진다
    #           (`글자가 깨진다`·`통신이 깨진다`는 국어에서 실제로 쓰므로 뺐다)
    #   갈리다 — 해석·결과가 갈린다는 diverge 직역이다. 달라진다·서로 다르다
    #           (`헷갈리다`는 다른 낱말이라 앞 경계를 붙여 뺐다)
    #   열다  — 서비스·기능을 연다는 open 직역이다. 쓰게 한다·내놓는다
    #           (`로그를 열어 봤다`·`트랜잭션을 연다`는 정상이라 목적어로 좁혔다)
    ("번역투 동사", r"(규칙|조건|요구사항|통제|권한|구성|뜻|R[0-9])[을를이가]\s*깨"
                r"|(해석|결과|처리|판단)[이가]\s*갈[린리]"
                r"|(서비스|기능|봇|공개)[를을]?\s*(열기로|열었다|열어 준|연다)"
                r"|[가-힣]에게[는도]?\s[^.]{0,24}열어 주", True),
    # 원고가 원고를 가리키는 말. 저자가 「정리하면 일곱 줄이 된다」를 두고 "보통 소설에서
    # 이렇게 말을 하나?"라고 한 갈래다. 2026-09-20 전수 조사에서 다섯 곳이 나왔다 —
    # `두 문장은 동시에 참이다` · `이 표는 모든 공격의 목록이 아니라` · `이 장이 확인한 범위는`
    # · `위 예제의 대기는` · `본문의 전후 비교 파일도`
    # `예제`·`목록`은 뺐다 — 독자가 실제로 돌리는 물건이라 가리키는 것이 정상이고
    # 부록은 「아래 목록은 그날 깔려 있던 버전이다」처럼 써야 한다. 원고가 원고를
    # 가리키는 것은 표·그림·절·문단 쪽이다
    ("원고 자기 언급", r"(이|위|아래) (표|그림|절|문단)[은는이가]|두 문장은"
                r"|이 장이 (확인|다룬|본)|본문의 [가-힣]+ 파일|이 책이 남기려는"
                r"|책 전체[의를] [가-힣]+다|이 구분이|토대다", True),
]

PEOPLE = r"(담당자|직원|개발팀|총무팀|검토자|보안 담당|한울연구소 팀|사람|팀장|누군가|회의)"

# 유보문. `않는다` · `아니다`는 뺐다 — `실제 평가 질문은 넣지 않는다`처럼
# **금지 규칙**이 훨씬 많이 걸린다(2026-09-19 실측: 옛 패턴 4~18%, 새 패턴 0~7%)
HEDGE = (r"(단정|주장하지|보장하지|증명하지 (못|않)|뜻이 아니|뜻은 아니|증거는 아니|근거가 되지|볼 수 없다|할 수 없다|말할 수 없다|아직 .{0,12}밖에|채택 보류|여기 없|검증 밖)")

# 장면이 있는 책. 여닫는 문단의 사람 검사는 여기에만 건다 (SKILL.md §7).
# 『컴퓨터 구성요소』처럼 설명만 있는 책은 전체가 현재형이고 사람이 나올 자리가 없다
NARRATIVE = {"ai-engineering"}

# `## 다룰 내용`은 **아직 안 쓴 장**의 표지다. 원서 문항 제목을 그대로 옮겨 둔 뼈대라
# §1이 막는 `문항 번호·페이지`가 그대로 들어 있다. 장을 쓰면 이 절을 지운다.
# (2026-09-19 기준 『컴퓨터 구성요소』 71개 장 중 70개가 아직 뼈대다)
STUB = "## 다룰 내용"

# 장 도입에서 터뜨린 사건은 뒤에서 받는다 (SKILL.md 「복선과 회수」).
# 책마다 심은 것이 달라서 여기 적어 둔다. 1장의 네 문제가 그 책의 복선이다
SEEDS = {"ai-engineering": ["20만 원", "육아휴직", "인사팀 전용", "접수했습니다"]}

# 시간축 표지 (SKILL.md 「시간축」). 절대 날짜가 아니라 관계로 잇는다
TIMELINE = re.compile(
    r"(그 주에|그다음 주|한 달 뒤|며칠 뒤|사흘|첫 주|되돌린|끝나 갈 무렵|앞두고|이 무렵"
    r"|그 뒤로|다음 분기|그날|얼마 지나지|그러던|이번에는|또 |다시 )")

# `A와 B는 다르다` 틀 (SKILL.md). **넓게 잡고 눈으로 고른다** —
# 좁은 정규식은 2026-09-19에 1장의 다섯 건 중 둘만 잡았다 (`다른 문제인데` ·
# `서로 다른 자리에 있다` · `코드와는 별개다`를 놓쳤다). 넓힌 그물은 책 전체 96건이다
CONTRAST = re.compile(r"(다르[다고며지]|서로 다른|다른 [가-힣]{1,8}[이인]|별개|무관하"
                      r"|뜻하지 않|보장하지 않)")

# 감정어. 인물의 동기를 적은 자리에 나온다 (SKILL.md 규칙 8)
FEELING = re.compile(
    r"(곤란|난감|당황|막막|답답|민망|허탈|겸연|짜증|불안|조마조마|찝찝|후련|미안"
    r"|선뜻|괜히|차마|하필|억울|씁쓸|자신이 없|눈치|마음이|가슴이|한숨)")


def strip(text):
    """코드블록과 주석을 걷어낸다. 주석은 렌더되지 않는 작업 메모다."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)


# 절을 잇는 어미. 이것 없이 긴 문장이 **명사구를 쌓은 문장**이다
LINK = re.compile(r"[가-힣](고|며|서|는데|은데|자|면|니까|지만|므로|라서|다가|면서|어야|아야)[\s,]")

# 닫는 문단에 사람이 없어도 되는 자리. 왜 예외인지 적는다
END_OK = {
    # 결어 두 문장에는 사람이 없는 것이 맞다. 대신 **바로 앞 문단이 담당자로 돌아온다** —
    # 2026-09-20에 저자가 「1장 마지막으로 갈수록 소설적 기법이 사라진다」고 짚어서 붙였다.
    # 예외로 빼 두면 그 앞까지 사람이 없어도 이 검사가 조용하다. 앞 문단을 같이 본다
    "01-document-assistant.mdx": "도입의 `오후 한나절`을 받는 장 결어. 앞 문단이 담당자로 돌아온다",
    "02-context-budget.mdx": "직원의 질문을 그대로 인용해 받는다",
    "03-final-project.mdx": "책 전체의 결어. 바로 앞 문단이 `개발팀`으로 닫는다",
}
SKIP = ("#", "|", "-", "<", "import", "*", "!", ">", "`", "$", "```")

# 본문과 그림의 숫자가 어긋나는지 본다 (2026-09-20).
# 저자가 「글에는 9월 2일로 되어있는데 그림에는 9월5일이야」로 잡아낸 갈래다.
# `PolicyTimeline`이 9/5 질문을 그리는데 본문은 9월 2일에 일어난 일로 적고 있었다.
# **날짜만 본다** — 측정값·점수는 그림에만 있는 것이 정상이고, `2/4`(넷 중 둘) 같은
# 분수 표기가 날짜로 잡히므로 본문에 `N월` 표기가 있는 장에서만 돌린다
# 그림에만 있어도 되는 날짜. **왜 예외인지 적는다** — 안 적으면 다음 사람이 그냥 지운다
DIAG_DATE_OK = {
    # 시간축의 눈금이다. 본문은 `8월에 규정이 개정돼`처럼 달만 말하고 날짜는 그림이 맡는다
    "PolicyTimeline": {"1월1일", "8월20일", "8월25일", "9월1일"},
}
DIAG_IMPORT = re.compile(r'from "(?:\.\./)+components/diagrams/([\w-]+)\.astro"')
DATE = re.compile(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일")
SLASH = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])")


def dates(text):
    out = {f"{int(m):d}월{int(d):d}일" for m, d in DATE.findall(text)}
    out |= {f"{int(m):d}월{int(d):d}일" for m, d in SLASH.findall(text)}
    return out


def diagram_dates(files, root):
    """장이 부르는 그림에만 있는 날짜를 돌려준다. 본문에 날짜가 없는 장은 건너뛴다."""
    comps = pathlib.Path("src/components/diagrams")
    out = []
    for f in files:
        t = f.read_text(encoding="utf-8")
        body = dates(strip(t))
        if not body:
            continue
        for name in DIAG_IMPORT.findall(t):
            c = comps / f"{name}.astro"
            if not c.exists():
                continue
            only = dates(c.read_text(encoding="utf-8")) - body - DIAG_DATE_OK.get(name, set())
            if only:
                out.append(f"    {f.name} ← {name}: 그림에만 {sorted(only)}")
    return out


def prose(text):
    body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
    body = strip(body)
    return [l.strip() for l in body.split("\n")
            if l.strip() and not l.strip().startswith(SKIP)]


def main(root):
    root = pathlib.Path(root)
    if (root / "book.yaml").exists() and "sample: true" in (root / "book.yaml").read_text(
            encoding="utf-8"):
        print(f"{root.name}: 레이아웃 검증용 샘플 책이라 건너뛴다 (book.yaml의 sample: true)")
        return 0
    files = sorted(root.rglob("*.md*"))
    narrative = root.name in NARRATIVE
    stubs = [f for f in files if STUB in f.read_text(encoding="utf-8")]
    written = [f for f in stubs
               if len(re.findall(r"^## ", f.read_text(encoding="utf-8"), re.M)) >= 5]
    files = [f for f in files if f not in stubs]
    fails = len(written)
    if stubs:
        print(f"· 아직 안 쓴 장 {len(stubs)}개는 건너뛴다 ({STUB})")
    for f in written:
        print(f"✕ 다 쓴 장에 뼈대가 남아 있다: {f.name} — {STUB} 절을 지운다")
    if not files:
        print("\n막는 검사에 걸린 항목 %d개" % fails)
        return 1 if fails else 0

    for name, pat, must_zero in GREPS:
        hits = []
        for f in files:
            text = strip(f.read_text(encoding="utf-8"))
            for i, line in enumerate(text.split("\n"), 1):
                if line.startswith("last_modified_at"):
                    continue
                if re.search(pat, line, re.M):
                    hits.append(f"    {f.name}:{i}  {line.strip()[:80]}")
        flag = "✕" if (hits and must_zero) else "✓"
        fails += bool(hits and must_zero)
        print(f"{flag} {name}: {len(hits)}곳")
        print("\n".join(hits[:6]))

    print()
    eyes, eyes2 = [], []
    for f in files:
        t = f.read_text(encoding="utf-8")
        p = prose(t)
        if not p:
            continue
        note = []
        # 유보문 밀도 (100문장당 10 아래). 부록은 정의문이라 `~가 아니다`가 정상이다
        if "07-appendices" not in str(f):
            body = "\n".join(p)
            sents = body.count("다.")
            hedge = len(re.findall(HEDGE, body))
            if sents and hedge / sents * 100 >= 10:
                note.append(f"유보문 {hedge}/{sents}")
        # 사이드바 목차는 h2 5개부터 뜬다. 부록은 짧아서 목차가 없어도 된다
        h2 = len(re.findall(r"^## ", t, re.M))
        if h2 < 5 and "07-appendices" not in str(f):
            note.append(f"h2 {h2}개")
        # 여는 문단·닫는 문단에 사람이 있는가 (본문 장만)
        if narrative and "07-appendices" not in str(f):
            if not re.search(PEOPLE, p[0]):
                note.append("여는 문단에 사람 없음")
            if not re.search(PEOPLE, p[-1]) and f.name not in END_OK:
                note.append("닫는 문단에 사람 없음")
        # 문장 길이 평균
        # 명사구 쌓기 후보는 **막는 검사가 아니다**(아래 eyes에 모은다)
        ss = [x for l in p for x in re.split(
            r"(?<=[.?])\s+", re.sub(r"\*\*|`|\[.*?\]\(.*?\)|\$[^$]*\$|\\[a-zA-Z]+", "", l))
            if x.strip()]
        for x in ss:
            if len(x) >= 70 and not LINK.search(x):
                eyes.append(f"    [{f.name[:22]}] {x[:88]}")
        if note:
            fails += 1
            print(f"  ✕ {f.name[:30]:32} {' · '.join(note)}")

    # 복선 회수 — 심은 사건이 뒤 장에서 불러내지는가
    for key in SEEDS.get(root.name, []):
        holders = [f.name for f in files if key in f.read_text(encoding="utf-8")]
        if len(holders) < 2:
            fails += 1
            print(f"✕ 복선 회수: `{key}`가 {len(holders)}개 장에만 있다 ({', '.join(holders)})")

    # 시간축 표지 — 부(部)마다 최소 하나
    if narrative:
        parts = sorted({f.parent.name for f in files if f.parent != root})
        for part in parts:
            got = [f for f in files if f.parent.name == part
                   and TIMELINE.search(" ".join(prose(f.read_text(encoding="utf-8"))[:2]))]
            if not got:
                fails += 1
                print(f"✕ 시간축: {part}의 어느 장도 도입에 관계 표지가 없다")

    # 인물의 동기 — **막는 검사가 아니다.** 감정어가 없어도 동작으로 보여 주면 된다
    # (`하던 일을 멈추고 공유 폴더를 뒤져` · `사흘을 기다리던 직원이`). 눈으로 보는 목록에 넣는다
    if narrative:
        for f in files:
            if "07-appendices" in str(f):
                continue
            intro = " ".join(prose(f.read_text(encoding="utf-8"))[:3])
            if not FEELING.search(intro):
                eyes2.append(f"    [{f.name[:26]}] {intro[:78]}")

    counts = []
    for f in files:
        n = len(CONTRAST.findall(strip(f.read_text(encoding="utf-8"))))
        if n:
            counts.append((n, f.name))
    if counts:
        counts.sort(reverse=True)
        print(f"\n— 눈으로 보는 목록: `A와 B는 다르다` 틀 {sum(n for n, _ in counts)}건 —")
        print("    " + " · ".join(f"{name[:24]} {n}" for n, name in counts[:8]))
        print("  (정상 용례가 섞인다. 되풀이면 지우고, 처음 세우는 구분이면 관찰·동작으로 푼다)")

    if eyes2:
        print(f"\n— 눈으로 보는 목록: 도입에 감정어가 없는 장 {len(eyes2)}개 —")
        print("\n".join(eyes2))
        print("  (동작으로 동기를 보여 주면 감정어는 없어도 된다. 동기 자체가 없는 곳만 고른다)")

    if eyes:
        print(f"\n— 눈으로 보는 목록: 명사구 쌓기 후보 {len(eyes)}곳 —")
        print("\n".join(eyes))
        print("  (`A, B, C를 ~한다` 꼴의 나열은 정상이다. §1이 권하는 형태다)")

    dd = diagram_dates(files, root)
    if dd:
        fails += 1
        print(f"\n✕ 본문에 없는 날짜가 그림에 있다: {len(dd)}곳 —")
        print("\n".join(dd))
        print("  (이야기가 기준이다. 그림이 본문 날짜를 따라간다)")

    print(f"\n막는 검사에 걸린 항목 {fails}개")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "src/content/book/ai-engineering"))
