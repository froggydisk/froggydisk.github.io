---
title: "[React Native] BottomTabNavigator unmountOnBlur가 SafeAreaView에 미치는 영향"

comments: true
categories:
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2022-11-21T
---

React Native에서 Bottom Tab Navigator를 사용할 때 특정 탭을 누를 때마다 화면이 리렌더링 되도록 하고 싶을 때가 있다. 

그럴 때 사용하는 것이 `unmountOnBlur: true` 이다. 사용법은 아래 코드와 같다. 

```java
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';

const BottomTab = createBottomTabNavigator();
const ExampleScreen = () => {
  return (
    <BottomTab.Navigator>
      <BottomTab.Screen
        name="NavigatorMain"
        component={NavigatorMain}
        options={ {
          tabBarLabel: 'Main',
          unmountOnBlur: true, // 이 부분
        } }
      />
    </BottomTab.Navigator>
  )}
```

문제는 해당 옵션을 사용하게 되면 리렌더링은 문제가 없지만 알 수 없는 깜빡임이 발생한다는 것이다. 

화면 렌더링 순서에 의해 발생하는 깜빡임으로, 사실 예민한 사람이 아니고서야 잘 눈치채지 못 할 지도 모른다. 

원인은 SafeAreaView의 적용 타이밍이 생각보다 빠르지 않다는 데에 있다. 

unmountOnBlur를 통해서 화면을 리렌더링할 시에는 <SafeAreaView> 태그 안의 요소가 먼저 그려진 뒤 status bar 만큼의 크기가 뒤늦게 margin값으로 내려온다. 

해결 방법은 단순히 SafeAreaView를 사용하지 않는 데에 있다. 

대신 react-native-status-bar-height라는 status bar의 높이를 알려주는 라이브러리가 있으니 그것을 통해 직접 컴포넌트에 스타일을 지정해 주면 된다. 

```java
import {getStatusBarHeight} from 'react-native-status-bar-height';
const ExampleScreen = () => {
return (
    <View
      style={ 
        {
        height: Dimensions.get('window').height,
        top: getStatusBarHeight() // 이 부분
        }
      }>
      ... 
    </View>
)}
```

### 참고
[react-native-status-bar-height](https://github.com/ovr/react-native-status-bar-height)
