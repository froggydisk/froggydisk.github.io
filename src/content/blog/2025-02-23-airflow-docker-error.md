---
title: "Airflow docker compose 시 gcc permission denied 에러"
comments: true
categories:
  - Blog
tags:
  - DevOps, Docker
last_modified_at: 2025-02-23T
---

## ⚠️ 에러

`docker compose`로 Airflow를 로컬 테스트하던 중에 `gcc permission denied` 에러가 발생했다.

에러가 난 부분을 살펴보니 Dockerfile에서 `RUN pip install -r requirement.txt`을 실행할 때 발생하고 있었다.

기존 Airflow 2.9.0 환경에서는 잘 진행되던 것이 2.10.5로 올리면서 갑자기 안되는 경우였으므로 패키지 호환성 문제인가 싶어서 먼저 requirement.txt에서 문제를 일으키는 라이브러리를 찾았다.

trino 관련 패키지가 빌드 시에 전부 gcc 에러를 내뿜고 있었다.

Airflow는 보통 constraint로 패키지들 간 버전이 묶이기 때문에 trino만 다른 버전으로 변경하는 것은 불가능했다.

사실 잘 생각해보면 gcc 에러는 Airflow의 도커 이미지가 권한이 없어서이지 패키지의 문제는 아닐 것이다.

## 🔑 해결

Airflow 공식 문서를 좀 찾아보니 [도커 빌드에 관한 문서](https://airflow.apache.org/docs/docker-stack/build.html#example-when-you-add-packages-requiring-compilation)가 있다.

**단순히 Airflow의 베이스 이미지에 build-essential이 포함되어 있지 않아서 발생하는 문제였다.**

> The compilation framework of Linux (so called build-essential) is pretty big, and for the production images, size is really important factor to optimize for, so our Production Image does not contain build-essential

해석해보면 build-essential이 무거워서 최적화를 위해 포함하지 않았다고 쓰여있다.

build-essential을 전부 설치하는 것이 맞는지는 모르겠지만 최적화는 나중으로 생각하고 우선 문서에 나와있는 것처럼 Dockerfile에 다음을 추가해준다.

```docker
FROM apache/airflow
# ==추가 ⬇️==
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential libopenmpi-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
...
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirement.txt
```

다시 `docker compose`를 해보니 문제없이 빌드된다.

빌드 후 이미지 크기를 보니 100 - 200MB의 용량 증가가 있었다.

기회가 되면 이미지 최적화도 진행해야겠다.
