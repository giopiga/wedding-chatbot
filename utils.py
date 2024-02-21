import os
import streamlit as st
from config.read_settings import read_key, read_pwd

content_firts_message = "Benvenuto! Sono il wedding chatbot. Come posso aiutarti?"


def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):

        # to clear chat history after swtching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass

        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": content_firts_message}
            ]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute


def display_msg(msg, author):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)


def configure_openai_api_key():
    # in prod and local:
    if "openai_api_key" in st.secrets:
        # read from secrets toml or from streamlit secrets
        openai_api_key = st.secrets["openai_api_key"]

    if openai_api_key:
        st.session_state["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key
    else:
        st.error("Please add your OpenAI API key to continue.")
        st.info(
            "Obtain your key from this link: https://platform.openai.com/account/api-keys"
        )
        st.stop()
    return


question_main = "Per poter accedere, ti chiediamo di rispondere alla domanda!"
question = "Come mi chiamo?"
question_asked = "Per poter accedere, scrivi come mi chiamo!"


def check_password():
    """Returns `True` if the user had the correct password."""
    if "pwd" in st.secrets:
        pwd = st.secrets["pwd"]

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # if hmac.compare_digest(st.session_state["password"], pwd):
        if st.session_state["password"].lower() == pwd.lower():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        question_asked, type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password errata! Riprova!")
    return False


def insert_password():
    if not check_password():
        st.stop()
