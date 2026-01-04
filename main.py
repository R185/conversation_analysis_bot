import os
import logging
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from random import randint
import analysis
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TEMP_FOLDER = "temp" # for files with conversations
os.makedirs(TEMP_FOLDER, exist_ok=True)

TOKEN = "mytkn"
CUSTOM_BOT_API_URL = "http://localhost:8081/bot"


async def start(update: Update, context: CallbackContext) -> None:

    await update.message.reply_text("Привет, чтобы я проанализировал переписку, "\
                                    "предлагаю тебе прислать мне json-файлик \nКак это сделать" \
                                    "написано <a href='https://telegra.ph/Kak-ehksportirovat-perepisku-chtoby-bot-eyo-prochital-01-04'> ТУТ! </a>", parse_mode= 'HTML')


async def is_user_subscribed(user_id: int, context: CallbackContext) -> bool:

    member = await context.bot.getChatMember(chat_id="mychnl", user_id=user_id)
    allowed_statuses = [
        ChatMember.ADMINISTRATOR,
        ChatMember.MEMBER,
        ChatMember.OWNER
    ]
    if member.status in allowed_statuses:
        return True
    else:
        return False


async def handle_document(update: Update, context: CallbackContext) -> None:

    if await is_user_subscribed(update.message.from_user.id, context):

        try:
            document = update.message.document
            file = await document.get_file()
            file_path = os.path.join(TEMP_FOLDER, str(randint(1, 10000))+document.file_name)
            await file.download_to_drive(file_path)
            await update.message.reply_text(f"✅ Подождите пару минут!")
            
            answer = await analysis.run_analyze_async(file_path, 250000)
            for x in range(0, len(answer), 4096):
                await update.message.reply_text(answer[x:x+4096])
            os.remove(file_path)
            os.remove(file_path.replace(".json", ".txt"))
            os.remove(file_path.replace(".json", "_result.txt"))
        
        except Exception as e:
            await update.message.reply_text(f"Какая-то страшная ошибка - {e}")
            os.remove(file_path)
            os.remove(file_path.replace(".json", ".txt"))
            os.remove(file_path.replace(".json", "_result.txt"))
        
    else:
        
        await update.message.reply_text(
            f"Пока бот работает в тестовом режиме и тестить его могуть только подписчики @vibeaddiction! \n\r"
        )


def main() -> None:

    application = Application.builder().token(TOKEN).base_url(CUSTOM_BOT_API_URL).concurrent_updates(True).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()