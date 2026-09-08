"""7장 심화: 수동 2차원 벡터로 분류·추천·이상 후보의 계산을 보여 준다.
학습한 텍스트 임베딩도, 운영용 판정기도 아니다.
"""
import json
from vector_search import cosine


def ranked(vector, candidates):
    return sorted(((name, cosine(vector, other)) for name, other in candidates.items()),
                  key=lambda row: (-row[1], row[0]))


def main():
    prototypes = {'계정':(1,0), '장비':(0,1)}
    classification = ranked((0.9,0.1), prototypes)
    recommendations = ranked((1,0), {'설정 안내':(0.9,0.1), '수리 안내':(0.1,0.9)})
    anomaly = 1 - max(score for _,score in ranked((-1,-1), prototypes))
    print(json.dumps({'vector_source':'저자 구성 2차원 예시; 실측 의미 벡터 아님',
        'nearest_class':classification[0][0],
        'class_score_gap':classification[0][1]-classification[1][1],
        'recommendation_order':[name for name,_ in recommendations],
        'anomaly_candidate_score':anomaly}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
