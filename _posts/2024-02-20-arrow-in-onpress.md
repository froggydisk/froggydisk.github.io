---
title: "[React Native] onPress에서 화살표 표현식의 생략"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2024-02-20T
---

React Native에서 onPress를 사용할 때 무의식적으로 화살표 표현식 `()=>`을 사용하고 있었는데 어느날 특정 경우에 생략이 가능하다는
것을 알게 되었다.

코드를 한 글자라도 줄일 수 있다는 생각에 과연 어떠한 조건에서 가능한지 궁금해서 찾아보았다. 다음의 두 가지 경우를 살펴보자.
### 1
```java
onPress={()=>handlePressFirst(value)}
```
### 2
```
onPress={handlePressSecond}
```

둘 다 정상적으로 실행되는 예시이다. 차이를 알겠는가?

`handlePressFirst` 함수는 value라는 인자를 받고 있고 `handlePressSecond`는 아무런 인자 없이 실행되는 함수임을 알 수 있다. 

만약 이렇게 하면 어떻게 될까?

```
onPress={handlePressFirst(value)}
```

이렇게 되면 해당 페이지가 렌더링 될 때 클릭 이벤트가 없어도 handlePressFirst 함수가 자동으로 실행될 것이다. 이는 예상치 못한 버그를 발생시킬 수 있으므로 좋지 않다. 주의하자. 

다만 전달할 인자가 아무것도 없는데 화살표 표현식을 사용하는 것은 아무런 문제가 없다.

```java
onPress={()=>handlePressSecond()}
```

가독성을 올리고 싶다면 onPress 안에 들어가는 함수가 아무런 인자를 받지 않는 함수일 때 화살표 표현식과 함수 뒤의 빈 괄호를 생략하면 된다.

잘 써먹을 만한 팁이지만 괜히 헷갈린다면 무조건 onPress 안에 `()=>`를 넣자.

참고로 이는 React의 onClick에서도 동일하다.
