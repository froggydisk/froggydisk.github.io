#!/usr/bin/env python3
"""장 MDX 한 편의 다이어그램을 dev 서버 렌더에서 뽑아 라이트·다크로 찍는다.

    python3 .claude/skills/book-chapter/scripts/render-diagrams.py <장.mdx> <출력 디렉터리> [--base http://localhost:4321]

- URL은 파일 경로에서 만든다 (숫자 접두사를 떼고 /books/<책>/<부>/<장>/)
- 컴포넌트 이름은 MDX의 import 순서가 아니라 본문에 <X /> 가 나온 순서로 잡는다
- 각 그림의 <style>은 컴포넌트 소스에서 가져오고, editorial.css 토큰 값을 인라인한다
- 결과: <출력>/<컴포넌트>-light.png, -dark.png. 찍은 뒤 Read로 눈으로 본다
"""
import os
import re
import subprocess
import sys
import urllib.request

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
LIGHT = {'--bg': '#faf9f5', '--bg-soft': '#f0eee6', '--ink': '#141413', '--body': '#2b2a26',
         '--muted': '#6b6a63', '--rule': '#e3e0d8', '--accent': '#cc785c', '--accent-strong': '#b3603f'}
DARK = {'--bg': '#191816', '--bg-soft': '#201f1c', '--ink': '#f5f3ec', '--body': '#dedbd0',
        '--muted': '#918e84', '--rule': '#2d2b26', '--accent': '#d9836a', '--accent-strong': '#e8a48c'}
FONTS = ('--font-sans:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,'
         '"Apple SD Gothic Neo",sans-serif;--font-mono:"JetBrains Mono","SF Mono",Menlo,monospace')


def url_of(mdx: str, base: str) -> str:
    m = re.search(r'src/content/book/([^/]+)/([^/]+)/([^/]+)\.mdx?$', mdx)
    if not m:
        sys.exit(f'경로 형식이 아니다: {mdx}')
    strip = lambda s: re.sub(r'^\d+-', '', s)
    return f'{base}/books/{m.group(1)}/{strip(m.group(2))}/{strip(m.group(3))}/'


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    base = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--base=')), 'http://localhost:4321')
    if len(args) != 2:
        sys.exit(__doc__)
    mdx, out = args
    os.makedirs(out, exist_ok=True)
    src = open(mdx, encoding='utf-8').read()
    imports = dict(re.findall(r'^import (\w+) from "([^"]+)";?$', src, re.M))
    used = re.findall(r'^<(\w+) />', src, re.M)
    url = url_of(mdx, base)
    html = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    blocks = re.findall(r'<div class="dg[^"]*"[^>]*>\s*<svg.*?</svg>\s*</div>', html, re.S)
    print(f'{url}\n본문 컴포넌트 {len(used)}개 · 렌더된 그림 {len(blocks)}개')
    if len(used) != len(blocks):
        print('개수가 다르다. .dg 래퍼가 없는 컴포넌트가 있는지 본다')
    root = os.path.dirname(os.path.abspath(mdx))
    for name, block in zip(used, blocks):
        comp = os.path.normpath(os.path.join(root, imports[name]))
        css = re.search(r'<style>(.*?)</style>', open(comp, encoding='utf-8').read(), re.S).group(1)
        h = int(re.search(r'viewBox="0 0 672 (\d+)"', block).group(1))
        for theme, tok in (('light', LIGHT), ('dark', DARK)):
            toks = ';'.join(f'{k}:{v}' for k, v in tok.items())
            doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>:root{{{toks};{FONTS}}}'
                   f'html,body{{margin:0;background:var(--bg);color:var(--body)}}body{{width:672px;padding:8px 14px}}'
                   f'.dg{{margin:0 !important}}{css}</style></head><body>{block}</body></html>')
            page = os.path.join(out, f'{name}-{theme}.html')
            open(page, 'w', encoding='utf-8').write(doc)
            png = os.path.join(out, f'{name}-{theme}.png')
            subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                            f'--window-size=700,{h + 16}', '--force-device-scale-factor=2',
                            f'--screenshot={png}', f'file://{page}'], capture_output=True, timeout=60)
            print(f'  {name} {theme}: H={h} → {png}')


if __name__ == '__main__':
    main()
