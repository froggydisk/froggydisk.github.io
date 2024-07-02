---
title: "[RN/AI] Pytorch로 AI 모델을 학습시켜 모바일 앱에 적용하기"
comments: true
categories:
  - Blog
tags:
  - Pytorch, React Native, labelImg
last_modified_at: 2024-06-30T
---

## [현재 작성중인 글입니다.]

앱을 만들다보면 자연스레 AI 기술에 관심을 가지게 된다.

"요즘 chatGPT가 그렇게 핫하다는데 나도 AI 좀 접목시켜 볼까...?" 라는 상상을 하게 된다

그렇다면 어떻게 해야할까? 하나하나 차근차근 파헤쳐보자.

## 🍀 프로세스

전체적인 흐름은 다음과 같다.

![이미지](/assets/img/ai-on-app-process.png)

### 1. 데이터 라벨링

AI 모델을 훈련시키기 위해서는 그에 적합한 데이터가 필요하다.

오픈소스 데이터를 활용하는 것이 가장 좋지만, 원하는 데이터가 없다면 직접 만들 수밖에 없다.

여기서는 `labelImg`라는 라벨러를 사용하여 데이터를 직접 만들어볼 것이다.

(이 과정이 정 귀찮다면 파인튜닝된 모델을 깃허브, 허깅페이스 같은 곳에서 받아와서 사용해도 좋다.)

### 2. 데이터 전처리

모델을 학습시키는 데이터의 형식에는 여러가지가 있지만 우리가 만들 모델은 csv를 필요로 하기에 xml 형태의 데이터를 csv로 변환할 것이다.

실전에서는 원하는 모델의 형식에 맞게 데이터셋을 변형해보자.

### 3. 모델 훈련

만들어 놓은 데이터셋으로 모델을 학습시켜본다.

GPU가 있으면 더 빠르고 좋지만, CPU로도 나름 괜찮은 모델을 학습할 수 있다.

우리는 도커를 통해 딥러닝용 가상환경 위에서 학습을 진행할 것이다.

### 4. 모델 테스트

의도한대로 잘 학습이 진행되었는지, 정확도는 얼마인지, 실제로 잘 작동하는지 확인한다.

더불어 라이브 테스트도 진행해보자.

### 5. 모델 변형

우리가 훈련시킨 모델을 모바일 앱에서 사용하기 위해서는 특정 형식이 필요하다.

모델 파일 형식이 `.pth`로 되어있을텐데, 이를 `.ptl`파일로 변경해주어야 한다.

이 과정에서 `torch.jit`을 통한 모델 튜닝에 관한 이야기를 할 것이다.

### 6. 모델 적용

해당 모델을 `Snack`에서 확인해보고, 실제로 `React Native` 프로젝트에도 적용해보자.

결과물을 보고 모델 최적화에 대해서도 고민해보자.

<br/>

---

## 🏷️ 데이터 라벨링 (Data Labeling)

모델 학습에 필요한 데이터를 만들기 위해서는 원본(raw) 데이터와 라벨링 툴이 필요하다.
(\*Object Detection에 필요한 데이터는 원본 이미지와 바운딩 박스에 관한 좌표 정보이다.)

먼저 원본 데이터부터 준비하자.

원본 데이터는 [Stanford Dogs Dataset](http://vision.stanford.edu/aditya86/ImageNetDogs/)을 사용할 것이다. 120종의 강아지 사진 총 20,580장이 모여있는 데이터셋이다.

모든 이미지를 사용할 필요는 없고, 원하는만큼 이미지를 특정 폴더로 옮겨준다. (모델 성능이 잘 안나올 경우 나중에 더 많은 데이터를 가져오면 되므로 일단은 조금만 옮겨보자. 물론 층화 샘플링(Stratified Sampling)을 해주면 가장 좋다.)

해당 폴더는 이제 새로운 데이터셋 폴더로 사용될 것이다.

기본 데이터가 준비되었다면 이제 [labelImg](https://github.com/HumanSignal/labelImg)라는 툴을 소개하고자 한다. 간단히 설명하자면 다음과 같다.

> Object Detection 모델 학습에 필요한 주석(Annotation) 처리된 이미지를 생성할 수 있게 도와주는 도구이다.

깃허브 페이지에 들어가보면 설치 및 사용 방법에 대해 상세히 설명하고 있다.

단, 필자는 `M3 MacBook Air 13`를 사용하고 있는데 설치 가이드에 부족한 내용이 있어 관련 내용을 추가한다.

**⚠️ pyrcc5: No such file or directory** 혹 이러한 에러를 만난다면 아래 코드대로 설치한다.

```bash
brew install qt qt@5
brew install libxml2
brew install pyqt@5
pip3 install pyqt5 lxml
git clone https://github.com/HumanSignal/labelImg.git
cd labelImg
make qt5py3
python3 labelImg.py
```

실행 화면은 아래와 같다.

![labelImg](/assets/img/labelImg.png)

`labelImg/data` 폴더 안에 `predefined_classes.txt`라는 파일이 있는데 이 안에는 분류하고 싶은 클래스명을 적어주면 된다.

조작 순서는 `이미지 불러오기 -> 바운딩 박스 생성 -> 저장하기` 순이다. 사용법이 직관적이므로 매우 쉽다.

단축키는 주로 이렇게 세 가지를 사용하면 된다.

| 키  |    설명     |
| :-: | :---------: |
|  w  |  박스 생성  |
|  d  | 다음 이미지 |
|  a  | 이전 이미지 |

사진 위에 바운딩 박스를 만들고 저장을 누르면 해당 정보가 xml 파일로 저장되는 것을 볼 수 있는데, 우선 한 폴더에 이미지 파일과 메타데이터 파일(xml)을 모아놓자.

## 🔖 데이터 전처리

우리가 사용할 모델은 `Object Detection`에서 유명한 SSD이다. SSD 모델 구현에 있어서는 [여기](https://github.com/qfgaohao/pytorch-ssd)를 참고하였다.

해당 모델을 사용하기 위해서는 위에서 라벨링한 데이터를 모델에 맞게 변형할 필요가 있다.

필수적인 두 가지는 이미지 폴더와 그와 관련한 바운딩 박스 정보를 담고 있는 csv 파일이다.

위에서 만든 데이터셋 폴더에 `xml_to_csv.py`(url 첨부) 파일을 넣고 실행시켜준다.

```bash
python3 xml_to_csv.py
```

다음과 같은 결과가 나온다.

```bash
🗂️ label
sub-test-annotations-bbox.csv
sub-train-annotations-bbox.csv
sub-validation-annotations-bbox.csv
🗂️ test
🗂️ train
🗂️ validation
```

## 모델 훈련

우리가 만든 데이터셋의 이름을 `dognose_dataset`이라고 하자.

먼저 pytorch-ssd를 받아오자.

```bash
git clone https://github.com/qfgaohao/pytorch-ssd.git
cd pytorch-ssd
```

해당 모델이 우리의 데이터를 사용할 수 있도록 `data` 폴더를 만들어서 그 안에 `dognose_dataset`을 넣어준다.

환경 구성: 도커 [deepo](https://github.com/ufoym/deepo)

현재 위치가 컨테이너 안에 마운트되도록 설정한다.

```bash
docker pull ufoym/deepo:cpu
docker run -it --shm-size 8G -v "$(pwd)":/mount ufoym/deepo:cpu bash
nvidia-docker run -it --gpus all --shm-size 8G -v "$(pwd)":/mount ufoym/deepo bash
pip install opencv-python
apt-get update
apt-get install libgl1-mesa-glx
```

```bash
python train_ssd.py --dataset_type open_images --datasets /mount/data/DND --net mb2-ssd-lite --pretrained_ssd models/mb2-ssd-lite-mp-0_686.pth --scheduler cosine --lr 0.01 --t_max 100 --validation_epochs 10 --num_epochs 100 --base_net_lr 0.001 --batch_size 8 --debug_steps 10

AttributeError: 'NoneType' object has no attribute 'shape'
# image_file = self.root / self.dataset_type / f"{image_id}.jpg"
image_file = self.root / self.dataset_type / f"{image_id}"
raise ValueError("Expected more than 1 value per channel when training, got input size {}".format(size))
drop=true
```

M3 MacBook Air 기준, cpu로 학습시 1 epoch 당 대략 3분 정도 소요되었다.

10 epoch마다 모델의 check point를 저장해주므로 적당한 loss가 나왔을 때 중지시켜도 된다.
