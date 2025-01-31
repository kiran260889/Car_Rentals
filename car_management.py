from database_connection import DatabaseConnection
from user_management import EmailService
from datetime import datetime

def view_available_cars():
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM cars WHERE available = TRUE")
        cars = cursor.fetchall()
        if cars:
            print("Available Cars:")
            for car in cars:
                print(
                    f"ID: {car[0]}, Make: {car[1]}, Model: {car[2]}, Year: {car[3]}, Mileage: {car[4]}, Rental Charge/Hour: ${car[8]}, Tax Rate: {car[9]}%, Min Rental Period: {car[6]} hours, Max Rental Period: {car[7]} hours")
        else:
            print("No cars available.")
    except Exception as e:
        print(f"Error fetching cars: {e}")
    finally:
        cursor.close()

def book_car(user_id):
    view_available_cars()

    car_id = input("Enter the Car ID to book: ")
    if not car_id.isdigit():
        print("Error: Car ID must be a valid integer.")
        return

    car_id = int(car_id)

    rental_start = input("Enter rental start date and time (YYYY-MM-DD HH:MM): ")
    rental_end = input("Enter rental end date and time (YYYY-MM-DD HH:MM): ")

    try:
        start_datetime = datetime.strptime(rental_start, "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(rental_end, "%Y-%m-%d %H:%M")

        current_time = datetime.now()
        if start_datetime <= current_time:
            print("Error: Rental start time must be in the future.")
            return

        if end_datetime <= start_datetime:
            print("Error: Rental end time must be after the start time.")
            return

        rental_duration = (end_datetime - start_datetime).total_seconds() / 3600

    except ValueError:
        print("Error: Invalid date format. Please use 'YYYY-MM-DD HH:MM'.")
        return

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM cars WHERE id = %s AND available = TRUE", (car_id,))
        car = cursor.fetchone()

        if not car:
            print("Error: Car is not available or does not exist.")
            return

        min_rent_period = car[6]
        max_rent_period = car[7]
        if rental_duration < min_rent_period or rental_duration > max_rent_period:
            print(f"Error: Rental duration must be between {min_rent_period} and {max_rent_period} hours.")
            return

        rental_charge_per_hour = float(car[8])
        tax_rate = float(car[9])

        rental_charge = rental_charge_per_hour * rental_duration
        tax = (tax_rate / 100) * rental_charge
        total_rental_fee = rental_charge + tax

        print(f"\nRental Details:")
        print(f"Rental Charge (Excl. Tax): ${rental_charge:.2f}")
        print(f"Tax: ${tax:.2f}")
        print(f"Total Rental Fee: ${total_rental_fee:.2f}")

        confirm = input("Confirm booking? (yes/no): ").lower()
        if confirm == 'yes':
            cursor.execute("""
                INSERT INTO bookings (user_id, car_id, rental_start, rental_end, status, total_fee)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, car_id, rental_start, rental_end, "awaiting approval", total_rental_fee))

            cursor.execute("UPDATE cars SET available = FALSE WHERE id = %s", (car_id,))
            db_conn.commit()

            cursor.execute("SELECT username, email FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                username, user_email = user
                car_make = car[1]
                car_model = car[2]

                email_service = EmailService()
                email_service.send_email(
                    user_email,
                    "Booking Confirmation",
                    f"Dear {username},\n\nYour booking is successful and is awaiting admin approval.\n\n"
                    f"Booking Details:\n"
                    f"Car: {car_make} {car_model}\n"
                    f"Rental Start: {rental_start}\n"
                    f"Rental End: {rental_end}\n"
                    f"Total Fee: ${total_rental_fee:.2f}\n\n"
                    f"Thank you for choosing our service!"
                )

                email_service.send_email(
                    "carrental2608@gmail.com",
                    "New Booking Request",
                    f"New Booking Request:\n\n"
                    f"User: {username}\n"
                    f"Car: {car_make} {car_model}\n"
                    f"Rental Start: {rental_start}\n"
                    f"Rental End: {rental_end}\n"
                    f"Total Fee: ${total_rental_fee:.2f}\n\n"
                    f"Please review and approve the booking."
                )

                print("\nCar booked successfully! Awaiting admin approval.")
                print(f"Booking notification has been sent to your email: {user_email}")
        else:
            print("Booking cancelled.")
    except Exception as e:
        print(f"Error booking car: {e}")
    finally:
        cursor.close()

def return_car(user_id):
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            SELECT bookings.id, cars.make, cars.model, bookings.rental_start, bookings.total_fee, bookings.car_id, cars.rental_charge_per_hour, cars.tax_rate, cars.min_rent_period
            FROM bookings
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.user_id = %s AND bookings.status = 'approved'
        """, (user_id,))
        bookings = cursor.fetchall()

        if not bookings:
            print("No active bookings found to return.")
            return

        print("\nYour Approved Bookings:")
        for booking in bookings:
            print(f"Booking ID: {booking[0]}, Car: {booking[1]} {booking[2]}, Rental Start: {booking[3]}")

        booking_id = input("\nEnter the Booking ID to return: ")
        if not booking_id.isdigit():
            print("Error: Booking ID must be a valid integer.")
            return

        booking_id = int(booking_id)

        cursor.execute("""
            SELECT bookings.id, users.username, users.email, cars.make, cars.model, bookings.rental_start, bookings.car_id, cars.rental_charge_per_hour, cars.tax_rate, cars.min_rent_period
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.id = %s AND bookings.user_id = %s AND bookings.status = 'approved'
        """, (booking_id, user_id))
        booking = cursor.fetchone()

        if not booking:
            print("Error: Booking not found or already returned.")
            return

        booking_id, username, user_email, make, model, rental_start, car_id, rental_charge_per_hour, tax_rate, min_rent_period = booking

        if isinstance(rental_start, str):
            rental_start = datetime.strptime(rental_start, "%Y-%m-%d %H:%M:%S")

        return_time = datetime.now()

        actual_rental_duration = (return_time - rental_start).total_seconds() / 3600

        if actual_rental_duration < min_rent_period:
            actual_rental_duration = min_rent_period

        rental_charge_per_hour = float(rental_charge_per_hour)
        tax_rate = float(tax_rate)

        rental_charge = rental_charge_per_hour * actual_rental_duration
        tax = (tax_rate / 100) * rental_charge
        total_rental_fee = rental_charge + tax

        cursor.execute("""
            UPDATE bookings
            SET status = 'returned', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (booking_id,))

        cursor.execute("UPDATE cars SET available = TRUE WHERE id = %s", (car_id,))
        db_conn.commit()

        invoice = f"""
        Invoice:
        ----------
        Booking ID: {booking_id}
        User: {username}
        Car: {make} {model}
        Rental Start: {rental_start}
        Return Time: {return_time}
        Rental Duration (Hours): {actual_rental_duration:.2f}
        Rental Charge (Excl. Tax): ${rental_charge:.2f}
        Tax: ${tax:.2f}
        Total Rental Fee: ${total_rental_fee:.2f}
        """

        email_service = EmailService()
        email_service.send_email(
            user_email,
            "Car Return Confirmation & Invoice",
            f"Dear {username},\n\nThank you for returning the car.\n\n{invoice}\n\nThank you for using our service!"
        )

        email_service.send_email(
            "carrental2608@gmail.com",
            "Car Returned Notification",
            f"Car Returned:\n\n{invoice}\n\nPlease check the system for updates."
        )

        print("\nCar returned successfully! An invoice has been sent to your email.")
    except Exception as e:
        print(f"Error returning car: {e}")
    finally:
        cursor.close()

def add_car():
    make = input("Enter car make: ")
    model = input("Enter car model: ")
    year = input("Enter car year: ")
    mileage = input("Enter car mileage: ")
    available = input("Is the car available now? (yes/no): ").lower() == 'yes'
    min_rent_period = int(input("Enter minimum rental period (in hours): "))
    max_rent_period = int(input("Enter maximum rental period (in hours): "))
    rental_charge_per_hour = float(input("Enter rental charge per hour (in NZD): "))
    tax_rate = float(input("Enter tax rate (percentage): "))

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO cars (make, model, year, mileage, available, min_rent_period, max_rent_period, rental_charge_per_hour, tax_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (make, model, year, mileage, available, min_rent_period, max_rent_period, rental_charge_per_hour, tax_rate))
        db_conn.commit()
        print("Car added successfully!")

        email_service = EmailService()
        email_service.send_email(
            "carrental2608@gmail.com",
            "Car Added Notification",
            f"A new car has been added to the inventory.\n\n"
            f"Car Details:\n"
            f"Make: {make}\n"
            f"Model: {model}\n"
            f"Year: {year}\n"
            f"Mileage: {mileage}\n"
            f"Rental Charge per Hour: ${rental_charge_per_hour:.2f}\n"
            f"Tax Rate: {tax_rate}%\n\n"
            f"Please check the system for more details."
        )
    except Exception as e:
        print(f"Error adding car: {e}")
    finally:
        cursor.close()

def update_car():
    print("\nAvailable Cars for Update:")
    view_available_cars()

    car_id = input("Enter the Car ID to update: ")
    if not car_id.isdigit():
        print("Error: Car ID must be a valid integer.")
        return

    car_id = int(car_id)

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        car = cursor.fetchone()

        if not car:
            print("Car not found.")
            return

        print(
            f"\nCurrent Details: Make: {car[1]}, Model: {car[2]}, Year: {car[3]}, Mileage: {car[4]}, "
            f"Min Rent Period: {car[6]}, Max Rent Period: {car[7]}, Rental Charge/Hour: {car[8]}, Tax Rate: {car[9]}"
        )

        make = input(f"Enter new make (current: {car[1]}): ") or car[1]
        model = input(f"Enter new model (current: {car[2]}): ") or car[2]
        year = input(f"Enter new year (current: {car[3]}): ") or car[3]
        mileage = input(f"Enter new mileage (current: {car[4]}): ") or car[4]
        available = input(f"Is the car available? (yes/no, current: {car[5]}): ").lower() == 'yes'
        min_rent_period = input(f"Enter new min rent period (current: {car[6]}): ") or car[6]
        max_rent_period = input(f"Enter new max rent period (current: {car[7]}): ") or car[7]
        rental_charge_per_hour = input(f"Enter new rental charge/hour (current: {car[8]}): ") or car[8]
        tax_rate = input(f"Enter new tax rate (current: {car[9]}): ") or car[9]

        cursor.execute("""
            UPDATE cars 
            SET make = %s, model = %s, year = %s, mileage = %s, available = %s, 
                min_rent_period = %s, max_rent_period = %s, 
                rental_charge_per_hour = %s, tax_rate = %s
            WHERE id = %s
        """, (make, model, year, mileage, available, min_rent_period, max_rent_period,
              rental_charge_per_hour, tax_rate, car_id))
        db_conn.commit()
        print("Car details updated successfully!")

        email_service = EmailService()
        email_service.send_email(
            "carrental2608@gmail.com",
            "Car Updated Notification",
            f"A car has been updated in the inventory.\n\n"
            f"Updated Car Details:\n"
            f"Car ID: {car_id}\n"
            f"Make: {make}\n"
            f"Model: {model}\n"
            f"Year: {year}\n"
            f"Mileage: {mileage}\n"
            f"Rental Charge per Hour: ${rental_charge_per_hour:.2f}\n"
            f"Tax Rate: {tax_rate}%\n\n"
            f"Please check the system for more details."
        )
    except Exception as e:
        print(f"Error updating car: {e}")
    finally:
        cursor.close()

def delete_car():
    print("\nAvailable Cars for Deletion:")
    view_available_cars()

    car_id = input("Enter the Car ID to delete: ")
    if not car_id.isdigit():
        print("Error: Car ID must be a valid integer.")
        return

    car_id = int(car_id)

    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
        car = cursor.fetchone()

        if not car:
            print("Car not found.")
            return

        cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        db_conn.commit()
        print("Car deleted successfully!")

        email_service = EmailService()
        email_service.send_email(
            "carrental2608@gmail.com",
            "Car Deleted Notification",
            f"A car has been deleted from the inventory.\n\n"
            f"Deleted Car Details:\n"
            f"Car ID: {car_id}\n"
            f"Make: {car[1]}\n"
            f"Model: {car[2]}\n"
            f"Year: {car[3]}\n"
            f"Mileage: {car[4]}\n\n"
            f"Please check the system for more details."
        )
    except Exception as e:
        print(f"Error deleting car: {e}")
    finally:
        cursor.close()

def list_bookings():
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            SELECT bookings.id, users.username, cars.make, cars.model, bookings.status, bookings.total_fee,bookings.comments,bookings.created_at
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
        """)
        bookings = cursor.fetchall()

        if bookings:
            print("Bookings:")
            for booking in bookings:
                print(
                    f"ID: {booking[0]}, User: {booking[1]}, Car: {booking[2]} {booking[3]}, Status: {booking[4]}, Total Fee: ${booking[5]:.2f},comments: {booking[6]},created_at: {booking[7]}")
        else:
            print("No bookings found.")
    except Exception as e:
        print(f"Error fetching bookings: {e}")
    finally:
        cursor.close()

def approve_booking():
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            SELECT bookings.id, users.username, users.email, cars.make, cars.model, bookings.total_fee
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.status = 'awaiting approval'
        """)
        pending_bookings = cursor.fetchall()

        if not pending_bookings:
            print("No bookings awaiting approval.")
            return

        print("\nPending Bookings:")
        for booking in pending_bookings:
            print(
                f"Booking ID: {booking[0]}, User: {booking[1]}, Car: {booking[3]} {booking[4]}, Total Fee: ${booking[5]:.2f}")

        booking_id = input("\nEnter the Booking ID to approve: ")

        if not booking_id.isdigit():
            print("Error: Booking ID must be a valid integer.")
            return

        booking_id = int(booking_id)

        cursor.execute("""
            SELECT bookings.id, users.username, users.email, cars.make, cars.model, bookings.total_fee
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.id = %s AND bookings.status = 'awaiting approval'
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            print("Invalid Booking ID or the booking is not pending approval.")
            return

        booking_id, username, user_email, car_make, car_model, total_fee = booking

        reason_for_approval = input("Enter the reason for approval (this will be sent to the admin only): ").strip()

        cursor.execute("""
            UPDATE bookings
            SET status = 'approved', comments = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (reason_for_approval, booking_id))
        db_conn.commit()
        print(f"\nBooking {booking_id} has been approved successfully!")

        user_email_body = f"""
        Dear {username},

        Your booking has been approved!

        Booking Details:
        ----------------
        Booking ID: {booking_id}
        Car: {car_make} {car_model}

        Thank you for choosing our service!

        Regards,
        Car Rental Service
        """

        email_service = EmailService()
        email_service.send_email(
            user_email,
            "Booking Approved",
            user_email_body
        )

        admin_email_body = f"""
        Admin Notification:

        Booking Approved:
        -----------------
        Booking ID: {booking_id}
        User: {username}
        Car: {car_make} {car_model}
        Total Fee: ${total_fee:.2f}
        Reason for Approval: {reason_for_approval}

        Please check the system for updates.

        Regards,
        Car Rental Service
        """

        email_service.send_email(
            "carrental2608@gmail.com",
            "Booking Approved Notification",
            admin_email_body
        )

        print("\nEmail notifications sent to the customer and the admin successfully!")

    except Exception as e:
        print(f"Error approving booking: {e}")
    finally:
        cursor.close()

def reject_booking():
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute("""
            SELECT bookings.id, users.username, users.email, cars.make, cars.model, cars.id AS car_id
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.status = 'awaiting approval'
        """)
        pending_bookings = cursor.fetchall()

        if not pending_bookings:
            print("No bookings awaiting approval.")
            return

        print("\nPending Bookings:")
        for booking in pending_bookings:
            print(f"Booking ID: {booking[0]}, User: {booking[1]}, Car: {booking[3]} {booking[4]}")

        booking_id = input("\nEnter the Booking ID to reject: ")

        if not booking_id.isdigit():
            print("Error: Booking ID must be a valid integer.")
            return

        booking_id = int(booking_id)

        cursor.execute("""
            SELECT bookings.car_id, users.username, users.email, cars.make, cars.model
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.id = %s AND bookings.status = 'awaiting approval'
        """, (booking_id,))
        result = cursor.fetchone()

        if not result:
            print("Invalid Booking ID or the booking is not pending approval.")
            return

        car_id, username, user_email, car_make, car_model = result

        comments = input("Enter the reason for rejection: ").strip()
        if not comments:
            print("Error: A reason is required for rejection.")
            return

        cursor.execute("""
            UPDATE bookings
            SET status = 'rejected', comments = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (comments, booking_id))
        cursor.execute("UPDATE cars SET available = TRUE WHERE id = %s", (car_id,))
        db_conn.commit()
        print(f"\nBooking {booking_id} has been rejected successfully! The car is now available again.")

        customer_email_body = f"""
        Dear {username},

        We regret to inform you that your booking has been rejected.

        Booking Details:
        ----------------
        Booking ID: {booking_id}
        Car: {car_make} {car_model}
        Reason for Rejection: {comments}

        Regards,
        Car Rental Service
        """

        admin_email_body = f"""
        Admin Notification:

        A booking has been rejected.

        Booking Details:
        ----------------
        Booking ID: {booking_id}
        User: {username}
        Car: {car_make} {car_model}
        Reason for Rejection: {comments}

        Please check the system for more details.

        Regards,
        Car Rental Service
        """

        email_service = EmailService()
        email_service.send_email(
            user_email,
            "Booking Rejected",
            customer_email_body
        )

        email_service.send_email(
            "carrental2608@gmail.com",
            "Booking Rejected Notification",
            admin_email_body
        )

        print("\nEmail notifications sent to the customer and the admin successfully!")
    except Exception as e:
        print(f"Error rejecting booking: {e}")
    finally:
        cursor.close()
def send_sos_alert(user_id):
    """Send an SOS alert to the admin during an active booking."""
    db_conn = DatabaseConnection().get_connection()
    cursor = db_conn.cursor()

    try:
        # Fetch the user's active booking
        cursor.execute("""
            SELECT bookings.id, users.username, users.email, cars.make, cars.model, bookings.rental_start
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN cars ON bookings.car_id = cars.id
            WHERE bookings.user_id = %s AND bookings.status = 'approved'
        """, (user_id,))
        booking = cursor.fetchone()

        if not booking:
            print("No active booking found. SOS alert cannot be sent.")
            return

        booking_id, username, user_email, car_make, car_model, rental_start = booking

        # Send SOS alert to admin
        email_service = EmailService()
        email_service.send_email(
            "carrental2608sos@gmail.com",  # SOS Team Email
            "SOS Alert from User",
            f"Emergency Alert!\n\n"
            f"User: {username}\n"
            f"Email: {user_email}\n"
            f"Car: {car_make} {car_model}\n"
            f"Rental Start: {rental_start}\n\n"
            f"Please take immediate action to assist the user."
        )

        print("SOS alert sent to the admin. Help is on the way!")
    except Exception as e:
        print(f"Error sending SOS alert: {e}")
    finally:
        cursor.close()

def user_menu(user_id):
    while True:
        print("\nUser Menu:")
        print("1. View Available Cars")
        print("2. Book a Car")
        print("3. Return a Car")
        print("4. Send SOS Alert")  # New option for SOS
        print("5. Exit")
        action = input("Enter your choice: ")

        if action == "1":
            view_available_cars()
            book_option = input("Do you want to book a car? (yes/no): ").lower()
            if book_option == 'yes':
                book_car(user_id)
        elif action == "2":
            book_car(user_id)
        elif action == "3":
            return_car(user_id)
        elif action == "4":  # SOS functionality
            send_sos_alert(user_id)
        elif action == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Add Car")
        print("2. Update Car")
        print("3. Delete Car")
        print("4. List Bookings")
        print("5. Approve Booking")
        print("6. Reject Booking")
        print("7. Exit")
        action = input("Enter your choice: ")

        if action == "1":
            add_car()
        elif action == "2":
            update_car()
        elif action == "3":
            delete_car()
        elif action == "4":
            list_bookings()
        elif action == "5":
            approve_booking()
        elif action == "6":
            reject_booking()
        elif action == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")