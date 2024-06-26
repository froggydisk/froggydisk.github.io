---
title: "[React Native] Blank screen issue on iOS"

comments: true
categories:
  - Blog
tags:
  - React Native, JavaScript
last_modified_at: 2022-11-13T
---

<p align="center"><img src="https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/black_screen.png?raw=true" width="250" height="500" style="border: 1px solid black" /></p>

어느 순간부터 빌드는 되는데 화면에 아무것도 나타나지 않는 증상이 나타났다. 빌드는 성공하였기 때문에 라이브러리를 설치하면서 어딘가 설정이 꼬인건가 싶었다. 

node_modules를 지웠다 설치하고를 몇 번이나 반복하였지만 해결되지 않았다. 당연히 캐시 삭제 정도로는 어림도 없었다. 

에러 코드조차 나오지 않는 버그였기에 원인 분석부터가 막막했다. 새로운 프로젝트를 새로 하나 팔까 하다가 우선 깃 히스토리를 거슬러 올라가 보기로 하였다. 

다행히 메인 브랜치에 push 해놓은 버전은 빌드가 잘 되었다. 

이제부터는 다른 부분을 찾아내는 노가다이다. 라이브러리를 새로 설치하고 코드를 하나하나 비교하면서 바꾸어 주었는데 생각지도 못한 곳에서 버그를 재현할 수 있었다. 

일단, 인터넷에서 검색하면 React Native는 `자바스크립트 프레임워크`라고 나온다. 그러므로 당연히 자바스크립트 코드를 사용할 수 있다.

하지만 디버깅까지 제대로 해준다고는 하지 않았다... 

```javascript
const example = () => {
  const array = [];
  for (let i = 0; i < 100; i += 2) {
    array.push(i);
  }
  return array;
};
```
문제가 된 부분은 위와 같다. for문을 사용할 때 `i += 2`에서 `=`를 빼먹는 실수가 있었는데 Metro에서는 아무런 버그를 띄워주지 않는다. 

갑자기 멈춰버린 앱을 리로드하면 그때부터 버그 지옥이 시작되는 것이다.

설마 JS 코드 오타를 잡아주지 않는다고는 생각하지 않았기에 더욱더 헤맸던 것 같다. 

### 결론
● **문제**: 앱을 빌드했을 때 Bundle 100% 혹은 Loading from Metro... 문구에서 화면이 멈추고 하얀색 공백 화면만 떠있는 현상.
<br>
● **해결**: 자바스크립트 문법이 틀린 것이 없나 살펴보고 수정한다. (혹은 최근에 설치한 라이브러리가 문제일 수 있다)


● **Issue**: The simulator is stuck with the message 'Bundle 100%' or 'Loading from Metro...' on the white screen.
<br>
● **How to solve**: Check the grammar of your JavaScript code. Metro doesn't let you know the typo of JS code, but just stops the App.

### 참고
[Blank Screen Issue on iOS #26605](https://github.com/facebook/react-native/issues/26605)
