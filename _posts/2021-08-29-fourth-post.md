---
title: "[Pytorch] Tensor element를 mutable하게 복사하기"
excerpt: "머신러닝/딥러닝"
#author_profile: false

categories:
categories:
  - Blog
tags:
  - Blog
last_modified_at: 2021-08-29T
---

<br>
일반적인 경우, 텐서 간의 복사는 복사된 참조 변수의 수정이 기존 참조 변수의 값에 똑같은 영향을 미친다.
예를 들면

```python
import torch
a = torch.tensor([1.,2.,3.])
b = a
print(b) #tensor([1., 2., 3.])
a[0] = 4
print(b) #tensor([4., 2., 3.])
```

하지만

```python
a = torch.tensor([1.,2.,3.])
b = torch.tensor([0.,0.,0.,0.])
for i in range(3):
  b[i] = a[i]
b[3] = a[1]
print(b) #tensor([1., 2., 3., 2.])
a[1] = 3
print(b) #tensor([1., 2., 3., 2.])
```

위와 같이 a와 b의 길이가 다르고 a의 요소들을 b에 배분하는 형식인 경우, 즉 텐서 요소 간의 복사에 있어서는 복사된 참조 변수의 수정이 기존 참조 변수에 영향을 미치지 못한다.
대신 b가 리스트나 numpy배열일 경우에는 b의 각 요소는 아래처럼 mutable하다. 

```python
a = torch.tensor([1.,2.,3.])
b = [0,0,0,0]
for i in range(3):
  b[i] = a[i]
b[3] = a[1]
print(b) #[tensor(1.), tensor(2.), tensor(3.), tensor(2.)]
a[1] = 3
print(b) #[tensor(1.), tensor(3.), tensor(3.), tensor(3.)]
```

다만 리스트나 넘파이를 사용할 경우에는 위의 예와 같이 리스트 안에 텐서가 여러개 들어가 있는 형태(list of tensors)가 되어버리는데 이를 그대로 torch.tensor(b)와 같이 텐서로 바꿔버리면 grad가 끊기면서 loss.backward()시에 
> RuntimeError: element 0 of tensors does not require grad and does not have a grad_fn  

와 같은 에러가 뜨게 된다. 그 때 쓸 수 있는 방법 중 하나가 torch.stack 이다.

```python
c = torch.stack(b) #tensor([1., 2., 3., 2.], grad_fn=<StackBackward>)
```

이걸 쓰면 grad_fn을 유지하면서 list of tensors를 하나의 텐서로 만들어 줄 수 있다. 
주의할 점은 새로운 변수 c에 선언하는게 아닌 b=torch.stack(b)와 같이 b에 덮어씌우게 되면 나중에 파라미터 업데이트 시에 b는 업데이트 되지 않는다. 이번 경우는 a와 b가 동시에 업데이트 되기를 원하므로 위와 같이 c에 새로운 텐서를 만들어주었다.   

전체 코드는 

```python
import torch
import torch.optim
device = torch.device("cuda")

a = torch.tensor([1.,2.,3.], requires_grad=True)
b = [0,0,0,0]
for i in range(3):
  b[i] = a[i]
b[3] = a[1]

def my_loss(embedding): #contrastive loss
    loss = -((embedding.exp()[:1].sum() / embedding.exp().sum()).log())
    return loss
optimizer = torch.optim.SGD([a], lr=0.001)

c = torch.stack(b)

loss = 0.0
loss = my_loss(c)
optimizer.zero_grad()
loss.backward()
optimizer.step()

print(b) #[tensor(1.0009, grad_fn=<AsStridedBackward>), tensor(1.9996, ...]
print(a) #tensor([1.0009, 1.9996, 2.9995], requires_grad=True)
```
a와 b가 성공적으로 동시 업데이트 된다.
물론 단순히 1차원 텐서가 아니라 그 이상의 텐서에 대해서도 적용 가능하다. 
