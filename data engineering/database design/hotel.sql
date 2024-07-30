-- Create the schema if it doesn't exist
CREATE DATABASE IF NOT EXISTS hotel;

-- Use the schema
USE hotel;

-- Room Types table
CREATE TABLE RoomTypes (
    RoomTypeID INT PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL,
    Description TEXT,
    MaxOccupancy INT NOT NULL CHECK (MaxOccupancy > 0)
);

-- Rooms table
CREATE TABLE Rooms (
    RoomID INT PRIMARY KEY,
    RoomTypeID INT NOT NULL,
    RoomNumber VARCHAR(10) NOT NULL,
    FloorNumber INT,
    FOREIGN KEY (RoomTypeID) REFERENCES RoomTypes(RoomTypeID)
);

-- Guests table
CREATE TABLE Guests (
    GuestID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100),
    Phone VARCHAR(20),
    Address VARCHAR(255),
    DateOfBirth DATE,
    LoyaltyPoints INT DEFAULT 0
);

-- Bookings table
CREATE TABLE Bookings (
    BookingID INT PRIMARY KEY,
    GuestID INT NOT NULL,
    RoomID INT NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    NumberOfGuests INT NOT NULL CHECK (NumberOfGuests > 0),
    BookingStatus VARCHAR(20) NOT NULL CHECK (BookingStatus IN ('Confirmed', 'Pending', 'Cancelled', 'Completed')),
    TotalPrice DECIMAL(10, 2) NOT NULL,
    PaymentStatus VARCHAR(20) NOT NULL CHECK (PaymentStatus IN ('Paid', 'Pending', 'Refunded')),
    SpecialRequests TEXT,
    BookingSource VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (GuestID) REFERENCES Guests(GuestID),
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
    CONSTRAINT chk_dates CHECK (CheckOutDate > CheckInDate)
);

-- Services table
CREATE TABLE Services (
    ServiceID INT PRIMARY KEY,
    ServiceName VARCHAR(100) NOT NULL,
    Description TEXT,
    Price DECIMAL(8, 2) NOT NULL
);

-- Booking Services table (for many-to-many relationship between Bookings and Services)
CREATE TABLE BookingServices (
    BookingServiceID INT PRIMARY KEY,
    BookingID INT NOT NULL,
    ServiceID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    TotalPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
);

-- Payments table
CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY,
    BookingID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentMethod VARCHAR(50) NOT NULL,
    TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Successful', 'Failed', 'Pending', 'Refunded')),
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID)
);

-- Create necessary indexes
CREATE INDEX idx_room_type ON Rooms(RoomTypeID);
CREATE INDEX idx_booking_guest ON Bookings(GuestID);
CREATE INDEX idx_booking_room ON Bookings(RoomID);
CREATE INDEX idx_booking_dates ON Bookings(CheckInDate, CheckOutDate);
CREATE INDEX idx_guest_name ON Guests(LastName, FirstName);