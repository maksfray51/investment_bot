import Constants
import logging
import locale
import time
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

GENDER, NAME, AGE, X, x_to_print, Y, y_to_print, RETIREMENT_AGE, FINANCIAL_SAFETY_CUSHION, SMALL_CAPITAL, \
    small_capital_to_print, BIG_CAPITAL, RISK_PROFILE_FRIENDS_CHARACTERISTIC_1, RISK_PROFILE_OPINION_2, \
    RISK_PROFILE_TRAVEL_3, RISK_PROFILE_LOSSES_4, RISK_PROFILE_ASSOCIATIONS_5, RISK_PROFILE_ALTERNATIVES_6, \
    RISK_PROFILE_TYPE_OF_ASSETS_7, RISK_PROFILE_PORTFOLIO_DECLINE_8, RISK_PROFILE_EXPERIENCE_9,\
    RISK_PROFILE_RESULT = range(22)

# Переменная, необходимая для подсчёта суммы в тесте на риск профиль
risk_profile_sum = 0
# Дефолтные кнопки, необходимые для теста на риск профиль
risk_profile_keyboard = [['A', 'B', 'C', 'D']]


def switch(answer):
    if answer == 'A':
        return 1
    elif answer == 'B':
        return 2
    elif answer == 'C':
        return 3
    elif answer == 'D':
        return 4


def comatose_portfolio():
    s = "Ваш тип риск профиля — лайтовенький.\n\nВы не особо любите риск и хотели бы получать небольшие дивиденды.\n\n"\
        "Тип сна: долгий дневной сон и крепкий ночной сон\n\n" \
        "Тип актива: банковский вклад\n\nУровень риска: нет риска потери денег при вкладе не превышающем 1.4 млн ₽. " \
        "Такой вклад застрахован государством"
    return s


def moderate_portfolio():
    s = "Твой тип риск профиля — умеренный.\n\n" \
        "Ты готов рисковать, но только после тщательного аналаза ситуации. Тебя будут очень волновать сильные " \
        "колебания рынка, но потерю 10% ты очень даже пережевёшь\n\n" \
        "Тип сна: крепкий ночной сон\n\n" \
        "Тип активов: различные фонды на облигации, ОФЗ (облигации федерального займа)\n\n" \
        "Уровень риска: очень низкий риск, потому что большая часть средств инвестируется в государственные ценные " \
        "бумаги и банковские сертификаты. Обычно это не гарантируется. Ставки варьируются в зависимости от ожидаемых"
    return s


def moderately_aggressive_portfolio():
    s = "Твой тип риск профиля — умеренно агрессивный.\n\nТы не боишься умеренных колебаний рынка. Готов сильно " \
        "рискнуть, чтобы зарабоать как можно больше\n\nТип сна: некоторое ворочание с боку на бок перед тем, " \
        "как заснуть, и яркие сны перед пробуждением\n\n" \
        "Тип активов: диверсифицированный портфель из \"голубых фишек\" американских акций. Фонды недвижимости\n\n" \
        "Уровень риска: риск от умеренного до значительного. В течение любого одного года фактическая доходность " \
        "фактически может быть отрицательной. Диверсифицированные портфели иногда теряют 25% или более от своей " \
        "фактической стоимости. Вопреки некоторым мнениям, это хорошая защита от инфляции в долгосрочной перспективе."
    return s


def aggressive_portfolio():
    s = "Твой тип риск профиль — агрессивный.\n\nТы вообще ненормальный кароче. Хочешь всё сразу и отель и кафе, " \
        "но больше всего тебе хочется много \"деняк\". Ты не боишься потерять вообще всё\n\n" \
        "Тип сна: яркие сны и случайные кошмары. Приступы бессонницы\n\n" \
        "Тип активов: диверсифицированные портфели акций развивающихся рынков\n\n" \
        "Уровень риска: колебания в сторону увеличения или уменьшения от 50% до 75% за один год не являются редкостью,"\
        " но имеют преимущества для диверсификации."
    return s


def risk_profile(risk_sum):
    if 0 < risk_sum <= 6:
        return comatose_portfolio()
    elif 7 < risk_sum <= 13:
        return moderate_portfolio()
    elif 14 < risk_sum <= 20:
        return moderately_aggressive_portfolio()
    elif 21 < risk_sum <= 25:
        return aggressive_portfolio()


def start(update: Update, context: CallbackContext) -> int:
    """Starting the conversation"""
    reply_keyboard = [['Boy', 'Girl', 'Other?']]

    update.message.reply_text(
        'Привет, друг!\n'
        'Меня зовут Инвест Бот. Я помогаю ответить на замечательный вопрос: "Сколько денег нужно для счастья?"\n\n'
        'Все хотят получить ответ на этот вопрос как можно скорее, но перед тем, как ответить на него, я бы хотел с '
        'тобой познакомиться.\n'
        '\nЕсли хочешь остановить тест напиши /cancel\n\n'
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

    global GENDER
    GENDER = update.message.text

    update.message.reply_text(
        'Отлично! Теперь давай узнаем как тебя зовут',
        reply_markup=ReplyKeyboardRemove(input_field_placeholder='Как тебя зовут?'),
    )
    return NAME


def name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Name of %s %s", user.first_name, update.message.text)

    global NAME
    NAME = update.message.text

    # reply_keyboard = [['Меньше 25', '25-35', '35-50', 'Больше 50']]

    update.message.reply_text(
        f'Приятно познакомиться, {update.message.text}!\n'
        'Подскажи, сколько тебе лет? (Напиши, пожалуйста, возраст числом :) )',
        reply_markup=ReplyKeyboardRemove())

    return AGE


def age(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Age of %s %s", user.first_name, update.message.text)

    global AGE
    AGE = int(update.message.text)

    update.message.reply_text(
        'А теперь пришло время ответить на главный вопрос!\n'
        'Для этого нам нужно немного пофантозировать :)\n\n'
        'Давай представим, что ты живёшь в Москве и при этом один(-на). '
        'Как ты думаешь, сколько денег тебе нужно в месяц, чтобы иметь возможность снимать квартиру, ну не совсем '
        'за МКАДом, кушать чуть больше, чем дошик каждый день (сам готовишь себе примитивные блюда). Может, ещё что-то,'
        ' без чего ты не сможешь обойтись. В общем, сейчас мы получим так называемое число Х. Это сумма, на которую '
        'ты сможешь прожить в Моксве один месяц\n\n'
        'P.S. Обещаю, я никому не скажу!\n'
        'P.P.S. В качестве ответа нужно просто ввести сумму в рублях (без пробелов)',
        reply_markup=ReplyKeyboardRemove()
    )
    return X


def number_x(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Number X of %s %s", user.first_name, update.message.text)

    global X
    X = int(update.message.text)

    update.message.reply_text(
        'Спасибо за твоё доверие! '
        'Теперь давай помечтаем...\n\n'
        'Подумай, сколько тебе денег в месяц нужно, чтобы тратить на ВСЁ, что ты хочешь. '
        'Можешь заказывать частные самолёты или летать везде бизнес классом. '
        'Иметь отличную машину или ездить на такси, или водителя...\n\n'
        'Подумай, сколько денег нужно на это всё?',
        reply_markup=ReplyKeyboardRemove()
    )

    return Y


def number_y(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Number Y of %s %s", user.first_name, update.message.text)

    global Y, y_to_print
    Y = int(update.message.text) * 2
    y_to_print = f'{Y:,.0f}'.replace(',', ' ')

    update.message.reply_text(
        'Это число будем называть числом Y.\n\n'
        'На самом деле, многие люди не знают, сколько денег они могли бы тратить в месяц, поэтому'
        ' часто занижают свои ожидания. Поэтому настоящее число Y для тебя это ' + y_to_print + '₽ !\n\n'
        'А теперь давай подумаем, в каком возрасте тебе хотелось бы больше не работь? '
        'В каком возрасте тебе хотелось бы выйти на пенсию?',
        reply_markup=ReplyKeyboardRemove())

    return RETIREMENT_AGE


def retirement_age(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Retirement age of %s %s", user.first_name, update.message.text)

    global RETIREMENT_AGE
    RETIREMENT_AGE = update.message.text

    reply_keyboard = [['Далее']]
    update.message.reply_text('К сожалению, я не могу рассказать, как именно заработать нужное для тебя количество'
                              ' денег, но я могу помочь тебе поставить чёткие цели, благодаря которым, у тебя будет'
                              ' ясность в голове по поводу нужного количества денег.\n\n'
                              'Я хотел бы предложить тебе стратегию, которая разделена на 3 этапа:\n'
                              '1) Стратегия, рассчитанная на 2 года, начиная с сегодняшнего дня\n'
                              '2) Стратегия, рассчитанная на 6-8 лет, начиная с сегодняшнего дня\n'
                              f'3) Стратегия, которая поможет выйти на пенсию в {RETIREMENT_AGE} лет',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, one_time_keyboard=True,
                                  input_field_placeholder='Погнали дальше?',
                                  resize_keyboard=True))

    return FINANCIAL_SAFETY_CUSHION


def financial_safety_cushion(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    # Делаем красивую запись для X
    global x_to_print
    x_to_print = f'{X:,.0f}'.replace(',', ' ')

    # Объявляем глобальную переменную, чтобы функция могла изменить перменную, объявленную на модульном уровне
    global FINANCIAL_SAFETY_CUSHION
    FINANCIAL_SAFETY_CUSHION = 6 * X
    # Аналогично делаем красивую запись для финансовой подушки безопасности
    financial_safety_cushion_to_print = f'{FINANCIAL_SAFETY_CUSHION:,.0f}'.replace(',', ' ')

    reply_keyboard = [['Далее']]
    update.message.reply_text('Мне очень не хочется нагружать тебя математикой, но без неё, к сожалению никуда. '
                              'Только с помощью неё я смогу объяснить свою стратегию...\n\n',
                              reply_markup=ReplyKeyboardRemove())
    time.sleep(3)
    update.message.reply_text('Судя по индексу S&P 500 среднегодовая доходность с 1923 года (год основания S&P) по '
                              '2016 год составляет 12,25%. С 1992 по 2016 год средняя доходность S&P500 '
                              'составила 10,72%. С 1987 по 2016 год она составляла 11,66%. При этом, в 2015 году '
                              'годовая доходность составила 1,31%, в 2014 году — 13,81%, а в 2013 году — 32,43%. '
                              'Как видно, в один год индекс падает, в другой — бешено растёт.\n\n',
                              reply_markup=ReplyKeyboardRemove())

    time.sleep(7)
    update.message.reply_text('Я привёл сюда эти проценты только ради того, чтобы сказать —'
                              ' чем больше срок инвестирования, тем меньше вероятность потерять все деньги. Из данных '
                              'выше можно сделать вывод, что в среднем рынок растёт на 12% в год, что означает, что '
                              'вложенные 100$ будут приность по 1$ каждый месяц. (12 % делим на 12 месяцев, полчучаем'
                              ' 1% в месяц. 1% от 100$ = 1$)\n\n', reply_markup=ReplyKeyboardRemove())

    time.sleep(7)
    update.message.reply_text('Самое важное перед началом инвестирования — отсутсвтие долгов. У тебя не должно быть '
                              'кредитов, рассрочек и всего такого. Лучше всё это закрыть.\n\n'
                              'Вторым этапом будет формирование подушки безопасности. Она должна равняться полугодовому'
                              ' заработку. Или 6X в нашем случае, т.к. X — минимально допустимая сумма денег, на '
                              f'которую мы можем прожить в случае чего. В твоём случае '
                              f'6X = {financial_safety_cushion_to_print} ₽', reply_markup=ReplyKeyboardRemove())

    time.sleep(7)
    update.message.reply_text('Эту подушку безопасности следует создать за ближайшие 2 года. '
                              f'То есть, к моменту, когда тебе будет {AGE + 2}, у тебя она уже должна быть',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, one_time_keyboard=True,
                                  input_field_placeholder='Погнали дальше?',
                                  resize_keyboard=True))

    return SMALL_CAPITAL


def strategy_for_small_capital(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    global x_to_print
    x_to_print = f'{X:,.0f}'.replace(',', ' ')
    global SMALL_CAPITAL
    SMALL_CAPITAL = X * 100

    global small_capital_to_print
    small_capital_to_print = f'{SMALL_CAPITAL:,.0f}'.replace(',', ' ')
    reply_keyboard = [['Далее']]

    update.message.reply_text('Ну а теперь переходим к самому вкусному. Какого размера капитал нужен, чтобы ежемесячно '
                              f'получать сумму равную X ({x_to_print} ₽)?\n\n'
                              f'Математика тут простая. Т.к. среднемесячная доходность равна 1%, то, значит, наш X ~ '
                              f'1%, а искомый капитал (обозначим его буквой sm = small capital) sm ~ 100%. '
                              f'Решая пропорцию 6-го класса получаем, что sm = {small_capital_to_print} ₽',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, one_time_keyboard=True,
                                  input_field_placeholder='Погнали дальше?',
                                  resize_keyboard=True))

    return BIG_CAPITAL


def strategy_for_big_capital(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    global BIG_CAPITAL
    BIG_CAPITAL = Y * 100
    big_capital_to_print = f'{BIG_CAPITAL:,.0f}'.replace(',', ' ')
    reply_keyboard = [['Далее']]

    update.message.reply_text(f'Представляешь, можно накопить всего лишь {small_capital_to_print} и больше никогда не '
                              f'работать! С натяжечкой, конечно, но всё же...',
                              reply_markup=ReplyKeyboardRemove())
    time.sleep(4)

    update.message.reply_text(f'Это вторая часть плана. То есть, сначала нужно к возрасту {AGE + 2} создать подушку '
                              f'безопасности, а к моменту, когда тебе будет уже {AGE + 6}-{AGE + 8} лет, у тебя должно '
                              f'быть {small_capital_to_print} ₽', reply_markup=ReplyKeyboardRemove())

    time.sleep(4)
    update.message.reply_text('Теперь нам наконец-то предстоить ответить на вопрос: "Сколько денег нужно для счастья? '
                              'Конечно, всё не так просто, но благодаря числу, которое мы сейчас найдём, у тебя будет '
                              'понимание, сколько денег просить у волшебника с именем "Жизнь".',
                              reply_markup=ReplyKeyboardRemove())
    time.sleep(5)

    update.message.reply_text('Нам нужно опять решить пропорция 6-го класса, только теперь, мы в месяц хотим получать '
                              f'не {x_to_print} ₽, а уже {y_to_print} ₽. Аналогично 1% ~ {y_to_print} ₽, 100% ~ bg (big '
                              f'capital). Решаем пропорцию и получаем, что наш bg = {big_capital_to_print} ₽',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, one_time_keyboard=True,
                                  input_field_placeholder='Погнали дальше?',
                                  resize_keyboard=True))

    return RISK_PROFILE_FRIENDS_CHARACTERISTIC_1


def risk_profile_friends_characteristic_1(update: Update, context: CallbackContext):
    global risk_profile_keyboard

    update.message.reply_text('А теперь, давай пройдём набольшой тестик на риск профиль. Вопрос 1 из 9: '
                              '"Как характерезуют тебя друзья?"\n\n'
                              'А: Крайне осторожный и мнительный \n'
                              'B: Осторожный человек \n'
                              'C: Готов пойти на риск, но только после анализа последствий\n'
                              'D: Игрок',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               input_field_placeholder='Кто ты?',
                                                               resize_keyboard=True))

    return RISK_PROFILE_OPINION_2


def risk_profile_opinion_2(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 1 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 2 из 9: "При любых инвестициях бывают взлёты и падения стоимости активов. Что ты'
                              ' об этом думаешь?"\n\n'
                              'A: Это меня останавливает, когда думаю об инвестициях\n'
                              'B: Меня это беспокоет, но я понимаю, что так работает финансовый рынок\n'
                              'C: Так устроен рынок, я не нервничаю\n'
                              'D: Это хорошо, на этом как раз и можно заработать',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_TRAVEL_3


def risk_profile_travel_3(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 2 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 3 из 9: "Вы накопили на путешествие своей мечты, но за 2 недели до поездки '
                              'потеряли работу. Как вы поступите?"\n\n'
                              'A: Отменю путешествие\n'
                              'B: Сделаю план путешествия скромнее, но поеду\n'
                              'C: Ничего не буду менять\n'
                              'D: Продлю отпуск',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_LOSSES_4


def risk_profile_losses_4(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 3 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 4 из 9: "Вы хотите получать высокий инвестиционный доход. Готовы ли вы принять '
                              'возможные убытки?"\n\n'
                              'A: Не готов, не буду спать ночами\n'
                              'B: Готов, но буду немного переживать\n'
                              'C: Готов. Чем больше риск, тем больше возможностей\n'
                              'D: Готов! Кто не рискует, тот не пьёт шампаское',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_ASSOCIATIONS_5


def risk_profile_associations_5(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 4 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 5 из 9: "Какие ассоциации вызывает у вас слово «риск»?"\n\n'
                              'A: Риск — это потери\n'
                              'B: Риск — это неопределённость\n'
                              'C: Риск — это возможности\n'
                              'D: Риск — это азарт',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_ALTERNATIVES_6


def risk_profile_alternatives_6(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 5 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 6 из 9: "Какую из двух альтернатив вы предпочтете?"\n\n'
                              'A: Получить гарантированно 50 000 рублей\n'
                              'B: Получить 120 000 рублей с верояностью 50% и с вероятностью 50% ничего не заработать',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_TYPE_OF_ASSETS_7


def risk_profile_type_of_assets_7(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 6 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 7 из 9: "У вас есть 250 000 руб. В какой вид активов вы вложите основную долю? '
                              'Помните, что больший риск связан с возможностью получения большего дохода."\n\n'
                              'A: В низкорискованные активы\n'
                              'B: В среднерискованные активы\n'
                              'C: В высокорискованные активы',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_PORTFOLIO_DECLINE_8


def risk_profile_portfolio_decline_8(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 7 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 8 из 9: "Мировой финансовый рынок имеет особенность расти и снижаться. '
                              'Что ты будешь делать, если стоимость вашего инвестиционного портфеля снизится '
                              'на 10%?"\n\nA: Продам всё и положу на депозит\n'
                              'B: Ничего не буду менять\n'
                              'C: Продам часть портфеля\n'
                              'D: Займу денег и прикуплю ещё',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_EXPERIENCE_9


def risk_profile_experience_9(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 8 of %s %s", user.first_name, update.message.text)

    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    update.message.reply_text('Вопрос 9 из 9: "Какой у тебя опыт инвестирования на фондовом рынке?"\n\n'
                              'A: Нет опыта\n'
                              'B: Есть, менее 1 года\n'
                              'C: Есть, 1 — 3 года\n'
                              'D: Есть, более 3-ёх лет',
                              reply_markup=ReplyKeyboardMarkup(risk_profile_keyboard,
                                                               one_time_keyboard=True,
                                                               resize_keyboard=True))

    return RISK_PROFILE_RESULT


def risk_profile_result(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Answer 9 of %s %s", user.first_name, update.message.text)

    # Опять увеличиваем сумму очков
    global risk_profile_keyboard, risk_profile_sum
    risk_profile_sum += switch(update.message.text)
    logger.info("Risk profile sum of %s %s", user.first_name, risk_profile_sum)

    # А тут мы уже выводим риск профиль
    update.message.reply_text(risk_profile(risk_profile_sum), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation", user.first_name)

    update.message.reply_text('Пока-пока! Надесь, мы ещё скоро поболтаем!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(Constants.API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, NAME...
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            NAME: [MessageHandler(Filters.text, name)],
            AGE: [MessageHandler(Filters.text, age)],
            X: [MessageHandler(Filters.text, number_x)],
            Y: [MessageHandler(Filters.text, number_y)],
            RETIREMENT_AGE: [MessageHandler(Filters.text, retirement_age)],
            FINANCIAL_SAFETY_CUSHION: [MessageHandler(Filters.regex('^(Далее)$'), financial_safety_cushion)],
            SMALL_CAPITAL: [MessageHandler(Filters.regex('^(Далее)$'), strategy_for_small_capital)],
            BIG_CAPITAL: [MessageHandler(Filters.regex('^(Далее)$'), strategy_for_big_capital)],
            RISK_PROFILE_FRIENDS_CHARACTERISTIC_1: [MessageHandler(Filters.text, risk_profile_friends_characteristic_1)],
            RISK_PROFILE_OPINION_2: [MessageHandler(Filters.text, risk_profile_opinion_2)],
            RISK_PROFILE_TRAVEL_3: [MessageHandler(Filters.text, risk_profile_travel_3)],
            RISK_PROFILE_LOSSES_4: [MessageHandler(Filters.text, risk_profile_losses_4)],
            RISK_PROFILE_ASSOCIATIONS_5: [MessageHandler(Filters.text, risk_profile_associations_5)],
            RISK_PROFILE_ALTERNATIVES_6: [MessageHandler(Filters.text, risk_profile_alternatives_6)],
            RISK_PROFILE_TYPE_OF_ASSETS_7: [MessageHandler(Filters.text, risk_profile_type_of_assets_7)],
            RISK_PROFILE_PORTFOLIO_DECLINE_8: [MessageHandler(Filters.text, risk_profile_portfolio_decline_8)],
            RISK_PROFILE_EXPERIENCE_9: [MessageHandler(Filters.text, risk_profile_experience_9)],
            RISK_PROFILE_RESULT: [MessageHandler(Filters.text, risk_profile_result)],
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
