# import below, to work Telegram Bot with Django Rest Framework properly
# start

import sys

sys.dont_write_bytecode = True

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

django.setup()

from app import models

from asgiref.sync import sync_to_async
# end


from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

import datetime

from generation import execute
from dotenv import load_dotenv

TELEGRAM_BOT_TOKEN = ""  # test token
COHERE_API_KEY = ""  # test key

(MENU_STATE,
 CHAT_STATE,
 PRICING_STATE,
) = range(3)


MAIN_MENU_KEYBOARD = [['💬 Начать диалог', '💼 Профиль'], ['💳 Стоимость']]
TARIFF_KEYBOARD = [['🎞 Базовый', '🎫 Оптимальный', '🎟 Премиум'], ['🔙 назад']]

CHANNEL_LINK = ""
CHANNEL_USERNAME = ""

DEVELOPER = "@"
SUPPORT_BOT = ""

VISA_CARD_NUMBER = ""
BITCOIN_ADDRESS = ""
ETHEREUM_ADDRESS = ""


def date_plus_(n):
    today = datetime.datetime.today()
    future_date = today + datetime.timedelta(days=n)
    print('today:', today)
    print('future_date:', future_date.strftime("%Y-%m-%d"))
    return future_date.strftime("%Y-%m-%d")

def get_date():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    print('get_date:', date)
    return date


def get_time():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return time

def left_days_(date):
    today = datetime.datetime.today()
    future_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    print('today:', today)
    print('future_date:', future_date)
    delta = future_date - today
    print('delta:', delta.days)
    return delta.days

@sync_to_async
def _post_client(user):
    try:
        models.TGClient(
            tg_id=user['id'],
            username=user['username'],
        ).save()

        return True
    except Exception as e:
        print(e)
        return False

@sync_to_async
def _post_balance(user):
    try:
        models.Balance(
            tg_id=user['id'],
            tariff='Free Trial',
            next_payment=date_plus_(3),
        ).save()

        return True
    except Exception as e:
        print(e)
        return False

    
@sync_to_async
def _upd_balance(user_id, tariff):
    try:
        models.Balance.objects.filter(tg_id=user_id).update(
            tariff=tariff,
            next_payment=date_plus_(30),
        )

        return True
    except Exception as e:
        print(e)
        return False

@sync_to_async
def _get_client_balance(user_id):
    return models.Balance.objects.filter(tg_id=user_id).values()

@sync_to_async
def _get_tariff(name):
    return models.Pricing.objects.filter(name=name).values()

@sync_to_async
def _is_client(user_id):
    return models.TGClient.objects.filter(tg_id=user_id).exists()

@sync_to_async
def _get_client(user_id):
    return models.TGClient.objects.filter(tg_id=user_id).values()

@sync_to_async
def _get_clients():
    return models.TGClient.objects.all().values()

def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        return update.message.new_chat_members[0].username == CHANNEL_USERNAME
    except Exception as e:
        print(e)
        return False


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id
    context.user_data['username'] = user.username

    if not await _is_client(context.user_data['id']):
        await _post_client(context.user_data)
        await _post_balance(context.user_data)

    await update.message.reply_text('🤖🧠💠 Приветствую, ' + user.first_name + '!')
    
    await update.message.reply_text(
        '\nВыберите опцию:',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False),
    )

    return MENU_STATE


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id
    context.user_data['username'] = user.username

    await update.message.reply_text(
        '\nВыберите опцию:',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False),
    )

    return MENU_STATE
    

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id

    txt = """
✍️ Искусственный интеллект готов ответить на любой вопрос.

Например,можно спросить Что такое квантовые волны,а также можно узнать почему татары любят чак-чак и можно попросить Написать сочинение про Татарстан
"""

    await update.message.reply_text(text=txt)

    return CHAT_STATE


async def chat_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text

    if prompt:
        await update.message.reply_text('🖨 Информация уже в пути ...')

        balance = await _get_client_balance(context.user_data['id'])

        if (abs(int(left_days_(balance[0]['next_payment']))) > 0):
            response = execute(prompt)

            if response:
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Извините, но об этом вам еще рано знать.")
        else:
            await update.message.reply_text("Извините, ваше время на тарифе закончились. Пожалуйста, Обновите свой тариф!")

    return CHAT_STATE


def proceed_payment():

    txt = f"""
Мы принимаем следующие способы оплаты:

VISA
{VISA_CARD_NUMBER}

BITCOIN
{BITCOIN_ADDRESS}

ETHEREUM
{ETHEREUM_ADDRESS}

Отправьте скриншот квитанции об оплате, свое имя пользователя или идентификатор Telegram {SUPPORT_BOT} или {DEVELOPER}

Проверка платежа: {SUPPORT_BOT}
Возникли проблемы? Пишите: {DEVELOPER}
"""
    return txt


async def tariff_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📖 Тарифные опции:',
        reply_markup=ReplyKeyboardMarkup(TARIFF_KEYBOARD, resize_keyboard=True)
    )
    return PRICING_STATE


async def basic_tariff_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = await _get_tariff('Базовый')

    if tariff:
        txt = f"""
🌚 Что входит в базовый тариф?:
    💰 Price: руб{tariff[0]['price']}
    🌟 Duration: {tariff[0]['duration']} дней
    """ + proceed_payment()

        await update.message.reply_text(
            text=txt,
        )

    return PRICING_STATE


async def advanced_tariff_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = await _get_tariff('Оптимальный')

    if tariff:
        txt = f"""
🌚 Что входит в оптимальный тариф?:
    💰 Стоимость: руб{tariff[0]['price']}
    🌟 Продолжительность: {tariff[0]['duration']} дней\n
    """ + proceed_payment()

        await update.message.reply_text(
            text=txt,
        )

    return PRICING_STATE


async def premium_tariff_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = await _get_tariff('Премиум')

    if tariff:
        txt = f"""
🌚 Что входит в премиум тариф?:
    💰 Стоимость: руб{tariff[0]['price']}
    🌟 Продолжительность: {tariff[0]['duration']} дней\n
    """ + proceed_payment()

        await update.message.reply_text(
            text=txt,
        )

    return PRICING_STATE



async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = await _get_client(user.id)

    if profile:
        balance = await _get_client_balance(user.id)
        print('balance:', balance)
        plan = await _get_tariff(balance[0]['tariff'])
        print('plan:', plan)

        txt = f"""
💼 Профиль:
    ID: {balance[0]['tg_id']} 
    Ваш тариф: {balance[0]['tariff']} 
    Стоимость: {plan[0]['price']} 
    Продолжительность: {plan[0]['duration']} 
    Осталось дней: {abs(int(left_days_(balance[0]['next_payment'])))} 
    Последний платеж: {balance[0]['created_at'].strftime('%d.%m.%Y')}
    """
        if (abs(int(left_days_(balance[0]['next_payment'])))):
            txt += '\n🛎 Не забудьте обновить свой тарифный план !'

        await update.message.reply_text(
            text=txt,
        )

    return MENU_STATE


# get total client
async def report_len_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cls = await _get_clients()

    await update.message.reply_text(text='🌝 Всего: ' + str(len(cls)))

    return MENU_STATE


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


def main():
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).read_timeout(100). \
        get_updates_read_timeout(100).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_handler),
            CommandHandler('chat', chat_handler),
        ],
        states={
            MENU_STATE: [
                MessageHandler(filters.Regex('.*Начать диалог$'), chat_handler),
                MessageHandler(filters.Regex('.*Профиль$'), profile_handler),
                MessageHandler(filters.Regex('.*Стоимость$'), tariff_handler),
            ],
            CHAT_STATE: [
                MessageHandler(filters.Regex('.*Начать диалог$'), chat_handler),
                MessageHandler(filters.Regex('.*Профиль$'), profile_handler),
                MessageHandler(filters.Regex('.*Стоимость$'), tariff_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_query_handler),
            ],
            PRICING_STATE: [
                MessageHandler(filters.Regex(".*Базовый$"), basic_tariff_handler),
                MessageHandler(filters.Regex(".*Оптимальный$"), advanced_tariff_handler),
                MessageHandler(filters.Regex(".*Премиум$"), premium_tariff_handler),
                MessageHandler(filters.Regex(".*назад$"), menu_handler),
            ],
        },
        fallbacks=[
            CommandHandler('start', start_handler),
            CommandHandler('chat', chat_handler),
            CommandHandler('me', profile_handler),
            CommandHandler('plans', tariff_handler),
            CommandHandler('r', report_len_handler),
            MessageHandler(filters.Regex('.*Начать диалог$'), chat_handler),
            MessageHandler(filters.Regex('.*Профиль$'), profile_handler),
            MessageHandler(filters.Regex('.*Стоимость$'), tariff_handler),
        ],
    )

    app.add_handler(conv_handler)

    app.add_error_handler(error_handler)

    print("updated...")
    app.run_polling()


if __name__ == "__main__":
    main()