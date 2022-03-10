---
title: "모바일에서 영역 터치 시 발생하는 하이라이트 제거"

comments: true
categories:
categories:
  - Blog
tags:
  - CSS
last_modified_at: 2022-03-02T
---

```python
a {
    color: $text-base-color;
    -webkit-tap-highlight-color: rgba(0,0,0,0); # or transparent;

    &:hover,
    &focus {
      color: $black;
    }
  }
```
모바일 작업을 하다보면 영역 클릭 시 원하지 않는 검은색 하이라이트가 나타나는 경우가 있다. 
이럴 때는 위와 같이 css에 `-webkit-tap-highlight-color:` `rgba(0,0,0,0);` 혹은 `transparent;` 를 적용하면 나타나지 않는다. `:focus` 안에 넣으면 안되므로 주의!

만약 영역 클릭 시 테두리가 생긴다면 아래처럼 `outline: none;`으로 해결가능하다. 
```python
a {
    &:focus {
      outline: none;
    }
}
```
