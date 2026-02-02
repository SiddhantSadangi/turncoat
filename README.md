# Turncoat

LLM turncoat debate app: two OpenRouter models debate a topic (for/against), with ElevenLabs TTS.

## App structure

- **Home** — Landing page that explains what a turncoat debate is and what this app does.
- **Debate** — Run a four-speech turncoat debate: pick a topic, two LLMs, two voices; generate speeches one by one (TTS when enabled).

There is no history or persistence; each session is independent.

## Phase 1 – API clients and test page

You can test the OpenRouter and ElevenLabs integrations from the app.

### Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **API keys** (either):

   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your keys, or  
   - Run the app and enter keys in the sidebar (stored in session only).

3. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

### Phase 1 test flow

1. Open the app; if keys are not in secrets, enter OpenRouter and ElevenLabs API keys.
2. **OpenRouter**: Click "Fetch models", then pick a model and run "Run completion" with a test prompt.
3. **ElevenLabs**: Click "Fetch voices", then pick a voice and run "Generate and play" with some text.

If both APIs respond, Phase 1 is done.

## Phase 4 – TTS playback

On the Debate page, each generated speech has a **Play** button. Click it to generate audio with ElevenLabs (using the voice chosen for that debater) and play it in the browser. Audio is cached in session; clearing all speeches also clears the audio cache.
