import streamlit as st
import httpx

API_BASE = "http://localhost:8000"
REFINE_REQUEST_TIMEOUT = 120.0

st.set_page_config(
    page_title="Refine — Mémoire de Parfum",
    page_icon="🌸",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Montserrat:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; font-weight: 300 !important; }
    .stButton > button {
        background-color: #1a1a1a;
        color: #f5f0eb;
        border: none;
        border-radius: 0px;
        padding: 0.75rem 2rem;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Guard
if not st.session_state.get("intent"):
    st.warning("No fragrance to refine.")
    if st.button("Start Over"):
        st.switch_page("app.py")
    st.stop()

st.markdown("""
<div style='text-align: center; padding: 3rem 0 2rem 0;'>
    <p style='font-family: Cormorant Garamond, serif; font-size: 0.9rem;
              color: #7a6a5a; letter-spacing: 0.2em; text-transform: uppercase;'>
        Refine Your Fragrance
    </p>
    <h1 style='font-size: 2.8rem; color: #1a1a1a;'>
        Adjust Your Blend
    </h1>
    <p style='color: #7a6a5a; font-size: 0.9rem;'>
        Choose how you'd like to adjust your fragrance
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

refinement_options = {
    "lighter": {
        "icon": "🪷",
        "label": "Lighter",
        "description": "Soften the overall intensity for a more subtle, skin-close wear"
    },
    "stronger": {
        "icon": "🌑",
        "label": "Stronger",
        "description": "Deepen the composition for a richer, more immersive experience"
    },
    "warmer": {
        "icon": "🔥",
        "label": "Warmer",
        "description": "Shift toward warmer notes — vanilla, amber, sandalwood"
    },
    "fresher": {
        "icon": "🌿",
        "label": "Fresher",
        "description": "Shift toward fresher notes — bergamot, neroli, lavender"
    },
}

selected_refinement = st.session_state.get("pending_refinement", None)

col1, col2 = st.columns(2)
cols = [col1, col2, col1, col2]

for col, (key, option) in zip(cols, refinement_options.items()):
    with col:
        is_selected = selected_refinement == key
        border = "3px solid #1a1a1a" if is_selected else "1px solid #e8e0d5"
        st.markdown(f"""
        <div style='border: {border}; padding: 1.5rem; text-align: center;
                    cursor: pointer; margin-bottom: 1rem;'>
            <p style='font-size: 2rem; margin: 0;'>{option['icon']}</p>
            <h3 style='font-size: 1.1rem; margin: 0.5rem 0;'>{option['label']}</h3>
            <p style='font-size: 0.78rem; color: #7a6a5a; line-height: 1.6;'>
                {option['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Select {option['label']}", key=f"select_{key}", use_container_width=True):
            selected_refinement = key
            st.session_state.pending_refinement = key

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Result", use_container_width=True):
        st.switch_page("pages/03_result.py")

with col2:
    if st.button("Apply Refinement →", use_container_width=True):
        if not selected_refinement:
            st.warning("Please select a refinement first.")
        else:
            with st.spinner("Refining your fragrance..."):
                try:
                    payload = {
                        "intent": st.session_state.intent,
                        "refinement": selected_refinement,
                    }

                    response = httpx.post(
                        f"{API_BASE}/refine/",
                        json=payload,
                        timeout=REFINE_REQUEST_TIMEOUT,
                    )
                    response.raise_for_status()
                    data = response.json()

                    st.session_state.intent = data["intent"]
                    st.session_state.blueprint = data["blueprint"]
                    st.session_state.fragrance_story = data["fragrance_story"]
                    st.session_state.refinement_count += 1
                    st.session_state.pending_refinement = None

                    st.success(f"Refinement applied: {selected_refinement.title()}")
                    st.switch_page("pages/03_result.py")

                except httpx.TimeoutException:
                    st.error("The refinement request took too long. Please try again.")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
