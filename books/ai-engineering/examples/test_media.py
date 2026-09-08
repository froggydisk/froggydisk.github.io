from pathlib import Path
import tempfile
import unittest
import wave
from media_demo import error_rate, pcm

class MediaTests(unittest.TestCase):
    def test_normalization_and_insertions(self):
        self.assertEqual(error_rate('가 나.', '가나'), 0)
        self.assertEqual(error_rate('가', '가나다'), 2)
        self.assertEqual(error_rate('가나', '가다'), .5)

    def test_empty_reference(self):
        with self.assertRaisesRegex(ValueError,'empty_reference'):
            error_rate('!','text')

    def test_wrong_rate_rejected_before_model(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.wav'
            with wave.open(str(path),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000)
                wav.writeframes(b'\0\0'*800)
            with self.assertRaisesRegex(ValueError,'expected_mono'):
                pcm(path)
