import os
import requests
import streamlit as st


APPLICATION_SERVICE_URL = os.getenv(
    "APPLICATION_SERVICE_URL",
    "http://127.0.0.1:9000"
)


st.set_page_config(
    page_title="Government Scheme Assistant - Exercise 4",
    page_icon="🎓",
    layout="wide",
)


def get_schemes():
    response = requests.get(
        f"{APPLICATION_SERVICE_URL}/api/schemes",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["schemes"]


def check_eligibility(profile):
    response = requests.post(
        f"{APPLICATION_SERVICE_URL}/api/eligibility/check",
        json=profile,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def ask_llm(prompt):
    response = requests.post(
        f"{APPLICATION_SERVICE_URL}/api/ask",
        json={"prompt": prompt},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def ask_rag(scheme_id, question, top_k=5):
    response = requests.post(
        f"{APPLICATION_SERVICE_URL}/api/query",
        json={
            "scheme_id": scheme_id,
            "question": question,
            "top_k": top_k,
        },
        timeout=240,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def load_schemes():
    return get_schemes()


st.title("🎓 Government Scheme Eligibility Assistant")

st.caption(
    "Exercise 4 — Microservice-based architecture with API orchestration"
)


try:
    schemes = load_schemes()
except Exception as exc:
    st.error(
        f"Unable to connect to the Application Service: {exc}"
    )
    st.stop()


scheme_lookup = {
    scheme["scheme_id"]: scheme
    for scheme in schemes
}


# -------------------------------------------------------------------
# Eligibility Profile
# -------------------------------------------------------------------

st.header("1. Check Eligibility")

left, right = st.columns(2)

with left:
    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        value=20,
    )

    education_level = st.selectbox(
        "Education Level",
        [
            "School education",
            "Diploma",
            "Undergraduate",
            "Graduate",
            "Postgraduate",
            "Research/PhD",
        ],
    )

    course_type = st.text_input(
        "Course Type",
        value="Technical Diploma",
    )

    study_year = st.number_input(
        "Study Year",
        min_value=1,
        max_value=10,
        value=1,
    )

    gender = st.selectbox(
        "Gender",
        ["Female", "Male"],
    )

    category = st.selectbox(
        "Category",
        ["General", "OBC", "SC", "ST"],
    )

with right:
    annual_income = st.number_input(
        "Annual Family Income (₹)",
        min_value=0.0,
        value=500000.0,
        step=10000.0,
    )

    geography = st.text_input(
        "State / Geography",
        value="Punjab",
    )

    institution_type = st.text_input(
        "Institution Type",
        value="AICTE approved",
    )

    disability = st.selectbox(
        "Disability",
        ["Not specified", "Yes", "No"],
    )

    academic_percentage = st.number_input(
        "Academic Percentage",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
    )

    academic_percentile = st.number_input(
        "Academic Percentile",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
    )


if st.button(
    "Check Eligibility",
    type="primary",
    use_container_width=True,
):
    profile = {
        "age": age,
        "education_level": education_level,
        "course_type": course_type,
        "study_year": study_year,
        "gender": gender,
        "category": category,
        "annual_income": annual_income,
        "geography": geography,
        "institution_type": institution_type,
        "disability": (
            None
            if disability == "Not specified"
            else disability
        ),
        "academic_percentage": (
            academic_percentage
            if academic_percentage > 0
            else None
        ),
        "academic_percentile": (
            academic_percentile
            if academic_percentile > 0
            else None
        ),
        "special_conditions": None,
    }

    try:
        result = check_eligibility(profile)

        st.session_state["eligibility_result"] = result

    except Exception as exc:
        st.error(
            f"Eligibility Service request failed: {exc}"
        )


# -------------------------------------------------------------------
# Eligibility Results
# -------------------------------------------------------------------

if "eligibility_result" in st.session_state:
    result = st.session_state["eligibility_result"]

    st.subheader("Eligibility Results")

    results = result.get("results", [])

    for match in results[:3]:
        score = match.get("score", 0)

        st.markdown(
            f"### {match.get('scheme_name', match.get('scheme_id'))}"
        )

        st.progress(
            min(max(float(score), 0.0), 1.0)
        )

        st.write(
            f"**Match:** {score * 100:.0f}%"
        )

        st.write(
            f"**Status:** {match.get('status', '').replace('_', ' ').title()}"
        )

        matched = match.get("matched_conditions", [])
        failed = match.get("failed_conditions", [])
        unverified = match.get("unverified_conditions", [])

        if matched:
            with st.expander("Matched conditions"):
                for item in matched:
                    st.write(f"✓ {item}")

        if failed:
            with st.expander("Failed conditions"):
                for item in failed:
                    st.write(f"✗ {item}")

        if unverified:
            with st.expander("Conditions requiring verification"):
                for item in unverified:
                    st.write(f"• {item}")

        st.divider()


# -------------------------------------------------------------------
# Scheme Questions
# -------------------------------------------------------------------

st.header("2. Ask About a Scheme")

selected_scheme_id = st.selectbox(
    "Select Scheme",
    list(scheme_lookup.keys()),
    format_func=lambda scheme_id: scheme_lookup[
        scheme_id
    ]["scheme_name"],
)

question = st.text_area(
    "Your Question",
    placeholder="For example: What are the benefits?",
)


top_k = st.slider(
    "Number of retrieved sources",
    min_value=1,
    max_value=10,
    value=5,
)


col1, col2 = st.columns(2)

with col1:
    ask_llm_button = st.button(
        "Ask LLM",
        use_container_width=True,
    )

with col2:
    ask_rag_button = st.button(
        "Ask RAG",
        type="primary",
        use_container_width=True,
    )


if ask_llm_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            result = ask_llm(question)

            st.subheader("LLM Answer")
            st.write(result.get("response", ""))

        except Exception as exc:
            st.error(
                f"LLM Service request failed: {exc}"
            )


if ask_rag_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            result = ask_rag(
                selected_scheme_id,
                question,
                top_k,
            )

            st.subheader("RAG Answer")
            st.write(result.get("answer", ""))

            sources = result.get("sources", [])

            if sources:
                st.subheader("Retrieved Sources")

                for index, source in enumerate(
                    sources,
                    start=1,
                ):
                    chunk_id = source.get(
                        "chunk_id",
                        "Unknown",
                    )

                    section = source.get(
                        "section",
                        "Unknown",
                    )

                    source_type = source.get(
                        "source",
                        "Unknown",
                    )

                    distance = source.get(
                        "distance",
                        None,
                    )

                    source_text = (
                        f"**{index}.** "
                        f"{source_type} | "
                        f"{section} | "
                        f"{chunk_id}"
                    )

                    if distance is not None:
                        source_text += (
                            f" | distance: {distance:.3f}"
                        )

                    st.markdown(source_text)

        except Exception as exc:
            st.error(
                f"RAG Service request failed: {exc}"
            )
