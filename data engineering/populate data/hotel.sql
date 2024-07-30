
-- Create the schema if it doesn't exist
CREATE DATABASE IF NOT EXISTS hotel;

-- Use the schema
USE hotel;

-- Populate RoomTypes table
INSERT INTO RoomTypes (RoomTypeID, TypeName, Description, MaxOccupancy) VALUES
(1, 'Standard', 'Comfortable room with basic amenities', 2),
(2, 'Deluxe', 'Spacious room with upgraded amenities', 3),
(3, 'Suite', 'Luxurious suite with separate living area', 4),
(4, 'Family', 'Large room suitable for families', 5),
(5, 'Executive', 'Premium room with business facilities', 2);

-- Populate Rooms table
INSERT INTO Rooms (RoomID, RoomTypeID, RoomNumber, FloorNumber) VALUES
(101, 1, '101', 1),
(102, 1, '102', 1),
(201, 2, '201', 2),
(202, 2, '202', 2),
(301, 3, '301', 3),
(302, 3, '302', 3),
(401, 4, '401', 4),
(501, 5, '501', 5);

-- Populate Guests table
INSERT INTO Guests (GuestID, FirstName, LastName, Email, Phone, Address, DateOfBirth, LoyaltyPoints) VALUES
(1, 'John', 'Doe', 'john.doe@email.com', '123-456-7890', '123 Main St, City, Country', '1980-01-15', 100),
(2, 'Jane', 'Smith', 'jane.smith@email.com', '987-654-3210', '456 Elm St, Town, Country', '1985-05-20', 50),
(3, 'Michael', 'Johnson', 'michael.j@email.com', '555-123-4567', '789 Oak Ave, Village, Country', '1975-11-30', 200),
(4, 'Emily', 'Brown', 'emily.b@email.com', '444-555-6666', '321 Pine Rd, City, Country', '1990-08-10', 75),
(5, 'David', 'Wilson', 'david.w@email.com', '777-888-9999', '654 Maple Ln, Town, Country', '1982-03-25', 150);

-- Populate Bookings table
INSERT INTO Bookings (BookingID, GuestID, RoomID, CheckInDate, CheckOutDate, NumberOfGuests, BookingStatus, TotalPrice, PaymentStatus, SpecialRequests, BookingSource) VALUES
(1, 1, 101, '2024-08-01', '2024-08-05', 2, 'Confirmed', 500.00, 'Paid', 'Late check-in', 'Website'),
(2, 2, 201, '2024-08-10', '2024-08-15', 3, 'Confirmed', 1000.00, 'Paid', 'Extra bed', 'Phone'),
(3, 3, 301, '2024-09-01', '2024-09-07', 2, 'Pending', 1500.00, 'Pending', 'Airport transfer', 'Agency'),
(4, 4, 401, '2024-09-15', '2024-09-20', 4, 'Confirmed', 1200.00, 'Paid', 'Crib for baby', 'Website'),
(5, 5, 501, '2024-10-01', '2024-10-03', 1, 'Confirmed', 600.00, 'Paid', 'Late check-out', 'Mobile App');

-- Populate Services table
INSERT INTO Services (ServiceID, ServiceName, Description, Price) VALUES
(1, 'Room Service', 'In-room dining', 20.00),
(2, 'Spa Treatment', 'Relaxing massage', 80.00),
(3, 'Airport Transfer', 'Pickup or drop-off service', 50.00),
(4, 'Laundry', 'Clothes washing and ironing', 15.00),
(5, 'Guided Tour', 'City sightseeing tour', 100.00);

-- Populate BookingServices table
INSERT INTO BookingServices (BookingServiceID, BookingID, ServiceID, Quantity, TotalPrice) VALUES
(1, 1, 1, 2, 40.00),
(2, 2, 2, 1, 80.00),
(3, 3, 3, 1, 50.00),
(4, 4, 4, 3, 45.00),
(5, 5, 5, 2, 200.00);

-- Populate Payments table
INSERT INTO Payments (PaymentID, BookingID, Amount, PaymentMethod, Status) VALUES
(1, 1, 500.00, 'Credit Card', 'Successful'),
(2, 2, 1000.00, 'Debit Card', 'Successful'),
(3, 3, 750.00, 'Bank Transfer', 'Pending'),
(4, 4, 1200.00, 'Credit Card', 'Successful'),
(5, 5, 600.00, 'Cash', 'Successful');