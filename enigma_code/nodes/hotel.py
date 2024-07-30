
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add previous directory to path
sys.path.append('..')
from enigma_code.databases import *

# Function to book a reservation
def book_reservation(database_name, guest_id, room_id, check_in_date, check_out_date, number_of_guests, total_price, payment_status, booking_status='Confirmed', special_requests=None, booking_source=None):
    query = """
    INSERT INTO Bookings (GuestID, RoomID, CheckInDate, CheckOutDate, NumberOfGuests, TotalPrice, PaymentStatus, BookingStatus, SpecialRequests, BookingSource)
    VALUES (:guest_id, :room_id, :check_in_date, :check_out_date, :number_of_guests, :total_price, :payment_status, :booking_status, :special_requests, :booking_source)
    """
    params = {
        'guest_id': guest_id,
        'room_id': room_id,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'number_of_guests': number_of_guests,
        'total_price': total_price,
        'payment_status': payment_status,
        'booking_status': booking_status,
        'special_requests': special_requests,
        'booking_source': booking_source
    }
    return execute_mysql_query(query, database_name, params)

# Function to cancel a reservation
def cancel_reservation(database_name, booking_id):
    query = """
    UPDATE Bookings
    SET BookingStatus = 'Cancelled'
    WHERE BookingID = :booking_id
    """
    params = {'booking_id': booking_id}
    return execute_mysql_query(query, database_name, params)

# Function to update a reservation
def update_reservation(database_name, booking_id, **kwargs):
    set_clause = ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
    query = f"""
    UPDATE Bookings
    SET {set_clause}, UpdatedAt = CURRENT_TIMESTAMP
    WHERE BookingID = :booking_id
    """
    params = {'booking_id': booking_id}
    params.update(kwargs)
    return execute_mysql_query(query, database_name, params)

# # Example usage
# if __name__ == "__main__":
#     database_name = 'hotel'
    
#     # Book a new reservation
#     booking_id = book_reservation(
#         database_name=database_name,
#         guest_id=1,
#         room_id=101,
#         check_in_date='2024-08-01',
#         check_out_date='2024-08-05',
#         number_of_guests=2,
#         total_price=500.00,
#         payment_status='Paid',
#         special_requests='Late check-in',
#         booking_source='Website'
#     )
#     print(f"New booking created with ID: {booking_id}")

#     # Cancel a reservation
#     if cancel_reservation(database_name, booking_id):
#         print(f"Booking ID {booking_id} has been cancelled.")

#     # Update a reservation
#     if update_reservation(database_name, booking_id, TotalPrice=550.00, SpecialRequests='Early check-in'):
#         print(f"Booking ID {booking_id} has been updated.")