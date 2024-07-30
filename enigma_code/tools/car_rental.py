
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
def search_car_rentals(location: Optional[str] = None, name: Optional[str] = None, price_tier: Optional[str] = None, start_date: Optional[Union[datetime, date]] = None, end_date: Optional[Union[datetime, date]] = None) -> list[dict]:
    """
    Search for car rentals based on location, name, price tier, start date, and end date.

    Args:
        location (Optional[str]): The location of the car rental. Defaults to None.
        name (Optional[str]): The name of the car rental company. Defaults to None.
        price_tier (Optional[str]): The price tier of the car rental. Defaults to None.
        start_date (Optional[Union[datetime, date]]): The start date of the car rental. Defaults to None.
        end_date (Optional[Union[datetime, date]]): The end date of the car rental. Defaults to None.

    Returns:
        list[dict]: A list of car rental dictionaries matching the search criteria.
    """
    query = "SELECT * FROM car_rentals WHERE 1=1"
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
    if start_date:
        query += " AND start_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND end_date <= ?"
        params.append(end_date)

    results = run_query(query, tuple(params))
    return json.dumps(results, indent=2)

@tool
def book_car_rental(rental_id: int) -> str:
    """
    Book a car rental by its ID.

    Args:
        rental_id (int): The ID of the car rental to book.

    Returns:
        str: A message indicating whether the car rental was successfully booked or not.
    """
    run_query(
        query = "UPDATE car_rentals SET booked = 1 WHERE id = ?", 
        params = (rental_id,)
    )

    return f"Car rental {rental_id} successfully booked."

@tool
def update_car_rental(rental_id: int, start_date: Optional[Union[datetime, date]] = None, end_date: Optional[Union[datetime, date]] = None) -> str:
    """
    Update a car rental's start and end dates by its ID.

    Args:
        rental_id (int): The ID of the car rental to update.
        start_date (Optional[Union[datetime, date]]): The new start date of the car rental. Defaults to None.
        end_date (Optional[Union[datetime, date]]): The new end date of the car rental. Defaults to None.

    Returns:
        str: A message indicating whether the car rental was successfully updated or not.
    """
    if start_date:
        query = "UPDATE car_rentals SET start_date = ? WHERE id = ?"
        params = (start_date, rental_id)
        run_query(query, params)
    if end_date:
        query = "UPDATE car_rentals SET end_date = ? WHERE id = ?"
        params = (end_date, rental_id)
        run_query(query, params)

    return f"Car rental {rental_id} successfully updated."

@tool
def cancel_car_rental(rental_id: int) -> str:
    """
    Cancel a car rental by its ID.

    Args:
        rental_id (int): The ID of the car rental to cancel.

    Returns:
        str: A message indicating whether the car rental was successfully cancelled or not.
    """
    query = "UPDATE car_rentals SET booked = 0 WHERE id = ?"
    params = (rental_id,)
    run_query(query, params)

    return f"Car rental {rental_id} successfully cancelled."