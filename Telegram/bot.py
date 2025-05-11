from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import dotenv
import os
import logging
import traceback
from pathlib import Path
import fitz  # PyMuPDF

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Environment Variables
env_path = Path(__file__).resolve().parent.parent / '.env'

dotenv.load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("Telegram_key")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not TOKEN:
    logger.error("Telegram_key not found in .env file.")
    raise ValueError("Telegram_key not found in .env file. Please check your .env setup.")
if not ADMIN_CHAT_ID:
    logger.error("ADMIN_CHAT_ID not found in .env file.")
    raise ValueError("ADMIN_CHAT_ID not found. Please add your chat ID to .env.")

# PDF Compression Function
def compress_pdf(input_path, output_path, target_size_mb=1):
    doc = fitz.open(input_path)
    doc.save(output_path, garbage=3, deflate=True, clean=True)
    return os.path.getsize(output_path) <= target_size_mb * 1024 * 1024

# Handle PDF Files
async def pdf_handler(update: Update, context: CallbackContext):
    document: Document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    file_path = f"downloads/{file_name}"
    compressed_path = f"downloads/compressed_{file_name}"
    
    # Download the PDF
    await update.message.reply_text("Downloading PDF...")
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(file_path)
    
    # Compress the PDF
    await update.message.reply_text("Compressing PDF...")
    if compress_pdf(file_path, compressed_path):
        await update.message.reply_text("Uploading compressed PDF...")
        await update.message.reply_document(document=compressed_path, caption="Here is your compressed PDF")
    else:
        await update.message.reply_text("Compression failed. File size is still above 1MB.")
    
    # Cleanup
    os.remove(file_path)
    os.remove(compressed_path)

# Error Handler
async def error_handler(update: Update, context: CallbackContext):
    logger.error("Exception while handling update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_text = ''.join(tb_list)
    error_message = f"⚠️ *Error Occurred!*\n📄 *Exception:*\n`{tb_text}`\n👤 *User:* {update.effective_user.full_name if update else 'N/A'}\n📩 *Chat ID:* {update.effective_chat.id if update else 'N/A'}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=error_message, parse_mode='Markdown')

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Send me a PDF, and I'll compress it for you!")

# Main Bot Setup
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), pdf_handler))
    app.run_polling()

if __name__ == "__main__":
    main()