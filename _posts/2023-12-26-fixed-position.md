---
title: "[React Native] 스크롤에 상관없이 고정된 컴포넌트 만들기"

comments: true
categories:
  - Blog
tags:
  - React Native, SafeAreaView
last_modified_at: 2023-12-26T
---


React와 React Native는 비슷하면서도 은근히 다른 부분이 많은 것 같다. 

두 프레임워크를 번갈아가며 사용하다보면 문법적인 부분에 대해서 헷갈릴 때가 자주 있다.

앱에서 새로운 기능을 만들다보니 컴포넌트 하나를 스크롤에 영향받지 않으면서 화면에 고정시킬 필요가 있었는데 React에서
자주 사용했던 문법을 썼더니 바로 에러가 났다.
```javascript
position: 'fixed'
```

예를 들면 쇼핑 사이트에서 장바구니나 문의하기 버튼이 화면 측면에 계속해서 따라다니는 기능이다. 

순간적으로 이거를 어떻게 해야하나 생각이 나질 않아 당황했는데 사실 곰곰히 생각해보면 간단한 질문이었다.

position이 `relative`일 리는 없을거고, `absolute`인 상태에서 스크롤을 무시할 수 있는 기능? 

아무 생각 없이 화면 위에 absolute 포지션 레이어를 하나 더 씌워버려서 스크롤이 되지 않는 상황까지 갔다가 문득 깨달았다. 

<b>그냥 ScrollView나 FlatList의 내부가 아니라 같은 레벨(위치)에 삽입해주면 되는 것이었다.</b>

스크롤을 해야할 정도로 구성 컴포넌트들이 많다면 화면 높이는 `Dimensions`로 계산해서 top으로 내려주어야 한다. 

이 과정에서 아이폰의 경우 다이나믹 아일랜드에 대해 기존에 사용하던 유명 라이브러리들이 제대로 작동하지 않는 현상을 만났다. 

그래서 현재는 그냥 맘편히 [`react-native-safe-area-context`](https://github.com/th3rdwave/react-native-safe-area-context)를 사용하고 있다.

다만 `SafeAreaView` 컴포넌트에 대해서는 다음과 같은 애니메이션 이슈가 존재하므로 주의하자.

> While React Native exports a SafeAreaView component, this component only supports iOS 10+ with no support for older iOS versions or Android. In addition, it also has some issues, i.e. if a screen containing safe area is animating, it causes jumpy behavior. So we recommend to use the useSafeAreaInsets hook from the react-native-safe-area-context library to handle safe areas in a more reliable way. [출처 React Navigation](https://reactnavigation.org/docs/handling-safe-area/)

이는 화면 전환을 할 때에도 가끔씩 발견되는 깜빡임 문제이다. 예민하지 않은 사람은 상관없을 수 있다.

따라서 Safe Area 관련 기능은 전부 `useSafeAreaInsets`를 사용하여 해결하기로 하고 다른 라이브러리는 삭제해주었다. 예를 들면 
`react-native-iphone-x-helper`와 같은 라이브러리다. 이게 제대로 작동하지 않는다는 것을 깨달을 때까지 시간이 꽤나 걸려서 묘한 배신감이 든다. 그리고 UI를 만들다보면 오히려 SafeAreaView를 사용하는 것이 더 귀찮음을 유발할 때가 많다. 특히 맨 처음 컴포넌트의 배경색을 지정할 때 그러하다. 

아무튼, 높이 관련 라이브러리를 하나로 통일해서 깔끔하다. 

```php
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const Demo = () => {
  const insets = useSafeAreaInsets();

  return (
    <View style={ { flex: 1 } }>
      <ScrollView>
        ...
      </ScrollView>
      <View style={ {
        position: 'absolute',
        top: Dimensions.get('window').height - insets.bottom - [컴포넌트 높이]
      } }/>
    </View>
  );
}
```

