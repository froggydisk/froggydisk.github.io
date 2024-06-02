---
title: "[Next] 서비스 배포 시 Mixed Content 오류"
comments: true
categories:
  - Blog
tags:
  - Next
last_modified_at: 2024-06-02T
---

Next.js(@14.2.3)를 활용하여 만든 EMR 데모 버전을 도커로 말아 쿠버네티스에 올렸는데 자꾸 `Mixed Content` 에러가 나고 있었다.

`Mixed Content` 에러는 웹페이지는 `https`로 서비스되고 있는데 어떠한 리소스를 `http`로 로드하려고 할 때 발생한다.

API URL은 `.env.*`에서 관리를 하고 있기 때문에 모든 API 콜에 있어서 동일하게 적용될 터이고 적용한 프로토콜은 분명 `https`였다.

구글링 해보면 흔히 나오는 해결 방법은 두 가지이다.

### 1. 헤더 안에 보안 정책 관련 메타 태그를 추가하기

```javascript
// layout.tsx
<Html>
  <Head>
    <meta
      httpEquiv="Content-Security-Policy"
      content="upgrade-insecure-requests"
    /> // <- add this
  </Head>
  <body>
    <Main />
    <NextScript />
  </body>
</Html>
```

모든 리소스를 강제로 https로 바꿔서 로드하는 것이라 효과가 있을거라 생각했지만 에러가 해결되지는 않았다.

`http`로 밖에 로드되지 않는 리소스도 분명 있을 것이기에 모든 문제를 해결해주는 만능키는 아니다.

### 2. Next의 프록시 설정 변경

처음에는 API URL로 들어갈 때 서버의 `Nginx` 안쪽에서 발생하는 리디렉션이 문제일까 하고 여러 설정을 바꿔보았지만 아무런 문제가 없었다.

그렇다면 매우 높은 확률로 클라이언트쪽 문제일 가능성이 높다.

우선, Next는 특정 경로에 대해 프록시를 설정할 수 있는 기능을 제공한다.

이 기능을 사용하는 이유는 여러가지 있을테지만 필자의 경우에는 보통 서버 코드를 변경할 수 없는 경우 `CORS` 문제를 해결하기 위해 사용한다.

관련 설정은 `next.config.mjs` 파일 안에서 설정해주면 되고, 이번 프로젝트에서는 로컬 컴퓨터에서 PACS 서버에 접근할 때 활용하고 있었다.

코드는 다음과 같다.

```javascript
async rewrites() {
    return [
      {
        source: "/pacs-api/:path*",
        destination: "http://localhost:8042/:path*",
      },
    ];
  },
```

`/pacs-api`로 시작하는 URL은 dev 환경에서만 사용하고 있었기에 전혀 의심하지 않고 있었는데 `Mixed Content` 에러를 판단함에 있어서 아무래도 source URL과는 상관없이 프로토콜을 우선적으로 적용하는 듯하다.

즉, destination이 `http`이기에 해당 웹페이지에서 보내는 모든 리소스 요청은 source와 상관없이 `http`로 보내지고 있었다.

# 결론

문제를 알았다면 해결은 어렵지 않다. `development` 환경에서만 해당 프록시가 동작하도록 바꿔주면 된다.

```javascript
async rewrites() {
  if (process.env.NODE_ENV === 'development') {
    return [
      {
        source: "/pacs-api/:path*",
        destination: "http://localhost:8042/:path*",
      },
    ];
  } else {
    return []; // 다른 환경에서는 리디렉션을 적용하지 않음
  }
},
```
