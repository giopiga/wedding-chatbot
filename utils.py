import os
import random
import streamlit as st
from config.read_settings import read_key, read_pwd

content_firts_message = "Benvenuto! Sono il wedding chatbot. Come posso aiutarti?"
#decorator
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
            st.session_state["messages"] = [{"role": "assistant", "content": content_firts_message}]
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
    if 'openai_api_key' in st.secrets:
        # read from secrets toml or from streamlit secrets
        openai_api_key = st.secrets['openai_api_key']

    if openai_api_key:
        st.session_state['OPENAI_API_KEY'] = openai_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.stop()
    return

question_main = "Per poter accedere, ti chiediamo di rispondere alla domanda!"
question = "Come mi chiamo?"
def insert_password():

    # in prod and local
    if 'pwd' in st.secrets:
        pwd = st.secrets['pwd']

    if 'ASK_PWD' not in st.session_state or st.session_state['ASK_PWD']==True:
        password_inserted = st.sidebar.text_input(
            label=question,
            type="password",
            value=st.session_state['PWD'] if 'PWD' in st.session_state else '',
            placeholder="nome"
            )
        
        if password_inserted.lower() == pwd.lower():
            st.session_state['PWD'] = password_inserted
            st.sidebar.success('Risposta corretta! Puoi iniziare a chattare!')
            # when the correct pwd is inserted, we remove the question
            st.session_state['ASK_PWD'] = False
            return True
        
        elif password_inserted.lower() is None or password_inserted.lower()=='':
            # to handle the case that the password is not been written yet
            st.error(question_main)
            st.stop()
        
        else:
            st.error(question_main)
            st.sidebar.error("Risposta errata")
            st.stop()
 
    else:
        pass


