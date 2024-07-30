
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join('./../..')))

# Import all modules
from imports import *


def run_query(query: str, params: tuple = ()) -> list[dict]:
    """
    Run an SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        params (tuple): The parameters to use with the SQL query.

    Returns:
        list[dict]: The results of the query as a list of dictionaries.
    """
    db = "travel2.sqlite"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [dict(zip([column[0] for column in cursor.description], row)) for row in results]

@tool
def search_hotels(
    location: Optional[str] = None,
    name: Optional[str] = None,
    price_tier: Optional[str] = None,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> list[dict]:
    """
    Search for hotels based on location, name, price tier, check-in date, and check-out date.

    Args:
        location (Optional[str]): The location of the hotel. Defaults to None.
        name (Optional[str]): The name of the hotel. Defaults to None.
        price_tier (Optional[str]): The price tier of the hotel. Defaults to None. Examples: Midscale, Upper Midscale, Upscale, Luxury
        checkin_date (Optional[Union[datetime, date]]): The check-in date of the hotel. Defaults to None.
        checkout_date (Optional[Union[datetime, date]]): The check-out date of the hotel. Defaults to None.

    Returns:
        list[dict]: A list of hotel dictionaries matching the search criteria.
    """
    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if price_tier:
        query += " AND price_tier = ?"
        params.append(price_tier)
    if checkin_date:
        query += " AND checkin_date >= ?"
        params.append(checkin_date)
    if checkout_date:
        query += " AND checkout_date <= ?"
        params.append(checkout_date)

    results = run_query(query, tuple(params))
    return json.dumps(results, indent=2)

@tool
def book_hotel(hotel_id: int) -> str:
    """
    Book a hotel by its ID.

    Args:
        hotel_id (int): The ID of the hotel to book.

    Returns:
        str: A message indicating whether the hotel was successfully booked or not.
    """
    query = "UPDATE hotels SET booked = 1 WHERE id = ?"
    params = (hotel_id,)
    run_query(query, params)

    return f"Hotel {hotel_id} successfully booked."

@tool
def update_hotel(
    hotel_id: int,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update a hotel's check-in and check-out dates by its ID.

    Args:
        hotel_id (int): The ID of the hotel to update.
        checkin_date (Optional[Union[datetime, date]]): The new check-in date of the hotel. Defaults to None.
        checkout_date (Optional[Union[datetime, date]]): The new check-out date of the hotel. Defaults to None.

    Returns:
        str: A message indicating whether the hotel was successfully updated or not.
    """
    if checkin_date:
        query = "UPDATE hotels SET checkin_date = ? WHERE id = ?"
        params = (checkin_date, hotel_id)
        run_query(query, params)
    if checkout_date:
        query = "UPDATE hotels SET checkout_date = ? WHERE id = ?"
        params = (checkout_date, hotel_id)
        run_query(query, params)

    return f"Hotel {hotel_id} successfully updated."

@tool
def cancel_hotel(hotel_id: int) -> str:
    """
    Cancel a hotel by its ID.

    Args:
        hotel_id (int): The ID of the hotel to cancel.

    Returns:
        str: A message indicating whether the hotel was successfully cancelled or not.
    """
    query = "UPDATE hotels SET booked = 0 WHERE id = ?"
    params = (hotel_id,)
    run_query(query, params)

    return f"Hotel {hotel_id} successfully cancelled."

