import requests
import streamlit as st


FASTAPI_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Government Scheme Eligibility Assistant",
    page_icon="🎓",
    layout="centered"
)


st.title("🎓 AI Government Scheme Eligibility Assistant")

st.write(
    "Ask a question about government scholarship eligibility "
    "and receive a response from the LLM."
)


question = st.text_area(
    "Enter your question:",
    placeholder=(
        "For example: I am a 22-year-old undergraduate student "
        "from Maharashtra. What information is important when "
        "checking scholarship eligibility?"
    ),
    height=120
)


if st.button("Ask Gemma", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")
    else:

        with st.spinner("Getting response from Gemma..."):

            try:
                response = requests.post(
                    f"{FASTAPI_URL}/ask",
                    json={"question": question},
                    timeout=120
                )

                response.raise_for_status()

                data = response.json()

                st.subheader("Response")

                st.write(data["answer"])

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the FastAPI application. "
                    "Make sure the FastAPI server is running."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The request timed out while waiting for the LLM."
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
