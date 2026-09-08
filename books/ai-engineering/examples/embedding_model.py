"""7장: E5 검색용 임베딩. 긴 입력을 조용히 자르지 않고 거부한다."""
from pathlib import Path
from vector_search import Vector, unit

MODEL_ID = 'intfloat/multilingual-e5-small'
REVISION = '614241f622f53c4eeff9890bdc4f31cfecc418b3'
SPACE = f'{MODEL_ID}@{REVISION}:mean-mask:l2:query-passage:v1'


class Embedder:
    def __init__(self, *, offline=False):
        import torch
        from transformers import AutoTokenizer, AutoModel
        torch.set_num_threads(4)
        self.torch = torch
        options = dict(revision=REVISION, trust_remote_code=False, token=False,
                       local_files_only=offline,
                       cache_dir=str(Path(__file__).parent / '.model-cache'))
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **options)
        self.model = AutoModel.from_pretrained(MODEL_ID, dtype=torch.float32,
                                               use_safetensors=True, **options)
        self.model.eval()

    def encode(self, texts, *, kind):
        if kind not in ('query', 'passage'):
            raise ValueError('kind는 query 또는 passage여야 한다')
        if not isinstance(texts, (list, tuple)) or not 1 <= len(texts) <= 16:
            raise ValueError('한 배치는 1~16개 텍스트로 제한한다')
        if any(not isinstance(t, str) or not t.strip() or len(t) > 20000 for t in texts):
            raise ValueError('각 텍스트는 비어 있지 않고 20000자 이하여야 한다')
        encoded = self.tokenizer([f'{kind}: {t}' for t in texts],
                                 truncation=False, padding=False)
        if any(len(ids) > 512 for ids in encoded['input_ids']):
            raise ValueError('접두사·특수 토큰을 포함해 512토큰을 초과한다')
        batch = self.tokenizer.pad(encoded, padding=True, return_tensors='pt')
        with self.torch.inference_mode():
            hidden = self.model(**batch).last_hidden_state
            mask = batch['attention_mask'].unsqueeze(-1).bool()
            pooled = hidden.masked_fill(~mask, 0).sum(dim=1) / mask.sum(dim=1)
        return [Vector(SPACE, unit(row)) for row in pooled.tolist()]
