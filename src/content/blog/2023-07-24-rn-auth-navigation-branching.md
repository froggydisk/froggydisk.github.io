---
title: "[React Native] 처음 앱 진입시 로그인 상태에 따른 네비게이션 분기"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2023-07-24T
---

보통 앱을 만들게 되면 현재 로그인한 상태에 따라 시작하는 `Screen`을 다르게 설정함으로써 UX를 개선한다.      
`NavigatorAuth, NavigatorMain`과 같이 로그인의 상태에 따라 진입하는 Navigator가 다른 경우에는 간단하다.         
아래의 코드처럼 로그인 상태값에 따라 삼항연산자를 활용하여 진입점을 바꾸어주면 된다.

```java
function App() {
  const [isLogin, setIsLogin] = useState(false);
  ... (setIsLogin에 상태값을 넣어주는 로직)

  return (
    <NavigationContainer>      
      {isLogin ? (
        <NavigatorMain /> // 로그인 되어있는 경우 홈 진입
      ) : (
        <NavigatorAuth /> // 로그인이 안 되어있는 경우 로그인 페이지 진입
      )}
    </NavigationContainer>
  );
}
```

하지만 굳이 두 개의 Navigator를 쓰지 않고 하나의 Navigator 안에서 진입점을 다르게 해주고 싶은 경우도 있을 것이다.                  
그러한 경우에는 **useNavigationContainerRef()를 활용해주면 된다.** 아래 코드를 살펴보자.
      
```java
// app.js 파일
function App() {
  const [isLogin, setIsLogin] = useState(false);
  ... (setIsLogin에 상태값을 넣어주는 로직)

  // 로그인이 안 되어있는 경우 로그인 페이지 진입
  const [route, setRoute] = useState('LoginScreen'); 
  useEffect(() => {
    if (isLogin) {
        setRoute('MainScreen'); // 로그인이 되어있는 경우 홈 진입
    }
  }, [isLogin]);

  return (
    <NavigationContainer>
        <NavigatorMain initialRouteName={route} />
    </NavigationContainer>
  );
}
```
우선 app.js에서 로그인 상태에 따른 분기를 처리해주고 이후 NavigatorMain에서 분기할 지점(initialRouteName)으로 화면을 전환하면 된다.

```java
// NavigatorMain.js 파일
import React, {useEffect, useRef} from 'react';
import {
  NavigationContainer,
  useNavigationContainerRef,
} from '@react-navigation/native';

const NavigatorMain = ({initialRouteName}) => {  
  const navigationRef = useNavigationContainerRef();
  useEffect(() => {
    // navigate 기능을 이용해 app.js에서 바뀐 진입점으로 화면을 전환
    navigationRef.navigate(initialRouteName); 
  }, [initialRouteName]);
  return (    
    <NavigationContainer ref={navigationRef}>
      ...
    </NavigationContainer>
  );
};
```

생각보다 간단하다. 이를 활용하면 두 곳으로의 분기 뿐만아니라 조건에 따라 여러 스크린으로의 분기도 가능하다.