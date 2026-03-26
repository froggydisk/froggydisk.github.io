---
title: "[React Native] Draggable Button과 ScrollView"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2022-10-27T
---


리액트 네이티브를 이용하여 앱을 만들 때 이리저리 끌고 다닐 수 있는 버튼을 만들고 싶을 때가 있다. 
<br>
만들어놓고 화면에서 요리조리 움직이다보면 나름 재미가 있다. 
<br>
바퀴를 다시 발명하지 말라고 누군가 그랬던가. 구현을 위해 필자가 사용한 것은 `react-native-draggable`이라는 이미 잘 만들어진 라이브러리이다.

### 설치
```javascript
npm install react-native-draggable

cd ios
arch -x86_64 pod install // m1이 아닌 경우에는 그냥 pod install
```

### 사용
```java
import Draggable from 'react-native-draggable';

<Draggable>
    <View> [내용] </View>
</Draggable>
```
<br>
이처럼 설치하고 사용하는 것은 매우 간단하다. 
<br>
하지만 늘 그렇듯 항상 단독으로 사용할 때는 괜찮은데 여러 기능들이 맞물리면서 문제가 발생한다. 
<br>
오늘 얘기할 내용은 `Draggable Button`을 사용할 때 주의해야 할 점이다. 

### 주의
리액트 네이티브의 특성상 가장 아래에 위치한 컴포넌트가 화면 z축 최상단에 위치하게 된다. 즉 `Draggable Button`을 코드 상에서 가장 아래쪽에 배치해야한다.
```java
return(
    <View>
        [화면 내용]...
        <Draggable></Draggable>
    </View>
)
```
이렇게만해도 다행히 iOS에서는 (웬일로) 잘 동작하지만 여러 제스쳐가 동시에 입력되어야 하는 스크린에서는 기능들이 원하는 대로 작동하지 않을 때가 많다. 
<br>
특히 ScrollView 안에서는 스크롤 동작과 타이밍이 겹치면서 버튼을 원하는대로 움직이기 전에 화면 스크롤이 되어버린다. 따라서 버튼을 눌렀을 때 스크롤 기능을 멈춰주고
버튼에서 손을 떼었을 때 다시 스크롤 기능을 살려줄 필요가 있다. 
<br>
처음 개발을 하였을 때는 EventListener가 대체 어디에 쓰이는 걸까 긴가민가 했는데 이제 보면 절대 없어서는 안 될 기능이다. 

```java
const [scrollable, setScrollable] = React.useState(true);

return(
    <View>
        <ScrollView scrollEnabled={scrollable}>
	    [화면 내용]...
            <Draggable
            // 버튼을 눌렀을 때의 이벤트
            onPressIn={() => setScrollable(false)}
            // 버튼에서 손을 떼었을 때의 이벤트
            onPressOut={() => setScrollable(true)}
            ></Draggable>
        </ScrollView>
    </View>
)
```

`Draggable Button`말고도 제스쳐가 필요한 컴포넌트가 하나의 스크린 상에 복수개 존재할 때는 이렇게 구현해 주면 충돌을 막을 수 있다!


### 참고
[Draggable Button GitHub](https://github.com/tongyy/react-native-draggable)