---
title: "[React Native] 컴포넌트 속성을 통해 전달하는 문자열의 줄바꿈 방법"

comments: true
categories:
  - Blog
tags:
  - React Native, React, Next
last_modified_at: 2024-02-21T
---

특정 컴포넌트를 구현할 때 속성을 통해 문자열을 보내줄 때가 있다. 보통 config로 따로 저장해놓은 고정 문구를 넣어주는 경우에 많이 쓰인다. 

이 경우에 디자인 상의 이유로 줄바꿈을 자주 사용하게 되는데, 따옴표 안에 개행문자`\n`를 넣어도 아무 일도 일어나지 않아 종종 당황하곤 한다. 이는 개행 문자가 그대로 문자열로 인식되기 때문이다. 

줄바꿈이 제대로 이루어지게 하기 위해서는 **중괄호**를 사용해 주어야 한다. 이런식으로 말이다.

```java
<OnBoardingPage
  subtitle={
    '집에서 얼마나 걷고, 뛰고, 쉬었는지 등의\n정보를 실시간으로 분석해드려요.'
  }
/>
```

> chatGPT는 그 이유에 대해 이렇게 말한다.  
> **"중괄호를 사용하면 JavaScript 표현식을 평가하고 결과를 문자열로 변환하여 JSX에 삽입할 수 있습니다."**

비슷한 느낌으로 `React`나 `Next`에서는 아예 컴포넌트 형식으로 전달하는 것을 추천한다. 

```java
<CheckUpCard
  content={
    <>
      질환 등의 감별을 위한
      <br />
      정밀검사
    </>
  }
/>
```

컴포넌트 형식으로 전달하는 방식은 **반응형으로 페이지를 구현할 필요가 있을 때** 사용하면 유용하다. 이 때 개행문자`\n` 대신 `<br>`태그를 사용하게 되는데 이렇게 되면 PC 버전이냐 모바일 버전이냐에 따라 줄바꿈을 다르게 적용할 수 있기 때문이다.

빈 태그가 아닌 <div>태그 등을 사용하면 스타일도 부여할 수 있으니 자유도가 한층 높아지는 것은 말할 것도 없다.