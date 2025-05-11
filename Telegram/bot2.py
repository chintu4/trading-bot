import os
import logging
import traceback
from pathlib import Path
import fitz  # PyMuPDF
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import dotenv

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
    logger.critical("Telegram_key not found in .env file.")
    raise ValueError("Telegram_key not found in .env file. Please check your .env setup.")
if not ADMIN_CHAT_ID:
    logger.critical("ADMIN_CHAT_ID not found in .env file.")
    raise ValueError("ADMIN_CHAT_ID not found. Please add your chat ID to .env.")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)  # Convert to integer

# Ensure download directory exists
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# PDF Compression Function
def compress_pdf(input_path, output_path, target_size_mb=1, jpeg_quality=70):
    try:
        doc = fitz.open(input_path)
        for i in range(len(doc)):
            for img_index, img in enumerate(doc[i].get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert image to compressed format
                pix = fitz.Pixmap(image_bytes)
                if pix.n > 3:  # Convert CMYK or other formats to RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # Save image in JPEG format with reduced quality
                img_data = pix.tobytes("jpeg", quality=jpeg_quality)
                doc.update_stream(xref, img_data)

        doc.save(output_path, garbage=3, deflate=True, clean=True)
        doc.close()

        file_size = os.path.getsize(output_path)
        is_within_target = file_size <= target_size_mb * 1024 * 1024
        if not is_within_target:
            logger.info(f"Compressed file size: {file_size/(1024*1024):.2f} MB. Target: {target_size_mb} MB")
        return is_within_target
    except Exception as e:
        logger.error(f"Error during compression: {e}")
        return False


# Handle PDF Files
async def pdf_handler(update: Update, context: CallbackContext):
    document: Document = update.message.document
    file_name = document.file_name or "document.pdf"
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    compressed_path = os.path.join(DOWNLOAD_DIR, f"compressed_{file_name}")

    try:
        await update.message.reply_text("Downloading PDF...")
        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_drive(file_path)

        await update.message.reply_text("Compressing PDF...")
        if compress_pdf(file_path, compressed_path, jpeg_quality=70):  # Adjust JPEG quality if needed
            await update.message.reply_text("Uploading compressed PDF...")
            with open(compressed_path, 'rb') as f:
                await update.message.reply_document(document=f, filename=f"compressed_{file_name}", caption="Here is your compressed PDF")
        else:
            await update.message.reply_text("Compression failed. File size is still too large.")

    except Exception as e:
        logger.error(f"Error in pdf_handler: {e}")
        await update.message.reply_text("An error occurred while processing your PDF.")

    finally:
        # Cleanup files
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Error Handler
async def error_handler(update: Update, context: CallbackContext):
    logger.error("Exception while handling update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_text = ''.join(tb_list)
    error_message = f"⚠️ *Error Occurred!*\n📄 *Exception:*\n`{tb_text}`\n👤 *User:* {update.effective_user.full_name if update else 'N/A'}\n📩 *Chat ID:* {update.effective_chat.id if update else 'N/A'}"
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=error_message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send error message to admin: {e}")


# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Send me a PDF, and I'll compress it for you!")


# Main Bot Setup
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), pdf_handler))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
