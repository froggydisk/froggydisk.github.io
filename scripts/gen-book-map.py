#!/usr/bin/env python3
"""목차 페이지용 구조 지도. 폭 680 고정 — 본문 열(최대 700px)에 가로 스크롤 없이 들어간다.

장 목록은 넣지 않는다. 바로 아래 텍스트 목차가 같은 내용을 이미 담고 있고,
680px 안에 카드 7장과 구조도를 함께 넣으면 글자가 읽을 수 없는 크기가 된다.
대신 블록마다 그것을 설명하는 부 번호를 배지로 붙인다.

배선은 전부 직교(가로/세로)로 두고, 마지막에 선분–사각형 교차 검사로
"연결 대상이 아닌 블록을 통과하는 선"이 없는지 확인한다. 렌더를 눈으로 볼 수 없으므로
이 검사가 유일한 확인 수단이다.
"""

import json
import os
import pathlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{REPO}/src/components/diagrams/BookArchitectureMap.astro"
LUCIDE = json.load(open(f"{REPO}/node_modules/@iconify-json/lucide/icons.json"))

W = 680
EPS = 0.6

# ---------------------------------------------------------------- 블록
# name: (x, y, w, h, 제목, 부 배지, 아이콘)
B = {
    "mem":   (172, 14, 300, 150, "MEMORY HIERARCHY", "02", "lucide:memory-stick"),
    "mmu":   (492, 14, 172, 96, "MMU &amp; TLB", "02", "lucide:book-marked"),
    "par":   (16, 196, 178, 148, "PARALLEL", "03", "lucide:boxes"),
    "cpu":   (226, 190, 220, 214, "CPU", "01", "lucide:cpu"),
    "chip":  (478, 190, 186, 96, "CHIPSET &amp; BUS", "01", "lucide:route"),
    "io":    (478, 306, 186, 118, "I/O INTERFACE", "04", "lucide:usb"),
    "bus":   (16, 452, 648, 40, "", "", ""),
    "logic": (16, 528, 320, 152, "LOGIC CIRCUIT", "06", "lucide:circuit-board"),
    "comp":  (352, 528, 312, 152, "COMPUTING", "07", "lucide:cloud-cog"),
}
H = 692   # 블록이 680 에서 끝난다. 아래 여백 12.


def x0(k): return B[k][0]
def y0(k): return B[k][1]
def x1(k): return B[k][0] + B[k][2]
def y1(k): return B[k][1] + B[k][3]
def cx(k): return B[k][0] + B[k][2] / 2
def cy(k): return B[k][1] + B[k][3] / 2


# ---------------------------------------------------------------- 배선
# (이름, 점들, 연결된 블록, 클레이여부, 시작화살표, 라벨[(x,y,anchor,text)...])
WIRES = [
    ("cpu↔mem", [(cx("cpu"), y0("cpu")), (cx("cpu"), y1("mem"))], ["cpu", "mem"], False, True,
     [(cx("cpu") + 7, 178, "start", "명령어 · 데이터")]),

    ("mem↔mmu", [(x1("mem"), 62), (x0("mmu"), 62)], ["mem", "mmu"], False, True, []),

    ("mmu→cpu", [(cx("mmu"), y1("mmu")), (cx("mmu"), 176), (462, 176), (462, 224),
                 (x1("cpu"), 224)], ["mmu", "cpu"], False, False,
     [(cx("mmu") + 7, 133, "start", "가상 → 실주소")]),

    # 두 블록 사이가 32px 뿐이라 라벨을 넣으면 양쪽 블록을 덮는다. 화살표만 둔다.
    ("cpu↔par", [(x0("cpu"), 268), (x1("par"), 268)], ["cpu", "par"], False, True, []),

    ("cpu↔chip", [(x1("cpu"), 238), (x0("chip"), 238)], ["cpu", "chip"], False, True, []),

    ("chip↔io", [(cx("chip"), y1("chip")), (cx("chip"), y0("io"))], ["chip", "io"], False, True, []),

    ("par→bus", [(cx("par"), y1("par")), (cx("par"), y0("bus"))], ["par", "bus"], False, True, []),
    ("cpu→bus", [(cx("cpu"), y1("cpu")), (cx("cpu"), y0("bus"))], ["cpu", "bus"], False, True, []),
    ("io→bus",  [(cx("io"), y1("io")), (cx("io"), y0("bus"))], ["io", "bus"], False, True, []),

    ("logic→", [(cx("logic"), y0("logic")), (cx("logic"), y1("bus"))], ["logic", "bus"], True, False,
     [(cx("logic") + 7, 514, "start", "이 위 전부의 재료")]),
    ("comp→", [(cx("comp"), y0("comp")), (cx("comp"), y1("bus"))], ["comp", "bus"], True, False,
     [(cx("comp") + 7, 514, "start", "이 위 전부를 측정")]),
]


def seg_hits_rect(p, q, r):
    """직교 선분이 사각형 내부를 지나는지. 변에 닿는 것은 통과로 보지 않는다."""
    rx, ry, rw, rh = r[0], r[1], r[2], r[3]
    ax, ay, bx, by = p[0], p[1], q[0], q[1]
    if abs(ay - by) < EPS:                      # 가로
        if not (ry + EPS < ay < ry + rh - EPS):
            return False
        lo, hi = min(ax, bx), max(ax, bx)
        return hi > rx + EPS and lo < rx + rw - EPS
    if abs(ax - bx) < EPS:                      # 세로
        if not (rx + EPS < ax < rx + rw - EPS):
            return False
        lo, hi = min(ay, by), max(ay, by)
        return hi > ry + EPS and lo < ry + rh - EPS
    raise AssertionError("직교가 아닌 선분")


def label_w(t, fs=9.0):
    return sum(fs * (1.0 if ord(c) > 0x2000 else 0.55) for c in t)


def check():
    bad = []
    # 라벨 상자가 블록을 덮는지. 화살표만 검사하면 글자가 블록 위에 얹히는 것을 놓친다.
    for name, _pts, connects, _a, _s, labels in WIRES:
        for lx, ly, anchor, text in labels:
            w = label_w(text)
            lx0 = lx if anchor == "start" else (lx - w / 2 if anchor == "middle" else lx - w)
            box = (lx0, ly - 9, w, 11)
            if lx0 < 0 or lx0 + w > W:
                bad.append(f"{name} 라벨 캔버스 밖")
            for bname, rect in B.items():
                a, b = box, rect
                if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                    bad.append(f"{name} 라벨이 {bname} 을 덮음")
    for name, pts, connects, *_ in WIRES:
        for i in range(len(pts) - 1):
            for bname, rect in B.items():
                if bname in connects:
                    continue
                if seg_hits_rect(pts[i], pts[i + 1], rect):
                    bad.append(f"{name} 구간{i + 1} → {bname} 통과")
    # 블록끼리 겹침
    keys = list(B)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = B[keys[i]], B[keys[j]]
            if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                bad.append(f"블록 겹침 {keys[i]}·{keys[j]}")
    # 캔버스 이탈
    for k, r in B.items():
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > W or r[1] + r[3] > H:
            bad.append(f"캔버스 밖 {k}")
    return bad


# ---------------------------------------------------------------- 그리기

# 블록 → 아래 텍스트 목차의 부 앵커. 누르면 그 부로 스크롤된다.
LINK = {
    "mem": (2, "메모리 계층 — 2부 목차로 이동"),
    "mmu": (2, "MMU와 TLB — 2부 목차로 이동"),
    "par": (3, "병렬 아키텍처 — 3부 목차로 이동"),
    "cpu": (1, "CPU — 1부 목차로 이동"),
    "chip": (1, "칩셋과 버스 — 1부 목차로 이동"),
    "io": (4, "입출력 인터페이스 — 4부 목차로 이동"),
    "logic": (6, "논리회로 — 6부 목차로 이동"),
    "comp": (7, "컴퓨팅 — 7부 목차로 이동"),
}


def link(key, inner):
    """블록을 목차 앵커로 감싼다. 대상이 없는 블록(버스)은 그대로 둔다."""
    if key not in LINK:
        return inner
    part, label = LINK[key]
    return f'<a class="hit" href="#part-{part}" aria-label="{label}">{inner}</a>'


def close(g, start, key):
    inner = "".join(g[start:])
    del g[start:]
    g.append(link(key, inner))


def icon(name, x, y, size, cls="ic"):
    body = LUCIDE["icons"][name.split(":", 1)[1]]["body"]
    return (f'<g class="{cls}" transform="translate({x:.1f},{y:.1f}) '
            f'scale({size / 24.0:.4f})">{body}</g>')


def head(k, inv=False):
    """블록 머리 — 아이콘을 제목 왼쪽에 세로 중앙으로 놓고, 부 배지는 오른쪽 끝에."""
    x, y, w, _h, title, badge, ic = B[k]
    base = y + 21                      # 제목 기준선
    g = []
    if ic:
        g.append(icon(ic, x + 12, base - 11, 15, "ic-accent"))
        tx = x + 33
    else:
        tx = x + 12
    cls = "blk-t blk-t-inv" if inv else "blk-t"
    g.append(f'<text class="{cls}" x="{tx}" y="{base}">{title}</text>')
    if badge:
        bw = 20
        g.append(f'<rect class="badge" x="{x + w - 12 - bw}" y="{y + 9}" width="{bw}" height="15" rx="2"/>')
        g.append(f'<text class="badge-t" x="{x + w - 12 - bw / 2}" y="{y + 20}" text-anchor="middle">{badge}</text>')
    return "".join(g)


def draw():
    g = []

    # 메모리 계층
    x, y, w, h = B["mem"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("mem"))
    tiers = [("REGISTERS", 0.30, "t0"), ("L1 · L2 · L3 CACHE", 0.48, "t1"),
             ("MAIN MEMORY (DRAM)", 0.70, "t2"), ("STORAGE (SSD / HDD)", 0.92, "t3")]
    ty = y + 32
    for label, frac, cls in tiers:
        bw = w * frac * 0.92
        g.append(f'<rect class="tier {cls}" x="{x + w / 2 - bw / 2:.1f}" y="{ty}" width="{bw:.1f}" height="21" rx="2"/>')
        g.append(f'<text class="tier-t" x="{x + w / 2}" y="{ty + 14}" text-anchor="middle">{label}</text>')
        ty += 25
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + h - 8}" text-anchor="middle">위로 갈수록 빠르고 작다</text>')

    close(g, _b, "mem")

    # MMU
    x, y, w, h = B["mmu"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("mmu"))
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 52}" text-anchor="middle">페이지 표를 캐시해</text>')
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 68}" text-anchor="middle">주소 변환을 줄인다</text>')

    close(g, _b, "mmu")

    # 병렬
    x, y, w, h = B["par"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("par"))
    # 코어 3개를 블록 가로 중앙에 놓는다. 여백을 눈대중으로 주면 한쪽으로 쏠린다.
    n, cw_, gap = 3, 34, 16
    row_w = n * cw_ + (n - 1) * gap
    sx0 = x + (w - row_w) / 2
    # 세로 중앙 — 머리(y+28)와 아래 설명줄(y+107) 사이의 중앙
    core_h = 40
    core_y = y + 28 + ((y + 107) - (y + 28) - core_h) / 2
    for i in range(n):
        px = sx0 + i * (cw_ + gap)
        g.append(f'<rect class="core" x="{px:.1f}" y="{core_y:.1f}" width="{cw_}" height="{core_h}" rx="2"/>')
        g.append(f'<text class="core-t" x="{px + cw_ / 2:.1f}" y="{core_y + 24:.1f}" text-anchor="middle">CPU</text>')
        if i < n - 1:
            ly = core_y + core_h / 2
            g.append(f'<line class="ln" x1="{px + cw_:.1f}" y1="{ly:.1f}" x2="{px + cw_ + gap:.1f}" y2="{ly:.1f}"/>')
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 116}" text-anchor="middle">SMP · MPP · NUMA</text>')
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 134}" text-anchor="middle">상호연결망으로 묶는다</text>')

    close(g, _b, "par")

    # CPU
    x, y, w, h = B["cpu"][:4]
    _b = len(g)
    g.append(f'<rect class="blk-dark" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("cpu", inv=True))
    iy = y + 36
    for label, cls in [("CONTROL UNIT", "unit-accent"), ("ALU", "unit"), ("REGISTERS", "unit")]:
        g.append(f'<rect class="{cls}" x="{x + 18}" y="{iy}" width="{w - 36}" height="46" rx="2"/>')
        tcls = "unit-t-inv" if cls == "unit-accent" else "unit-t"
        g.append(f'<text class="{tcls}" x="{x + w / 2}" y="{iy + 28}" text-anchor="middle">{label}</text>')
        iy += 54
    for i in range(8):
        py = y + 30 + i * 23
        g.append(f'<rect class="pin" x="{x + 3}" y="{py}" width="9" height="8" rx="1"/>')
        g.append(f'<rect class="pin" x="{x + w - 12}" y="{py}" width="9" height="8" rx="1"/>')

    close(g, _b, "cpu")

    # 칩셋
    x, y, w, h = B["chip"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("chip"))
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 52}" text-anchor="middle">North / South Bridge</text>')
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + 70}" text-anchor="middle">버스 컨트롤러</text>')

    close(g, _b, "chip")

    # I/O
    x, y, w, h = B["io"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("io"))
    devs = [("lucide:bell-ring", "INTERRUPT"), ("lucide:refresh-cw", "DMA"),
            ("lucide:hard-drive", "STORAGE"), ("lucide:network", "NETWORK")]
    # 두 열 폭을 가장 긴 라벨에 맞춰 같게 두고, 그 묶음을 블록 중앙에 놓는다.
    # (라벨 길이가 달라 열마다 폭이 다르면 오른쪽이 들쭉날쭉해 보인다)
    ic_w, ic_gap, col_gap = 14, 5, 16
    label_max = max(label_w(l, 8.5) + len(l) * 0.34 for _i, l in devs)   # 0.34 = letter-spacing
    col_w = ic_w + ic_gap + label_max
    grid_w = col_w * 2 + col_gap
    dx0 = x + (w - grid_w) / 2
    row_pitch, rows = 34, 2
    grid_h = ic_w + row_pitch * (rows - 1)
    dy0 = (y + 28) + ((y + h) - (y + 28) - grid_h) / 2
    for i, (ic, label) in enumerate(devs):
        dx = dx0 + (i % 2) * (col_w + col_gap)
        dy = dy0 + (i // 2) * row_pitch
        g.append(icon(ic, dx, dy, ic_w, "ic-accent"))
        g.append(f'<text class="dev-t" x="{dx + ic_w + ic_gap:.1f}" y="{dy + 11:.1f}">{label}</text>')

    close(g, _b, "io")

    # 버스
    x, y, w, h = B["bus"][:4]
    _b = len(g)
    g.append(f'<rect class="blk-dark" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    for i, label in enumerate(["ADDRESS BUS", "DATA BUS", "CONTROL BUS"]):
        g.append(f'<text class="bus-t" x="{x + w * (0.17 + i * 0.33):.1f}" y="{y + 25}" text-anchor="middle">{label}</text>')

    close(g, _b, "bus")

    # 논리회로
    x, y, w, h = B["logic"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("logic"))
    subs = [("게이트 · 부울대수", "lucide:git-merge"), ("래치 · 플립플롭", "lucide:toggle-left"),
            ("기억장치 회로", "lucide:grid-3x3"), ("타이밍 · 해저드", "lucide:activity")]
    for i, (label, ic) in enumerate(subs):
        sx, sy = x + 14 + (i % 2) * 150, y + 36 + (i // 2) * 52
        g.append(f'<rect class="sub" x="{sx}" y="{sy}" width="140" height="44" rx="2"/>')
        g.append(icon(ic, sx + 10, sy + 15, 15))
        g.append(f'<text class="sub-t" x="{sx + 32}" y="{sy + 27}">{label}</text>')
    g.append(f'<text class="blk-s" x="{x + w / 2}" y="{y + h - 8}" text-anchor="middle">플립플롭 n개 = n비트 레지스터</text>')

    close(g, _b, "logic")

    # 컴퓨팅
    x, y, w, h = B["comp"][:4]
    _b = len(g)
    g.append(f'<rect class="blk" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
    g.append(head("comp"))
    subs = [("성능 평가 · SPEC", "lucide:gauge"), ("암달의 법칙", "lucide:trending-up"),
            ("GPU · TPU · ARM", "lucide:microchip"), ("클라우드 · 엣지", "lucide:atom")]
    for i, (label, ic) in enumerate(subs):
        sx, sy = x + 14 + (i % 2) * 146, y + 36 + (i // 2) * 52
        g.append(f'<rect class="sub" x="{sx}" y="{sy}" width="136" height="44" rx="2"/>')
        g.append(icon(ic, sx + 10, sy + 15, 15))
        g.append(f'<text class="sub-t" x="{sx + 32}" y="{sy + 27}">{label}</text>')
    g.append(f'<text class="blk-s eq" x="{x + w / 2}" y="{y + h - 8}" text-anchor="middle">실행시간 = 명령어 수 × CPI × 클럭 주기</text>')

    close(g, _b, "comp")

    # 배선
    for name, pts, _c, accent, start, labels in WIRES:
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + "".join(f" L{px:.1f},{py:.1f}" for px, py in pts[1:])
        cls = "ln-accent" if accent else "ln"
        mk = "ac" if accent else "a"
        ms = f' marker-start="url(#{mk})"' if start else ""
        g.append(f'<path class="{cls}" d="{d}"{ms} marker-end="url(#{mk})"/>')
        for lx, ly, anchor, text in labels:
            tc = "wire-t wire-t-accent" if accent else "wire-t"
            g.append(f'<text class="{tc}" x="{lx:.1f}" y="{ly}" text-anchor="{anchor}">{text}</text>')

    return "".join(g)


bad = check()
print(f"캔버스 {W}x{H} · 블록 {len(B)}개 · 배선 {len(WIRES)}개")
print("검사:", "통과 (블록 통과·겹침·이탈 없음)" if not bad else bad)
if bad:
    raise SystemExit(1)

svg = f'''<svg class="bm" viewBox="0 0 {W} {H}" role="img"
    aria-label="컴퓨터 구조 지도. 메모리 계층과 MMU가 CPU에 명령어와 데이터를 넣고, 칩셋을 지나 입출력이 붙으며, 주소·데이터·제어 버스가 이들을 잇는다. 논리회로는 이 전부를 만드는 재료이고 컴퓨팅은 이 전부를 재는 척도다. 블록마다 그것을 설명하는 부 번호가 붙어 있다">
    <defs>
      <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path class="mk" d="M0,1 L9,5 L0,9 z"/>
      </marker>
      <marker id="ac" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path class="mk-accent" d="M0,1 L9,5 L0,9 z"/>
      </marker>
    </defs>
    {draw()}
  </svg>'''

assert "{" not in svg and "}" not in svg, "SVG 안에 중괄호"

CSS = """
/* 목차 앞의 구조 지도.
   생성물이다. 손으로 고치지 말고 scripts/gen-book-map.py 를 다시 돌린다.

   폭 680 고정 — 본문 열이 최대 700px 이라 가로 스크롤이 생기지 않는다.
   색은 editorial.css 토큰만 쓴다. 토큰이 테마를 따라가므로 다크 전용 재정의가 없다.
   CPU·버스는 --ink 로 칠하고 그 위 글자를 --bg 로 둔다. 다크에서 두 값이 뒤집혀도
   명암 관계가 그대로 유지된다. */

.bm-wrap {
  --bm-line: color-mix(in srgb, var(--ink) 34%, transparent);
  --bm-tier: color-mix(in srgb, var(--accent) 22%, var(--bg));

  /* 표지·소개와 떨어뜨린다. 원래 .book-contents 가 갖고 있던 간격(3.2rem)을
     지도가 맨 앞으로 오면서 대신 받는다. */
  /* 아래 목차와의 간격은 .book-contents 의 margin-top(3.2rem)과 상쇄돼 그 값이 남는다 */
  margin: 3.2rem 0 0.9rem;
  padding: 4px 0;
  background: var(--bg-soft);
  border: 1px solid var(--rule);
  border-radius: 3px;
}
.bm {
  display: block;
  width: 100%;
  height: auto;
  color: var(--ink);
}

.bm .blk { fill: var(--bg); stroke: var(--bm-line); stroke-width: 1.1; }
.bm .blk-dark { fill: var(--ink); stroke: var(--ink); stroke-width: 1.1; }
.bm .blk-t { font-family: var(--font-sans); font-size: 11.5px; font-weight: 600; fill: var(--ink); letter-spacing: 0.05em; }
.bm .blk-t-inv { fill: var(--bg); }
.bm .blk-s { font-family: var(--font-sans); font-size: 9.5px; fill: var(--muted); }
.bm .eq { font-family: var(--font-mono); font-size: 9.5px; fill: var(--accent-strong); }

.bm .badge { fill: none; stroke: var(--accent); stroke-width: 1; }
.bm .badge-t { font-family: var(--font-mono); font-size: 9.5px; fill: var(--accent-strong); }

.bm .tier { stroke: var(--bm-line); stroke-width: 0.9; }
.bm .t0 { fill: var(--bg); }
.bm .t1 { fill: var(--bm-tier); }
.bm .t2 { fill: var(--accent); }
.bm .t3 { fill: var(--accent); opacity: 0.72; }
.bm .tier-t { font-family: var(--font-mono); font-size: 8px; fill: var(--ink); letter-spacing: 0.03em; }

.bm .core { fill: var(--bg-soft); stroke: var(--bm-line); stroke-width: 0.9; }
.bm .core-t { font-family: var(--font-mono); font-size: 8.5px; fill: var(--muted); }

.bm .unit { fill: var(--bg); stroke: none; }
.bm .unit-accent { fill: var(--accent); stroke: none; }
.bm .unit-t { font-family: var(--font-sans); font-size: 10.5px; font-weight: 600; fill: var(--ink); letter-spacing: 0.04em; }
.bm .unit-t-inv { font-family: var(--font-sans); font-size: 10.5px; font-weight: 600; fill: #fff; letter-spacing: 0.04em; }
.bm .pin { fill: var(--muted); }
.bm .bus-t { font-family: var(--font-mono); font-size: 9.5px; fill: var(--bg); letter-spacing: 0.09em; }

.bm .sub { fill: var(--bg-soft); stroke: var(--rule); stroke-width: 0.9; }
.bm .sub-t { font-family: var(--font-sans); font-size: 10px; fill: var(--body); }
.bm .dev-t { font-family: var(--font-mono); font-size: 8.5px; fill: var(--muted); letter-spacing: 0.04em; }

/* 회색은 실제로 오가는 것, 클레이는 재료·측정 관계 */
.bm .ln { stroke: currentColor; stroke-width: 1.2; fill: none; }
.bm .ln-accent { stroke: var(--accent); stroke-width: 1.4; fill: none; }
.bm .mk { fill: currentColor; }
.bm .mk-accent { fill: var(--accent); }
.bm .ic { color: var(--ink); }
.bm .ic-accent { color: var(--accent-strong); }
.bm .wire-t { font-family: var(--font-mono); font-size: 9px; fill: var(--muted); }
.bm .wire-t-accent { fill: var(--accent-strong); }

/* 블록을 누르면 아래 텍스트 목차의 해당 부로 이동한다. */
.bm .hit { cursor: pointer; }
.bm .hit .blk,
.bm .hit .blk-dark { transition: stroke 0.16s ease, stroke-width 0.16s ease; }
.bm .hit:hover .blk { stroke: var(--accent); stroke-width: 1.8; }
.bm .hit:hover .blk-dark { stroke: var(--accent); stroke-width: 2.2; }
.bm .hit:hover .blk-t { fill: var(--accent-strong); }
.bm .hit:hover .blk-t-inv { fill: var(--bg); }
.bm .hit:hover .badge { stroke-width: 1.6; }
/* 키보드 이동에서도 어느 블록인지 보이게 */
.bm .hit:focus-visible { outline: none; }
.bm .hit:focus-visible .blk,
.bm .hit:focus-visible .blk-dark { stroke: var(--accent); stroke-width: 2.2; }
@media (prefers-reduced-motion: reduce) {
  .bm .hit .blk,
  .bm .hit .blk-dark { transition: none; }
}
"""

component = f"""---
/**
 * 책 목차 앞의 구조 지도.
 *
 * 생성물이다. 손으로 고치지 말고 scripts/gen-book-map.py 를 다시 돌린다.
 * 그 스크립트가 배선을 직교로만 두고, 선분–사각형 교차 검사로
 * 연결 대상이 아닌 블록을 통과하는 화살표가 없는지 확인한다.
 *
 * 아래 텍스트 목차가 장 제목을 담당하므로 여기서는 장을 나열하지 않고
 * 블록마다 부 번호 배지만 붙인다. pagefind 색인에서도 뺀다.
 */
---

<div class="bm-wrap" data-pagefind-ignore>
  {svg}
</div>


<style>{CSS}</style>
"""

pathlib.Path(OUT).write_text(component, encoding="utf-8")
print(f"작성: {OUT} ({len(component)} bytes)")
