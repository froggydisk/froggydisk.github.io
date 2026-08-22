import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

/**
 * 본문 이미지에 loading/decoding과 intrinsic width·height를 붙인다.
 *
 * 왜 필요한가:
 *  - 포스트 이미지가 전부 즉시 로드돼서, 글 하단 이미지까지 첫 화면에서 같이 내려왔다.
 *  - width/height가 없어서 이미지가 도착할 때마다 본문이 밀렸다(CLS).
 *
 * 42개 이미지를 손으로 고치는 대신 빌드 단계에서 처리한다. 새 글도 자동으로 적용된다.
 *
 * 규칙:
 *  - height가 이미 있으면 손대지 않는다. 글쓴이가 의도한 비율일 수 있다.
 *    (예: black_screen.png는 1170x2532인데 250x500으로 지정돼 있다)
 *  - width가 정수로만 있으면 원본 비율로 height를 계산한다.
 *  - width가 '50%' 같은 CSS 값이면 px height를 만들 수 없으므로 비운다.
 *  - 첫 이미지는 lazy로 만들지 않는다. LCP 요소일 수 있어서 우선순위를 낮추면 손해다.
 *  - height를 우리가 넣은 이미지에만 data-intrinsic을 달아,
 *    CSS의 `img[data-intrinsic] { height: auto }`가 그 이미지에만 적용되게 한다.
 *    (전역 height:auto는 위 black_screen 같은 수동 지정까지 덮어버린다)
 */

const PUBLIC_DIR = fileURLToPath(new URL('../../public', import.meta.url));

/** 같은 파일을 포스트마다 다시 열지 않도록 빌드 동안 캐시한다. */
const sizeCache = new Map();

async function intrinsicSize(src) {
  if (sizeCache.has(src)) return sizeCache.get(src);

  let size = null;
  // public/ 아래 로컬 경로만 측정 가능하다. 외부 URL·data URI는 건너뛴다.
  if (src.startsWith('/') && !src.startsWith('//')) {
    const file = path.join(PUBLIC_DIR, decodeURIComponent(src.split('?')[0]));
    if (file.startsWith(PUBLIC_DIR) && existsSync(file)) {
      try {
        const meta = await sharp(file).metadata();
        if (meta.width && meta.height) size = { width: meta.width, height: meta.height };
      } catch {
        // 측정 실패는 치명적이지 않다. 속성 없이 넘어간다.
      }
    }
  }

  sizeCache.set(src, size);
  return size;
}

function collectImages(tree) {
  const found = [];
  const walk = (node) => {
    if (node.type === 'element' && node.tagName === 'img') found.push(node);
    if (node.children) for (const child of node.children) walk(child);
  };
  walk(tree);
  return found;
}

export default function rehypeImageAttrs() {
  return async (tree) => {
    const images = collectImages(tree);

    await Promise.all(
      images.map(async (node, index) => {
        const props = node.properties || (node.properties = {});

        if (props.decoding == null) props.decoding = 'async';
        // 첫 이미지는 화면 안에 있을 수 있으므로 지연시키지 않는다
        if (props.loading == null && index > 0) props.loading = 'lazy';

        if (props.height != null) return;

        const size = await intrinsicSize(String(props.src ?? ''));
        if (!size) return;

        if (props.width == null) {
          props.width = size.width;
          props.height = size.height;
        } else if (/^\d+$/.test(String(props.width))) {
          const width = Number(props.width);
          props.height = Math.round((width * size.height) / size.width);
        } else {
          return; // '50%' 같은 값 — px height를 만들 수 없다
        }

        props['data-intrinsic'] = '';
      })
    );
  };
}
