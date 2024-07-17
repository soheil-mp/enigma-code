
# Import the libraries
from langchain.embeddings import *
from langchain.vectorstores import *

# Class for handling vector stores
class VectorStoreManager:

    # Dictionary of embedding models
    EMBEDDING_MODELS = {
        "openai": OpenAIEmbeddings,
        "ollama": lambda: OllamaEmbeddings(model="llama3"),
        "huggingface": lambda: HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        "cohere": lambda: CohereEmbeddings(user_agent="langchain"),
    }

    # Dictionary of vector stores
    VECTOR_STORES = {
        "pinecone": Pinecone,
        "faiss": FAISS,
        "annoy": Annoy,
        "chroma": Chroma,
    }

    # Constructor function
    def __init__(self, vectorstore_name, embedding_model, index_name=None, vectorstore_path=None):
        """
        Initialize the VectorStoreHandler class.

        Args:
        vectorstore_name (str): The name of the vector store.
        embedding_model (str): The name of the embedding model.
        index_name (str): The name of the index (for Pinecone).
        vectorstore_path (str): The path to the vector store (for FAISS and Annoy).

        Returns:
        None
        """
        self.vectorstore_name = vectorstore_name.lower()
        self.embedding_model = embedding_model.lower()
        self.index_name = index_name
        self.vectorstore_path = vectorstore_path
        self.embedding = self._load_embedding_model()
        self.vectorstore = None

    # Function to load the embedding model
    def _load_embedding_model(self):
        """
        Load the embedding model.

        Returns:
        Embeddings: The embedding model
        """

        # Return the embedding model
        return self.EMBEDDING_MODELS[self.embedding_model]()
    
    
    # Function to load an existing vector store
    def load_vectorstore(self):
        """
        Load an existing vector store

        Returns:
        VectorStore: The vector store object.

        """

        # Get the VectorStore class
        VectorStore = self.VECTOR_STORES[self.vectorstore_name]
        
        # Pinecone
        if self.vectorstore_name == "pinecone":
            self.vectorstore = VectorStore.from_existing_index(index_name=self.index_name, embedding=self.embedding)
        
        # FAISS
        elif self.vectorstore_name == "faiss":
            self.vectorstore = VectorStore.load_local(folder_path=self.vectorstore_path, embeddings=self.embedding, allow_dangerous_deserialization=True)
        
        # Annoy
        elif self.vectorstore_name == "annoy":
            self.vectorstore = VectorStore.load_local(folder_path=self.vectorstore_path, embeddings=self.embedding)
        
        # Chroma
        elif self.vectorstore_name == "chroma":
            self.vectorstore = VectorStore(collection_name="your_collection_name", embedding_function=self.embedding, persist_directory="./chroma_db")
        
        return self.vectorstore
    

