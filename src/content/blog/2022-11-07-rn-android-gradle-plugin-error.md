---
title: "[React Native] Android Gradle plugin 의존성 에러"

comments: true
categories:
  - Blog
tags:
  - React Native, Android
last_modified_at: 2022-11-07T
---


React Native로 개발을 하고는 있지만 주로 iOS 시뮬레이터만 보고 하다보니 오랜만에 안드로이드 빌드를 하게 되었다. 
<br>
안드로이드 스튜디오에 들어가서 아무 생각 없이 Gradle upgrade를 했더니 빌드가 안되기 시작했다. 
<br>
react-native run-android를 하였을 때 what went wrong에 뜨는 에러는 다음과 같다. 

```r
The Android Gradle plugin supports only kotlin-android-extensions 
Gradle plugin version 1.6.20 and higher. 
The following dependencies do not satisfy the required version: 
project ':react-native-safe-area-context' -> org.jetbrains.kotlin:
kotlin-gradle-plugin:1.6.10
```

아마 Gradle plugin의 버전이 높아서 react-native-safe-area-context의 의존성과 맞지 않는다는 이야기 같다. 
<br>
한참을 고민하다가 Gradle 업데이트를 한 것이 생각나서 급하게 다운그레이드를 해주었다. 
<br>
다운그레이드는 별게 없다. 프로젝트의 android 폴더 안에 있는 build.gradle 파일을 수정해 주기만 하면 된다.

```r
dependencies {
    classpath('com.android.tools.build:gradle:7.2.2')
}
```

gradle:x.x.x 부분에서 숫자만 이전 버전으로 변경해준다. 

### 참고
[[Gradle] Android 빌드를 위한 Gradle Version 관리](https://icat2048.tistory.com/462)
<br>
[[Android|Kotlin] Gradle Sync Issue: Android Gradle plugin supports only Kotlin Gradle plugin version ... and higher](https://daewonyoon.tistory.com/293)