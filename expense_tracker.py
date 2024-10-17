from expense import Expense
import os
import calendar
import datetime
from google.oauth2.service_account import Credentials
import gspread

# Authenticate using service account JSON
json_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
creds = Credentials.from_service_account_file(json_path, scopes=[
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
])

# Function to authenticate and open Google Sheet
def get_sheet():
    client = gspread.authorize(creds)
    SHEET_ID = '1MfuLY5V8gAxtZ0_M-_aYEs09ugq_0hQarBgjHDTmySc'  # Replace with your Google Sheet ID
    sheet = client.open_by_key(SHEET_ID)
    return sheet

def main():
    print(f"🎯 Running Expense Tracker!")
    budget = 2000

    # Get the Google Sheet
    sheet = get_sheet()

    # Ensure headers are set up correctly (name, price, category)
    setup_headers(sheet)

    # Get user input for expense.
    expense = get_user_expense()

    # Save the expense to Google Sheets.
    save_expense_to_sheet(expense, sheet)

    # Summarize the expenses from Google Sheets.
    summarize_expenses_from_sheet(sheet, budget)

def get_user_expense():
    print(f"🎯 Getting User Expense")
    expense_name = input("Enter expense name: ")
    expense_amount = float(input("Enter expense amount: "))
    expense_categories = [
        "🍔 Food",
        "🏠 Home",
        "💼 Work",
        "🎉 Fun",
        "✨ Misc",
    ]

    while True:
        print("Select a category: ")
        for i, category_name in enumerate(expense_categories):
            print(f"  {i + 1}. {category_name}")

        value_range = f"[1 - {len(expense_categories)}]"
        selected_index = int(input(f"Enter a category number {value_range}: ")) - 1

        if selected_index in range(len(expense_categories)):
            selected_category = expense_categories[selected_index]
            new_expense = Expense(
                name=expense_name, category=selected_category, amount=expense_amount
            )
            return new_expense
        else:
            print("Invalid category. Please try again!")

# Function to ensure headers are set in the sheet
def setup_headers(sheet):
    worksheet = sheet.get_worksheet(0)  # Assuming first worksheet
    headers = worksheet.row_values(1)
    expected_headers = ['Name', 'Price', 'Category']

    # Only add headers if they aren't present
    if headers != expected_headers:
        worksheet.update('A1', [expected_headers])

# Function to save the expense in a table format in Google Sheet
def save_expense_to_sheet(expense: Expense, sheet):
    # Append the new expense to the Google Sheet in the correct columns
    worksheet = sheet.get_worksheet(0)  # Assuming you are using the first worksheet
    worksheet.append_row([expense.name, expense.amount, expense.category])

# Function to summarize expenses from Google Sheets
def summarize_expenses_from_sheet(sheet, budget):
    worksheet = sheet.get_worksheet(0)
    expenses = worksheet.get_all_records()  # Fetch all data from the sheet (ignore headers)
    print(expenses)

    col_values = worksheet.col_values(2)[1:]  # Assuming there's a header row in row 1
    numeric_values = [float(value) for value in col_values if value.isnumeric()]
    print(numeric_values)


    total_spent = sum(numeric_values)
#    amount_by_category = {}


# Print the summary
#    print("Expenses By Category 📈:")
#    for key, amount in amount_by_category.items():
#        print(f"  {key}: ${amount:.2f}")

    print(f"💵 Total Spent: {total_spent:.2f}")

    remaining_budget = budget - total_spent
    print(f"✅ Budget Remaining: {remaining_budget:.2f}")

    # Calculate remaining days of the month
    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    if remaining_days > 0:
        daily_budget = remaining_budget / remaining_days
        print(green(f"👉 Budget Per Day: {daily_budget:.2f}"))
    else:
        print("No remaining days in this month.")

# Function to add color to text (green)
def green(text):
    return f"\033[92m{text}\033[0m"

if __name__ == "__main__":
    main()
