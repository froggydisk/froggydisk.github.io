---
title: "[React Native] 안드로이드 다크모드에서 텍스트 색이 모두 흰색으로 나오는 이슈"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2023-07-23T
---


개발을 하다보면 다크모드를 고려하지 않고 개발을 하게 되는 경우가 있다.   
React Native에서는 **텍스트의 기본 색상이 #000, 폰트크기는 14, fontWeight은 400**이므로 <Text>태그에서 아무런 style 적용을 해주지 않더라도 기본 설정이 적용이 된다. 
그렇기에 기본 설정을 사용하는 경우에는 아무런 신경을 써주지 않아도 된다.   

**단, 문제는 안드로이드의 다크모드는 예외라는 것이다.**

이슈가 처음 보고되었을 때 적잖이 당황했던 적이 있다. 안드로이드 스튜디오에서도 따로 설정을 해주지 않는 이상 다크모드가 적용되어 있는 경우가 적으므로 따로 테스트해 볼 생각을 전혀 못했던 것이다. 

다행히 구글링 해보니 같은 이슈를 겪는 사람들이 있어서 해결 방법을 정리해보았다.     
먼저 수정할 파일은 **[프로젝트폴더]/android/app/src/main/res/values/styles.xml**이다.

```java
<style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
    <!-- Customize your theme here. -->
    <item name="android:editTextBackground">@drawable/rn_edit_text_material</item>
    <item name="android:textColor">#000</item> // Text 태그의 폰트 색상
    <item name="android:textColorHint">#999</item> // TextInput 태그의 힌트 폰트 색상
    <item name="android:editTextColor">#000</item> // TextInput 태그의 폰트 색상
</style>
```
이렇게 하면 폰트 문제가 깔끔하게 해결된다. 

하지만 추가 테스트를 하다보니 이번에는 **Alert.alert**의 모달 배경에 회색 필터가 씌워지는 현상이 일어난다. ([참고](https://github.com/facebook/react-native/issues/31345))   
해결을 위해 수정할 파일은 **[프로젝트폴더]/android/app/src/main/java/com/[앱이름]/MainApplication.java**이다.

```java
import androidx.appcompat.app.AppCompatDelegate; // 추가

@Override
public void onCreate() {
super.onCreate();
SoLoader.init(this, /* native exopackage */ false);
ReactNativeFlipper.initializeFlipper(this, getReactNativeHost().getReactInstanceManager());
AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO); // 추가
}
```
위 코드는 안드로이드에서 앱의 다크모드를 강제로 막아준다. 

애초부터 다크모드를 막아줄 것이면 위의 폰트 색상은 왜 적용해주었는가 싶지만 처음 설정은 전역 폰트의 색상 설정이 가능한만큼 검정색이 아닌 다른 색으로의 설정도 가능하다는 점에서 의의가 있다.  
보통 디자인에 따라 다르지만 순수 블랙을 사용하지 않고 **#333**등의 색상 코드를 사용하는 경우가 있기에 어찌되었든 알아두면 유용한 설정이다. 