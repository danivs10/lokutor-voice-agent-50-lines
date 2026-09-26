# Voice agent in about 50 lines

A small, inspectable push-to-talk loop: a recorded WAV clip goes to Lokutor STT, the transcript goes to an LLM, and Lokutor TTS saves the spoken answer to `reply.wav`. Conversation history stays in memory until the program exits. This is not a live, interruptible voice agent or a production client.

## Run

1. Get a free Lokutor API key at [app.lokutor.com](https://app.lokutor.com/) (dashboard > API Keys). Get an OpenAI API key separately; OpenAI usage may cost money.
2. Set `LOKUTOR_API_KEY` and `OPENAI_API_KEY` in your shell. Do not commit them or put them in a browser client. Optional: set `OPENAI_MODEL` (default `gpt-4o-mini`; check availability in your OpenAI account).
3. Record a short WAV file, then run `python3 agent.py`. Enter its path when prompted. Play `reply.wav` in an audio player and enter another clip to continue. Blank input quits. Each reply overwrites `reply.wav`, so copy it if you want to save a previous turn.

The script uses only Python's standard library. It expects a WAV file with speech; for predictable STT results, record 16 kHz mono PCM. TTS returns PCM16 WAV at 44.1 kHz mono. It sends audio to Lokutor and text/history to OpenAI. Network requests time out after 60 seconds. Review privacy and usage terms before using real conversations.

## Why two keys?

Lokutor serves both [STT](https://docs.lokutor.com/api-reference/rest.md) and [TTS](https://docs.lokutor.com/api-reference/rest.md); this short example uses OpenAI Chat Completions for the text reply. Swap `reply()` for another LLM if you prefer. For real-time microphone, playback, interruption and server-managed agent turns, use the [Lokutor Voice Agent SDK](https://docs.lokutor.com/sdk/agent.md) rather than this REST teaching sample.

## Test without paid calls

`python3 -m unittest discover -s tests -v` mocks all HTTP calls. The test never uses your keys or makes a synthesis request.
