---
title: "[React Native] iOS 푸쉬 알림을 위해 Firebase를 적용하면서 만난 에러들"

comments: true
categories:
categories:
  - Blog
tags:
  - React Native, Firebase
last_modified_at: 2023-02-09T
---

앱을 만들다보면 어느 순간 노티 기능을 적용해야할 때가 온다. 차근차근 개발을 진행하다보니 나 또한 어느새 그러한 페이즈에 도달해 있었다.

검색해보니 React Native로 앱을 만들 때 노티 기능은 보통 Firebase를 연동하는 경우가 많은 듯하다. 

설정할 것이 꽤나 많지만 차근차근 진행하면 그렇게 어렵지는 않다. 아무래도 안드로이드보다는 iOS가 좀 더 손이 많이 간다. 

깔끔하게 설명해주는 글이 있어서 먼저 소개한다. 아직 설정 전인 분들은 참고하셔도 좋을 것 같다. 

📍[Android에서 Firebase를 이용한 푸쉬 알림 설정](https://velog.io/@mayinjanuary/React-Native-Firebase-로-푸쉬-알림-구현하기-안드로이드-세팅)  
📍[iOS에서 Firebase를 이용한 푸쉬 알림 설정](https://velog.io/@mayinjanuary/React-Native-Firebase-로-푸쉬-알림-구현하기-2-IOS-앱-세팅하기)

안드로이드는 에뮬레이터에서도 푸쉬 알림 테스트가 가능하기에 설정 난이도가 높지 않고 고맙게도 특별한 에러도 없었다.  

반면, iOS는 시뮬레이터에서는 테스트가 불가능하여 실제 기기에 빌드해서 테스트를 진행할 수밖에 없다. 

문제는 설정은 잘 따라서 한 것 같은데 빌드가 안되는 것이었다...

보통 처음에 만나는 버그는 다음과 같다. 

## 에러 1
```
The Swift pod `FirebaseCoreInternal` depends upon `GoogleUtilities`, which does not define modules.
To opt into those targets generating module maps (which is necessary to import them from Swift when building as static libraries), 
you may set `use_modular_headers!` globally in your Podfile, or specify `:modular_headers => true` for particular dependencies.
```

해결 방법은 **podfile에서 config=use_native_modules 아래에 `pod 'GoogleUtilities', :modular_headers => true`를 추가**해주는 것이다. 

이후에 pod install을 다시 해주면 된다.

여기서 모든 문제가 해결이 되는 사람은 매우 매우 다행인 것이다. 두 번째로 만나는 에러는 아마 다음일 것이다.

## 에러 2
```
Module 'Firebase' not found 혹은 Module 'FirebaseCore' not found
```

구글링을 해보면 여러가지 해결 방법이 나오는데 필자는 1번 해결 방법과 같은 위치에 **`pod 'FirebaseCore', :modular_headers => true`**(FirebaseCore 말고 상황에 맞게 모듈명을 교체)를 추가해 주는 것으로 해결할 수 있었다. (혹시라도 Xcode에서 @import FirebaseCore를 #import "FirebaseCore/FirebaseCore.h"로 바꿔주어 에러를 해결하려 하면 또 다른 에러를 만날 가능성이 매우 높을 것이므로 추천하지는 않는다.)

하지만 여기까지 진행해도 Xcode는 여전히 에러를 내뿜는 경우가 있다. 

## 에러 3
```
Redefinition of module ‘Firebase’ 혹은 Redefinition of module 'FirebaseCore'
```

이걸 해결한답시고 podfile에 2번 해결 방법을 지우고 `use_frameworks! :linkage => :static`를 추가할 수 있는데 이 설정은 flipper와 충돌을 일으키기에 잠재적인 에러의 원인이 될 가능성이 농후하다. 실제로 podfile에서 user_flipper()를 주석 처리해야 하는 경우가 많을 것이라고 예상된다.

필자의 경우에는 flipper를 사용하지 않으니 MQTT가 작동하지 않는 버그를 만났다. ([stackoverflow](https://stackoverflow.com/questions/72289521/swift-pods-cannot-yet-be-integrated-as-static-libraries-firebasecoreinternal-lib))

잘 되는 사람은 그대로 진행해도 되지만 개인적으로는 `use_frameworks! :linkage => :static`보다는 not found 모듈을 일일이 `pod [모듈], :modular_headers => true` 해주는 것을 추천한다.

그래서 Redefinition 에러는 어떻게 해결하느냐고?

에러 메시지만 봐도 알겠지만 이유는 모듈을 여러번 정의하였기 때문이다. 이는 해당 모듈과 관련한 패키지가 여러개 존재할 가능성을 시사한다. 

잘 생각해보면 Firebase 홈페이지에서 처음으로 앱을 등록할 때 `firebase-ios-sdk` 패키지를 Xcode 상에서 등록하라는 가이드를 받는다. 시키는대로 착실하게 진행한 사람은 아마도 위와 같은 에러를 만날 것이다. 
하지만 우리는 2번에서 `FirebaseCore` 라이브러리를 수동으로 다운받았기에 사실상 같은 기능을 하는 필요없는 패키지를 다운받은 것이다. 

웃기게도 firebase-ios-sdk가 모듈을 찾지 못해서 수동으로 다운받았더니 적반하장으로 왜 다시 정의하냐고 에러를 주는 것이다. 어딘가 꼬여있음이 분명하다.

아무튼! 이러한 사실을 깨달았다면 이제 해결은 간단하다. 

**Xcode에서 firebase-ios-sdk를 삭제해주면 된다.** ([stackoverflow](https://stackoverflow.com/questions/70760326/flutter-on-ios-redefinition-of-module-firebase))

이걸로 not found 에러와 redefinition 에러의 무한 반복에서 벗어나셨다면 축하드린다.

필자는 이를 위해 꼬박 하루를 써버렸다. 언제나 가장 어려운 건 환경 세팅이라는 것에는 변함이 없다. 누군가는 시간을 절약하길 간절히 바란다.

혹시나 참고를 원하시는 분이 있을까봐 Podfile 내용도 첨부한다.

```java
require_relative '../node_modules/react-native/scripts/react_native_pods'
require_relative '../node_modules/@react-native-community/cli-platform-ios/native_modules'

platform :ios, '12.4'
install! 'cocoapods', :deterministic_uuids => false

target 'example_app' do
  config = use_native_modules!

  # Flags change depending on the env values.
  flags = get_default_flags()
  
  pod 'FirebaseCore', :modular_headers => true # <- 여기 추가
  pod 'GoogleUtilities', :modular_headers => true # <- 여기 추가

  use_react_native!(
    :path => config[:reactNativePath],
    # to enable hermes on iOS, change `false` to `true` and then install pods
    :hermes_enabled => false,
    :fabric_enabled => flags[:fabric_enabled],
    :flipper_configuration => FlipperConfiguration.enabled,
    # An absolute path to your application root.
    :app_path => "#{Pod::Config.instance.installation_root}/.."
  )

  target 'example_appTests' do
    inherit! :complete
    # Pods for testing
  end

  post_install do |installer|
    react_native_post_install(installer)
    __apply_Xcode_12_5_M1_post_install_workaround(installer)
  end
end
```

스택오버플로우를 보다보면 `$RNFirebaseAsStaticFramework = true;`를 추가하라는 글도 많은데 `use_frameworks! :linkage => :static`를 사용하지 않는다면 굳이 추가해주지 않아도 된다. React Native Firebase [공식 문서](https://rnfirebase.io)에도 잘 나와있으니 한번쯤 확인해보는 것도 좋겠다.




