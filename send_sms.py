import os
from twilio.rest import Client


# Twilio authentication credentials
account_sid = os.getenv('AC7b8570f82fad2c936a111cb5a5cde978')
auth_token = os.getenv('d9ac818bcb4caf620fe94e849d6c7ab7')
twilio_number = os.getenv('+12706793374')
messaging_service_sid = os.getenv('MG8dcb57207af16ec2b50885ae75598637')


# E-wallet balance
#ewallet_balance = 0

# Twilio client
client = Client(account_sid, auth_token)


# Function to send SMS message
async def send_sms(message):
    client.messages.create(
        body=message,
        from_=twilio_number,
        to='+84373104304',
        messaging_service_sid = messaging_service_sid
    )

# Command handler for /balance command
async def balance(update, context):
    #global ewallet_balance
    message = f'Số dư trong ví của bạn hiện tại là {balance} đồng.'
    await update.message.reply_text(message)
    send_sms(message)

# Command handler for /deposit command
async def deposit(update, context):
    #global ewallet_balance
    amount = int(context.args[0])
    ewallet_balance += amount
    message = f'Số dư trong ví của bạn đã tăng lên {balance} đồng.'
    await update.message.reply_text(message)
    send_sms(message)

# Command handler for /withdraw command
async def withdraw(update, context):
    #global ewallet_balance
    amount = int(context.args[0])
    if amount > ewallet_balance:
        await update.message.reply_text('Số dư trong ví của bạn không đủ để thực hiện giao dịch này.')
    else:
        ewallet_balance -= amount
        message = f'Số dư trong ví của bạn đã giảm xuống {balance} đồng.'
        await update.message.reply_text(message)
        send_sms(message)

