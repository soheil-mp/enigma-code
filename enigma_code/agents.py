

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





