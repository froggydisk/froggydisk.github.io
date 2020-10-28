---
title: "[HTML/CSS] 모바일에서 hover 효과 없애기"
excerpt: "반응형 웹페이지 만들기"
#author_profile: false

categories:
categories:
  - Blog
tags:
  - Blog
last_modified_at: 2020-08-28T
---

<br>
아이폰이나 아이패드와 같은 기기에서는 PC와는 다르게 hover 효과가 적용되지 않는다.  
그 이유는 마우스가 아닌 터치 방식을 사용하기 때문이다.  
그러다보니 모바일에서 드랍다운 메뉴 같은 경우, 한 번 누르면 계속 호버된 상태가 되어 효과가 사라지지 않는 경우가 있다.  
이 때 화면의 다른 부분을 누르면 호버효과가 사라지게 만들고 싶을 때 쓸만한 방법이 있다.
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <title>모바일에서 hover 효과 없애기</title>
    <link href="style.css" rel="stylesheet" type="text/css" />
    <style>
@media ( max-width: 768px ){
        button {
          -webkit-tap-highlight-color:transparent;
        }
      }
    </style>
  </head>
  <body ontouchstart="">

  </body>
```
호버 효과를 적용하는 class의 style 안에 **-webkit-tap-highlight-color:transparent;**를 넣어주고(터치 시 탭효과 제거)  
body에 **ontouchstart=""**를 적용하면 끝
