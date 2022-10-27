---
title: "Buy me a coffee 버튼 만들기 ☕️"

comments: true
categories:
categories:
  - Blog
tags:
  - HTML/CSS
last_modified_at: 2022-03-03T
---

여러 블로그를 돌아다니다보니 포스트 아래쪽에 달려있는 예쁜 버튼들에 눈길이 갔다. `Buy me a coffee`로도 유명한 후원 버튼이었는데 애드 포스트가 덕지덕지 붙어있는 것보다 훨씬 깔끔해 보여서 한 번 만들어보기로 하였다. 후원보다는 디자인적인 욕심이 큰 것 같다. 

# 순서 
1. 우선 마음에 드는 버튼 디자인을 찾거나 직접 디자인한다. 나의 경우에는 여러 레퍼런스를 찾아보았는데 [waster.log](https://velog.io/@whdnjsdyd111/CSS-버튼-이쁘게-꾸미기)에서 많은 도움을 받았다. 
2. 다음으로는 버튼에 단순히 `onclick="location.href=`를 붙여주면 끝이난다.  

하나는 카카오, 다른 하나는 `buy me a coffee`로 해서 총 두 개의 버튼을 만들었다. 카카오는 모바일에서만 가능하고 카카오계정이 드러나다보니 조금 노골적인 느낌이 들었다. `buy me a coffee`는 후원페이지도 직접 꾸밀 수 있고 깔끔한 UI가 마음에 들었는데 후원 절차가 비교적 까다롭고 한화 결제가 불가능하다는 것이 마음에 걸렸다. 또한 일정 금액 이상이 아니면 인출도 불가능하다.  

코드는 아래와 같다. 
```python
<!DOCTYPE html>
<html>
  <head>
    <script src="[fontawesome사이트에서 발급되는 url]" crossorigin="anonymous"></script>
  </head>
  <body>
    <div class="support-link-btn">
      <button class="w-btn w-btn-yellow" onclick="location.href='[카카오페이 송금 url]'">
        <span>Give me a kakao</span>
        <i class="fa-solid fa-heart fa-beat" style="--fa-animation-duration: 1s;"></i>
      </button>
      <button class="w-btn w-btn-gra1 w-btn-gra-anim" onclick="location.href='[buy me a coffee 후원페이지 url]'">
        <span>Buy me a coffee</span>
        <i class="fa-solid fa-mug-hot"></i>
      </button>
    </div>
  </body>
</html>


<style type="text/css">
@import url("https://fonts.googleapis.com/css?family=Poppins:200,300,400,500,600,700,800,900&display=swap");

# 버튼 위치 조정
.support-link-btn {
      text-align: center;
      margin-top: 3em;
  }

# 버튼 디자인 설정
.w-btn {
    font-size: 0.8em;
    position: relative;
    border: none;
    display: inline-block;
    padding: 15px 30px;
    border-radius: 15px;
    font-family: "paybooc-Light", sans-serif;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    text-decoration: none;
    font-weight: 600;
    transition: 0.25s;
}

.w-btn:hover {
    transform: scale(1.1);
    cursor: pointer;
}

.w-btn:active {
    transform: scale(1.1);
}

# hover 시 물결 효과
@keyframes ring {
    0% {
        width: 30px;
        height: 30px;
    }
    100% {
        width: 300px;
        height: 300px;
        border-color: transparent;
    }
}

.w-btn:hover::after {
    content: "";
    border-radius: 100%;
    border: 6px solid #9dc8c8;
    position: absolute;
    z-index: -1;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: ring 1.5s infinite;
}

# 카카오 버튼
.w-btn-yellow {
  background-color: #fce205;
  color: #3B240B;
}

# buy me a coffee 버튼
.w-btn-gra1 {
    background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
    color: white;
}

.w-btn-gra-anim {
    background-size: 400% 400%;
    animation: gradient 7s ease infinite;
}

@keyframes gradient {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}
</style>
```

버튼 안에 들어갈 아이콘을 찾을 때는 [fontawesome](https://fontawesome.com)을 추천한다. 완성본은 footer쪽을 보세요! ⬇️
