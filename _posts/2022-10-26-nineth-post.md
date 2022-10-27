---
title: "[React Native] Bottom Tab Navigator 없애기"

comments: true
categories:
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2022-10-26T
---


React Native를 이용하여 앱을 만들게 되면 [@react-navigation/bottom-tab](https://reactnavigation.org/docs/bottom-tab-navigator/) 라이브러리의 네비게이터를 자주 이용하게 된다. 
<br> 
네비게이터를 하나만 사용할 때는 문제가 없는데 여러개의 네비게이터들이 차곡차곡 쌓이면서부터 문제가 발생하기 시작한다.
<br> 
특정 스크린으로 이동할 때에는 하단 메뉴바를 안보이게 해야 할 때가 많은데 주로 아래와 같이 해결할 것이다.
```javascript
    import {getFocusedRouteNameFromRoute} from '@react-navigation/native';
    ...
    const NavigatorExample = ({navigation, route}) => {
        React.useLayoutEffect(() => {
        var screens = {NavigatorOne: 1, NavigatorTwo: 2}; // 하단 메뉴탭을 숨길 곳
        const routeName = getFocusedRouteNameFromRoute(route);
        console.log(routeName);
        if (routeName in screens) {
            navigation.setOptions({tabBarStyle: {display: 'none'}});
        } else {
            navigation.setOptions({tabBarStyle: {display: 'flex'}});
        }
        }, [navigation, route]);
    return(
        ...
    )
    }
```
이렇게 하면 원하는 스크린에서 하단 탭이 사라지기는 하나 그 흔적을 남기게 된다. 
<br> 
필자가 경험한 바로는 보통 세 가지 버그가 일어나기 쉽다.
1. 화면 이동 뒤 하단 메뉴가 있던 자리만 현재 스크린의 배경색과 색이 다르다. 
2. 화면 이동 뒤 하단 메뉴가 있던 자리에 버튼을 위치시키면 제대로 눌리지 않는다. 
3. 화면을 이동하는 찰나에 이전 화면의 하단 탭이 사라지면서 알 수 없는 잔상(flicker)을 남긴다. 

위와 같은 문제를 해결하기 위해서는 가장 윗 부분의 태그, 즉 보통 `<SafeAreaView>`일 텐데 이곳을 잘 공략해야한다.
```java
<SafeAreaView style={ {height:'100%'} }>
```
보통 위와 같이 설정해주는 것이 일반적이다. 하지만 저렇게 지정할 시에는 해당 스크린에서 일어나는 모든 일은 하단 탭 바로 윗단까지만 적용되게 된다.
고로 하단 탭이 사라진 자리에 대한 영향력이 없다는 의미이다. 
<br>
해결을 위해 추천하는 방법은 아래와 같다.
```java
const NavigatorExample = ({navigation, route}) => {
    ...
    return (
    <View style={ {height: Dimensions.get('window').height} }> // 이 부분이 중요
        <Stack.Navigator
        screenOptions={{ headerShown: false }}>
        <Stack.Screen name="RootHome" component={RootHome} />
        <Stack.Screen name="ExampleGo" component={ExampleGo} />
        </Stack.Navigator>
    </View>
    );
};
```
바로 `Dimension.get('window')`를 활용하는 방법이다. 이것이 위치해야할 곳은 bottom tab 네비게이터 위에서 stack 네비게이터가 분기하는 지점이다. 
즉 bottom tab 네비게이터 위에 있으면서 stack 네비게이터의 루트가 될 네비게이터와 그 홈 스크린이 적당하다. 
<br>
위의 예를 들어보면 NavigatorExample이라는 stack 네비게이터가 어떤 bottom tab 네비게이터 위에 있다고 가정하자. 
그러면 NavigatorExample 네비게이터와 그 홈 스크린인 RootHome 스크린의 height는 Dimension.get('window').height로 지정해주어야 한다. 
위에서는 RootHome에 대한 예시가 없지만 잊지 말자. 
<br>
이렇게 하면 버그는 해결되었을 것이다! 그래도 불안하다면 웬만한 스크린의 높이 지정은 Dimension을 이용하도록 하자. 
