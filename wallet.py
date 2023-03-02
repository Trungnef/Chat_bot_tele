import sqlite3
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters,  CallbackContext
import logging
from telegram.constants import ParseMode
from telegram import Update
import config


# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('e_wallet.db')
c = conn.cursor()


# Tạo bảng user nếu chưa tồn tại
c.execute('''CREATE TABLE IF NOT EXISTS user
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              balance INTEGER NOT NULL DEFAULT 0)''')
conn.commit()

# Xử lý lệnh /wallet
async def gumoo(update, context =  CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id, text="Chào mừng đến với E-wallet Gumoo Bot. Hãy tạo tài khoản của bạn bằng cách sử dụng lệnh /register và /helps để biết thêm chức năng!")
  

# Xử lý lệnh /register
async def register(update, context):
    # Lấy thông tin người dùng từ tin nhắn
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Kiểm tra xem người dùng đã đăng ký chưa
    c.execute("SELECT * FROM user WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is not None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Bạn đã đăng ký tài khoản rồi!")
        return

    # Thêm người dùng mới vào cơ sở dữ liệu
    c.execute("INSERT INTO user (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    await context.bot.send_message(chat_id=update.message.chat_id, text="Đăng ký tài khoản thành công!")

# Xử lý lệnh /balance
async def balance(update, context):
    # Lấy thông tin người dùng từ tin nhắn
    user_id = update.message.from_user.id

    # Lấy số dư của người dùng từ cơ sở dữ liệu
    c.execute("SELECT balance FROM user WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Bạn chưa đăng ký tài khoản. Vui lòng sử dụng lệnh /register để đăng ký!")
        return

    balance = result[0]
    await context.bot.send_message(chat_id=update.message.chat_id, text="Số dư của bạn là: {} VND".format(balance))

async def deposit(update, context):
    # Lấy thông tin người dùng từ tin nhắn
    user_id = update.message.from_user.id
    amount = context.args[0]

    # Kiểm tra xem người dùng đã đăng ký chưa
    c.execute("SELECT * FROM user WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Bạn chưa đăng ký tài khoản. Vui lòng sử dụng lệnh /register để đăng ký!")
        return

    # Nạp tiền vào tài khoản của người dùng
    balance = result[2]
    if (int(amount) >= 0):
        balance += int(amount)
        c.execute("UPDATE user SET balance=? WHERE id=?", (balance, user_id))
        conn.commit()
        await context.bot.send_message(chat_id=update.message.chat_id, text="Nạp tiền thành công! Số dư mới của bạn là: {} VND".format(balance))
    else:     
        await context.bot.send_message(chat_id=update.message.chat_id, text="Âm tiền rồi nhóc dùng withdraw đi thằng óc :3")

async def withdraw(update, context):
    # Lấy thông tin người dùng từ tin nhắn
    user_id = update.message.from_user.id
    amount = context.args[0]

    # Kiểm tra xem người dùng đã đăng ký chưa
    c.execute("SELECT * FROM user WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Bạn chưa đăng ký tài khoản. Vui lòng sử dụng lệnh /register để đăng ký!")
        return

    # Rút tiền từ tài khoản của người dùng
    balance = result[2]
    if balance < int(amount):
        await context.bot.send_message(chat_id=update.message.chat_id, text="Số dư của bạn không đủ để thực hiện giao dịch này!")
        return
    if (int(amount) >= 0):
        balance -= int(amount)
        c.execute("UPDATE user SET balance=? WHERE id=?", (balance, user_id))
        conn.commit()
        await context.bot.send_message(chat_id=update.message.chat_id, text="Rút tiền thành công! Số dư mới của bạn là: {} VND".format(balance))
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Cạu bị ảo đá à! Rút âm sao được ạ :3")
        
async def balances(update, context):
    # Lấy thông tin người dùng từ tin nhắn
    user_id = update.message.from_user.id

    # Kiểm tra xem người dùng đã đăng ký chưa
    c.execute("SELECT * FROM user WHERE id=?", (user_id,))
    result = c.fetchone()
    if result is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Bạn chưa đăng ký tài khoản. Vui lòng sử dụng lệnh /register để đăng ký!")
        return

    # Hiển thị số dư tài khoản của người dùng
    balance = result[2]
    await context.bot.send_message(chat_id=update.message.chat_id, text="Số dư tài khoản của bạn là: {} VND".format(balance))
    
async def helps(update, context):
    help_message = '''
    Bot e-wallet hỗ trợ các lệnh sau:
    /register - Đăng ký tài khoản
    /deposit + [số tiền] - Nạp tiền vào tài khoản
    /withdraw + [số tiền] - Rút tiền từ tài khoản
    /balances - Hiển thị số dư tài khoản
    /helps - Hiển thị trợ giúp
    /stop - Để dừng lại
    /back - Để quay lại bot Gumoo
    '''
    await context.bot.send_message(chat_id=update.message.chat_id, text=help_message)
    
async def stop(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id, "Bot is stopping...")
    # Stop the updater
    context.bot.update.stop()
    # Stop the event loop
    context.bot.update.is_idle = False
    


