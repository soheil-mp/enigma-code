
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join('./../..')))

# Import all modules
from imports import *

# Function to lookup a policy based on a query
@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events.
    """
    # Query the retriever for the top 2 most similar documents and join their content
    return "\n\n".join([doc["page_content"] for doc in retriever.query(query, k=2)])