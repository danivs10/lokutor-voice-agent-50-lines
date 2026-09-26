import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent


class AgentTest(unittest.TestCase):
    def test_transcribe_multipart(self):
        with patch.object(agent, "request", return_value=b'{"text":"Hello"}') as req:
            self.assertEqual(agent.transcribe(b"RIFFfake", "lk-test"), "Hello")
        url, body, key, content_type = req.call_args.args
        self.assertEqual(url, "https://api.lokutor.com/stt/transcribe")
        self.assertIn(b'name="audio"', body)
        self.assertIn(b"RIFFfake", body)
        self.assertEqual(key, "lk-test")
        self.assertIn("multipart/form-data; boundary=", content_type)
        self.assertTrue(body.endswith(("--" + content_type.split("boundary=")[1] + "--\r\n").encode()))

    def test_llm_history(self):
        with patch.object(agent, "request", return_value=b'{"choices":[{"message":{"content":"Hi!"}}]}') as req:
            out = agent.reply([{"role": "user", "content": "Hello"}], "oa-test")
        self.assertEqual(out, "Hi!")
        self.assertEqual(req.call_args.args[0], "https://api.openai.com/v1/chat/completions")
        self.assertEqual(json.loads(req.call_args.args[1])["messages"][0]["content"], "Hello")

    def test_tts_request(self):
        with patch.object(agent, "request", return_value=b"RIFFaudio") as req:
            self.assertEqual(agent.speak("Hi", "lk-test"), b"RIFFaudio")
        self.assertEqual(req.call_args.args[0], "https://api.lokutor.com/tts/synthesize")
        self.assertEqual(json.loads(req.call_args.args[1]), {"text": "Hi", "voice": "F1", "language": "en"})

    def test_auth_headers_and_error(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return None
            def read(self): return b"OK"
        with patch.object(agent.urllib.request, "urlopen", return_value=FakeResponse()) as open_:
            self.assertEqual(agent.request("https://example.com", b"{}", "test"), b"OK")
        request = open_.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test")
        self.assertEqual(request.get_header("Content-type"), "application/json")


if __name__ == "__main__": unittest.main()
