/** 포스트 파일명(YYYY-MM-DD-slug)에서 SEO 관련 값을 뽑아내는 공용 헬퍼 */

export function postSlug(id: string): string {
  return id.replace(/^\d{4}-\d{2}-\d{2}-/, '');
}

/**
 * 파일명 날짜는 타임존 없는 표기이므로 UTC 자정으로 고정한다.
 * (로컬 KST 빌드와 CI UTC 빌드가 하루 어긋나는 것을 막는다)
 */
export function postDate(id: string): Date {
  return new Date(id.slice(0, 10) + 'T00:00:00Z');
}

/** 빌드 머신 타임존과 무관하게 동일한 날짜 문자열을 만든다 */
export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

export function parseTags(raw: string[] | undefined): string[] {
  return (raw || [])
    .flatMap((t) => t.split(',').map((s) => s.trim()))
    .filter(Boolean);
}

/**
 * last_modified_at 문자열을 Date로. 실패하면 발행일로 폴백.
 * 기존 글은 대부분 `2024-02-05T`처럼 시각이 빠진 형태라 이를 관대하게 처리한다.
 */
export function modifiedDate(id: string, lastModified?: string): Date {
  if (lastModified) {
    let v = lastModified.trim().replace(' ', 'T').replace(/T$/, '');
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) v += 'T00:00:00Z';
    else if (!/(Z|[+-]\d{2}:?\d{2})$/.test(v)) v += 'Z';
    const d = new Date(v);
    if (!Number.isNaN(d.getTime())) return d;
  }
  return postDate(id);
}

/** 마크다운 잔여 마커를 걷어낸 순수 텍스트 길이 판정용 */
function clean(s: string): string {
  return s
    .replace(/^\s{0,3}[-*+]\s+/gm, '')
    .replace(/[#>`*_~|]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * 마크다운/MDX 본문에서 meta description 용 요약을 추출한다.
 * 코드블록·JSX·임포트문·이미지·링크 문법을 제거하고 첫 문단들을 이어붙인다.
 */
export function excerpt(body: string, max = 155): string {
  const base = body
    // MDX 임포트/익스포트
    .replace(/^\s*(import|export)\s+.*$/gm, '')
    // 펜스 코드블록
    .replace(/^\s*(`{3,}|~{3,})[\s\S]*?^\s*\1\s*$/gm, '')
    // HTML/JSX 태그
    .replace(/<[^>]+>/g, ' ')
    // 이미지 → 제거, 링크 → 텍스트만
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');

  // 헤딩 줄은 통째로 버리고 산문부터 요약한다. 산문이 거의 없으면 헤딩 텍스트로 폴백.
  const withoutHeadings = base.replace(/^\s{0,3}#{1,6}\s+.*$/gm, '');
  const source = clean(withoutHeadings).length >= 40 ? withoutHeadings : base;

  let text = source
    // 남은 헤딩 마커·인용·리스트 마커
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s{0,3}>\s?/gm, '')
    .replace(/^\s{0,3}[-*+]\s+/gm, '')
    .replace(/^\s{0,3}\d+\.\s+/gm, '')
    // 수평선·표 구분선
    .replace(/^\s*([-*_]\s*){3,}$/gm, '')
    .replace(/^\s*\|[\s\-:|]+\|\s*$/gm, '')
    // 인라인 강조·코드
    .replace(/`([^`]*)`/g, '$1')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(\*|_)(.*?)\1/g, '$2')
    .replace(/~~(.*?)~~/g, '$1')
    // 각주·엔티티 잔여물
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (text.length <= max) return text;

  const cut = text.slice(0, max);
  // 문장 경계 우선, 없으면 공백 경계
  const sentence = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('다. '), cut.lastIndexOf('요. '));
  if (sentence > max * 0.6) return cut.slice(0, sentence + 1).trim();
  const space = cut.lastIndexOf(' ');
  return (space > max * 0.6 ? cut.slice(0, space) : cut).trim() + '…';
}
