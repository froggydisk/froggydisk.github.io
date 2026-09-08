"""7장: 실제 모델로 패딩 불변성·정규화·초과 입력 거부를 검증한다."""
import json
import math
from embedding_model import Embedder


def main():
    model = Embedder(offline=True)
    short = '교육비 한도는?'
    single = model.encode([short], kind='query')[0]
    batched = model.encode([short, '팀장의 승인을 받은 뒤에 교육비를 신청하는 절차는 어떻게 되나요?'], kind='query')[0]
    delta = max(abs(a-b) for a,b in zip(single.values, batched.values))
    assert delta < 1e-5, delta
    assert len(single.values) == 384
    norm = math.sqrt(sum(x*x for x in single.values))
    assert abs(norm-1) < 1e-10
    rejected = []
    for name,texts,kind in [('empty',[''],'query'), ('role',[short],'document'),
                            ('over_tokens',['교육비 승인 신청 '*500],'passage')]:
        try:
            model.encode(texts,kind=kind)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    print(json.dumps({'dimension':len(single.values),'unit_norm':norm,
                     'single_batch_max_delta':delta,'rejected':rejected},indent=2))

if __name__ == '__main__':
    main()
