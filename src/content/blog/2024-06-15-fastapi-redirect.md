---
title: "[FastAPI] API 요청 시 307 Temporary Redirect가 뜨는 이슈"
comments: true
categories:
  - Blog
tags:
  - Python, FastAPI
last_modified_at: 2024-06-15T
---

어느 순간부터 FastAPI 서버에 API 요청을 할 때 status code가 307가 뜨기 시작했다.

분명 쿠버네티스에 띄워놓은 서비스는 잘 돌아가고 있는데 로컬에서만 안되는게 신기했다.

저번에 건드린 `next.config.mjs` 파일이 문제가 되었나해서 `rewrite()` 함수를 요리조리 건드려 보았지만 여전히 응답은 같았다.

그러던 중 스택오버플로에서 해답을 찾았다. ([stackoverflow](https://stackoverflow.com/questions/70351360/keep-getting-307-temporary-redirect-before-returning-status-200-hosted-on-fast))

FastAPI로 서버를 구성하다보면 보통 API url 끝에 `/` 를 붙이는 경우가 많다.

예를 들면 이런 경우다.

```java
@app.get("/patients/")
```

보통은 API 요청을 할 때 끝부분에 `/`가 있든 없든 문제가 발생하지 않지만 로컬에서는 `/`를 빠트리게 되면 `307 Temporary Redirect` 이슈가 발생하는 듯하다.

FastAPI는 docs를 제공하므로 백엔드 개발자가 실수할 일이 없으니 프론트 개발자가 API url을 작성할 때 주의하면 되겠다.

결론은 **`/` 확인을 잘하자**.
