import os
import utils
import streamlit as st
from streaming import StreamHandler

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import RecursiveCharacterTextSplitter


st.header("Chatta con il Wedding Chatbot!")
st.write("""Il chatbot risponderà alle tue domande riguardo il matrimonio!""")
st.write(
    """Ti chiediamo di non fare troppe domande, in quanto il numero di interazioni è limitato! 
         Grazie!"""
)


class CustomDataChatbot:

    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_model = "gpt-3.5-turbo"
        utils.insert_password()

    def save_file(self, file):
        folder = "tmp"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_path = f"./{folder}/{file.name}"
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        return file_path

    @st.spinner(
        "Un giorno, il marinaio spiegò le vele al vento, ma il vento non capì..."
    )
    def setup_qa_chain(self):
        # Load documents
        docs = []

        file_path = "Wedding Chatbot Info.pdf"
        loader = PyPDFLoader(file_path)
        docs.extend(loader.load())

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Create embeddings and store in vectordb
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)

        # Define retriever
        retriever = vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4}
        )

        # Setup memory for contextual conversation
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm, retriever=retriever, memory=memory, verbose=True
        )
        return qa_chain

    @utils.enable_chat_history
    def main(self):

        user_query = st.chat_input(placeholder="Chiedimi qualcosa!")

        if user_query:
            qa_chain = self.setup_qa_chain()

            utils.display_msg(user_query, "user")

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                response = qa_chain.run(user_query, callbacks=[st_cb])
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()
