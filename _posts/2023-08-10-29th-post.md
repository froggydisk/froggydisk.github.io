---
title: "[React Native] && 구문 사용 시 Text 에러"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2023-08-10T
---

개발 중에 예상치 못한 에러를 만나 기록해둔다.       
뜬금없이 `Error: Text strings must be rendered within a <Text> component.`에러를 만나게 되었는데 이는 주로 <Text>태그가 아니라 <View>안에 문자열을 사용하여 나타나는 에러다. 
React로 개발을 하다가 React Native로 넘어오게 되거나 멀티로 개발을 할 때 흔히 하는 실수이다. 

하지만 이번에는 눈을 씻고 찾아봐도 원인을 찾기 힘들었다.
예를 들어 아래와 같은 코드가 존재한다고 해보자.

```java
const [sample, setSample] = useState(undefined)
useEffect(()=> {
    setSample(0~100 사이 랜덤한 정수)
}, [])
return(
    <View>
        {sample && <Text>test</Text>}
    </View>
)
```

예상컨대 맨 처음에는 sample값이 `undefined`이기에 화면에 test는 나타나지 않는다.      
전체 layout이 그려진 뒤 useEffect가 실행되면서 setSample()에 의해 sample값이 `0~100 사이 정수`로 바뀌게 되고, 이후 `test`라는 문자열이 화면에 나타날 것으로 예상된다.

아, 여기서 놓치면 안되는 것이 자바스크립트에서 `0`은 `false`로 취급되기 때문에 특별히 `0`의 경우에는 `undefined`와 같이 `test`는 나타나지 않을 것이다. 
덧붙이자면, **`false, undefined, null, 0, -0, Nan, ""`** 다음과 같은 여섯 가지의 경우는 모두 `false`로 취급되므로 주의하자.

그렇다면 위의 여섯 가지의 경우는 React Native에서 모두 `false`로 처리될까? (RN 0.71.6 버전 기준)         
아쉽게도 React Native 상의 `&& 구문`에서는 제대로 처리되지 않는 모습을 보인다.

실험해본 결과 sample값이 `0`과 `-0`의 경우에는 모두 `Error: Text strings must be rendered within a <Text> component.`에러를 나타냈다.

따라서 위와 같은 에러를 만난 경우 `&& 구문`을 잘 확인해보자.
참고로, 삼항연산자의 경우에는 해당 에러가 발생하지 않았다. 