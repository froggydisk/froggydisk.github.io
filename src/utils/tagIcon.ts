/**
 * 태그별 아이콘. archive 목록의 대표 태그 한 줄에서 쓴다.
 * 로고가 있는 것은 형태를 빌려오고(React=원자, Pytorch=불꽃, Next=삼각형),
 * 나머지는 그 태그가 다루는 물건이나 동작으로 고른다.
 * 이름은 @iconify-json/lucide · @iconify-json/ph 에 실재하는 것만 쓴다.
 */
const TAG_ICON: Record<string, string> = {
  // 카테고리
  'React Native': 'lucide:smartphone',
  'AI': 'lucide:sparkles',
  'Deep Learning': 'lucide:brain-circuit',
  'Kubernetes': 'lucide:boxes',
  'Tools': 'lucide:wrench',
  'CSS': 'lucide:palette',
  'DevOps': 'lucide:infinity',
  'Python': 'lucide:file-code',
  'React': 'lucide:atom',
  'Hardware': 'lucide:cpu',
  'Git': 'lucide:git-branch',
  'Linux': 'ph:linux-logo',
  'Database': 'lucide:database',
  'Security': 'lucide:shield',
  'Next': 'lucide:triangle',
  // 주제 태그
  'GPU': 'ph:graphics-card',
  'Agent': 'lucide:bot',
  'LLM': 'lucide:message-square-code',
  'Pytorch': 'lucide:flame',
  'API': 'lucide:webhook',
  'Mobile': 'lucide:tablet-smartphone',
  'Docker': 'lucide:container',
  'Mac': 'ph:apple-logo',
  'Harness Engineering': 'lucide:settings-2',
  'Testing': 'lucide:flask-conical',
  'Server': 'lucide:server',
  'Workflow': 'lucide:workflow',
  'SEO': 'lucide:search',
  'JavaScript': 'lucide:braces',
  'Performance': 'lucide:gauge',
};

export const TAG_ICON_FALLBACK = 'lucide:tag';

/** 없는 태그는 기본 태그 아이콘으로 떨어진다 */
export function tagIcon(tag: string): string {
  return TAG_ICON[tag] ?? TAG_ICON_FALLBACK;
}

/** 매핑이 빠진 태그를 찾을 때 쓴다 */
export function knownTags(): string[] {
  return Object.keys(TAG_ICON);
}
