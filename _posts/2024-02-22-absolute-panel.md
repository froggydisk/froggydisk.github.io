---
title: "[React Native] 화면 전체를 덮는 absolute 포지션의 컴포넌트 스타일링"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2024-02-22T
---

화면 전체를 덮는 absolute 포지션의 컴포넌트를 구현할 때 보통 이런식으로 스타일링을 한다.
```javascript
container: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
}
```

모달을 띄우거나 할 때 뒷 배경을 옅은 회색으로 한다던가 opacity를 주기 위해서 주로 쓰게 되는데 쓸 때마다 코드가 너무 길어져 신경이 쓰였다.

아무 생각 없이 쓰던거라 더 좋은 방법을 찾을 생각조차 안하고 있었는데 우연히 공식문서에서 관련 내용을 발견했다.

React Native에서는 다음과 같이 **한 줄**로 구현이 가능하다.

```javascript
container: {...StyleSheet.absoluteFillObject}
```
[공식문서 - StyleSheet](https://reactnative.dev/docs/stylesheet)

공식문서를 잘 읽어보는 것에 대한 중요성을 다시금 느낀다.