"""Minimal push-to-talk voice agent: WAV input -> Lokutor STT -> LLM -> Lokutor TTS."""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

LOKUTOR = "https://api.lokutor.com"
OPENAI = "https://api.openai.com/v1/chat/completions"


def request(url, body, key, content_type="application/json"):
    req = urllib.request.Request(url, body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": content_type,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"{url} returned HTTP {error.code}: {detail}") from error


def transcribe(wav, key):
    boundary = f"lokutor-{uuid.uuid4().hex}"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; "
            f"filename=\"input.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode()
    body += wav + f"\r\n--{boundary}--\r\n".encode()
    result = request(f"{LOKUTOR}/stt/transcribe", body, key,
                     f"multipart/form-data; boundary={boundary}")
    return json.loads(result)["text"]


def reply(history, key):
    payload = json.dumps({"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                          "messages": history}).encode()
    data = request(OPENAI, payload, key)
    return json.loads(data)["choices"][0]["message"]["content"]


def speak(text, key):
    payload = json.dumps({"text": text, "voice": "F1", "language": "en"}).encode()
    return request(f"{LOKUTOR}/tts/synthesize", payload, key)


def main():
    lk, oa = os.environ["LOKUTOR_API_KEY"], os.environ["OPENAI_API_KEY"]
    history = [{"role": "system", "content": "You are a concise, helpful voice assistant."}]
    print("Record short WAV clips and enter each path. Blank line quits.")
    while path := input("WAV path: ").strip():
        text = transcribe(Path(path).expanduser().read_bytes(), lk).strip()
        if not text:
            print("No speech recognized; try another clip.")
            continue
        print(f"You: {text}")
        history.append({"role": "user", "content": text})
        answer = reply(history, oa)
        history.append({"role": "assistant", "content": answer})
        Path("reply.wav").write_bytes(speak(answer, lk))
        print(f"Agent: {answer}\nSaved reply.wav (44.1 kHz mono WAV)")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, FileNotFoundError, RuntimeError) as exc:
        sys.exit(f"Error: {exc}")
