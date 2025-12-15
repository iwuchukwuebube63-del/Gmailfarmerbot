import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Telegram bot token
TOKEN = '8407604450:AAEfDPd7kjOWtdnQe82TQfvuWjHGkcxY12c'

# Google API credentials
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
SERVICE_ACCOUNT_FILE = '/storage/emulated/0/Download/dulcet-chiller-481423-f9-094a6cce853e.json'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create a Google API client
def create_google_client():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('admin', 'directory_v1', credentials=creds)

# Create a Google account
async def create_account(email, password):
    client = create_google_client()
    user_body = {
        'primaryEmail': email,
        'name': {'familyName': 'User', 'givenName': 'Google'},
        'password': password,
    }
    try:
        client.users().insert(body=user_body).execute()
        return f'Account created: {email}'
    except Exception as e:
        return f'Error: {str(e)}'

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Send me an email address')

async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Now send me a password')

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.user_data['email']
    password = update.message.text
    result = await create_account(email, password)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    email_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler)
    password_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)

    application.add_handler(start_handler)
    application.add_handler(email_handler)
    application.add_handler(password_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
