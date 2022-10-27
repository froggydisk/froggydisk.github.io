---
title: "Top1 Accuracy와 Top5 Accuracy 이해하기"
excerpt: "논문에 자주 등장하는 Top1, Top5의 의미는?"

comments: true
categories:
categories:
  - Blog
tags:
  - Image Recognition
last_modified_at: 2020-06-12T
---

<br>
딥러닝 관련 논문을 읽다보면 `Top1`, `Top5`, `Top10`과 같은 말들을 자주 볼 수 있습니다.  
대충 감이 오기는 하지만 정확히 무엇을 의미하는 것일까요?  
대표적으로 Top1 뒤에는 Accuracy가 오는 경우와 Loss가 오는 경우 이렇게 두 가지가 있습니다.  
Top1 Accuracy는 분류기가 가장 가까운 클래스를 예측했을 때 정답이었던 경우의 전체 예측수에 대한 비율을 의미합니다.  
반대로 Top1 Loss의 경우에는 가장 가까운 클래스를 예측했을 때 정답이 아니었던 경우의 전체 예측수에 대한 비율을 의미합니다.  
예를 들어 강아지, 고양이, 미어캣, 개구리, 너구리를 구분하는 분류기가 있다고 합시다.  
위의 다섯 동물 중 어느 한 동물의 이미지를 분류기에 집어넣었더니 분류기의 마지막 층으로부터 Softmax 함수를 지나서 나온 결과가 (0.1, 0.15, 0.3, 0.4, 0.05) 였다고 합시다.   
벡터의 각 요소가 (강아지, 고양이, 미어캣, 개구리, 너구리) 순으로 각각의 클래스로 분류될 확률이라고 한다면 이미지가 분류될 클래스 중에 가장 확률이 높은 것은 0.4의 확률을 가진 `개구리`가 됩니다. 같은 방법으로 두번째로 확률이 높은 클래스는 미어캣이 되겠네요.  
이미지가 분류될 확률이 높은 순으로 클래스를 나열하면 개구리 → 미어캣 → 고양이 → 강아지 → 너구리 순이 됩니다.  
만약에 이미지의 정답 라벨이 개구리였다고 했을 때 Top1 Accuracy는 1이 되고 Top1 Loss는 0이 되겠네요.  
이런식으로 열 장의 이미지를 넣어서 가장 확률이 높은 클래스로 예측을 했을 때 정답인 경우가 6번 있었다면 Top1 Accuracy는 0.6이 됩니다.  
예상하셨겠지만 Top5 Accuracy는 가장 가까운 클래스를 다섯 개 뽑았을 때 그 안에 정답이 존재한 경우의 비율을 의미합니다.   
참고로 위의 예에서는 분류기가 5개의 클래스 밖에 구분하지 못하므로 여기서는 Top5 Accuracy는 의미가 없다고 할 수 있습니다.  
입력 이미지가 다섯 종류의 동물 중 하나라고 했을 때, 분류될 수 있는 클래스가 다섯개 뿐이므로 무조건 정답이 Top5 안에는 들어있게 되기 때문이죠.  
혹여나 입력 이미지가 위의 다섯 종류에 국한되어 있지 않는다면 Top5 Accuracy가 의미를 가지겠지요.  
보통 Top1 Accuracy + Top1 Loss = 1 이 되므로 Accuracy든 Loss든 결국에는 같은 이야기를 하고 있다고 생각하시면 됩니다. 