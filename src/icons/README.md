# src/icons

astro-icon 이 로컬 SVG 아이콘을 찾는 디렉터리다 (`iconDir` 기본값).

이 사이트는 Iconify 컬렉션(`lucide`, `ph`)만 쓰기 때문에 여기에 둘 파일이 없다.
다만 디렉터리 자체가 없으면 빌드마다 아래 경고가 뜬다.

```
[WARN] [astro-icon] Failed to load icons from "src/icons":
ENOENT: no such file or directory, scandir 'src/icons/'
```

그래서 비워둔 채 이 파일만 남겨 디렉터리를 유지한다.
로컬 SVG 아이콘이 필요해지면 여기에 넣고 `<Icon name="파일이름" />` 으로 쓴다.
