import streamlit as st

st.set_page_config(
    page_title="Choose Your Memory — Mémoire de Parfum",
    page_icon="🌸",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Montserrat:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; font-weight: 300 !important; }
    .stButton > button {
        background-color: transparent;
        color: #1a1a1a;
        border: 1px solid #c8b8a8;
        border-radius: 0px;
        padding: 1.5rem 2rem;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1a1a1a;
        color: #f5f0eb;
        border-color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style='text-align: center; padding: 3rem 0 2rem 0;'>
    <p style='font-family: Cormorant Garamond, serif; font-size: 0.9rem;
              color: #7a6a5a; letter-spacing: 0.2em; text-transform: uppercase;'>
        Step 1 of 3
    </p>
    <h1 style='font-size: 2.8rem; color: #1a1a1a;'>
        Choose Your Memory
    </h1>
    <p style='color: #7a6a5a; font-size: 0.9rem; letter-spacing: 0.05em;'>
        What kind of fragrance memory do you want to create?
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='font-size: 2.5rem;'>🕯️</p>
        <h3 style='font-size: 1.3rem; color: #1a1a1a;'>Past</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.7;'>
            Recreate a memory from the past.<br>
            A place, a person, a moment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Recreate a Memory", key="past"):
        st.session_state.memory_frame = "past"
        st.switch_page("pages/02_questionnaire.py")

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='font-size: 2.5rem;'>🌸</p>
        <h3 style='font-size: 1.3rem; color: #1a1a1a;'>Present</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.7;'>
            Express who you are right now.<br>
            Your identity, your chapter.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Express the Present", key="present"):
        st.session_state.memory_frame = "present"
        st.switch_page("pages/02_questionnaire.py")

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='font-size: 2.5rem;'>✨</p>
        <h3 style='font-size: 1.3rem; color: #1a1a1a;'>Future</h3>
        <p style='font-size: 0.8rem; color: #7a6a5a; line-height: 1.7;'>
            Design a fragrance for a moment<br>
            yet to happen.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Create a Future Memory", key="future"):
        st.session_state.memory_frame = "future"
        st.switch_page("pages/02_questionnaire.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app.py")
