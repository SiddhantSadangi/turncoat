# Turncoat

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://turncoat.streamlit.app)

**Turncoat** is an app where two AI models debate a topic—each arguing *for* and *against* the motion. Try it at **[turncoat.streamlit.app](https://turncoat.streamlit.app)** (enter your API keys in the sidebar). You pick the topic, choose the models and voices, then generate and play the four speeches.

## What you need

- **OpenRouter API key** — [Get one here](https://openrouter.ai/keys). Required to generate the debate speeches.
- **ElevenLabs API key** — [Get one here](https://elevenlabs.io/app/settings/api-keys). Optional; used to turn speeches into spoken audio. Without it you can still generate and read all speeches; audio buttons are shown but disabled until you add the key.

## How to run the app

1. Install [Python](https://www.python.org/downloads/) (3.10 or newer).
2. In a terminal, go to the app folder and run:

   ```bash
   pip install -r requirements.txt
   streamlit run streamlit_app.py
   ```

3. Your browser will open the app. In the **sidebar**, enter at least your **OpenRouter** API key (required). Add your **ElevenLabs** key if you want to hear the speeches; without it you can still generate and read them. Keys stay in your session and are not saved to disk.

   Alternatively, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your keys there so you don’t type them each time.

## What you can do

- **Home** — Read what a turncoat debate is and how Turncoat works.
- **Debate** — Enter a topic (the motion), pick two AI models (and two voices if you have an ElevenLabs key), set the round duration in the sidebar, then:
  - Generate speeches **one by one** (each speech appears in its box), or use **Generate all speeches** to create all four in one go.
  - With an ElevenLabs key: click **Play** on any speech to hear it, or use **Generate all audio** to create audio for all four. Without the key, those buttons are shown but disabled (click the info icon next to them to see why).
  - Use **Clear all speeches** to start over.

Sessions are independent: there is no saved history. Turncoat runs locally in your browser.

## License

[MIT](LICENSE).
