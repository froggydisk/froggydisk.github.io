---
title: "[React Native] 서버에서 이미지를 fetch 해올 때 화면에 제대로 나타나지 않는 현상"

comments: true
categories:
  - Blog
tags:
  - React Native, Multer
last_modified_at: 2022-11-09T
---

글을 쓰면서도 조금은 부끄럽지만 가끔은 정말 간단한 걸로 몇 시간을 헤매고는 한다. 
<br>
React Native에서 Multer를 이용하여 서버에서 이미지를 불러오는데 다운 받아온 이미지가 화면에 표시되지 않는 현상이 있었다. 
<br>
공식 문서를 그대로 따라서 fetch 함수를 사용하였고 uri도 로그에 제대로 찍혀 있는데도 계속 문제가 남아있어 머리를 꽁꽁 싸맸다.
<br>
나중에 보니 해결 방법은 매우 간단했다. 
<br>
잊고 있었던 것이다. 샘플 이미지는 전부 local의 asset 폴더에 저장하여 사용하고 있었기에 그동안 신경쓰지 않고 있었지만 사실 `이미지는 width와 height를 지정해주는 것이 좋다`는 것을.
<br>
그렇다. fetch 문제인 줄 알고 axios로 바꿔도 보고 하였지만 결국 설정 문제였던 것이다. 
resizeMode 옵션을 너무 신뢰하고 있었는지 이를 눈치채는데 오랜 시간이 걸렸다. 
한 번도 아니고 두 번이나 똑같은 문제로 헤맨 전적이 있다. 
<br>
누군가는 시간을 아끼기 바란다. 

```r
<Image
    source={ {uri: URI} }
    style={ {height: 100, width: 100} }
/>
```

### 참고
[React Native Doc. - Image](https://reactnative.dev/docs/image)
