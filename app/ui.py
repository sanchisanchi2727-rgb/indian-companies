
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/ask"

st.set_page_config(
    page_title="Indian Companies RAG",
    page_icon="🏢"
)

st.title("Indian Companies Intelligence")
st.caption("Ask questions about Indian companies using RAG and hybrid search.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask about an Indian company...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching company information..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=180
                )
                response.raise_for_status()
                result = response.json()

                answer = result.get("answer", "No answer returned.")
                st.markdown(answer)

                sources = result.get("sources", [])
                if sources:
                    with st.expander("View sources"):
                        for source in sources:
                            st.write(
                                f"**{source.get('company', 'Unknown')}**"
                            )
                            st.caption(
                                source.get('source', 'Unknown source')
                            )
                            st.write(source.get("text", ""))

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except requests.RequestException as error:
                st.error(f"Could not connect to the RAG API: {error}")
