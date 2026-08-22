---
title: "[React Native] TextInput으로 받은 String을 Number 타입으로 바꿔주기"

comments: true
categories:
  - Blog
tags:
  - React Native
last_modified_at: 2023-07-20T
---

TextInput 안에서 받은 `String` 타입 숫자값를 알아서 `Number` 타입으로 변경되게 하고 싶었는데 이렇게 해주니 에러가 났다.

```java
<TextInput
    value={data.year}
    onChangeText={text => setData({...data, year: Number(text)})}
/>
```

### 에러 ⚠️
**Warning: Failed prop type: Invalid prop value of type number supplied to ForwardRef(TextInput), expected string.**   
입력값이 `Number`로 바껴서 저장이 되므로 value값에 들어가는 데이터가 `Number` 타입이 되는데 value값은 `String` 값이어야 하기 때문에 에러가 발생한다. 

이를 해결하기 위해 아래를 시도해본다.
```java
<TextInput
    value={data.year.toString()}
    onChangeText={text => setData({...data, year: Number(text)})}
/>
```
간단하고 좋다. 
하지만 키보드를 `numeric`으로 해주지 않으면 키보드 입력에서 `String` 값을 잘못 넣는 순간 바로 `NaN`이 떠서 지워지지 않는 현상이 일어난다.  
잘 되기는 하지만 무언가 찝찝하기는 하다.  
좀 더 고민을 해보면, 입력을 끝낼 때 `Number`로 타입변환을 해주는 방법도 있다. 

```javascript
<TextInput
    value={data.year.toString()}    
    onChangeText={text => setData({...data, year: text})}
    onEndEditing={() =>
      setData({...data, year: Number(data.year)})
    }    
    ...
/>
```

이 방법에서는 `String` 값을 입력하더라도 `NaN`이 나타나지 않는다. 하지만 `Number`로 형변환을 해야하는 경우는 보통 타입이 강제되는 경우가 많기 때문에 (API request 등) NaN이 안 나타난다고 해서 안심할 만한 상황은 아니다. 오히려 키보드를 `numeric`으로 하고 이중으로 타입 검사를 해주는 편이 안전하다. 

이러한 경우는 엣지 케이스가 많기 때문에 항상 이것저것 테스트 시나리오를 고려해야한다. 
예를 들면 `numeric` 키보드에서 숫자만 받는다고 타입 검사를 안하다가 복사 붙여넣기를 하는 유저를 만나 오류를 직면할 수도 있는 것이다. 

이렇게 정형화되어 있는 패턴에서는 TDD가 필요한 이유를 절실히 느낀다. 
