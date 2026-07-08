# BazaarBhasha 🛍️🗣️ — Streamlit version (via OpenRouter)

**Type your product details once. Get catchy, ready-to-post descriptions in 11 Indian languages — for WhatsApp, Instagram, and your storefront.**

This build calls Claude through **[OpenRouter](https://openrouter.ai)** rather than Anthropic's API directly — useful if OpenRouter is where your credits/key already live. Since Streamlit has a real Python backend, **you** (the person deploying it) set one OpenRouter API key as a secret, and anyone who opens the app can use it — no one else needs their own key.

## Files

```
app.py                           — the whole app
requirements.txt                 — streamlit + requests
.streamlit/secrets.toml.example  — template showing the secret format (not a real key)
.gitignore                       — keeps your real secrets.toml out of git
```

## 1. Run it locally first

```bash
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# now open .streamlit/secrets.toml and paste your real key in place of the placeholder

streamlit run app.py
```

It'll open at `http://localhost:8501`. Test it end-to-end (generate a real description) before you deploy.

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys) — it starts with `sk-or-`. Add credit to your OpenRouter account under **Settings → Credits** if you haven't already; even a couple of dollars covers a lot of description generations.

## 2. Push the code to GitHub

Your `secrets.toml` should **never** be committed — `.gitignore` already excludes it, only `secrets.toml.example` (with a fake key) goes to GitHub.

```bash
git init
git add app.py requirements.txt .gitignore .streamlit/secrets.toml.example README.md
git commit -m "Add BazaarBhasha Streamlit app (OpenRouter)"
git branch -M main
git remote add origin https://github.com/<your-username>/bazaarbhasha.git
git push -u origin main
```

(Or use GitHub's website: **New repository → Add file → Upload files**, and upload everything except the real `secrets.toml`.)

## 3. Deploy on Streamlit Community Cloud (free)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **Create app** (or **New app**).
3. Choose **"Deploy a public app from GitHub"**, then pick:
   - **Repository:** `<your-username>/bazaarbhasha`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Before clicking Deploy, open **Advanced settings → Secrets** and paste in:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-real-key-here"
   ```
   (If you forget this step, you can add it later from the app's **Settings → Secrets** menu — it'll restart automatically.)
5. Click **Deploy**. After a minute or two you'll get a public URL like:
   `https://bazaarbhasha.streamlit.app`
6. Open it, try generating a description, and use that URL as your **App link** in the submission form.

## Why your original key was rejected

The first version of this app called `api.anthropic.com` directly with an Anthropic-format API key (`sk-ant-...`). OpenRouter keys (`sk-or-...`) are a different service with a different endpoint and a different (OpenAI-compatible) request format — Anthropic's API will always reject an OpenRouter key, and vice versa. This version now calls `https://openrouter.ai/api/v1/chat/completions` with model slugs like `anthropic/claude-sonnet-5`, which is how OpenRouter expects requests to be shaped.

## A note on cost

Because the API key is shared across every visitor once you set it as a secret, anyone who finds your public link can use your OpenRouter credits. For a hackathon demo this is usually fine (it's just for testing and evaluation), but if you're worried about it:

- The sidebar has a **"Use my own API key instead"** checkbox — visitors (including evaluators) can supply their own key if they'd rather not use yours.
- You can also default to the cheaper **Claude Haiku 4.5** model in the sidebar to keep costs low.
- OpenRouter lets you set a spend limit per key under **Settings → Keys** if you want a hard ceiling.

## Notes for judges / submission form

- **App link:** your `*.streamlit.app` URL.
- **Problem:** small resellers only write product descriptions in one language (usually English or Hindi), which limits their reach to buyers who are more comfortable in their own regional language.
- **Why it matters:** a huge share of Meesho-style buyers are Tier 2/3 and regional-language-first. A description that actually speaks their language is more persuasive and more shareable than a generic English caption.

## Customizing further

- Languages, colors, and the prompt sent to Claude are all near the top of `app.py` — edit `LANGUAGES`, `SYSTEM_PROMPT`, or `MODELS` directly.
- To switch models, use any OpenRouter model slug in the `MODELS` dict (browse options at [openrouter.ai/models](https://openrouter.ai/models)).
- Want a "Copy" button instead of / alongside the WhatsApp button? `st.code()` already shows a copy icon on hover in the top-right of each code block — no extra code needed.

