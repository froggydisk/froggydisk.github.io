---
title: "[쿠버네티스] Harbor Core가 실행되지 않을 때"
comments: true
categories:
  - Blog
tags:
  - Kubernetes, Harbor
last_modified_at: 2025-01-21T
---

오랜만에 Helm을 이용해서 Harbor를 새로 띄우는 작업을 했다.

웬걸, `harbor-core`와 `harbor-registry`가 `Running`으로 바뀌질 않는다.

`kubectl logs`로 로그를 보니 `harbor-core`의 문제였다.

좀 더 보니 `Redis`에 연결하지 못하는 문제가 있는 듯했다.

```text
failed to ping redis://my-harbor-redis:6379/0?idle_timeout_seconds=30...
```

`harbor-redis` 파드 안으로 들어가서 `Redis` 접속이 가능한지 확인하고 `ping`도 보내보았는데 별다른 문제가 없었다.

버전 문제인가 하여 헬름 차트를 바꿔가며 버전별로 실행을 했지만 `helm install`을 할 때마다 계속해서 같은 문제가 발생했다.

그러다가 `goharbor`의 깃헙 레포에서 이슈 하나를 발견했는데 다행히도 나와 같은 증상을 겪은 사람이 있었다. ([참고](https://github.com/goharbor/harbor-helm/issues/1216]))

요는 `쿠버네티스 DNS`에 문제가 있는지 확인하라는 내용이었다.

`kube-system` 네임스페이스에 있는 `coredns` 파드를 확인하고 모두 지워 재시작해주니 `harbor-core`가 `redis`를 정상적으로 찾기 시작했다.

`VPN`을 설정하다가 `10.0.0.1/24`번대 `IP`를 건드릴 일이 있었는데 그 때 `쿠버네티스 DNS` 설정과 충돌한 것이 아닐까 추측해본다.
