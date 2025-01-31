Car Rental Management System
This is a Car Rental Management System built using Python. The system allows users to register,Login,bookcar and Returncar.Admins can Addcar,Updatecar,Deletecar,approve booking and Reject booking. The system also includes an SOS functionality for users to send emergency alerts during an active booking.

Features
User Features:
Register: Users can create an account by providing a username, email, and password.
Login: Users can log in to their accounts using their credentials.
View Available Cars: Users can view a list of available cars for rent.
Book a Car: Users can book a car by selecting a car ID and specifying the rental period.The system will generate an estimated amount and sends notification to admin for approval.
Return a Car: Users can return a rented car, and the system will calculate the total rental fee.
SOS Alert: Users can send an emergency alert (SOS) during an active booking. The SOS admin will be notified immediately via email.

Admin Features:
Add Car: Admins can add new cars to the system with details like make, model, year, mileage, rental charge, and tax rate.
Update Car: Admins can update the details of existing cars.
Delete Car: Admins can delete cars from the system.
List Bookings: Admins can view all bookings, including their status (awaiting approval, approved, rejected, or returned).
Approve Booking: Admins can approve pending bookings and notify the user via email.
Reject Booking: Admins can reject pending bookings and notify the user via email.

Classes Used in the System
The Car Rental Management System is designed using object-oriented programming (OOP) principles. Below is a detailed explanation of the classes used in the system:

1. DatabaseConnection Class
This class is a Singleton that manages the database connection. It ensures that only one instance of the database connection is created and reused throughout the application.

Key Features:
Singleton Design Pattern: Ensures a single instance of the database connection.

Lazy Initialization: The connection is initialized only when needed.

Configuration via config.ini: Reads database credentials from a configuration file.

Methods:
_initialize_connection(): Initializes the database connection using credentials from config.ini.

get_connection(): Returns the active database connection.

2. EmailService Class
This class is also a Singleton that handles sending emails. It manages the email configuration and provides a method to send emails.

Key Features:
Singleton Design Pattern: Ensures a single instance of the email service.

Configuration via config.ini: Reads email credentials (SMTP server, port, email, and password) from a configuration file.

Email Sending: Sends emails using the smtplib library.

Methods:
_initialize_email_config(): Initializes the email configuration using credentials from config.ini.

send_email(to_email, subject, body): Sends an email to the specified recipient.

3. User and Admin Management Functions
While not implemented as classes, the user and admin management functionalities are modularized into functions in the user_management.py file. These functions handle user registration, authentication, and admin-specific operations.

Key Functions:
create_user(role='user'): Registers a new user or admin.

authenticate_user(role='user'): Authenticates a user or admin during login.

create_admin(): Registers a new admin (only accessible by authenticated admins).

4. Car Management Functions
The car management functionalities are also modularized into functions in the car_management.py file. These functions handle car-related operations such as adding, updating, deleting, and booking cars.

Key Functions:
view_available_cars(): Displays a list of available cars.

book_car(user_id): Allows a user to book a car.

return_car(user_id): Allows a user to return a rented car.

add_car(): Allows an admin to add a new car.

update_car(): Allows an admin to update car details.

delete_car(): Allows an admin to delete a car.

5. Main Script (car_rental.py)
The main script ties everything together. It uses the argparse library to provide a command-line interface for users and admins.

Key Features:
Command-Line Interface: Users and admins can interact with the system via the command line.

Role-Based Access: Users and admins have separate menus and functionalities.



send_sos_alert(user_id): Allows a user to send an SOS alert during an active booking.

authenticate_admin(): Authenticates an admin during login.
