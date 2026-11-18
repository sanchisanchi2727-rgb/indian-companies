
import streamlit as st
import requests

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Indian Companies AI Assistant",
    page_icon="🏢",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/api/ask"


# --------------------------------
# CUSTOM CSS
# --------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0b1120;
    color: white;
}

.main-title {
    font-size: 36px;
    font-weight: bold;
    color: #60a5fa;
}

.subtitle {
    color: #94a3b8;
    font-size: 16px;
}

.answer-box {
    background-color: #17243b;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# HEADER
# --------------------------------

st.markdown(
    '<div class="main-title">🏢 Indian Companies Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered company research using Retrieval-Augmented Generation'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("🏢 Company Intelligence")

st.sidebar.write(
    "Ask questions about Indian companies."
)

st.sidebar.divider()

st.sidebar.markdown("### Example Questions")

examples = [
    "Tell me about TCS",
    "Explain Infosys business",
    "Compare TCS and Infosys",
    "Tell me about Reliance Industries",
    "What services does Wipro provide?"
]

for example in examples:

    if st.sidebar.button(example, use_container_width=True):
        st.session_state["question"] = example


if st.sidebar.button("Clear Conversation"):
    st.session_state["history"] = []
    st.rerun()


# --------------------------------
# CHAT HISTORY
# --------------------------------

if "history" not in st.session_state:
    st.session_state["history"] = []

if "question" not in st.session_state:
    st.session_state["question"] = ""


# --------------------------------
# DISPLAY PREVIOUS QUESTIONS
# --------------------------------

for chat in st.session_state["history"]:

    with st.chat_message("user"):
        st.write(chat["question"])

    with st.chat_message("assistant"):
        st.markdown(chat["answer"])

        if chat.get("sources"):

            with st.expander("View Sources"):
                for source in chat["sources"]:
                    st.write(source)


# --------------------------------
# QUESTION INPUT
# --------------------------------

st.subheader("💬 Ask Your Question")

question = st.text_input(
    "Enter your question",
    key="question",
    placeholder="Example: Tell me about TCS company..."
)

# --------------------------------
# GET ANSWER
# --------------------------------

if st.button("🔍 Get Answer", type="primary"):

    if not question.strip():

        st.warning("Please enter a question.")

    elif len(question.strip()) < 3:

        st.warning("Please enter at least 3 characters.")

    else:

        try:

            with st.spinner(
                "Searching company information and generating answer..."
            ):

                response = requests.post(
                    API_URL,
                    json={"question": question.strip()},
                    timeout=180
                )

            if response.ok:

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer received from AI."
                )

                sources = result.get("sources", [])

                st.session_state["history"].append({

                    "question": question.strip(),
                    "answer": answer,
                    "sources": sources

                })

                st.rerun()

            else:

                st.error(
                    f"API Error: {response.status_code}"
                )

                st.code(response.text)

        except requests.exceptions.ConnectionError:

            st.error(
                "FastAPI is not running. "
                "Please start your backend on port 8000."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Request timed out. Please try again."
            )

        except requests.exceptions.RequestException as error:

            st.error(f"Request failed: {error}")


# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption(
    "Indian Companies Intelligence | "
    "Powered by Python, Streamlit, FastAPI and RAG"
)
