import streamlit as st

st.set_page_config(
    page_title="Mémoire de Parfum",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Session state initialization ---
if "memory_frame" not in st.session_state:
    st.session_state.memory_frame = None
if "intent" not in st.session_state:
    st.session_state.intent = None
if "blueprint" not in st.session_state:
    st.session_state.blueprint = None
if "fragrance_story" not in st.session_state:
    st.session_state.fragrance_story = None
if "refinement_count" not in st.session_state:
    st.session_state.refinement_count = 0


# --- Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Montserrat:wght@300;400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 300 !important;
        letter-spacing: 0.05em;
    }

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
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #4a3728;
        color: #f5f0eb;
    }

    .main {
        background-color: #faf8f5;
    }

    hr {
        border-color: #e8e0d5;
    }
</style>
""", unsafe_allow_html=True)


# --- Hero ---
st.markdown("""
<div style='text-align: center; padding: 4rem 0 2rem 0;'>
    <h1 style='font-size: 3.5rem; color: #1a1a1a; margin-bottom: 0.5rem;'>
        Mémoire de Parfum
    </h1>
    <p style='font-family: Cormorant Garamond, serif; font-size: 1.2rem;
              color: #7a6a5a; font-style: italic; letter-spacing: 0.1em;'>
        Where memories become fragrance
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<p style='text-align: center; color: #5a4a3a; font-size: 0.9rem;
          letter-spacing: 0.05em; line-height: 1.8;'>
    An AI-powered fragrance experience that transforms your past, present,<br>
    or future memories into a personalized, skin-safe scent composition.
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Begin Your Fragrance Journey →", use_container_width=True):
        st.switch_page("pages/01_memory_frame.py")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# --- Three pillars ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 1.8rem;'>🕯️</p>
        <h3 style='font-size: 1rem; color: #1a1a1a;'>Past</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.6;'>
            Recreate a memory you want to relive forever
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 1.8rem;'>🌸</p>
        <h3 style='font-size: 1rem; color: #1a1a1a;'>Present</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.6;'>
            Express who you are in this moment
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 1.8rem;'>✨</p>
        <h3 style='font-size: 1rem; color: #1a1a1a;'>Future</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.6;'>
            Design a fragrance for a moment yet to come
        </p>
    </div>
    """, unsafe_allow_html=True)
