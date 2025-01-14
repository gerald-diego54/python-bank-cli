from datetime import datetime
from itertools import islice
from os import system, path
import msvcrt

BANK_FILE_NAME = "bank_data.txt"
USER_FILE_NAME = "user_data.txt"
USER_ID_FIELD_NAME = "User ID"
USER_CREATED_AT_FIELD_NAME = "Created At"
BANK_TRANSACTION_FIELD_NAME = "Transaction ID"
USER_FILE_FIELD_NAMES = [USER_ID_FIELD_NAME, "Account Name", "Account Number", "Pincode", USER_CREATED_AT_FIELD_NAME]
BANK_FILE_FIELD_NAMES = [BANK_TRANSACTION_FIELD_NAME, USER_ID_FIELD_NAME, "Balance", "Withdraw", "Deposit", USER_CREATED_AT_FIELD_NAME]
EXIT_OPTION = 4

def clear_screen():
    system("cls")

def display_main_screen():
    print("\n\n")
    print("88888888                        888")
    print("888   888                       888")
    print("888   888                       888")
    print("88888888      8888b.  8.888b.   888  888")
    print("888   888       \"88b  888 \"88b  888 888")
    print("888   888  .d8888888  888  888  88888")
    print("888   888  888   888  888  888  888 888")
    print("88888888   \"Y8888888  888  888  888  888")
    print("\n🏦 Welcome to the bank v1.0 Beta 💰\n")

def display_transaction_options():
    print("\nTransaction Options:\n")
    print("[0] Balance Inquiry 💰")
    print("[1] Withdrawal 💵")
    print("[2] Transactions 🔄")
    print("[3] Deposit ⬇️")
    print("[4] Exit ❌\n")

def handle_transaction_choice(choice, user_data):
    clear_screen()
    display_main_screen()

    bank_data = get_user_bank_data(user_data[0])
    balance = get_balance(bank_data)
    today = datetime.today().strftime("%Y-%m-%d")

    if choice == 0:
        print("💰 Your balance is: $", balance)
    elif choice == 1:
        handle_withdrawal(balance, user_data, today)
    elif choice == 2:
        print("🔄 Transaction History:")
        transaction_history(user_data[0])
    elif choice == 3:
        handle_deposit(balance, user_data, today)
    elif choice == EXIT_OPTION:
        print("Exiting the application... 🚪👋")
        return False
    return True

def filter_transactions(bank_data, start_date, end_date, user_id):
    filtered_data = []
    for row in bank_data:
        try:
            created_at = datetime.strptime(row[USER_CREATED_AT_FIELD_NAME], "%Y-%m-%d")
            if (start_date <= created_at <= end_date) and (user_id == '' or row[USER_ID_FIELD_NAME] == user_id):
                filtered_data.append(row)
        except (ValueError, KeyError):
            continue
    return filtered_data

def display_transactions_paginated(filtered_data, page, rows_per_page=6):
    start_index = (page - 1) * rows_per_page
    end_index = start_index + rows_per_page

    print("\nTransaction History")
    print("-" * 75)
    print(f"{BANK_TRANSACTION_FIELD_NAME:<15}{USER_ID_FIELD_NAME:<10}{'Balance':<10}{'Withdraw':<10}{'Deposit':<10}{USER_CREATED_AT_FIELD_NAME:<15}")
    print("-" * 75)

    for row in islice(filtered_data, start_index, end_index):
        print(
            f"{row[BANK_TRANSACTION_FIELD_NAME]:<15}{row[USER_ID_FIELD_NAME]:<10}{row['Balance']:<10}{row['Withdraw']:<10}"
            f"{row['Deposit']:<10}{row[USER_CREATED_AT_FIELD_NAME]:<15}"
        )

    print("-" * 75)

def transaction_history(user_id):
    clear_screen()
    display_main_screen()

    bank_data = load_bank_data()

    start_date, end_date = get_date_range()
    if start_date is None or end_date is None:
        return

    filtered_data = filter_transactions(bank_data, start_date, end_date, user_id)
    filtered_data = filter_by_user_id(filtered_data, user_id)

    if not filtered_data:
        print("No transactions found for the given filters.")
        return

    paginate_transactions(filtered_data)

def load_bank_data():
    bank_data = []
    with open(BANK_FILE_NAME, "r") as txtfile:
        next(txtfile)
        for line in txtfile:
            fields = line.strip().split(" | ")
            bank_data.append({
                BANK_TRANSACTION_FIELD_NAME: fields[0],
                USER_ID_FIELD_NAME: fields[1],
                "Balance": fields[2],
                "Withdraw": fields[3],
                "Deposit": fields[4],
                USER_CREATED_AT_FIELD_NAME: fields[5],
            })
    return bank_data

def get_date_range():
    start_date_input = input("Enter the starting date (YYYY-MM-DD): ")
    end_date_input = input("Enter the ending date (YYYY-MM-DD): ")

    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
        return start_date, end_date
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return None, None

def filter_by_user_id(data, user_id):
    return [row for row in data if row[USER_ID_FIELD_NAME] == user_id] if user_id else data

def paginate_transactions(data):
    total_pages = -(-len(data) // 6)
    page = 1

    while True:
        display_transactions_paginated(data, page)

        next_action = input("Type 'next' for next page, 'prev' for previous page, or 'exit' to quit: ").lower()
        page = navigate_pages(next_action, page, total_pages)
        if page is None:
            break

def navigate_pages(action, current_page, total_pages):
    if action == "next" and current_page < total_pages:
        return current_page + 1
    elif action == "prev" and current_page > 1:
        return current_page - 1
    elif action == "exit":
        return None
    else:
        print("Invalid action or no more pages in the chosen direction.")
        return current_page

def handle_withdrawal(balance, user_data, date):
    amount = int(input("Enter amount withdrawn: "))
    if amount > balance:
        print("Error: Insufficient funds!")
    else:
        updated_balance = balance - amount
        create_bank_record([generate_id(BANK_FILE_NAME), user_data[0], updated_balance, amount, 0, date])
        print("💰 Your total balance is: $" + str(updated_balance))

def handle_deposit(balance, user_data, date):
    amount = int(input("Enter amount to deposit: "))
    updated_balance = balance + amount
    create_bank_record([generate_id(BANK_FILE_NAME), user_data[0], updated_balance, 0, amount, date])
    print("⬇️ You deposited: $" + str(amount))
    print("💰 Your total balance is: $" + str(updated_balance))

def generate_id(file_name):
    with open(file_name, "r") as txtfile:
        rows = txtfile.readlines()
        return 1000 if len(rows) <= 1 else int(rows[-1].split(" | ")[0]) + 1

def create_bank_record(record):
    with open(BANK_FILE_NAME, "a") as txtfile:
        txtfile.write(" | ".join(map(str, record)) + "\n")

def get_balance(bank_data):
    try:
        return int(bank_data[-1]["Balance"])
    except (IndexError, ValueError, KeyError):
        return 0

def get_user_bank_data(user_id):
    bank_data = []
    with open(BANK_FILE_NAME, "r") as txtfile:
        for line in txtfile:
            fields = line.strip().split(" | ")
            if fields[1] == user_id:  # Match the User ID
                bank_data.append({
                    BANK_TRANSACTION_FIELD_NAME: fields[0],
                    USER_ID_FIELD_NAME: fields[1],
                    "Balance": fields[2],
                    "Withdraw": fields[3],
                    "Deposit": fields[4],
                    USER_CREATED_AT_FIELD_NAME: fields[5],
                })
    return bank_data

def files_exist():
    return path.isfile(USER_FILE_NAME) and path.isfile(BANK_FILE_NAME)

def authenticate_user(account_number):
    with open(USER_FILE_NAME, "r") as txtfile:
        for line in txtfile:
            if line.split(" | ")[2] == account_number:
                return line.strip().split(" | ")
    return None

def verify_password(input_pin, stored_pin):
    return int(stored_pin) == input_pin

def prompt_continue():
    while True:
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response in ["yes", "no"]:
            return response == "yes"

def initialize_users():
    with open(USER_FILE_NAME, 'w') as txtfile:
        users = [
            (1001, "Alice Johnson", "1234567890", 1234, "2023-11-29 12:09:19"),
            (1002, "Bob Smith", "9876543210", 5678, "2023-11-29 12:09:19"),
            (1003, "Charlie Brown", "1357924680", 9012, "2023-11-29 12:09:19"),
            (1004, "David Lee", "2468012345", 3456, "2023-11-29 12:09:19"),
            (1005, "Emily Wong", "5678901234", 7890, "2023-11-29 12:09:19"),
            (1006, "Frank White", "6789012345", 1111, "2023-11-29 12:09:19"),
            (1007, "Grace Brown", "7890123456", 2222, "2023-11-29 12:09:19"),
            (1008, "Hannah Black", "8901234567", 3333, "2023-11-29 12:09:19"),
            (1009, "Ivy Green", "9012345678", 4444, "2023-11-29 12:09:19"),
            (1010, "Jack Blue", "0123456789", 5555, "2023-11-29 12:09:19"),
            (1011, "Kim White", "1122334455", 6666, "2023-11-29 12:09:19"),
            (1012, "Liam Red", "2233445566", 7777, "2023-11-29 12:09:19"),
            (1013, "Mia Violet", "3344556677", 8888, "2023-11-29 12:09:19"),
            (1014, "Noah Orange", "4455667788", 9999, "2023-11-29 12:09:19"),
            (1015, "Olivia Yellow", "5566778899", 1010, "2023-11-29 12:09:19"),
            (1016, "Paul Brown", "6677889900", 2020, "2023-11-29 12:09:19"),
            (1017, "Quinn Silver", "7788990011", 3030, "2023-11-29 12:09:19"),
            (1018, "Riley Copper", "8899001122", 4040, "2023-11-29 12:09:19"),
            (1019, "Sophie Gold", "9900112233", 5050, "2023-11-29 12:09:19"),
            (1020, "Tom Purple", "1001223344", 6060, "2023-11-29 12:09:19"),
            (1021, "Uma Steel", "2112334455", 7070, "2023-11-29 12:09:19"),
            (1022, "Victor Bronze", "3223445566", 8080, "2023-11-29 12:09:19"),
            (1023, "Wendy Platinum", "4334556677", 9090, "2023-11-29 12:09:19"),
            (1024, "Xander Copper", "5445667788", 1011, "2023-11-29 12:09:19"),
            (1025, "Yara Diamond", "6556778899", 1111, "2023-11-29 12:09:19")
        ]

        for user in users:
            txtfile.write(" | ".join(map(str, user)) + "\n")

def initialize_bank():
    with open(BANK_FILE_NAME, 'w') as txtfile:
        txtfile.write(" | ".join(BANK_FILE_FIELD_NAMES) + "\n")

def initialize_files():
    if not files_exist():
        initialize_users()
        initialize_bank()

def terminal_getpass(prompt='Password: '):
    for c in prompt:
        msvcrt.putch(c.encode())
    pw = ""
    while 1:
        c = msvcrt.getch()
        if c == b'\r' or c == b'\n':
            break
        if c == b'\003':
            raise KeyboardInterrupt
        if c == b'\b':
            pw = pw[:-1]
            msvcrt.putch(b'\b')
        else:
            pw = pw + c.decode()
            msvcrt.putch(b"*")
    msvcrt.putch(b'\r')
    msvcrt.putch(b'\n')
    return pw

def verify_user_pin(user_data):
    pin = terminal_getpass("Enter your pin: ")
    return verify_password(int(pin), user_data[3])


def run_transaction_flow(user_data):
    while True:
        display_transaction_options()
        try:
            choice = int(input("Enter your choice: "))
            if not handle_transaction_choice(choice, user_data):
                break
        except ValueError:
            print("Invalid input. Please enter a valid option.")

        if not prompt_continue():
            break

def main():
    clear_screen()
    initialize_files()
    display_main_screen()

    account_number = input("Enter your account number: ")
    user_data = authenticate_user(account_number)

    if not user_data:
        print("Account not found!")
        return

    if not verify_user_pin(user_data):
        print("Invalid credentials!")
        return

    print(f"Welcome, {user_data[1]}!")
    run_transaction_flow(user_data)

if __name__ == "__main__":
    main()
