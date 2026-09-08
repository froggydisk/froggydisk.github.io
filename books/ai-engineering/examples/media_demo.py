"""14장: 가상 문서 OCR와 합성 음성의 실제 인식. macOS 실측용."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import unicodedata
import urllib.request
import wave

ROOT = Path(__file__).parent
MODEL = 'openai/whisper-tiny'
REVISION = '169d4a4341b33bc18d8881c4b69c2e104e1cc0af'


def error_rate(reference, prediction):
    def chars(text):
        return ''.join(c for c in unicodedata.normalize('NFC', text) if c.isalnum())
    a, b = chars(reference), chars(prediction)
    if not a:
        raise ValueError('empty_reference')
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        curr = [i]
        for j, y in enumerate(b, 1):
            curr.append(min(curr[-1]+1, prev[j]+1, prev[j-1]+(x != y)))
        prev = curr
    return prev[-1] / len(a)


def pcm(path):
    with wave.open(str(path), 'rb') as audio:
        if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) != (1, 2, 16000):
            raise ValueError('expected_mono_pcm16_16khz')
        if not 0 < audio.getnframes() <= 30*16000:
            raise ValueError('duration_limit')
        import numpy as np
        return np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype('float32') / 32768


def main():
    from PIL import Image, ImageDraw, ImageFont
    import PIL
    import torch
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    torch.set_num_threads(4)
    folder = ROOT / 'fixtures/media'
    cache = ROOT / '.model-cache'
    tessdata = cache / 'tessdata'
    tessdata.mkdir(parents=True, exist_ok=True)
    # 버전은 실행 기록의 tessdata_revision과 함께 고정한다.
    revision = '87416418657359cb625c412a48b6e1d6d41c29bd'
    target = tessdata / 'kor.traineddata'
    if not target.exists():
        urllib.request.urlretrieve(f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{revision}/kor.traineddata', target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != '6b85e11d9bbf07863b97b3523b1b112844c43e713df8b66418a081fd1060b3b2':
        raise ValueError('ocr_weights_checksum_mismatch')
    policy = '교육비는 분기당 30만 원이다.\n수강 전에 팀장의 승인을 받아야 한다.'
    picture = Image.new('RGB', (1400, 280), 'white')
    ImageDraw.Draw(picture).multiline_text((45, 55), policy,
        font=ImageFont.truetype('/System/Library/Fonts/AppleSDGothicNeo.ttc', 44), fill='black', spacing=24)
    path = folder / 'policy.png'
    picture.save(path)
    start = time.perf_counter()
    ocr = subprocess.run(['tesseract', str(path), 'stdout', '--tessdata-dir', str(tessdata),
                         '-l', 'kor', '--psm', '6'], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    ocr_seconds = time.perf_counter() - start
    question = '교육비 한도는 얼마인가요?'
    start = time.perf_counter()
    subprocess.run(['say', '-v', 'Yuna', '-o', str(folder/'question.aiff'), question], check=True, timeout=30)
    tts_seconds = time.perf_counter() - start
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(folder/'question.aiff'), '-ar', '16000',
                    '-ac', '1', '-c:a', 'pcm_s16le', str(folder/'question.wav')], check=True, timeout=30)
    sound = pcm(folder/'question.wav')
    start = time.perf_counter()
    options = dict(revision=REVISION, cache_dir=str(cache), token=False)
    processor = WhisperProcessor.from_pretrained(MODEL, **options)
    model = WhisperForConditionalGeneration.from_pretrained(MODEL, dtype=torch.float32, **options).eval()
    load_seconds = time.perf_counter() - start
    start = time.perf_counter()
    features = processor(sound, sampling_rate=16000, return_tensors='pt', return_attention_mask=True)
    with torch.inference_mode():
        ids = model.generate(**features, language='ko', task='transcribe', max_new_tokens=128, do_sample=False)
    transcript = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
    asr_seconds = time.perf_counter() - start
    result = dict(model=MODEL, revision=REVISION, device='cpu', dtype='float32', threads=4,
        pillow=PIL.__version__, tessdata_revision=revision,
        tessdata_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        tesseract=subprocess.run(['tesseract','--version'], capture_output=True,text=True,check=True).stdout.splitlines()[0],
        ocr=dict(reference=policy,text=ocr,seconds=ocr_seconds,cer=error_rate(policy,ocr)),
        speech=dict(reference=question,text=transcript,duration_seconds=len(sound)/16000,
                    tts_seconds=tts_seconds,load_seconds=load_seconds,asr_seconds=asr_seconds,
                    cer=error_rate(question,transcript)),
        scope='synthetic_clean_media_not_real_user_quality',
        usage='OCR text and transcript require review before indexing or tool confirmation')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
