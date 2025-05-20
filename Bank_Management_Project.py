import json, random, getpass, os, pandas as pd, matplotlib.pyplot as plt
from termcolor import colored
from datetime import datetime

#Shows colored text in system terminal
os.system('color')

#Approximate conversion rates to USD
CURRENCY_RATES={
    'USD': 1,
    'INR': 85, 
    'EUR': 0.95, 
    'JPY': 150 
}

#'directory=os.path.join(os.path.expanduser('~'), 'BankData')' for different systems
directory=r'C:\Users\pc\Desktop\my_folder\Python'
os.makedirs(directory, exist_ok=True)
file_path=os.path.join(directory, 'accounts.json')

#Utitlity functions to load and save accounts
def load_data():
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(colored(f"{file_path} not found. Creating a new file.", "yellow"))
        return {}  
    except json.JSONDecodeError:
        print(colored("Error: accounts.json is not in a valid JSON format.", "light_red"))
        return {} 
    
def save_accounts(accounts):
    try:
        with open(file_path, 'w') as file:
            json.dump(accounts, file, indent=4)
    except IOError as e:
        print(colored(f'Error saving accounts data: {e}', 'light_red'))

def generate_account_number():
    return str(random.randint(10000000000, 99999999999))

def currency_converter(amount, from_currency, to_currency):
    try:
        if from_currency==to_currency:
            return amount
        usd_amount=amount*CURRENCY_RATES[to_currency]
        return round(usd_amount/CURRENCY_RATES[from_currency], 2)
    except KeyError:
        print(colored('Unsupported currency type.', 'light_red'))
        return None

#User account creation, and saving accounts data.     
def create_account(accounts):
    print(colored('\n----- Create an Account -----', 'green'))
            
    try:
        name = input('Enter your name: ')
        currency = input('Enter currency (USD, INR, EUR, JPY): ').upper()
        if currency not in CURRENCY_RATES:
            print(colored('Unsupported currency type.', 'light_red'))
            return currency
        account_type = input('Enter account type (Savings/Checking): ').lower()
        
        max_amount=10000
        max_initial_deposit=currency_converter(max_amount, 'USD', currency)
        while True:
            initial_balance = float(input('Enter initial deposit amount: '))
            if initial_balance < 0:
                print("Initial balance amount can't be below zero.")
                return initial_balance
            if initial_balance > max_initial_deposit:
                print(colored(f"Initial balance amount can't be above the threshold value ({max_initial_deposit} {currency}).", 'light_red'))
                return initial_balance
            else:
                pin = getpass.getpass('Set a 4-digit PIN: XXXX')
                if pin.isdigit() and len(pin) == 4:
                    break
                else:
                    print(colored('Invalid PIN. PIN must be a 4-digit number', "light_red"))
                    return pin
                    
        security_question = input('Set a security question for account recovery: ')
        security_answer = getpass.getpass('Set an answer to the security question: XXXX...XXXX')
        account_id = str(len(accounts) + 1).zfill(4)

        accounts[account_id] = {
            'Account number': generate_account_number(),
            'Name': name,
            'Currency': currency,
            'Account type': account_type,
            'Balance': initial_balance,
            'PIN': pin,
            'USD amount': currency_converter(initial_balance, currency, 'USD'),
            'Transactions': [{'type': 'Deposit', 'amount': initial_balance, 'date': str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))}],
            'Loans': 0,
            'Created at': str(datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')),
            'Security question': security_question,
            'Security answer': security_answer,
            'OTP': None,
            'Active': True
        }
        
        save_accounts(accounts)
        print(colored(f'\nAccount created successfully! Your account number is', "light_green"), colored(f'{accounts[account_id]["Account number"]}', "light_blue"), colored('and your account ID is', 'green'), colored(f'{account_id}', "light_blue"))
    except ValueError:
        print(colored('\nInvalid input for initial balance. Please enter a numerical value.', 'light_red'))

def suggest_actions(account_id, accounts):
    account=accounts.get(account_id)
    
    if len(account['Transactions'])<3:
        print(colored('\nTip: Increase your savings by depositing regularly!', 'cyan'))
    if sum(1 for t in account['Transactions'][-1::-3] if t['type']=='Withdrawal')>3:
        print(colored('\nWarning: Frequent withdrawals detected. Consider limiting withdrawals to save more', 'yellow'))
    if account['Balance']==0:
        print(colored('\nSuggestion: You may want to deposit funds to avoid overdraft or low balance issues.', 'light_red'))
    if account["Loans"]>0:
        print(colored("\nAlert: You have due loans to pay as soon as possible.", "light_yellow"))
    else:
        return (colored('\nKeep managing your money wisely. You are doing great!', 'light_blue'))

def check_low_balance(account_id, accounts):
    account=accounts.get(account_id)
    if account['Balance']==0:
        account['USD amount']=0  
    if account['Balance']<500:
        print(colored('\nAlert: Your balance is running low!', 'light_red'))
    save_accounts(accounts)

def predict_balance(account_id, accounts):
    account=accounts.get(account_id)
    
    try:
        if account["Balance"]==0:
            predicted_balance=0
            print(colored("\nPredicted balance in 6 months:", "blue"), colored(f"{predicted_balance} {account['Currency']}", "light_yellow"))
        elif account['Transactions']:
            avg_deposit=sum(t['amount'] for t in account['Transactions'] if t['type']=='Deposit')/max(1, len([t for t in account['Transactions'] if t['type']=='Deposit']))
            avg_withdrawal=sum(t['amount'] for t in account['Transactions'] if t['type']=='Withdrawal')/max(1, len([t for t in account['Transactions'] if t['type']=='Withdrawal']))
            predicted_balance=account['Balance']+(avg_deposit-avg_withdrawal)*6
            print(colored("\nPredicted balance in 6 months:", "blue"), colored(f"{predicted_balance:.2f} {account['Currency']}", "light_yellow"))
        else:
            return (colored('\nNot enough data to predict balance.', 'yellow')) 
    except ZeroDivisionError:
        print(colored('\nError in calculating average transaction amount.', 'light_red'))

def deposit(account_id, accounts):
    print(colored('\n----- Deposit Money -----', 'yellow'))
                    
    account=accounts.get(account_id)
    
    try:
        amount=float(input('Enter deposit amount: '))
        if amount>1000000:
            print(colored(f"Exceeding normal deposit threshold. Please make a deposit under 1000000 {account['Currency']}", "yellow"))
            return None
        account['Balance']+=amount
        account['USD amount']+=currency_converter(amount, account['Currency'], 'USD')
        account['Transactions'].append({'type': 'Deposit', 'amount': amount, 'date': str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))})
        
        save_accounts(accounts)
        print(colored('Deposit successful!', 'yellow'))
        suggest_actions(account_id, accounts)
    except ValueError:
        print(colored('Invalid deposit amount. Amount must be a numerical value.', 'light_red'))

def withdraw(account_id, accounts):
    print(colored('\n----- Withdraw Money -----', 'yellow'))
                    
    account=accounts.get(account_id)
    
    try:
        amount=float(input('Enter withdrawal amount: '))
        if amount<= account['Balance']:
            currency=account['Currency']
            account['Balance']-=amount
            account['USD amount']-= currency_converter(amount, currency, 'USD')
            account['Transactions'].append({'type': 'Withdrawal', 'amount': amount, 'date': str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))})
            
            save_accounts(accounts)
            print(colored('Withdrawal successful!', 'yellow'))
            check_low_balance(account_id, accounts)
            suggest_actions(account_id, accounts)
            predict_balance(account_id, accounts)
        else:
            print(colored("Insufficient balance", 'light_red'))
            check_low_balance(account_id, accounts)
            suggest_actions(account_id, accounts)
    except ValueError:
        print(colored('Invalid withdrawal amount. Amount must be a numerical value.', 'light_red'))

def check_balance(account_id, accounts):
    print(colored('\n----- Check Balance -----', 'light_blue'))
                    
    account=accounts.get(account_id)
    print('Your balance is:', colored(f'{account['Balance']} {account['Currency']}', "yellow"))
    
    check_low_balance(account_id, accounts)

def view_transactions(account_id, accounts):
    account=accounts.get(account_id)
    print('\nTransaction History:')
    
    for transaction in account['Transactions']:
        if transaction['amount']!=0:
            print(f"\t\n{colored(transaction['type'], 'light_magenta')} of {colored(transaction['amount'], 'light_magenta')} on {colored(transaction['date'], 'light_magenta')}")

def accounts_table():
    data=load_data()
    df=pd.DataFrame.from_dict(data, orient='index')
    selected_df=df[['Name', 'Account number', 'Currency', 'Account type', 'Balance']]
    filtered_df=selected_df[df['Active']== True]

    filename=os.path.join(directory, 'bank.csv')
    filtered_df.to_csv(filename, index_label='Account ID')

    transaction_records=[]
    for account_id, details in load_data().items():
        transactions=details.get('Transactions', [])
        for txn in transactions:
            txn_record={
                'Account ID': account_id,
                'Date': txn.get('date'),
                'Type': txn.get('type'),
                'Amount': txn.get('amount'),
                'Transfered to': txn.get('to'),
                'Transfered from': txn.get('from')
            }
            transaction_records.append(txn_record)
    transaction_df=pd.DataFrame(transaction_records)
    txn_filename=os.path.join(directory, 'transactions.csv')
    transaction_df.to_csv(txn_filename, index=False, date_format="Y%-m%-d% H%=i%-s%")

def plot_transaction_history(account_id, accounts): 
    account = accounts.get(account_id)
    
    if not account or 'Transactions' not in account:
        print("No transaction data found.")
        return
    
    dates = []
    amounts = []
    ttypes = []
    
    for t in account['Transactions']:
        try:
            date_obj = datetime.strptime(t['date'], '%d-%m-%Y %H:%M:%S')
            dates.append(date_obj)
            amount = t['amount'] if t['type'] in ['Deposit', 'Transfer In', 'Loan'] else -t['amount']
            amounts.append(amount)
            ttypes.append(t['type'])
        except KeyError:
            continue
    plt.figure(figsize=(10, 5))
    plt.plot(dates, amounts, marker='o', linestyle='-', color='royalblue')
    for i, (x, y, label) in enumerate(zip(dates, amounts, ttypes)):
        plt.annotate(label,
                     (x, y),
                     textcoords='offset points',
                     xytext=(0, 10),
                     ha='center',
                     fontsize=8,
                     color='green')

    plt.title(f"Transaction History for Account ID {account_id}")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to transfer money
def transfer_money(account_id, accounts, recipient_account_id):
    print(colored('\n----- Transfer Money -----', 'light_blue'))
    
    sender_account = accounts.get(account_id)
    recipient_account = accounts.get(recipient_account_id)
    sender_currency=sender_account['Currency']
    recipient_currency=recipient_account['Currency']
    
    try:
        amount = float(input("Enter the amount to transfer: "))
        if amount <= 0:
            print(colored("Transfer amount must be greater than zero.", "light_red"))
            return
        
        if sender_account["Balance"] >= amount:
            sender_account["Balance"] -= amount
            converted_amount=currency_converter(amount, sender_currency, recipient_currency)
            recipient_account["Balance"] += converted_amount
            if converted_amount is None:
                print(colored("Currency conversion failed. Transfer aborted.", "light_red"))
                return
            # Record transactions for both accounts
            sender_account["Transactions"].append({"type": "Transfer Out", "amount": amount, "to": recipient_account["Account number"], "date": str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))})
            recipient_account["Transactions"].append({"type": "Transfer In", "amount": converted_amount, "from": sender_account["Account number"], "date": str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))})

            save_accounts(accounts)
            check_low_balance(account_id, accounts)
            print(colored("\nSuccessfully transferred", "light_green"), colored(f"{amount} {sender_account['Currency']}", 'yellow'), colored("to account number", "light_green"), colored(recipient_account['Account number'], 'light_blue'))
        else:
            print(colored("Insufficient balance.", "light_red"))
    except ValueError:
        print(colored("Invalid input. Please enter a valid number for the amount.", "light_red"))


#AI assistant, answer user's request with pre-coded statements.
def ai_assistant(account_id, accounts):
    print(colored('\n----- AI Assistant -----', 'cyan'))
                    
    print('''Suggested queries:
          
        1. Create account
        2. Withdraw money
        3. Deposit money
        4. Account balance
        5. Transactions
        6. Loan application
        7. PIN recovery
        8. Exit''')
    
    while True:
        query=input('\nAsk the AI Assistant: ').strip().lower()
        
        if query=='create account' or query=='1':
            return create_account(accounts), print(colored("\nAI: To open a new account, go to the main menu and select 'Create Account'.", 'cyan'))
            continue
        elif query=='withdraw money' or query=='2':
            return withdraw(account_id, accounts), print(colored("\nAI: You can withdraw money by selecting 'Withdraw Money' from the main menu and entering your PIN for security.", 'cyan'))
            continue
        elif query=='deposit money' or query=='3':
            return deposit(account_id, accounts), print(colored("\nAI: To deposit money, select 'Deposit Money' from the main menu and follow the instructions.", 'cyan'))
            continue
        elif query=='account balance' or query=='4':
            return check_balance(account_id, accounts), print(colored("\nAI: You can check your balance from the main menu using the 'Check Balance' option.", 'cyan'))
            continue
        elif query=='transactions' or query=='5':
            return view_transactions(account_id, accounts), print(colored("\nAI: To view your transaction history, go to the main menu and select 'View Transactions'.", 'cyan'))
            continue
        elif query=='loan application' or query=='6':
            return apply_for_loan(account_id, accounts), print(colored("\nAI: For loan applications, go to 'Annual Interest and Loans' in the main menu and select 'Apply for Loan'.", 'cyan'))
            continue
        elif query=='pin recovery' or query=='7':
            return recover_pin(account_id, accounts), print(colored("\nAI: If you've forgotten your PIN, you can recover it by selecting 'PIN Recovery' from the security menu in '2FA and Account Recovery' option.", 'cyan'))
            continue
        elif query=='accounts file':
            print(colored(f"AI: The accounts data is stored in a JSON file for secure access and data persistence. Your account data is stored in {file_path}", 'cyan'))
        elif query=='balance prediction':
            return predict_balance(account_id, accounts), print()
        elif query=='low balance alert':
            print(colored("AI: A low balance alert is triggered if your balance falls below a set threshold. Be sure to maintain sufficient funds.", 'cyan'))
        elif query=='ai suggestions':
            print(colored("AI: The AI can suggest deposits if your balance is low or if it detects frequent withdrawals.", 'cyan'))
        elif query=='early advice':
            print(colored("AI: If your transaction count is low, the AI assistant may provide guidance on how to optimize your savings.", 'cyan'))
        elif query=='exit' or query=='8':
            print(colored("AI: Thank you for using the AI assistant.", 'cyan'))
            break
        else:
            print("AI: Sorry, I couldn't understand that query. Please try again.")

def send_otp(account_id, accounts):
    print(colored('\n----- OTP Request -----', 'light_magenta'))
    
    account=accounts.get(account_id)
    otp = random.randint(100000, 999999)
    account['OTP']=otp
    print(colored(f"OTP sent to your accounts file.", "cyan"))  # Placeholder for actual OTP delivery
    
    save_accounts(accounts)

def verify_otp(account_id, accounts):
    print(colored('\n----- OTP Verification -----', 'light_magenta'))
                    
    account=accounts.get(account_id)
    
    try:
        entered_otp=int(input("Enter the OTP: "))
        if entered_otp==account['OTP']:
            print(colored("Access granted.", 'light_green'))
            print(f"Your account PIN: {account['PIN']}")
            account['OTP']=0
            save_accounts(accounts)
        else:
            print(colored('Access denied. Invalid OTP.', 'red'))
            otp = random.randint(100000, 999999)
            account['OTP']=otp
            save_accounts(accounts)
        return False
    except ValueError:
        print('Invalid input. Please enter a numeric value.')
    
def calculate_annual_interest(account_id, accounts):
    print(colored('\n----- Interest Calculation -----', 'light_green'))
                        
    account=accounts.get(account_id)
    
    if account["Account type"].lower() == "savings":
        rate = 0.04  # 4% annual interest for savings
    else:
        rate = 0.02  # 2% for other account types
    interest = round(account["Balance"] * rate, 2)
    account["Balance"] += interest
    account["Transactions"].append({"type": "Interest", "amount": interest, "time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))})
    
    currency_converter(account["Balance"], account['Currency'], 'USD')
    save_accounts(accounts)
    print("Interest of", colored(f"{interest} {account['Currency']}", "green"), "credited.")

def apply_for_loan(account_id, accounts):
    print(colored('\n----- Loan Request -----', 'light_green'))
                        
    account=accounts.get(account_id)
    currency=account["Currency"]
    
    if account["Loans"]>=currency_converter(100000000, "USD", currency):
        print(colored("Warning: Please pay off your due loan amount first. Any further loans will not be provided.", "light_red"))
        print(colored(f"Your remaining loan balance: {account['Loans']}","yellow"))
        return None
    amount = float(input("Enter loan amount: "))
    if account['Account type']=='savings':
        max_amount=100000
    elif account['Account type']=='checking':
        max_amount=10000000
    max_loan=currency_converter(max_amount, 'USD', currency)
    if amount>max_loan:
        print(colored(f"Exceeding normal credit limit. Please make a request under {max_loan} {currency}", "yellow"))
        return None
    duration_years = int(input("Enter loan duration in years: "))
    interest_rate = 0.05  # 5% annual interest
    total_payable = round(amount * ((1 + interest_rate) ** duration_years), 2)
    account["Loans"] += total_payable
    account["Balance"] += amount
    account["Transactions"].append({"type": "Loan", "amount": amount, "time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))})
    
    save_accounts(accounts)
    print(colored(f"Loan of {amount} approved. Total payable amount: {total_payable} {account['Currency']} over {duration_years} year(s)", "green"))

def make_loan_payment(account_id, accounts):
    print(colored('\n----- Loan Payment -----', 'light_green'))
                        
    account=accounts.get(account_id)
    payment_amount = float(input("Enter loan payment amount: "))
    
    if payment_amount <= account["Loans"]:
        account["Loans"] -= payment_amount
        account["Balance"] -= payment_amount
        account["Transactions"].append({"type": "Loan Payment", "amount": payment_amount, "time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))})
              
        save_accounts(accounts)
        print(colored("Loan payment successful.", "green"))
        print(colored(f"Your remaining loan balance: {account['Loans']}","yellow"))
    else:
        print(colored("Amount exceeds outstanding loan balance. ", "light_red"))
        print(colored(f"Your remaining loan balance: {account['Loans']}","yellow"))

def recover_pin(account_id, accounts):
    print(colored('\n----- Account PIN Recovery -----', 'light_magenta'))
                    
    account=accounts.get(account_id)
    answer = getpass.getpass(f"Answer your security question: {account['Security question']}: XXXX...XXXX")
    
    if answer == account["Security answer"]:
        while True:
            new_pin = getpass.getpass("Enter your new PIN: XXXX")
            if new_pin.isdigit() and len(new_pin) == 4:
                    break
            else:
                print('Invalid PIN. PIN must be a 4-digit number')
                return new_pin
        account["PIN"] = new_pin
        
        save_accounts(accounts)
        print(colored("PIN reset successfully!", "green"))
    else:
        print(colored("security answer is incorrect.", "red"))

def deactivate_account(account_id, accounts):
    account=accounts.get(account_id)
    
    print(colored('\n----- Account Deactivation -----', 'light_red'))
        
    confirm=input('Are you sure you want to deactivate your account (yes/no)? ').lower()
        
    if confirm.lower()=='yes':
        account['Active']=False
            
        save_accounts(accounts)
        print(colored('Account deactivated successfully!', 'light_blue'))
        print(colored(f'Withdrew {round(account["Balance"], 2)} successfully!', 'yellow'))
    
    else:
        print(colored('Account deactivation cancelled.', 'light_red'))

#User authentication, for security purpose.
def authenticate(accounts):
    account_id=input('Enter your account ID: ')
    
    # Check if the account ID exists.
    if account_id not in accounts:
        print(colored('Account not found!', 'light_red'))
        return None
    
    if not accounts[account_id]['Active']:
        print(colored('Account is inactive.', 'light_red'))
        return None
    
    attempts=3 # Allow the user 3 attempts to enter the correct PIN.
    while attempts>=0:
        pin=getpass.getpass('Enter your PIN: XXXX')
        
        # Validate the PIN input.
        if pin == accounts[account_id]['PIN']:
            print(colored('Authentication successful!', 'light_green'))
            return account_id # Authentication successful; return the account ID.
        else:
            print(colored('Incorrect PIN!', 'light_red'))
            attempts -= 1
    
    else:
        print(colored('Authentication failed.', 'light_red'))
        return None

#Main program, executes when the program runs. 
def main():
    accounts=load_data()
    
    while True:
        print('\n-----Bank Management System-----')
        print('''\n
    1. Create Account
    2. Deposit Money
    3. Withdraw Money
    4. Check Balance and Money Transfer
    5. View Transactions
    6. AI Assistant
    7. Annual Interest and Loans
    8. 2FA and Account Recovery
    9. Deactivate Account
    10. Exit''')
        
        choice=input('\nChoose an option: ').strip().lower()

        if choice=='1' or choice=='create account':
            create_account(accounts)
        elif choice in ['2', '3', '4', '5', '6', '7', '9', 'deposit money', 'withdraw money', 'check balance', 'view transactions', 'ai assistant', 'annual interest and loans', 'deactivate account']:
            account_id=authenticate(accounts)
            
            if account_id:
                if choice =='2' or choice=='deposit money':
                    deposit(account_id, accounts)
                elif choice =='3' or choice=='withdraw money':
                    withdraw(account_id, accounts)
                elif choice =='4' or choice=='check balance':
                    print(colored("\n----- Check Balance and Money Transfer -----", "blue"))
                    print('''\n
    1. Check account balance
    2. Transfer money''')
                    ch=input("\nEnter your choice: ").lower()
                    
                    if ch=='1'or ch=='check account balance':
                        check_balance(account_id, accounts)
                    elif ch=='2'or ch=='transfer money':
                        recipient_account_id = input("Enter the recipient's account ID: ")
                        if not recipient_account_id in accounts:
                            print(colored("Recipient account not found.", "light_red"))
                        else:
                            transfer_money(account_id, accounts, recipient_account_id)
                    else:
                        print(colored("Invalid choice.", "light_red"))
                elif choice =='5' or choice=='view transactions':
                    print(colored('\n----- View Transaction History -----', 'light_yellow'))
                    view_transactions(account_id, accounts)
                    plot_transaction_history(account_id, accounts)
                elif choice =='6' or choice=='ai assistant':
                    ai_assistant(account_id, accounts)
                elif choice =='7' or choice=='annual interest and loans':
                    print(colored('\n----- Interest Calculation and Loan Approval -----', 'green'))
                    print('''\n
    1. Apply annual interest
    2. Apply for loan
    3. Make loan payment
                    ''')
                    ch=input("\nEnter your choice: ").lower()
                    
                    if ch=='1'or ch=='apply annual interest':
                        calculate_annual_interest(account_id, accounts)
                    elif ch=='2' or ch=='apply for loan':
                        apply_for_loan(account_id, accounts)
                    elif ch=='3' or ch=='make loan payment':
                        make_loan_payment(account_id, accounts)
                    else:
                        print("Invalid choice.", "light_red")
                elif choice =='9' or choice=='deactivate account':
                    deactivate_account(account_id, accounts)
        
        elif choice =='8' or choice=='2fa and account pin recovery':
            account_id=input('Enter your account ID: ')
            
            if account_id in accounts:
                print(colored('\n----- PIN Recovery and 2FA -----', 'light_magenta'))
                print('''\n
    1. Recover account PIN
    2. Send OTP for 2FA
    3. Verify OTP''')
                ch=input('\nEnter your choice: ').lower()
                if ch=='1' or ch=='recover account pin':
                    recover_pin(account_id, accounts)
                elif ch=='2' or ch=='send otp for 2fa':
                    send_otp(account_id, accounts)
                elif ch=='3' or ch=='verify otp':
                    verify_otp(account_id, accounts)
                else:
                    print("Invalid choice.", "light_red")
            else:
                print('Account not found.')
        
        elif choice =='10' or choice=='exit':
            accounts_table()
            print(colored('\nThank you for using the Bank Management System!', 'light_blue'))
            print(colored("\n....Exiting....", 'yellow'))
            input()
            break
        
        else:
            print(colored('\nInvalid choice. Please try again.', "light_red"))

# Run the main function if this script is run directly
if __name__ == "__main__":
    main() 