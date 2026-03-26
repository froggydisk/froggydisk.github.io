---
title: "[React Native] 갑자기 Hot Reload가 안될 때 대처법"
comments: true
categories:
  - Blog
tags:
  - Hot Reload, Fast Refresh
last_modified_at: 2024-07-08T
---

VSCode에서 앱 작업을 하며 코드 저장을 할 때마다 변경 사항이 자동으로 시뮬레이터나 디바이스에 반영이 되는 편리함에 취해있던 어느날.

갑자기 `Hot Reload`가 먹통이 되었다.

따로 설정을 해준 적도 없었기에 어떻게 살려낼 수 있을지 막막했다.

여러 원인을 감각적으로는 알고 있었는데 정리해놓은 적이 없어서 후회가 몰려왔다.

그래서 이번 기회에 정리하기로 마음먹었다.

이미 [React Native 깃 페이지](https://github.com/facebook/react-native/issues/33102)에서 이슈로 다뤄진 내용이라 레퍼런스 찾는 것은 어렵지 않았다.

정리하자면 다음과 같다.

## 1

iOS 기준으로 `cmd + D`를 누르거나 디바이스를 좌우로 흔들어 개발자 창을 연다. 이후 `enable fast refresh`를 시킨다.  
➡ 필자는 해당 버튼을 찾을 수가 없어서 실패하였다.

## 2

디바이스와 컴퓨터가 완전히 동일한 와이파이 네트워크상에 존재하는지 확인한다. (이름이 같아도 2.4G/5G는 다른 네트워크다!) 물론 시뮬레이터로 작업할 때는 관련이 없다.

## 3

프로젝트의 루트 경로로 가서 다음과 같은 명령어를 입력한다.

```bash
rm -rf .git/index.lock
```

의외로 이 방법으로 해결한 사람들이 많은 듯하다. 필자도 `index.lock` 파일을 지워주었더니 거짓말처럼 문제가 해결되었다.
