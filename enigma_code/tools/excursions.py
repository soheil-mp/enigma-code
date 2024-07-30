
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join('./../..')))

# Import all modules
from imports import *

def run_query(query: str, params: tuple = (), fetch_all: bool = True) -> Union[list[dict], None]:
    """
    Run an SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        params (tuple): The parameters to use with the SQL query.
        fetch_all (bool): Whether to fetch all results or just execute the query.

    Returns:
        Union[list[dict], None]: The results of the query as a list of dictionaries, or None for non-SELECT queries.
    """
    db = "travel2.sqlite"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetch_all:
        results = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in results]
    else:
        results = None
        conn.commit()
    
    cursor.close()
    conn.close()
    return results

@tool
def search_trip_recommendations(
    location: Optional[str] = None,
    name: Optional[str] = None,
    keywords: Optional[str] = None,
) -> list[dict]:
    """
    Search for trip recommendations based on location, name, and keywords.

    Args:
        location (Optional[str]): The location of the trip recommendation. Defaults to None.
        name (Optional[str]): The name of the trip recommendation. Defaults to None.
        keywords (Optional[str]): The keywords associated with the trip recommendation. Defaults to None.

    Returns:
        list[dict]: A list of trip recommendation dictionaries matching the search criteria.
    """
    query = "SELECT * FROM trip_recommendations WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if keywords:
        keyword_list = keywords.split(",")
        keyword_conditions = " OR ".join(["keywords LIKE ?" for _ in keyword_list])
        query += f" AND ({keyword_conditions})"
        params.extend([f"%{keyword.strip()}%" for keyword in keyword_list])

    results = run_query(query, tuple(params))
    return json.dumps(results, indent=2)

@tool
def book_excursion(recommendation_id: int) -> str:
    """
    Book a excursion by its recommendation ID.

    Args:
        recommendation_id (int): The ID of the trip recommendation to book.

    Returns:
        str: A message indicating whether the trip recommendation was successfully booked or not.
    """
    query = "UPDATE trip_recommendations SET booked = 1 WHERE id = ?"
    run_query(query, (recommendation_id,), fetch_all=False)
    return f"Trip recommendation {recommendation_id} successfully booked."

@tool
def update_excursion(recommendation_id: int, details: str) -> str:
    """
    Update a trip recommendation's details by its ID.

    Args:
        recommendation_id (int): The ID of the trip recommendation to update.
        details (str): The new details of the trip recommendation.

    Returns:
        str: A message indicating whether the trip recommendation was successfully updated or not.
    """
    query = "UPDATE trip_recommendations SET details = ? WHERE id = ?"
    run_query(query, (details, recommendation_id), fetch_all=False)
    return f"Trip recommendation {recommendation_id} successfully updated."

@tool
def cancel_excursion(recommendation_id: int) -> str:
    """
    Cancel a trip recommendation by its ID.

    Args:
        recommendation_id (int): The ID of the trip recommendation to cancel.

    Returns:
        str: A message indicating whether the trip recommendation was successfully cancelled or not.
    """
    query = "UPDATE trip_recommendations SET booked = 0 WHERE id = ?"
    run_query(query, (recommendation_id,), fetch_all=False)
    return f"Trip recommendation {recommendation_id} successfully cancelled."