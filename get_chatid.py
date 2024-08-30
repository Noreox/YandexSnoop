from aiogram import Bot, types
import asyncio

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Замените на HTTP-API токен вашего бота

async def get_chat_id():
    bot = Bot(token=API_TOKEN)
    updates = await bot.get_updates()
    if updates:
        chat_id = updates[-1].message.chat.id
        print(f"Ваш chat_id: {chat_id}")
    else:
        print("Нет доступных обновлений. Отправьте сообщение боту и попробуйте снова.")
    await bot.session.close()  # Закрытие сессии, не бота

if __name__ == '__main__':
    asyncio.run(get_chat_id())