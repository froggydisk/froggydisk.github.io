"""17장: 상한이 있는 큐·마감·장애·버전 롤백을 실제 비동기 작업으로 관찰한다."""
import asyncio
from collections import Counter
import json
import math
import time
from uuid import uuid4


async def experiment(version, *, fault=False, count=20, capacity=4, workers=2):
    queue = asyncio.Queue(maxsize=capacity)
    rows = []
    async def work():
        while True:
            item = await queue.get()
            try:
                if item is None:
                    return
                trace, started, deadline = item
                status = 'ok'
                try:
                    async with asyncio.timeout_at(deadline):
                        await asyncio.sleep(0.2 if fault else 0.01)
                except TimeoutError:
                    status = 'deadline_exceeded'
                rows.append(dict(trace_id=trace,version=version,status=status,
                                 seconds=time.perf_counter()-started))
            finally:
                queue.task_done()
    tasks = [asyncio.create_task(work()) for _ in range(workers)]
    loop = asyncio.get_running_loop()
    for _ in range(count):
        trace = uuid4().hex
        start = time.perf_counter()
        try:
            queue.put_nowait((trace,start,loop.time()+0.05))
        except asyncio.QueueFull:
            rows.append(dict(trace_id=trace,version=version,status='overloaded',
                             seconds=time.perf_counter()-start))
    await queue.join()
    for _ in tasks:
        await queue.put(None)
    await asyncio.gather(*tasks)
    times = sorted(r['seconds'] for r in rows if r['status'] != 'overloaded')
    statuses = dict(Counter(r['status'] for r in rows))
    return dict(version=version,requests=count,queue_capacity=capacity,workers=workers,
                statuses=statuses,admitted_p95_seconds=times[math.ceil(len(times)*.95)-1],
                rows=rows)


async def main():
    baseline = await experiment('release-a')
    failure = await experiment('release-b',fault=True)
    rollback = await experiment('release-a')
    assert baseline['statuses'] == {'overloaded':16,'ok':4}
    assert failure['statuses'] == {'overloaded':16,'deadline_exceeded':4}
    assert rollback['statuses'] == baseline['statuses']
    print(json.dumps(dict(scope='in_process_synthetic_wait_not_model_load',
                         runs=[baseline,failure,rollback]),indent=2))


if __name__ == '__main__':
    asyncio.run(main())
