import argparse
from user_management import create_user, authenticate_user, authenticate_admin, create_admin
from src.car_management import user_menu, admin_menu

def main():
    parser = argparse.ArgumentParser(description="Car Rental Management System")
    subparsers = parser.add_subparsers(dest="role")

    # User commands
    user_parser = subparsers.add_parser('user', help="User actions")
    user_parser.set_defaults(func=user_menu)

    # Admin commands
    admin_parser = subparsers.add_parser('admin', help="Admin actions")
    admin_parser.set_defaults(func=admin_menu)

    args = parser.parse_args()

    if args.role == "user":
        print("1. Register")
        print("2. Login")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            create_user(role='user')
        elif user_choice == "2":
            user = authenticate_user(role='user')
            if user:
                user_menu(user[0])  # Pass the user_id to the user menu

    elif args.role == "admin":
        print("1. Register Admin")
        print("2. Login")
        admin_choice = input("Enter your choice: ")

        if admin_choice == "1":
            create_admin()
        elif admin_choice == "2":
            admin = authenticate_admin()
            if admin:
                admin_menu()

if __name__ == "__main__":
    main()