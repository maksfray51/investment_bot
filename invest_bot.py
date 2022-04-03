import Constants
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

GENDER, NAME, AGE, BIO = range(4)


def start(update: Update, context: CallbackContext) -> int:
    """Starting the conversation"""
    reply_keyboard = [['Boy', 'Girl', 'Other?']]

    update.message.reply_text(
        'Привет, друг!\n'
        'Меня зовут Инвест Бот. Я помогаю ответить на замечательный вопрос: "Сколько денег нужно для счастья?"\n\n'
        'Все хотят получить ответ на этот вопрос как можно скорее, но перед тем, как ответить на него, я бы хотел с '
        'тобой познакомиться.\n'
        'Ты мальчик(мужчинка/мужчина) или девочка(девушка, женщина)?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Boy? Girl? Space alien? Dog?',
            resize_keyboard=True
        )
    )
    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    """Starting the risk test"""
    user = update.message.from_user
    logger.info("Gender of %s %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Отлично! Теперь давай узнаем как тебя зовут',
        reply_markup=ReplyKeyboardRemove(input_field_placeholder='Как тебя зовут?'),
    )
    return NAME


def name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Name of %s %s", user.first_name, update.message.text)

    reply_keyboard = [['Меньше 25', '25-35', '35-50', 'Больше 50']]

    update.message.reply_text(
        f'Приятно познакомиться, {update.message.text}!\n'
        'Подскажи, сколько тебе лет?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Age?', resize_keyboard=True
        )
    )

    return AGE


def age(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Age of %s %s", user.first_name, update.message.text)

    update.message.reply_text('Спасибо тебе за ответы! До новых встреч!')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation", user.first_name)

    update.message.reply_text('Bye! Hope we`ll talk soon', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(Constants.API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            NAME: [MessageHandler(Filters.text, name)],
            AGE: [MessageHandler(Filters.text, age)],

        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
