# 다이어그램 작성 관례

`src/components/diagrams/*.astro`. **`PaginationDriftTimeline.astro`를 복사해서 시작한다.**

### 크기 — 가로 스크롤을 만들지 않는다

본문 폭은 `--measure: 672px`다. 여기에 딱 맞춘다.

```
viewBox="0 0 672 <H>"     // 폭은 항상 672
width: 100%; height: auto  // svg
```

- **`min-width`를 기본으로 걸지 않는다.** 이게 걸려 있으면 데스크톱에서도 항상 스크롤이 생긴다
- 좌우 여백을 24px씩 남기고 실제 내용은 24~648 안에 배치한다
- 모바일에서 글자가 뭉개지지 않도록 미디어 쿼리에서만 최소 폭을 준다

```css
@media (max-width: 700px) {
  .dg { overflow-x: auto; }
  .dg svg { min-width: 560px; }
}
```

- 칸 수가 늘면 폭을 넓히지 말고 **칸 너비를 줄인다.** 672 - 라벨열 - 여백 안에서 나눈다
- 높이는 필요한 만큼 쓴다. 세로로 긴 건 문제가 안 된다

### 색 — 사이트 토큰만 쓴다

컴포넌트마다 팔레트를 따로 만들지 않는다. `editorial.css`의 전역 토큰이 이미 라이트/다크를 다 처리하므로 **`:global(body:not([data-theme="dark"]))` 오버라이드도 필요 없다.**

| 역할 | 토큰 |
|---|---|
| 배경 패널 | `--bg-soft` |
| 테두리 (헤어라인) | `--rule` |
| 본문 텍스트 | `--body` |
| 강조 텍스트 · 정답 | `--ink` |
| 라벨, 캡션, 부가 설명 | `--muted` |
| 문제 · 경고 · 주의 | `--accent` / `--accent-strong` |
| 폰트 | `--font-sans` / `--font-mono` |

의미 구분은 **색상 수를 늘려서가 아니라 굵기와 채움으로** 한다.

- 중립: `fill: --bg-soft`, `stroke: --rule`, 1px
- 문제: `stroke: --accent` 1.5px, `fill="var(--accent)" fill-opacity="0.12"`
- 정답: `stroke: --ink` 1.6px + `fill: --bg-soft`, 또는 `fill: --ink`에 `--bg` 글자로 반전

### 스타일 — 편집체

- **그림자 금지.** `box-shadow`, `filter` 쓰지 않는다
- 테두리는 헤어라인 1px. 강조해도 1.6~1.8px
- `rx`는 3. 둥근 카드나 알약 모양을 만들지 않는다
- macOS 창 크롬, 신호등 점 같은 장식 금지
- 구분은 채운 상자가 아니라 **헤어라인 가로줄**로
- 제목은 `--muted` 11.5px에 `letter-spacing: 0.09em`

### 색은 CSS가 아니라 속성으로 — 가장 자주 걸리는 함정

SVG에서 **CSS 규칙은 presentation attribute를 이긴다.** 아래처럼 쓰면 아이콘 글자가 통째로 안 보인다.

```
.dg text { fill: var(--body); }        /* 이 한 줄이 */
<text fill="var(--bg)">✓</text>        /* 이 속성을 덮어쓴다 → 어두운 글자가 어두운 원 위에 */
```

규칙은 하나다.

- **`<style>`에는 색을 절대 넣지 않는다.** `fill`, `stroke` 선언 금지. 타이포그래피(`font-family`, `font-size`, `font-weight`, `letter-spacing`)만 클래스로
- 기본색은 `<svg fill="var(--body)">`로 준다. `fill`은 상속되고, 자식의 속성이 우선한다
- 개별 색은 전부 요소의 속성으로

```bash
grep -n "fill: var\|stroke: var" src/components/diagrams/*.astro   # 결과가 없어야 정상
```

### 선행 공백은 렌더링에서 사라진다

SVG `<text>`는 기본값(`xml:space="default"`)에서 선행·후행 공백을 버리고 중간 공백을 하나로 줄인다.
그래서 코드 블록을 그릴 때 들여쓰기를 공백으로 주면 전부 왼쪽에 붙어버린다. 소스에는 남아 있으니 빌드로는 안 잡힌다.

```
<text x="24">{'  <Header />'}</text>              ✕ 들여쓰기가 사라진다
<text x={indent ? 40 : 24}>{'<Header />'}</text>  ✓ x 좌표로 준다
```

`<tspan>`을 이어 붙일 때는 반대로 주의한다. 태그 사이에 줄바꿈이나 공백을 넣으면 그게 한 칸으로 렌더링되니
한 줄에 빈틈없이 붙여 쓴다.

### 아이콘 대비

O / △ / X 같은 판정 아이콘은 **채운 원 + `var(--bg)` 글자**로 통일하고, 의미는 원의 색으로만 구분한다.
속 빈 원에 같은 색 얇은 글자를 넣으면 흐려서 안 보인다.

| 판정 | 원 |
|---|---|
| X | `--muted` |
| △ | `--accent-strong` (`--accent`는 라이트에서 대비 3.1로 부족하다) |
| O | `--ink` |

### 여백은 베이스라인이 아니라 글자 상자로 계산한다

`y`는 베이스라인이라 그대로 여백을 잡으면 위는 ascender만큼 넓어지고 아래는 descender만큼 좁아진다.

- 글자 윗선 ≈ `baseline - fontSize * 0.8`, 아랫선 ≈ `baseline + fontSize * 0.22`
- 카드 높이는 상수로 이름 붙여 빼고(`PAD_TOP`, `LINE`, `NOTE_GAP`, `PAD_BOTTOM`) 줄 수로 계산한다

### 코드 작성

- 폰트와 색은 요소마다 attribute로 쓰지 말고 `<style>`에 클래스로 정의한다 (`.m`, `.cap`, `.ttl`, `.val`)
- 좌표는 프론트매터에서 계산한다. 카드 높이가 가변이면 누적 계산 후 `viewBox`도 그 값으로 만든다
- **텍스트에 `<`, `>`가 들어가면 프론트매터 배열에 문자열로 두고 `{}`로 렌더한다.** JSX 본문에 그냥 쓰면 파싱이 깨진다. 부득이하면 `&lt;`
- `<svg>`에 `role="img"`와 `aria-label`로 그림이 말하는 결론을 한 문장으로 넣는다

### 렌더링된 적 없는 컴포넌트

import만 되어 있고 본문에 배치된 적이 없는 컴포넌트는 **한 번도 검증되지 않은 것**이다. "미사용 import가 있네" 하고 그냥 꽂으면 안 된다.

```bash
# import 했는데 렌더링하지 않는 컴포넌트 찾기
for f in src/content/blog/*.mdx; do
  grep -oE "^import ([A-Za-z]+) from" "$f" | awk '{print $2}' | while read c; do
    [ "$(grep -c "<$c" "$f")" = 0 ] && echo "$f: $c"
  done
done
```

찾았다면 배치가 아니라 판단이 먼저다.

- **그림이 그 자리에 정말 필요한지 본다.** 안 쓰이고 있었다면 그럴 만한 이유가 있었을 수 있다. 필요 없으면 import를 지우는 것도 답이다
- 배치하기로 했다면 **규격부터 전부 확인한다.** viewBox 폭, 기본 `min-width`, 폰트 크기, 글자 겹침, 팔레트, 본문과의 중복
- 실제로 `FeedbackBottleneck`은 8px 글자에, 박스를 33px 넘어 옆 노드까지 침범하는 라벨과, 본문 문장을 그대로 반복하는 하단 주석을 달고 있었다

### 겹침 검사

SVG는 겹쳐도 에러가 안 나므로 빌드만으로는 못 잡는다. 그려놓고 반드시 확인한다.

- **곡선 위의 라벨** — 베지에 정점을 계산해서 글자 상자와 15px 이상 떨어뜨린다.
  `Q` 곡선의 정점은 `0.25·P0 + 0.5·P1 + 0.25·P2`. 글자 상자는 대략 `baseline - fontSize*0.8 ~ baseline`
- **패턴·해치 위의 글자** — 읽기 힘들다. 글자 뒤에 `fill="var(--bg)"` 받침 사각형을 깐다
- **화살표 머리와 옆 라벨** — marker는 지정 좌표에서 더 뻗는다. 8px 이상 여유
- 한글은 글자당 폭이 폰트 크기와 거의 같다고 보고, 숫자·영문은 그 0.6배로 잡아 텍스트 폭을 어림한다

---

---

`SKILL.md`의 §6에서 SVG로 갈지 표로 갈지 먼저 판단하고 여기로 온다.
