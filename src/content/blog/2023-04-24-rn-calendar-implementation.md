---
title: "[React Native] 리액트 네이티브에서 달력 구현하기"

comments: true
categories:
  - Blog
tags:
  - React Native, react-native-calendars
last_modified_at: 2023-04-24T
---

## 라이브러리
---
리액트 네이티브로 앱을 만들 때는 달력을 구현해야할 일이 생각보다 자주 생긴다. 어떤 앱이든 시간의 흐름에 따라 과거 정보를 조회하는 경우가 많기 때문인데, 그렇기에 직접 구현해두면 두고두고 쓸 일이 많을 것이다. 물론 훌륭한 라이브러리가 많기 때문에 시간이 충분하지 않은 사람은 다른 사람의 힘을 빌리는 것도 때론 중요하다. 필자 또한 다른 사람이 짜놓은 코드를 빌려다가 내부만 조금 고쳐쓰는 경우가 많다.  
그런 의미에서 오늘은 유명한 라이브러리 중 하나인 [`react-native-calendars`](https://github.com/wix/react-native-calendars)를 소개한다.


## 설치
---
npm을 통해 설치해준다.
```bash
npm i react-native-calendars
```
기본적인 사용법은 매우 간단하고 홈페이지에 자세한 설명이 나와있으니 참고하면 된다. 

## 기능 구현
---
문제가 있다면 날짜를 클릭하였을 때 onPress 이벤트 설정을 직접해주어야 한다는 것이었고 기본 모듈에서는 달력 위의 숫자들을 눌러도 아무런 일도 일어나지 않는다. Agenda 기능도 지원하고 있으나 원하는 형태가 아니어서 어쩔 수 없이 구글링을 통해 직접 구현하였다. ([참고](https://devbksheen.tistory.com/entry/React-Native-%EB%8B%AC%EB%A0%A5-%EA%B8%B0%EB%8A%A5-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0)) 예시 코드는 다음과 같다.
```javascript
import React, {useState} from 'react';
import {View, Text} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {CalendarList} from 'react-native-calendars';

const CalendarView = () => {
  const posts = [
    {
      id: 1,
      title: '제목입니다.',
      contents: '내용입니다.',
      date: '2022-10-08',
    },
    {
      id: 2,
      title: '제목입니다.',
      contents: '내용입니다.',
      date: '2022-10-09',
    },
  ];

// 클릭한 날짜를 담는 변수
  const [date, setDate] = useState();
  const [selectedDate, setSelectedDate] = useState();

// posts 안에 들어있는 모든 일정을 달력에 표시하기 위한 변수
  const markedDates = posts.reduce((acc, current) => {
    acc[current.date] = {marked: true};
    return acc;
  }, {});

// 날짜가 선택되었을 때 해당 날짜에 배경색을 입히기 위한 변수
  const markedSelectedDates = {
    ...markedDates,
    [selectedDate]: {
      selected: true,
      marked: markedDates[selectedDate]?.marked,
    },
  };

  return (
    <SafeAreaView style={ {height: '100%'}}>
      <CalendarList
        horizontal={true}
        pagingEnabled={true}
        markedDates={markedSelectedDates}
        onDayPress={day => {
          setDate(day);
          setSelectedDate(day.dateString);
        }}
        theme={ {
          selectedDayBackgroundColor: '#959CA7',
          monthTextColor: '#959CA7',
          textDayFontWeight: '500',
          textMonthFontWeight: '600',
          textDayHeaderFontWeight: '300',
          textMonthFontSize: 18,
        }}
      />
      {date && (
        <View style={ {marginLeft: 16, marginTop: 10}}>
          <Text style={ {fontSize: 11, color: '#959CA7', textAlign: 'right'}}>
            Test: 현재 선택하신 날짜는 {date.day}일 입니다.
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
};

export default CalendarView;
```

## 버그
---

커스터마이징을 적용할 때는 공식 문서 말고도 내부 코드를 뜯어보는 것을 추천한다.

#### 🔒 에러 1

WeekCalendar에서 헤더를 한국어로 바꾸면 컨테이너와 영역이 겹치는 일이 발생한다. [공식 문서](https://wix.github.io/react-native-calendars/docs/Components/Calendar)에서는 스타일 수정 방법에 대해 아래와 같이 설명하고 있다.

```javascript
theme={ {
  arrowColor: 'white',
  'stylesheet.calendar.header': {
    week: {
      marginTop: 5,
      flexDirection: 'row',
      justifyContent: 'space-between'
    }
  }
} }
```
하지만 이는 WeekCalaendar에서는 적용이 되지 않는다. 해당 기능이 위치한 style.js 소스코드를 살펴보니 아래와 같이 export 방식이 달랐다.
```javascript
...(theme?.stylesheet?.expandable?.main || {})
```

#### 🔑 해결
node_modules 폴더 안을 고치는 것은 관리 이슈가 커지기 때문에 아래와 같이 내 코드에서 직접 설정해주는 방식을 택하였다. 
```javascript
<CalendarProvider
  date={date}
  onDateChanged={d => setDate(d)}
  style={ {flex: 0} }>
  <WeekCalendar
    displayLoadingIndicator
    allowShadow={false}
    theme={ {
      textDayFontSize: 16,
      textDayHeaderFontSize: 14,
      stylesheet: {expandable: {main: {container: {marginTop: 5}}}}, // <- 여기
    } }
  />
</CalendarProvider>
```

theme 안에서 `stylesheet: {expandable: {main: {container: {marginTop: 5}}}}`와 같이 설정해주면 된다.

#### 🔒 에러 2

WeekCalendar을 사용할 때 로딩이 너무 오래 걸리는 이슈가 존재한다. 📌 [깃허브 이슈](https://github.com/wix/react-native-calendars/issues/2214)  

#### 🔑 해결
 이는 RecyclerListView에서 너무 많은 페이지가 미리 렌더링되고 있기 때문이다. RecyclerListView에 대한 정보는 [다음](https://github.com/Flipkart/recyclerlistview)을 확인하자. 해당 페이지에서는 renderAheadOffset의 값을 가능한 낮게 설정하는 것을 권하고 있다. 높게 설정할수록 계산 비용이 많아지므로 로딩이 오래 걸리게 된다.  
따라서 `node_modules/react-native-calendars/src/infinite-list/index.js`로 이동하여 RecyclerListView의 prop을 아래와 같이 바꾸어주면 된다. 
```javascript
<RecyclerListView 
ref={listRef} 
isHorizontal={isHorizontal} 
... 
renderAheadOffset={0 * pageWidth}   // <- 숫자를 0으로 수정한다.
.../>
```

누군가에게는 도움이 되었길 바란다.