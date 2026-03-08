import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Your Fragrance — Mémoire de Parfum",
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
    .note-card {
        background: #faf8f5;
        border: 1px solid #e8e0d5;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Guard
if not st.session_state.get("blueprint"):
    st.warning("No fragrance generated yet.")
    if st.button("Start Over"):
        st.switch_page("app.py")
    st.stop()

blueprint = st.session_state.blueprint
story = st.session_state.fragrance_story
frame = st.session_state.get("memory_frame", "past")
frame_icons = {"past": "🕯️", "present": "🌸", "future": "✨"}

# ─── Header ──────────────────────────────────────────────
st.markdown(f"""
<div style='text-align: center; padding: 3rem 0 1rem 0;'>
    <p style='font-family: Cormorant Garamond, serif; font-size: 0.9rem;
              color: #7a6a5a; letter-spacing: 0.2em; text-transform: uppercase;'>
        Your Fragrance Blueprint
    </p>
    <h1 style='font-size: 2.8rem; color: #1a1a1a;'>
        {frame_icons[frame]} Your {frame.capitalize()} Memory, Bottled
    </h1>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Fragrance Story ─────────────────────────────────────
st.markdown(f"""
<div style='background: #f5f0eb; padding: 2rem; border-left: 3px solid #c8b8a8;
            margin: 1.5rem 0; font-family: Cormorant Garamond, serif;
            font-size: 1.05rem; line-height: 1.9; color: #3a2a1a; font-style: italic;'>
    {story}
</div>
""", unsafe_allow_html=True)

# ─── Fragrance Blueprint ─────────────────────────────────
st.markdown("### The Composition")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Top Notes** *(First impression)*")
    for note in blueprint.get("top_notes", []):
        sub = " *(substituted)*" if note.get("is_substituted") else ""
        st.markdown(f"""
        <div class='note-card'>
            <strong>{note['name'].title()}</strong>{sub}<br>
            <span style='font-size:0.75rem; color:#7a6a5a;'>{note['family']} · {note['description']}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("**Heart Notes** *(Character)*")
    for note in blueprint.get("heart_notes", []):
        sub = " *(substituted)*" if note.get("is_substituted") else ""
        st.markdown(f"""
        <div class='note-card'>
            <strong>{note['name'].title()}</strong>{sub}<br>
            <span style='font-size:0.75rem; color:#7a6a5a;'>{note['family']} · {note['description']}</span>
        </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("**Base Notes** *(Lasting impression)*")
    for note in blueprint.get("base_notes", []):
        sub = " *(substituted)*" if note.get("is_substituted") else ""
        st.markdown(f"""
        <div class='note-card'>
            <strong>{note['name'].title()}</strong>{sub}<br>
            <span style='font-size:0.75rem; color:#7a6a5a;'>{note['family']} · {note['description']}</span>
        </div>
        """, unsafe_allow_html=True)

# ─── Details ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Intensity", blueprint.get("intensity", "—").title())
with col2:
    st.metric("Projection", blueprint.get("projection", "—").title())
with col3:
    st.metric("Longevity", blueprint.get("longevity", "—").title())

# ─── Safety note ─────────────────────────────────────────
st.markdown(f"""
<div style='background: #f0ede8; padding: 1rem 1.2rem; margin-top: 1rem;
            border-left: 3px solid #a89880; font-size: 0.8rem; color: #5a4a3a;'>
    🛡️ {blueprint.get('safety_note', '')}
</div>
""", unsafe_allow_html=True)

# ─── Actions ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### Refine Your Fragrance")

col1, col2, col3, col4 = st.columns(4)

refinements = {
    "Lighter": "lighter",
    "Stronger": "stronger",
    "Warmer": "warmer",
    "Fresher": "fresher",
}

for col, (label, value) in zip([col1, col2, col3, col4], refinements.items()):
    with col:
        if st.button(label, use_container_width=True, key=f"refine_{value}"):
            st.switch_page("pages/04_refine.py")
            st.session_state.pending_refinement = value

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("← Start Over", use_container_width=True):
        for key in ["memory_frame", "intent", "blueprint",
                    "fragrance_story", "refinement_count"]:
            st.session_state.pop(key, None)
        st.switch_page("app.py")

with col2:
    if st.button("Save This Blend ✓", use_container_width=True):
        st.success("Blend saved to your profile!")
