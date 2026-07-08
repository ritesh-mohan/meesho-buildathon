import json
import re
from urllib.parse import quote

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="BazaarBhasha — Multi-language Product Descriptions",
    page_icon="🛍️",
    layout="centered",
)

LANGUAGES = [
    {"code": "hi", "name": "Hindi", "native": "हिंदी", "accent": "#F5A623", "default": True},
    {"code": "en", "name": "English", "native": "English", "accent": "#3FC1C9", "default": True},
    {"code": "ta", "name": "Tamil", "native": "தமிழ்", "accent": "#E8567C", "default": True},
    {"code": "te", "name": "Telugu", "native": "తెలుగు", "accent": "#3FA76B", "default": True},
    {"code": "bn", "name": "Bengali", "native": "বাংলা", "accent": "#9B7BF0", "default": True},
    {"code": "mr", "name": "Marathi", "native": "मराठी", "accent": "#F5A623", "default": False},
    {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ", "accent": "#E8567C", "default": False},
    {"code": "ml", "name": "Malayalam", "native": "മലയാളം", "accent": "#3FA76B", "default": False},
    {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી", "accent": "#3FC1C9", "default": False},
    {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ", "accent": "#9B7BF0", "default": False},
    {"code": "or", "name": "Odia", "native": "ଓଡ଼ିଆ", "accent": "#F5A623", "default": False},
]
LANG_BY_LABEL = {f"{l['name']} ({l['native']})": l for l in LANGUAGES}

MODELS = {
    "Claude Sonnet 5 — best quality": "anthropic/claude-sonnet-5",
    "Claude Haiku 4.5 — faster & cheaper": "anthropic/claude-haiku-4.5",
}

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

CATEGORIES = [
    "Women's Ethnic Wear", "Kurtis & Suits", "Sarees", "Men's Wear",
    "Kids Wear", "Jewellery & Accessories", "Footwear", "Home & Kitchen",
    "Beauty & Personal Care", "Bags & Wallets", "Electronics Accessory", "Other",
]

# ---------------------------------------------------------------------------
# Styling — light touch, keeps native Streamlit widgets but themes them
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;800&family=Noto+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans', sans-serif; }
    .bb-title { font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 2.4rem;
                margin-bottom: 0; }
    .bb-title span { color: #F5A623; }
    .bb-tagline { color: #8B8398; font-size: 1.02rem; margin-top: 0.2rem; margin-bottom: 1.6rem; }
    .bb-eyebrow { display:inline-block; font-size:0.78rem; letter-spacing:0.06em; text-transform:uppercase;
                  color:#F5A623; background:rgba(245,166,35,0.12); border:1px solid rgba(245,166,35,0.35);
                  padding:4px 12px; border-radius:999px; margin-bottom:14px; font-weight:600; }
    .tag-card { border-left: 5px solid var(--accent, #F5A623); background: rgba(255,255,255,0.03);
                border-radius: 4px 14px 14px 4px; padding: 14px 16px; margin-bottom: 14px; }
    .tag-lang-name { font-weight:700; color: var(--accent, #F5A623); }
    .tag-lang-native { color:#8B8398; font-size:0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<span class="bb-eyebrow">✨ Built with Claude</span>', unsafe_allow_html=True)
st.markdown('<div class="bb-title">Bazaar<span>Bhasha</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="bb-tagline">Describe your product once. Get ready-to-post descriptions '
    'in every language your buyers actually speak — for WhatsApp, Instagram and your storefront.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — model + API key handling
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Settings")
    model_label = st.selectbox("Model", list(MODELS.keys()), index=0)
    model_id = MODELS[model_label]

    secret_key = st.secrets.get("OPENROUTER_API_KEY", "")
    if secret_key:
        st.success("Using the app's configured API key.")
        use_own_key = st.checkbox("Use my own API key instead", value=False)
        user_key = st.text_input("Your OpenRouter API key", type="password") if use_own_key else ""
        api_key = user_key or secret_key
    else:
        st.info("No API key is configured for this app yet.")
        api_key = st.text_input("OpenRouter API key", type="password", placeholder="sk-or-v1-...")

    st.caption(
        "Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys) (starts with `sk-or-`). "
        "If you're the one deploying this app, set `OPENROUTER_API_KEY` in **Settings → Secrets** "
        "on Streamlit Cloud so visitors don't need their own key."
    )

# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------

SAMPLE = {
    "product_name_input": "Cotton Anarkali Kurti",
    "category_input": "Kurtis & Suits",
    "price_input": "₹549",
    "details_input": "Pure cotton, floor length, mirror work on sleeves, machine washable, "
                      "available in 5 colours (maroon, navy, mustard, green, black), "
                      "free size fits up to XL, ships in 2-3 days",
}

with st.expander("Try a sample product instead"):
    if st.button("Fill sample values"):
        for k, v in SAMPLE.items():
            st.session_state[k] = v
        st.rerun()

with st.form("product_form"):
    product_name = st.text_input(
        "Product name", key="product_name_input", placeholder="e.g. Cotton Anarkali Kurti"
    )

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox(
            "Category", CATEGORIES,
            index=CATEGORIES.index(st.session_state.get("category_input", CATEGORIES[0]))
                  if st.session_state.get("category_input") in CATEGORIES else 0,
            key="category_input",
        )
    with col2:
        price = st.text_input("Price (optional)", key="price_input", placeholder="₹499")

    details = st.text_area(
        "Key details — type in English or Hindi, whatever's easiest",
        key="details_input",
        placeholder="e.g. Pure cotton, floor length, mirror work on sleeves, machine washable, "
                    "available in 5 colours, free size up to XL, ships in 2 days",
        height=110,
    )

    default_labels = [f"{l['name']} ({l['native']})" for l in LANGUAGES if l["default"]]
    all_labels = [f"{l['name']} ({l['native']})" for l in LANGUAGES]
    selected_labels = st.multiselect("Generate descriptions in", all_labels, default=default_labels)

    submitted = st.form_submit_button("Generate descriptions", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Claude call
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert e-commerce copywriter who writes catchy, high-converting product descriptions for small Indian resellers who sell via WhatsApp, Instagram and social commerce apps like Meesho.

Rules:
- Return ONLY a single valid JSON object, nothing else — no markdown fences, no commentary before or after.
- The JSON keys must be exactly the language codes given to you, and the value for each key is the description string for that language, written natively in that language's own script (not transliterated, not word-for-word translated from English — write it as a native speaker copywriter would).
- Each description: 2-4 short sentences, warm and persuasive, suitable for a WhatsApp broadcast or Instagram caption. Include 2-3 relevant emojis placed naturally. Mention the strongest selling points from the details given. End with a short, natural call-to-action (e.g. order now / DM to order / limited stock), phrased naturally in that language.
- Keep each description under 55 words.
- Do not invent facts (like price, materials, or delivery time) that were not given to you.
- Keep the core message consistent across languages, but let phrasing and tone feel natural and local to each language rather than a stiff literal translation."""


def build_user_prompt(product_name, category, price, details, langs):
    lang_list = "\n".join(f"{l['code']}: {l['name']} ({l['native']})" for l in langs)
    return f"""Product name: {product_name}
Category: {category}
Price: {price or 'not specified — do not mention a price'}
Key details (may be in English or Hindi): {details}

Generate descriptions for these languages:
{lang_list}

Respond with only the JSON object."""


def parse_json_loosely(text):
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)


class AuthError(Exception):
    pass


class RateLimitError(Exception):
    pass


def call_openrouter(api_key, model, product_name, category, price, details, langs):
    user_prompt = build_user_prompt(product_name, category, price, details, langs)

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Optional but recommended by OpenRouter for their leaderboards/rate-limit tiers.
            "HTTP-Referer": "https://bazaarbhasha.streamlit.app",
            "X-Title": "BazaarBhasha",
        },
        json={
            "model": model,
            "max_tokens": 2000,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60,
    )

    if not response.ok:
        detail = ""
        try:
            detail = response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        if response.status_code == 401:
            raise AuthError("That API key was rejected. Double-check it in the sidebar.")
        if response.status_code == 429:
            raise RateLimitError("Rate limited by OpenRouter — wait a moment and try again.")
        raise RuntimeError(f"Request failed ({response.status_code}). {detail}")

    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("No response returned by the model.")
    text = choices[0]["message"]["content"]
    return parse_json_loosely(text)


# ---------------------------------------------------------------------------
# Handle submit
# ---------------------------------------------------------------------------

if submitted:
    selected_langs = [LANG_BY_LABEL[label] for label in selected_labels]

    if not api_key:
        st.error("Please add an OpenRouter API key in the sidebar first.")
    elif not product_name.strip():
        st.error("Please enter a product name.")
    elif not details.strip():
        st.error("Please add a few key details about the product.")
    elif not selected_langs:
        st.error("Pick at least one language to generate in.")
    else:
        with st.spinner("Writing descriptions…"):
            try:
                descriptions = call_openrouter(
                    api_key, model_id, product_name.strip(), category,
                    price.strip(), details.strip(), selected_langs,
                )
                st.session_state["results"] = (selected_langs, descriptions)
            except AuthError as e:
                st.error(str(e))
            except RateLimitError as e:
                st.error(str(e))
            except json.JSONDecodeError:
                st.error("Could not parse the model's response. Please try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if "results" in st.session_state:
    langs, descriptions = st.session_state["results"]
    st.subheader("Your descriptions")

    for lang in langs:
        text = descriptions.get(lang["code"], "(no description returned)")
        st.markdown(
            f'<div class="tag-card" style="--accent:{lang["accent"]}">'
            f'<span class="tag-lang-name">{lang["name"]}</span> '
            f'<span class="tag-lang-native">{lang["native"]}</span></div>',
            unsafe_allow_html=True,
        )
        st.code(text, language=None)
        wa_url = f"https://wa.me/?text={quote(text)}"
        st.link_button("💬 Share on WhatsApp", wa_url)
        st.divider()

st.caption(
    "Built for the Buildathon · each deployer sets their own OpenRouter API key as a secret · "
    "no data is stored by this app"
)
