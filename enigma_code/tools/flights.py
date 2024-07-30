
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
def fetch_user_flight_information() -> str:
    """Fetch all tickets for the user along with corresponding flight information and seat assignments."""
    config = ensure_config()
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    query = """
    SELECT
    t.ticket_no, t.book_ref,
    f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
    bp.seat_no, tf.fare_conditions
    FROM
    tickets t
    JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
    JOIN flights f ON tf.flight_id = f.flight_id
    JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
    WHERE
    t.passenger_id = ?
    """
    
    results = run_query(query, (passenger_id,))
    return json.dumps(results, indent=2)

@tool
def search_flights(
    departure_airport: Optional[str] = None,
    arrival_airport: Optional[str] = None,
    start_time: Optional[Union[date, datetime]] = None,
    end_time: Optional[Union[date, datetime]] = None,
    limit: int = 20,
) -> str:
    """Search for flights based on departure airport, arrival airport, and departure time range."""
    query = "SELECT * FROM flights WHERE 1 = 1"
    params = []

    if departure_airport:
        query += " AND departure_airport = ?"
        params.append(departure_airport)
    if arrival_airport:
        query += " AND arrival_airport = ?"
        params.append(arrival_airport)
    if start_time:
        query += " AND scheduled_departure >= ?"
        params.append(start_time)
    if end_time:
        query += " AND scheduled_departure <= ?"
        params.append(end_time)
    
    query += " LIMIT ?"
    params.append(limit)

    results = run_query(query, tuple(params))
    return json.dumps(results, indent=2)

@tool
def update_ticket_to_new_flight(ticket_no: str, new_flight_id: int) -> str:
    """Update the user's ticket to a new valid flight."""
    config = ensure_config()
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    # Check if the new flight exists
    new_flight = run_query("SELECT departure_airport, arrival_airport, scheduled_departure FROM flights WHERE flight_id = ?", (new_flight_id,))
    if not new_flight:
        return "Invalid new flight ID provided."

    new_flight_dict = new_flight[0]
    timezone = pytz.timezone("Etc/GMT-3")
    current_time = datetime.now(tz=timezone)
    departure_time = datetime.strptime(new_flight_dict["scheduled_departure"], "%Y-%m-%d %H:%M:%S.%f%z")

    time_until = (departure_time - current_time).total_seconds()
    if time_until < (3 * 3600):
        return f"Not permitted to reschedule to a flight that is less than 3 hours from the current time. Selected flight is at {departure_time}."

    # Check if the ticket exists
    current_flight = run_query("SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,))
    if not current_flight:
        return "No existing ticket found for the given ticket number."

    # Check if the signed-in user owns this ticket
    current_ticket = run_query("SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?", (ticket_no, passenger_id))
    if not current_ticket:
        return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

    # Update the ticket
    run_query("UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?", (new_flight_id, ticket_no), fetch_all=False)
    return "Ticket successfully updated to new flight."

@tool
def cancel_ticket(ticket_no: str) -> str:
    """Cancel the user's ticket and remove it from the database."""
    config = ensure_config()
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    # Check if the ticket exists
    existing_ticket = run_query("SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,))
    if not existing_ticket:
        return "No existing ticket found for the given ticket number."

    # Check if the signed-in user owns this ticket
    current_ticket = run_query("SELECT flight_id FROM tickets WHERE ticket_no = ? AND passenger_id = ?", (ticket_no, passenger_id))
    if not current_ticket:
        return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

    # Cancel the ticket
    run_query("DELETE FROM ticket_flights WHERE ticket_no = ?", (ticket_no,), fetch_all=False)
    return "Ticket successfully cancelled."