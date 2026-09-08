"""16장: 보존된 실제 실행을 빠짐없이 채점한다. 의미 평가는 명시적 주석으로 분리한다."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

EXPECTED = {'R01': 'answered', 'R02': 'insufficient_evidence',
            'R03': 'insufficient_evidence', 'R04': 'insufficient_evidence'}


def evaluate(record, expected=EXPECTED):
    rows = record['rows']
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise ValueError('case_set_mismatch')
    statuses = Counter()
    details = []
    for row in rows:
        actual = row['result']['status']
        statuses[actual] += 1
        match = actual == expected[row['id']]
        details.append(dict(id=row['id'], expected=expected[row['id']], actual=actual,
                            status_match=match, semantic_review='not_scored'))
    calls = record.get('model_calls', [])
    return dict(cases=len(rows), status_matches=sum(r['status_match'] for r in details),
                statuses=dict(statuses), model_calls=len(calls),
                complete_generations=sum(c['generation']['status']=='ok' for c in calls),
                adoption='hold', reason='status_matching_does_not_establish_semantic_quality',
                details=details)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    raw = args.record.read_bytes()
    result = evaluate(json.loads(raw))
    result.update(input_sha256=hashlib.sha256(raw).hexdigest(),
                  evaluator_version='status-eval-v1', dataset='R01-R04-development')
    print(json.dumps(result,ensure_ascii=False,indent=2))
