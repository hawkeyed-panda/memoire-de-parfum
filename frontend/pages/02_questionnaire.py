import streamlit as st
import httpx

API_BASE = "http://localhost:8000"
# Full pipeline: 2 LLM calls + Neo4j + Weaviate; allow up to 3 min
FRAGRANCE_REQUEST_TIMEOUT = 180.0

st.set_page_config(
    page_title="Your Story — Mémoire de Parfum",
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

# Guard — must have selected a memory frame
if "memory_frame" not in st.session_state or not st.session_state.memory_frame:
    st.warning("Please choose a memory frame first.")
    if st.button("Go Back"):
        st.switch_page("pages/01_memory_frame.py")
    st.stop()

frame = st.session_state.memory_frame
frame_labels = {"past": "Past", "present": "Present", "future": "Future"}
frame_icons = {"past": "🕯️", "present": "🌸", "future": "✨"}

st.markdown(f"""
<div style='text-align: center; padding: 3rem 0 2rem 0;'>
    <p style='font-family: Cormorant Garamond, serif; font-size: 0.9rem;
              color: #7a6a5a; letter-spacing: 0.2em; text-transform: uppercase;'>
        Step 2 of 3
    </p>
    <h1 style='font-size: 2.8rem; color: #1a1a1a;'>
        {frame_icons[frame]} Your {frame_labels[frame]} Memory
    </h1>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)

questionnaire_data = {}

# ─── PAST ───────────────────────────────────────────────
if frame == "past":
    st.markdown("### Describe the memory")
    memory_description = st.text_area(
        "Briefly describe the memory you want to relive",
        placeholder="e.g. Walking through my grandmother's rose garden on a summer morning...",
        height=100,
    )
    questionnaire_data["memory_description"] = memory_description

    st.markdown("### What emotions were strongest?")
    emotions = st.multiselect(
        "Select all that apply",
        ["comfort", "joy", "nostalgia", "peace", "love", "excitement"],
    )
    questionnaire_data["emotions"] = emotions

    st.markdown("### What did the air feel like?")
    air_texture = st.radio(
        "", ["warm", "fresh", "humid", "dry"], horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["air_texture"] = air_texture

    st.markdown("### Do you remember any scents?")
    scent_hints = st.multiselect(
        "Select all that apply",
        ["floral", "sweet", "green", "earthy", "clean", "unclear"],
    )
    questionnaire_data["scent_hints"] = scent_hints or ["unclear"]

    st.markdown("### How intense was the scent?")
    intensity = st.radio(
        "", ["soft", "gentle", "rich"], horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["intensity_memory"] = intensity

    st.markdown("### Skin sensitivity")
    sensitivity = st.radio(
        "", ["very_gentle", "balanced", "expressive"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["skin_sensitivity"] = sensitivity

# ─── PRESENT ─────────────────────────────────────────────
elif frame == "present":
    st.markdown("### Which best describes your life right now?")
    life_chapter = st.radio(
        "", ["fast_paced", "balanced", "explorative", "grounded", "transformative"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["life_chapter"] = life_chapter

    st.markdown("### When you wear this fragrance, you want to feel:")
    daily_feeling = st.multiselect(
        "Select all that apply",
        ["confident", "calm", "energized", "elegant", "powerful"],
    )
    questionnaire_data["daily_feeling"] = daily_feeling

    st.markdown("### What scent direction draws you?")
    scent_direction = st.radio(
        "", ["fresh_citrus", "woody", "floral", "musky", "warm_spicy"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["scent_direction"] = scent_direction

    st.markdown("### This fragrance is mainly for:")
    social_context = st.radio(
        "", ["work", "everyday", "evening"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["social_context"] = social_context

    st.markdown("### Projection preference")
    projection = st.radio(
        "", ["skin_close", "balanced", "statement"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["projection"] = projection

# ─── FUTURE ──────────────────────────────────────────────
elif frame == "future":
    st.markdown("### What is this fragrance for?")
    future_moment = st.radio(
        "",
        ["wedding", "career_milestone", "travel", "personal_transformation", "new_chapter"],
        label_visibility="collapsed"
    )
    questionnaire_data["future_moment"] = future_moment

    st.markdown("### How do you want to feel in that moment?")
    emotional_intention = st.multiselect(
        "Select all that apply",
        ["radiant", "empowered", "emotional", "grounded", "confident"],
    )
    questionnaire_data["emotional_intention"] = emotional_intention

    st.markdown("### When others smell this fragrance, it should feel:")
    desired_impression = st.multiselect(
        "Select all that apply",
        ["memorable", "intimate", "elegant", "bold", "timeless"],
    )
    questionnaire_data["desired_impression"] = desired_impression

    st.markdown("### If you imagine this moment as a scent, it feels:")
    scent_imagination = st.radio(
        "",
        ["soft_floral", "fresh_luminous", "warm_comforting", "deep_woody"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["scent_imagination"] = scent_imagination

    st.markdown("### Longevity preference")
    longevity = st.radio(
        "", ["subtle", "evolving", "lasting"],
        horizontal=True, label_visibility="collapsed"
    )
    questionnaire_data["longevity"] = longevity

# ─── Optional free text ───────────────────────────────────
st.markdown("---")
st.markdown("### Anything else you'd like to share? *(optional)*")
free_text = st.text_area(
    "",
    placeholder="Add any details, feelings, or context that might help capture your memory...",
    height=100,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Submit ───────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/01_memory_frame.py")

with col2:
    if st.button("Create My Fragrance →", use_container_width=True):
        st.caption("Creating your fragrance may take 1–2 minutes. Please wait…")
        with st.spinner("Crafting your fragrance..."):
            try:
                # Build request payload
                payload = {
                    "memory_frame": frame,
                    frame: questionnaire_data,
                    "free_text_memory": free_text,
                }

                response = httpx.post(
                    f"{API_BASE}/fragrance/generate",
                    json=payload,
                    timeout=FRAGRANCE_REQUEST_TIMEOUT,
                )

                if response.status_code != 200:
                    try:
                        err = response.json()
                        msg = err.get("message", err.get("detail", response.text))
                    except Exception:
                        msg = response.text
                    st.error(f"Server error: {msg}")
                    st.stop()

                data = response.json()

                # Store in session
                st.session_state.intent = data["intent"]
                st.session_state.blueprint = data["blueprint"]
                st.session_state.fragrance_story = data["fragrance_story"]
                st.session_state.refinement_count = 0

                st.switch_page("pages/03_result.py")

            except httpx.TimeoutException:
                st.error(
                    "The request took too long. The fragrance pipeline can take 1–2 minutes. "
                    "Please try again; if it persists, check that the backend and Docker services (Neo4j, Weaviate, Redis) are running."
                )
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
