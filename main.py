import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from random import randint
import analysis

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

my_fav_subs = ["sub1"]


TEMP_FOLDER = "temp" # for files with conversations
os.makedirs(TEMP_FOLDER, exist_ok=True)

TOKEN = "mytoken"


async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""

    await update.message.reply_text("Привет, чтобы я проанализировал переписку, предлагаю тебе прислать мне json-файлик \nКак это сделать написано <a href='https://telegra.ph/Kak-ehksportirovat-perepisku-chtoby-bot-eyo-prochital-01-04'> ТУТ! </a>", parse_mode= 'HTML')


async def handle_document(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.username in my_fav_subs:

        document = update.message.document
        file = await document.get_file()
        file_path = os.path.join(TEMP_FOLDER, str(randint(1, 10000))+document.file_name)
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"✅ Подождите пару минут!")

        answer = analysis.run_analyze(file_path)
        for x in range(0, len(answer), 4096):
            await update.message.reply_text(answer[x:x+4096], parse_mode="Markdown")
        os.remove(file_path)
        os.remove(file_path.replace(".json", ".txt"))
        os.remove(file_path.replace(".json", "_result.txt"))
        
    else:

        await update.message.reply_text(
            f"Пока бот работает в тестовом режиме и тестить его могуть только подписчики @vibeaddiction \n\rНапиши @Rreflector чтобы тоже воспользоваться ботом!"
        )


def main() -> None:

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()