from aiogram import Bot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_BOT_TOKEN')

async def get_chat_id():
    bot = Bot(token=API_TOKEN)
    updates = await bot.get_updates()
    if updates:
        chat_id = updates[-1].message.chat.id
        print(f"Ваш chat_id: {chat_id}")
        print("Добавьте этот chat_id в файл .env")
    else:
        print("Нет доступных обновлений. Отправьте сообщение боту и попробуйте снова.")
    await bot.session.close()

if __name__ == '__main__':
    asyncio.run(get_chat_id())