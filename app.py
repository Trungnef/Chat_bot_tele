import os
import telegram
import sqlite3
from flask import Flask, request


TOKEN = '6146399413:AAFOepxo2mHJtyVLIGJLNtKNzbI9Z2UmMGo'

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
#bot = telegram.Bot(token=os.environ.get('6146399413:AAFOepxo2mHJtyVLIGJLNtKNzbI9Z2UmMGo'))

bot = telegram.Bot(token=TOKEN)

# Initialize SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, telegram_id TEXT, wallet_balance INTEGER)''')
conn.commit()

# Define helper functions
def get_user_id(telegram_id):
    """Get user ID from database or create new user if not found"""
    c.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO users (telegram_id, wallet_balance) VALUES (?, ?)", (telegram_id, 0))
        conn.commit()
        return c.lastrowid
    else:
        return result[0]

def get_wallet_balance(user_id):
    """Get user's wallet balance from database"""
    c.execute("SELECT wallet_balance FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is None:
        return 0
    else:
        return result[0]

def update_wallet_balance(user_id, amount):
    """Update user's wallet balance in database"""
    c.execute("UPDATE users SET wallet_balance=wallet_balance+? WHERE id=?", (amount, user_id))
    conn.commit()

# Define Flask routes
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    user_id = get_user_id(chat_id)

    # Check message text for commands
    message_text = update.message.text.lower()
    if message_text.startswith('/balance'):
        wallet_balance = get_wallet_balance(user_id)
        bot.send_message(chat_id=chat_id, text=f"Your wallet balance is {wallet_balance:,} đ")
    elif message_text.startswith('/deposit'):
        amount = int(message_text.split(' ')[1])
        update_wallet_balance(user_id, amount)
        wallet_balance = get_wallet_balance(user_id)
        bot.send_message(chat_id=chat_id, text=f"Your wallet balance has been updated to {wallet_balance:,} đ")
    elif message_text.startswith('/withdraw'):
        amount = int(message_text.split(' ')[1])
        wallet_balance = get_wallet_balance(user_id)
        if wallet_balance < amount:
            bot.send_message(chat_id=chat_id, text="Sorry, you do not have enough balance to withdraw")
        else:
            update_wallet_balance(user_id, -amount)
            wallet_balance = get_wallet_balance(user_id)
            bot.send_message(chat_id=chat_id, text=f"Your wallet balance has been updated to {wallet_balance:,} đ")

