

# Import the libraries
import json
import os
from groq import Groq

# Load .env file
from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')

# Base agent class
class BaseAgent:

    # Constructor function
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.known_functions = {}
        self.functions = []

    # Function for adding functions to bot
    def add_function(self, func, description, parameters):
        """Add a function to the bot's known functions and function descriptions."""
        func_name = func.__name__
        self.known_functions[func_name] = func
        self.functions.append({
            "name": func_name,
            "description": description,
            "parameters": parameters
        })

    # Function for sending queries to the agent
    def query(self, user_input, model="llama3-8b-8192", max_tokens=4096, temperature=0):
        """Send a query to the bot and get a response."""
        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            functions=self.functions,
            max_tokens=max_tokens,
            temperature=temperature
        )

        function_call = response.choices[0].message.function_call
        if function_call:
            args = json.loads(function_call.arguments)
            function_response = self.known_functions[function_call.name](**args)

            messages.append(
                {
                    "role": "function",
                    "name": function_call.name,
                    "content": function_response,
                }
            )

            final_response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )

            return final_response.choices[0].message.content
        else:
            return response.choices[0].message.content












import json
import os
import numpy as np
from groq import Groq
from dotenv import load_dotenv
import faiss
from sentence_transformers import SentenceTransformer

load_dotenv(dotenv_path='../.env')

class BaseAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.known_functions = {}
        self.functions = []
        
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.texts = []

    def add_function(self, func, description, parameters):
        func_name = func.__name__
        self.known_functions[func_name] = func
        self.functions.append({
            "name": func_name,
            "description": description,
            "parameters": parameters
        })

    def add_to_vector_store(self, texts):
        embeddings = self.embedding_model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.texts.extend(texts)

    def retrieve_documents(self, query, k=5):
        query_embedding = self.embedding_model.encode([query])
        _, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        return [self.texts[i] for i in indices[0]]

    def prepare_input(self, user_input):
        retrieved_docs = self.retrieve_documents(user_input)
        retrieved_content = " ".join(retrieved_docs)
        return f"User query: {user_input}\n\nRelevant information: {retrieved_content}"

    def get_initial_response(self, combined_input, model, max_tokens, temperature):
        messages = [{"role": "user", "content": combined_input}]
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            functions=self.functions,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def handle_function_call(self, function_call, model, temperature):
        args = json.loads(function_call.arguments)
        function_response = self.known_functions[function_call.name](**args)
        messages = [
            {"role": "user", "content": "Function call result"},
            {"role": "function", "name": function_call.name, "content": function_response}
        ]
        final_response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return final_response.choices[0].message.content

    def query(self, user_input, model="llama3-8b-8192", max_tokens=4096, temperature=0):
        combined_input = self.prepare_input(user_input)
        response = self.get_initial_response(combined_input, model, max_tokens, temperature)

        function_call = response.choices[0].message.function_call
        if function_call:
            return self.handle_function_call(function_call, model, temperature)
        else:
            return response.choices[0].message.content