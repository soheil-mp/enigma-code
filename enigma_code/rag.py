

# Import the libraries
import langchain

# TODO: Add docs and create seperate module for RAG
# TODO: Maybe optimize this
class RAG:
    
    def __init__(self, llm, vectorstore):
        self.llm = llm
        self.vectorstore = vectorstore
        self.setup_chat_chain()
        self.chat_history = []        

    def setup_chat_chain(self):
        self.chat_chain = langchain.chains.ConversationalRetrievalChain.from_llm(
            self.llm, 
            self.vectorstore.as_retriever(), 
            return_source_documents=True
        )

    def chat_query(self, question):
        result = self.chat_chain({"question": question, "chat_history": self.chat_history})
        self.chat_history.append((question, result["answer"]))
        return result['answer']