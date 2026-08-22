---
title: "[React Native] 안드로이드 스튜디오 Add configuration에서 No module만 선택 가능한 현상"

comments: true
categories:
  - Blog
tags:
  - React Native, Android Studio
last_modified_at: 2023-07-03T
---

### 🔒 에러

React Native로 앱을 만들다보면 iOS 시뮬레이터가 너무 편해서 안드로이드를 소홀히 하게 되는 때가 있다.  
안드로이드 apk 파일을 건네줄 필요가 있어서 오랜만에 안드로이드 스튜디오를 켰는데 이상하게 Run 아이콘이 있어야 할 자리에 `add configuration` 밖에 보이지 않았다.
인터넷을 찾아보니 module을 추가해주면 된다는데 아무리 모듈을 추가하려고 해도 선택지에 `No module` 이외에 아무것도 뜨지 않는다. 

### 🔑 해결

그렇다. 사람은 가끔 바보가 된다. VScode 켜듯이 아무 생각 없이 React Native 프로젝트 폴더를 열어버렸던 것이다.  
**안드로이드 스튜디오에서는 프로젝터 폴더 안의 android 폴더를 열어주어야한다.**  
마치 Xcode에서 ios 폴더를 열어주는 것과 같다. 