"""2장의 독립 실행 계산 예제. 외부 모델 호출이나 성능 측정이 아니다."""

import math


def probabilities(logits: list[float], temperature: float) -> list[float]:
    if not logits or not all(math.isfinite(x) for x in logits):
        raise ValueError("유한한 로짓을 하나 이상 입력해야 한다")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("온도는 유한한 양수여야 한다")
    peak = max(logits)
    weights = [math.exp((x - peak) / temperature) for x in logits]
    total = sum(weights)
    return [weight / total for weight in weights]


if __name__ == "__main__":
    for temperature in (0.5, 1.0, 2.0):
        result = probabilities([2.0, 1.0, 0.0], temperature)
        print(temperature, [round(p, 3) for p in result])
