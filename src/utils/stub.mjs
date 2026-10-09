/**
 * 아직 쓰지 않은 장(목차만 잡아둔 뼈대)을 가려낸다.
 *
 * 컴퓨터 구조 책은 장마다 "다룰 내용" 한 줄만 둔 채 목차를 먼저 공개했다.
 * 이런 페이지가 sitemap의 40%를 차지하면 구글이 사이트 전체를 얇은 콘텐츠로 본다.
 * 목차·라우트에는 그대로 두고, 색인(noindex)과 sitemap에서만 뺀다.
 * 본문을 채우면 저절로 색인 대상이 된다.
 *
 * astro.config.mjs(파일을 직접 읽는다)와 라우트·sitemap.xml.ts(컬렉션 body)가
 * 같은 판정을 써야 두 sitemap이 어긋나지 않으므로 이 파일 하나에 둔다.
 *
 * 2026-10 기준 뼈대 장은 258자 이하, 가장 짧은 실제 장은 1776자다.
 */
export const STUB_MIN_CHARS = 800;

/** @param {string} body 프런트매터를 뺀 마크다운 본문 */
export function isStubBody(body) {
  const text = body.replace(/<!--[\s\S]*?-->/g, '').replace(/\s/g, '');
  return text.length < STUB_MIN_CHARS;
}

/** @param {string} raw 프런트매터를 포함한 파일 전체 */
export function isStubFile(raw) {
  const body = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
  return isStubBody(body);
}
