
# Import the libraries
import langchain
import langchain_community
from langchain.document_loaders import *
from langchain.text_splitter import *
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy import text
from langchain.schema import Document


# Class for handling data
class DataHandler:

    # Constructor function 
    def __init__(self):
        pass

    # Function for loading dataset from various sources
    def load_dataset(self, file_path):
        """
        Load the dataset based on the extension of the file.
        """
        
        # Get the extension of the file
        extension = file_path.split(".")[-1]

        # PDF file
        if extension == "pdf":
            loader = langchain.document_loaders.PDFLoader(file_path)                             

        # Word file
        elif extension == "docx":
            loader = langchain.document_loaders.DocxLoader(file_path)                          

        # Text file
        elif extension == "txt":
            loader = langchain.document_loaders.TextLoader(file_path)                           

        # CSV file
        elif extension == "csv":
            loader = langchain.data_loaders.CSVLoader(file_path)                               

        # JSON file
        elif extension == "json":
            loader = langchain.data_loaders.JSONLoader(file_path)                               

        # XML file
        elif extension == "xml":
            loader = langchain.data_loaders.XMLLoader(file_path)                               

        # Database
        elif extension == "db":
            loader = langchain.data_loaders.DatabaseLoader(file_path)                           

        # Else
        else:
            raise Exception("Unsupported file format")                                         
        
        # Load the dataset
        dataset = loader.load()                                                                

        return dataset                                                                         

    # Function for cleaning the dataset
    def clean_dataset(self, dataset):
        """
        Clean the dataset by removing the unwanted characters.
        """
        pass

    # Function for preprocessing the dataset
    def preprocess_dataset(self, dataset):
        """
        Preprocess the dataset by tokenizing the text.
        """
        pass

    # Function for chunking the dataset
    def chunk_dataset(self, documents, chunk_type, chunk_size, chunk_overlap):
        """
        This function chunks the dataset.

        Args:
        dataset (str): The dataset to be chunked.
        chunk_type (str): The type of chunking to be performed (e.g., char, word, sentence).

        """
        
        # Character chunking
        if chunk_type == "char":
            splitter = langchain.text_splitter.CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)          
            chunks = splitter.split_documents(documents)  

        # Token chunking
        elif chunk_type == "token":
            splitter = langchain.text_splitter.TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = splitter.split_documents(documents)  

        # Sentence chunking
        elif chunk_type == "sentence":
            splitter = langchain.text_splitter.SentenceTransformersTokenTextSplitter()
            chunks = splitter.split_documents(documents)  

        # HTML-Headers chunking
        elif chunk_type == "html-headers":
            splitter = langchain.text_splitter.HTMLHeaderTextSplitter(headers_to_split_on=["h1", "h2", "h3", "h4", "h5", "h6"])
            chunks = [splitter.split_text(doc.page_content) for doc in documents]

        # Markdown-Headers chunking
        elif chunk_type == "markdown-headers":
            splitter = langchain.text_splitter.MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4"), ("#####", "h5"), ("######", "h6")])
            chunks = [splitter.split_text(doc.page_content) for doc in documents]

        # Newline chunking
        elif chunk_type == "newline":
            chunks = [i.page_content.split("\n") for i in documents]
            chunks = [Document(page_content=chunk) for chunk in chunks[0]]

        # Else
        else:
            raise Exception("Unsupported chunk type")                                                                                   
        
        return chunks                                                                                                                                                                                                    
   

# Class for loading datasets from various databases on cloud
class DatabaseQueryTool:
    """
    Class for loading datasets from various databases using SQLAlchemy.
    Supports MySQL, PostgreSQL, and SQLite databases.
    """
    
    # Supported database connection templates
    SUPPORTED_DATABASES = {
        "mysql": "mysql+mysqlconnector://{username}:{password}@{host}",
        "postgresql": "postgresql+psycopg2://{username}:{password}@{host}",
        "sqlite": "sqlite:///{host}"
    }

    def __init__(self, database_type, username, password, host):
        """
        Initialize the DatabaseLoader with database connection details.

        :param database_type: Type of the database (e.g., 'mysql', 'postgresql', 'sqlite')
        :param username: Username for the database
        :param password: Password for the database
        :param host: Host address of the database
        """
        self.database_type = database_type.lower()
        self.username = username
        self.password = password
        self.host = host
        self.engine = self._create_engine()

    def _create_engine(self):
        """
        Create the SQLAlchemy engine based on the database type.

        :return: SQLAlchemy engine
        :raises ValueError: If the database type is unsupported
        """
        if self.database_type not in self.SUPPORTED_DATABASES:
            raise ValueError(f"Unsupported database type: {self.database_type}")
        
        # Format the connection string using the provided details
        connection_string = self.SUPPORTED_DATABASES[self.database_type].format(
            username=self.username,
            password=self.password,
            host=self.host
        )
        return create_engine(connection_string)

    def run_sql_query(self, query):
        """
        Run the SQL query and return results.

        :param query: SQL query to be executed
        :return: List of results from the query
        """
        # Open a connection to the database and execute the query
        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            return result.fetchall()