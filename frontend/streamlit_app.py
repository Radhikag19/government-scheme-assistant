import requests
import streamlit as st


FASTAPI_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Government Scheme Eligibility Assistant",
    page_icon="🏛️",
    layout="wide"
)


# =========================================================
# BACKEND FUNCTIONS
# =========================================================

@st.cache_data
def load_schemes():

    response = requests.get(
        f"{FASTAPI_URL}/schemes",
        timeout=30
    )

    response.raise_for_status()

    return response.json()["schemes"]


@st.cache_data
def load_profile_options():

    response = requests.get(
        f"{FASTAPI_URL}/profile/options",
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def match_schemes(profile):

    response = requests.post(
        f"{FASTAPI_URL}/schemes/match",
        json={
            "profile": profile
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def ask_llm(question):

    response = requests.post(
        f"{FASTAPI_URL}/ask",
        json={
            "question": question
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()


def ask_rag(
    scheme_id,
    question,
    top_k=5
):

    response = requests.post(
        f"{FASTAPI_URL}/chat",
        json={
            "scheme_id": scheme_id,
            "question": question,
            "top_k": top_k
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# LOAD BACKEND DATA
# =========================================================

try:

    schemes = load_schemes()

    profile_options = load_profile_options()

except requests.RequestException as error:

    st.error(
        "Could not connect to the FastAPI backend.\n\n"
        f"Error: {error}"
    )

    st.stop()


# =========================================================
# PAGE TITLE
# =========================================================

st.title(
    "🏛️ Government Scheme Eligibility Assistant"
)

st.caption(
    "Check your eligibility or directly ask questions "
    "about any government scheme."
)


# =========================================================
# TWO-COLUMN APPLICATION
# =========================================================

left_column, right_column = st.columns(
    2,
    gap="large"
)


# =========================================================
# LEFT COLUMN
# ELIGIBILITY CHECK
# =========================================================

with left_column:

    st.header("1. Check Eligibility")

    st.write(
        "Enter your details to find the government "
        "schemes that best match your profile."
    )

    # -----------------------------------------------------
    # Profile fields
    # -----------------------------------------------------

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=100,
        value=20
    )

    education_options = [
        "Not specified"
    ] + profile_options.get(
        "education_level",
        []
    )

    education_level = st.selectbox(
        "Education Level",
        education_options
    )

    course_options = [
        "Not specified"
    ] + profile_options.get(
        "course_type",
        []
    )

    course_type = st.selectbox(
        "Course Type",
        course_options
    )

    study_year = st.selectbox(
        "Study Year",
        [
            "Not specified",
            "1",
            "2",
            "3",
            "4",
            "5"
        ]
    )

    gender_options = [
        "Not specified"
    ] + profile_options.get(
        "gender",
        []
    )

    gender = st.selectbox(
        "Gender",
        gender_options
    )

    category_options = [
        "Not specified"
    ] + profile_options.get(
        "category",
        []
    )

    category = st.selectbox(
        "Category",
        category_options
    )

    disability = st.selectbox(
        "Disability",
        [
            "Not specified",
            "Yes",
            "No"
        ]
    )

    annual_income = st.number_input(
        "Annual Family Income (₹)",
        min_value=0.0,
        value=500000.0,
        step=10000.0
    )

    indian_locations = [
        "Not specified",
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Andaman and Nicobar Islands",
        "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi",
        "Jammu and Kashmir",
        "Ladakh",
        "Lakshadweep",
        "Puducherry"
    ]

    geography = st.selectbox(
        "Geography",
        indian_locations
    )

    institution_options = [
        "Not specified"
    ] + profile_options.get(
        "institution_type",
        []
    )

    institution_type = st.selectbox(
        "Institution Type",
        institution_options
    )

    academic_percentage = st.number_input(
        "Academic Percentage",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1
    )

    academic_percentile = st.number_input(
        "Academic Percentile",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1
    )

    # -----------------------------------------------------
    # Build profile
    # -----------------------------------------------------

    profile = {

        "age": (
            age
            if age > 0
            else None
        ),

        "education_level": (
            None
            if education_level == "Not specified"
            else education_level
        ),

        "course_type": (
            None
            if course_type == "Not specified"
            else course_type
        ),

        "study_year": (
            None
            if study_year == "Not specified"
            else int(study_year)
        ),

        "gender": (
            None
            if gender == "Not specified"
            else gender
        ),

        "category": (
            None
            if category == "Not specified"
            else category
        ),

        "disability": (
            None
            if disability == "Not specified"
            else disability == "Yes"
        ),

        "annual_income": (
            annual_income
            if annual_income > 0
            else None
        ),

        "geography": (
            None
            if geography == "Not specified"
            else geography
        ),

        "institution_type": (
            None
            if institution_type == "Not specified"
            else institution_type
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

        "special_conditions": None
    }

    # -----------------------------------------------------
    # Check eligibility
    # -----------------------------------------------------

    if st.button(
        "Check Eligibility",
        type="primary",
        use_container_width=True
    ):

        try:

            result = match_schemes(profile)

            st.session_state[
                "eligibility_results"
            ] = result["results"]

        except requests.RequestException as error:

            st.error(
                f"Eligibility check failed: {error}"
            )

    # -----------------------------------------------------
    # Display top 3 schemes
    # -----------------------------------------------------

    if "eligibility_results" in st.session_state:

        results = st.session_state[
            "eligibility_results"
        ]

        st.subheader(
            "Top 3 Matching Schemes"
        )

        top_results = results[:3]

        if not top_results:

            st.info(
                "No matching schemes were found."
            )

        else:

            for index, result in enumerate(
                top_results,
                start=1
            ):

                scheme_name = result.get(
                    "scheme_name",
                    result.get("scheme_id")
                )

                score = result.get(
                    "score",
                    0
                )

                match_percentage = round(
                    score * 100
                )

                st.markdown(
                    f"**{index}. {scheme_name}**"
                )

                st.write(
                    f"Match Percentage: "
                    f"**{match_percentage}%**"
                )

                st.divider()

        # -------------------------------------------------
        # RAG hand-off message
        # -------------------------------------------------

        st.info(
            "💡 **Want more information about a specific "
            "scheme?** Use **Ask RAG** on the right to "
            "ask detailed questions about any government "
            "scheme."
        )


# =========================================================
# RIGHT COLUMN
# SCHEME-SPECIFIC LLM vs RAG
# =========================================================

with right_column:

    st.header("2. Ask About a Scheme")

    st.write(
        "Select any scheme and compare a direct LLM answer "
        "with a knowledge-base-grounded RAG answer."
    )

    # -----------------------------------------------------
    # Scheme selection
    # -----------------------------------------------------

    scheme_map = {
        scheme["scheme_name"]: scheme["scheme_id"]
        for scheme in schemes
    }

    selected_scheme_name = st.selectbox(
        "Select Scheme",
        list(scheme_map.keys())
    )

    selected_scheme_id = scheme_map[
        selected_scheme_name
    ]

    # -----------------------------------------------------
    # Question
    # -----------------------------------------------------

    question = st.text_input(
        "Your Question",
        placeholder=(
            "Example: What is the annual income limit?"
        )
    )

    st.caption(
        "The same question can be tested with and "
        "without retrieval."
    )

    # -----------------------------------------------------
    # Buttons
    # -----------------------------------------------------

    llm_column, rag_column = st.columns(2)

    # -----------------------------------------------------
    # Normal LLM
    # -----------------------------------------------------

    with llm_column:

        ask_llm_button = st.button(
            "Ask LLM",
            use_container_width=True
        )

    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    with rag_column:

        ask_rag_button = st.button(
            "Ask RAG",
            type="primary",
            use_container_width=True
        )

    # -----------------------------------------------------
    # LLM response
    # -----------------------------------------------------

    if ask_llm_button:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Generating direct LLM answer..."
            ):

                try:

                    result = ask_llm(
                        question
                    )

                    st.subheader(
                        "LLM Answer — No Retrieval"
                    )

                    st.write(
                        result["answer"]
                    )

                except requests.RequestException as error:

                    st.error(
                        f"LLM request failed: {error}"
                    )

    # -----------------------------------------------------
    # RAG response
    # -----------------------------------------------------

    if ask_rag_button:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Retrieving scheme information "
                "and generating grounded answer..."
            ):

                try:

                    result = ask_rag(
                        scheme_id=selected_scheme_id,
                        question=question,
                        top_k=5
                    )

                    st.subheader(
                        "Grounded RAG Answer"
                    )

                    st.write(
                        result["answer"]
                    )

                    # -------------------------------------
                    # Retrieved sources
                    # -------------------------------------

                    sources = result.get(
                        "sources",
                        []
                    )

                    if sources:

                        st.subheader(
                            "Retrieved Knowledge"
                        )

                        st.caption(
                            "The answer above was generated "
                            "using these retrieved chunks "
                            "from the selected scheme."
                        )

                        for index, source in enumerate(
                            sources,
                            start=1
                        ):

                            st.write(
                                f"**Source {index}**"
                            )

                            st.write(
                                f"- Scheme: "
                                f"{source.get('scheme_id')}"
                            )

                            st.write(
                                f"- Section: "
                                f"{source.get('section')}"
                            )

                            st.write(
                                f"- Source Type: "
                                f"{source.get('source')}"
                            )

                            st.write(
                                f"- Chunk ID: "
                                f"{source.get('chunk_id')}"
                            )

                            st.divider()

                except requests.RequestException as error:

                    st.error(
                        f"RAG request failed: {error}"
                    )
