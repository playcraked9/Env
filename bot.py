import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram and Twilio credentials from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("7729338094:AAH0-e-bVHjOA_V-ykT6z9i1BfFiamchhuo")
TWILIO_ACCOUNT_SID = os.getenv("ACdb504a3a22a24d6dcd969f4cf9a6ddb6")
TWILIO_AUTH_TOKEN = os.getenv("9816759522a2ca0277848fe3ef87ac88")
TWILIO_PHONE_NUMBER = os.getenv("+12093539917")

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# In-memory storage for user OTPs
user_otps = {}

# Function to send OTP via SMS using Twilio
def send_otp_via_sms(phone_number, otp):
    message = twilio_client.messages.create(
        body=f"Your OTP code is: {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# Function to generate a random 6-digit OTP
def generate_otp():
    return random.randint(100000, 999999)

# Command handler for /start
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Use /getotp <phone_number> to receive an OTP via SMS.")

# Command handler to generate and send OTP
async def get_otp(update: Update, context):
    if len(context.args) != 1:
        await update.message.reply_text("Please provide your phone number using the format: /getotp <phone_number>")
        return

    phone_number = context.args[0]
    otp = generate_otp()

    # Store OTP in memory for this user (using chat_id)
    user_otps[update.message.chat_id] = otp

    # Send OTP via SMS
    try:
        send_otp_via_sms(phone_number, otp)
        await update.message.reply_text(f"OTP has been sent to {phone_number}. Please check your SMS.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send OTP: {e}")

# Command handler to verify OTP
async def verify_otp(update: Update, context):
    if len(context.args) != 1:
        await update.message.reply_text("Please provide the OTP using the format: /verifyotp <otp>")
        return

    user_id = update.message.chat_id
    entered_otp = int(context.args[0])

    # Check if the OTP matches
    if user_id in user_otps and user_otps[user_id] == entered_otp:
        await update.message.reply_text("✅ OTP is valid!")
        # Remove OTP after successful verification
        del user_otps[user_id]
    else:
        await update.message.reply_text("❌ Invalid OTP. Please try again.")

# Main function to start the bot
async def main():
    # Create the Application for the bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getotp", get_otp))
    application.add_handler(CommandHandler("verifyotp", verify_otp))

    # Start the bot
    await application.start_polling()

    # Run the bot until the user stops it
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
