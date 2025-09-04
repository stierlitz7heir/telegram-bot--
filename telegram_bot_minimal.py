#!/usr/bin/env python3
"""
Минимальная версия Telegram бота для Render
"""
import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('BOT_TOKEN', "7292664340:AAE6D9rOSq3Ay6ItoZuFGLA15jeHgieB0V0")
bot = telebot.TeleBot(BOT_TOKEN)

# ID пользователя
USER_ID = None

def create_main_keyboard():
    """Создает основную клавиатуру с кнопками"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔍 Проверить сейчас", callback_data="check_now"),
        InlineKeyboardButton("📊 Статус", callback_data="status")
    )
    keyboard.add(
        InlineKeyboardButton("📅 Текущая дата", callback_data="current_date"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    
    return keyboard

def test_website():
    """Тестирует доступность сайта"""
    try:
        response = requests.get("https://politehnikum-eng.ru", timeout=10)
        return response.status_code == 200
    except:
        return False

@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    global USER_ID
    USER_ID = message.from_user.id
    
    logger.info(f"Бот запущен пользователем {USER_ID}")
    
    try:
        welcome_text = (
            "🤖 Бот мониторинга расписания запущен!\n\n"
            "Это минимальная версия бота для тестирования.\n"
            "Используйте кнопки ниже для управления:"
        )
        
        bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        bot.reply_to(message, f"❌ Ошибка при запуске: {e}")

@bot.message_handler(commands=['check'])
def check_command(message):
    """Обработчик команды /check - принудительная проверка"""
    logger.info(f"Принудительная проверка от пользователя {message.from_user.id}")
    
    try:
        bot.reply_to(message, "🔍 Выполняю проверку...", reply_markup=create_main_keyboard())
        
        # Тестируем сайт
        site_available = test_website()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        check_result = f"""
🔍 РЕЗУЛЬТАТ ПРОВЕРКИ

⏰ Время проверки: {current_time}
🌐 Статус сайта: {'✅ Доступен' if site_available else '❌ Недоступен'}
🤖 Статус бота: ✅ Работает
📊 Платформа: Render

✅ Проверка завершена!
        """
        
        bot.send_message(message.chat.id, check_result, reply_markup=create_main_keyboard())
        
    except Exception as e:
        logger.error(f"Ошибка при принудительной проверке: {e}")
        bot.reply_to(message, f"❌ Ошибка при проверке: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Обработчик callback запросов"""
    try:
        if call.data == "check_now":
            bot.answer_callback_query(call.id, "🔍 Проверка...")
            
            site_available = test_website()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if site_available:
                result = f"✅ Проверка выполнена!\n⏰ Время: {current_time}\n🌐 Сайт доступен"
            else:
                result = f"⚠️ Проверка выполнена!\n⏰ Время: {current_time}\n❌ Сайт недоступен"
            
            bot.send_message(call.message.chat.id, result, reply_markup=create_main_keyboard())
            
        elif call.data == "status":
            site_available = test_website()
            
            status_text = f"""
📊 СТАТУС БОТА:

🆔 USER_ID: {USER_ID}
⏰ Время: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🌐 Платформа: Render
🤖 Статус: ✅ Работает
🔗 Сайт: {'✅ Доступен' if site_available else '❌ Недоступен'}

ℹ️ Минимальная версия бота
            """
            bot.edit_message_text(status_text, call.message.chat.id, call.message.message_id, reply_markup=create_main_keyboard())
            
        elif call.data == "current_date":
            current_date = datetime.now().strftime("%d.%m.%Y")
            bot.answer_callback_query(call.id, f"📅 {current_date}")
            bot.send_message(call.message.chat.id, f"📅 Текущая дата: {current_date}", reply_markup=create_main_keyboard())
            
        elif call.data == "help":
            help_text = """
❓ СПРАВКА:

🤖 Минимальная версия бота

✅ ФУНКЦИИ:
• Проверка статуса бота
• Тестирование сайта
• Отображение времени

🔧 КОМАНДЫ:
/start - Запустить бота
/check - Принудительная проверка

📞 ПОДДЕРЖКА:
Бот работает на Render
            """
            bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, reply_markup=create_main_keyboard())
            
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик всех остальных сообщений"""
    try:
        welcome_text = (
            "🤖 Минимальная версия бота:\n\n"
            "Используйте кнопки ниже для управления или команды:\n"
            "/start - Запустить бота\n"
            "/check - Проверка\n"
            "/help - Справка"
        )
        bot.reply_to(message, welcome_text, reply_markup=create_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

if __name__ == "__main__":
    logger.info("🚀 Запуск минимального Telegram бота...")
    logger.info("Отправьте /start боту для начала работы")
    
    try:
        # Запускаем бота
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
