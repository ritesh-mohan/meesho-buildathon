# BazaarBhasha 🛍️🗣️ — Streamlit version (free models via OpenRouter)

**Type your product details once. Get catchy, ready-to-post descriptions in 11 Indian languages — for WhatsApp, Instagram, and your storefront.**

This build calls **free, $0-per-token models on [OpenRouter](https://openrouter.ai)** — no Anthropic billing, no OpenRouter credit required. The model dropdown is populated **live** from OpenRouter's model catalog (filtered to models priced at zero), since the free-tier lineup rotates fairly often. Since Streamlit has a real Python backend, **you** (the person deploying it) set one OpenRouter API key as a secret, and anyone who opens the app can use it — no one else needs their own key.

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

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys) — it starts with `sk-or-`. **No credit card or purchase is required** to use the free models this app defaults to; you just need an account and a key. (If you ever switch to a paid model via the "Custom model ID" option in the sidebar, you'll need credit in your account for that.)

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

## If you see "..." or empty descriptions

This is a known failure mode on some free models: a "reasoning" model can burn its entire token budget on hidden internal thinking and have nothing left to write the real answer, or a weaker model just gets lazy and drops in a placeholder instead of writing out several similar-looking descriptions in full. The app now:

- Explicitly disables hidden reasoning tokens on models that support turning it off
- Prioritizes plain instruction-following models (Llama 3.3 70B, Gemma 3, etc.) at the top of the dropdown over "thinking" models
- Gives the model a bigger token budget (4096) to work with
- Detects placeholder/empty output before showing it to you, and tells you clearly which languages failed and why, instead of silently rendering "..."

If you still hit this, the fix is almost always the same: **pick a different model from the sidebar dropdown** (a plain instruct model, not a reasoning one) or generate fewer languages in one go.

## Why your original key was rejected, and why models were being charged

Two separate issues from earlier versions, both fixed now:

1. The first version called `api.anthropic.com` directly with an Anthropic-format key (`sk-ant-...`). OpenRouter keys (`sk-or-...`) are a different service with a different endpoint — Anthropic's API will always reject an OpenRouter key. This version calls `https://openrouter.ai/api/v1/chat/completions` instead, which is what OpenRouter expects.
2. The next version defaulted to `anthropic/claude-sonnet-5` and `anthropic/claude-haiku-4.5` — real OpenRouter model slugs, but **paid** ones (Anthropic doesn't offer free Claude access through OpenRouter or anywhere else). This version instead fetches OpenRouter's current $0/token models live and defaults to one of those, so nothing gets billed unless you deliberately pick a paid model via "Custom model ID" in the sidebar.

## A note on free-model quality and limits

- Free models are rate-limited by OpenRouter (roughly 20 requests/minute), which is more than enough for this app's usage pattern.
- The specific free models available rotate — a model that works today might be retired next month. If a generation fails or errors out, just pick a different model from the dropdown; the list refreshes from OpenRouter automatically (cached for an hour at a time).
- Free open-weight models are generally a notch below Claude on following strict formatting instructions and writing natural, idiomatic text in Indian regional scripts. The app is written defensively around this (loose JSON parsing, clear system prompt), but do spot-check a few outputs before using them, especially for less common languages.
- If you later want higher quality and don't mind paying, use the **"Custom model ID…"** option in the sidebar and enter something like `anthropic/claude-sonnet-5` — you'll just need credit in your OpenRouter account for that request.

## A note on shared access

Since the key lives only in this app's secrets, every visitor uses the same key — there's no way for someone to bring their own instead. For a hackathon demo this is fine (free models cost nothing regardless of who calls them), but it does mean anyone with your app's URL shares your OpenRouter rate-limit allowance.

## Notes for judges / submission form

- **App link:** your `*.streamlit.app` URL.
- **Problem:** small resellers only write product descriptions in one language (usually English or Hindi), which limits their reach to buyers who are more comfortable in their own regional language.
- **Why it matters:** a huge share of Meesho-style buyers are Tier 2/3 and regional-language-first. A description that actually speaks their language is more persuasive and more shareable than a generic English caption.

## Customizing further

- Languages, colors, and the prompt sent to the model are all near the top of `app.py` — edit `LANGUAGES`, `SYSTEM_PROMPT`, or `FALLBACK_FREE_MODELS` directly.
- The model dropdown is generated by `fetch_free_models()`, which queries `openrouter.ai/api/v1/models` and keeps only $0/token entries. `FALLBACK_FREE_MODELS` is only used if that request fails.
- Each result has its own "📋 Copy" button (`copy_button()` in `app.py`) that copies straight to the clipboard.

