

import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join('./../..')))

# Import all modules
from imports import *


# Tools

class ToFlightBookingAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle flight updates and cancellations."""
    request: str = Field(description="Any necessary followup questions the update flight assistant should clarify before proceeding.")

class ToBookCarRental(BaseModel):
    """Transfers work to a specialized assistant to handle car rental bookings."""
    location: str = Field(description="The location where the user wants to rent a car.")
    start_date: str = Field(description="The start date of the car rental.")
    end_date: str = Field(description="The end date of the car rental.")
    request: str = Field(description="Any additional information or requests from the user regarding the car rental.")

    class Config:
        schema_extra = {
            "example": {
                "location": "Basel",
                "start_date": "2023-07-01",
                "end_date": "2023-07-05",
                "request": "I need a compact car with automatic transmission.",
            }
        }

class ToHotelBookingAssistant(BaseModel):
    """Transfer work to a specialized assistant to handle hotel bookings."""
    location: str = Field(description="The location where the user wants to book a hotel.")
    checkin_date: str = Field(description="The check-in date for the hotel.")
    checkout_date: str = Field(description="The check-out date for the hotel.")
    request: str = Field(description="Any additional information or requests from the user regarding the hotel booking.")

    class Config:
        schema_extra = {
            "example": {
                "location": "Zurich",
                "checkin_date": "2023-08-15",
                "checkout_date": "2023-08-20",
                "request": "I prefer a hotel near the city center with a room that has a view.",
            }
        }

class ToBookExcursion(BaseModel):
    """Transfers work to a specialized assistant to handle trip recommendation and other excursion bookings."""
    location: str = Field(description="The location where the user wants to book a recommended trip.")
    request: str = Field(description="Any additional information or requests from the user regarding the trip recommendation.")

    class Config:
        schema_extra = {
            "example": {
                "location": "Lucerne",
                "request": "The user is interested in outdoor activities and scenic views.",
            }
        }

# Tool

class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        schema_extra = {
            "example": {"cancel": True, "reason": "User changed their mind about the current task."},
            "example 2": {"cancel": True, "reason": "I have fully completed the task."},
            "example 3": {"cancel": False, "reason": "I need to search the user's emails or calendar for more information."}}
        

