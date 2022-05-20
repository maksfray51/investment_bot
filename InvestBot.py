from typing import Callable

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


# GENDER, NAME, AGE, X, x_to_print, Y, y_to_print, RETIREMENT_AGE, FINANCIAL_SAFETY_CUSHION, SMALL_CAPITAL, \
#     small_capital_to_print, BIG_CAPITAL, RISK_PROFILE_FRIENDS_CHARACTERISTIC_1, RISK_PROFILE_OPINION_2, \
#     RISK_PROFILE_TRAVEL_3, RISK_PROFILE_LOSSES_4, RISK_PROFILE_ASSOCIATIONS_5, RISK_PROFILE_ALTERNATIVES_6, \
#     RISK_PROFILE_TYPE_OF_ASSETS_7, RISK_PROFILE_PORTFOLIO_DECLINE_8, RISK_PROFILE_EXPERIENCE_9,\
#     RISK_PROFILE_RESULT = range(22)
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


class Bot(object):
    # Переменная, необходимая для подсчёта суммы в тесте на риск профиль
    risk_profile_sum = 0
    # Дефолтные кнопки, необходимые для теста на риск профиль
    risk_profile_keyboard = [['A', 'B', 'C', 'D']]

    def __init__(self, gender, name, age, x, x_to_print, y, y_to_print, retirement_age, financial_safety_cushion,
                 small_capital, small_capital_to_print, big_capital, big_capital_to_print,
                 risk_profile_friends_characteristic_1, risk_profile_opinion_2, risk_profile_travel_3,
                 risk_profile_losses_4, risk_profile_associations_5, risk_profile_alternatives_6,
                 risk_profile_type_of_assets_7, risk_profile_portfolio_decline_8, risk_profile_experience_9,
                 risk_profile_result):
        self.gender = gender
        self.name = name
        self.age = age
        self.x = x
        self.x_to_print = x_to_print
        self.y = y
        self.y_to_print = y_to_print
        self.retirement_age = retirement_age
        self.financial_safety_cushion = financial_safety_cushion
        self.small_capital = small_capital
        self.small_capital_to_print = small_capital_to_print
        self.big_capital = big_capital
        self.big_capital_to_print = big_capital_to_print
        self.risk_profile_friends_characteristic_1 = risk_profile_friends_characteristic_1
        self.risk_profile_opinion_2 = risk_profile_opinion_2
        self.risk_profile_travel_3 = risk_profile_travel_3
        self.risk_profile_losses_4 = risk_profile_losses_4
        self.risk_profile_associations_5 = risk_profile_associations_5
        self.risk_profile_alternatives_6 = risk_profile_alternatives_6
        self.risk_profile_type_of_assets_7 = risk_profile_type_of_assets_7
        self.risk_profile_portfolio_decline_8 = risk_profile_portfolio_decline_8
        self.risk_profile_experience_9 = risk_profile_experience_9
        self.risk_profile_result = risk_profile_result

    def get_start(self, update: Update, context: CallbackContext):
        """Starting the conversation"""
        reply_keyboard = [['Boy', 'Girl', 'Other?']]

        update.message.reply_text(
            'Привет, друг!\n'
            'Меня зовут Инвест Бот. Я помогаю ответить на замечательный вопрос: "Сколько денег нужно для счастья?"\n\n'
            'Все хотят получить ответ на этот вопрос как можно скорее, но перед тем, как ответить на него, я бы '
            'хотел с тобой познакомиться.\n\nЕсли хочешь остановить тест напиши /cancel\n\n Ты мальчик '
            '(мужчинка/мужчина) или девочка(девушка, женщина)?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                             one_time_keyboard=True,
                                             input_field_placeholder='Boy? Girl? Space alien? Dog?',
                                             resize_keyboard=True))
        return self.gender

    def get_gender(self, update: Update, context: CallbackContext) -> Callable[[Update, CallbackContext], int]:
        """Starting the risk test"""
        user = update.message.from_user
        logger.info("Gender of %s %s", user.first_name, update.message.text)

        # global GENDER
        # GENDER = update.message.text
        self.gender = update.message.text

        update.message.reply_text(
            'Отлично! Теперь давай узнаем как тебя зовут',
            reply_markup=ReplyKeyboardRemove(input_field_placeholder='Как тебя зовут?'),
        )
        return self.name

    def get_name(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("Name of %s %s", user.first_name, update.message.text)
        self.name = update.message.text

        # reply_keyboard = [['Меньше 25', '25-35', '35-50', 'Больше 50']]

        update.message.reply_text(
            f'Приятно познакомиться, {update.message.text}!\n'
            'Подскажи, сколько тебе лет? (Напиши, пожалуйста, возраст числом :) )',
            reply_markup=ReplyKeyboardRemove())

        return self.age

    def get_age(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("Age of %s %s", user.first_name, update.message.text)
        self.age = int(update.message.text)

        update.message.reply_text(
            'А теперь пришло время ответить на главный вопрос!\n'
            'Для этого нам нужно немного пофантозировать :)\n\n'
            'Давай представим, что ты живёшь в Москве и при этом один(-на). '
            'Как ты думаешь, сколько денег тебе нужно в месяц, чтобы иметь возможность снимать квартиру, ну не совсем '
            'за МКАДом, кушать чуть больше, чем дошик каждый день (сам готовишь себе примитивные блюда). Может, '
            'ещё что-то, без чего ты не сможешь обойтись. В общем, сейчас мы получим так называемое число Х. '
            'Это сумма, на которую ты сможешь прожить в Моксве один месяц\n\nP.S. Обещаю, я никому не скажу!\nP.P.S. '
            'В качестве ответа нужно просто ввести сумму в рублях (без пробелов)',
            reply_markup=ReplyKeyboardRemove()
        )
        return self.x

    def get_number_x(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("Number X of %s %s", user.first_name, update.message.text)
        self.x = int(update.message.text)

        update.message.reply_text(
            'Спасибо за твоё доверие! '
            'Теперь давай помечтаем...\n\n'
            'Подумай, сколько тебе денег в месяц нужно, чтобы тратить на ВСЁ, что ты хочешь. '
            'Можешь заказывать частные самолёты или летать везде бизнес классом. '
            'Иметь отличную машину или ездить на такси, или водителя...\n\n'
            'Подумай, сколько денег нужно на это всё?',
            reply_markup=ReplyKeyboardRemove()
        )

        return self.y

    def get_number_y(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("Number Y of %s %s", user.first_name, update.message.text)
        self.y = int(update.message.text) * 2
        self.y_to_print = f'{self.y:,.0f}'.replace(',', ' ')

        update.message.reply_text(
            'Это число будем называть числом Y.\n\n'
            'На самом деле, многие люди не знают, сколько денег они могли бы тратить в месяц, поэтому'
            ' часто занижают свои ожидания. Поэтому настоящее число Y для тебя это ' + self.y_to_print + '₽ !\n\n'
            'А теперь давай подумаем, в каком возрасте тебе хотелось бы больше не работь? '
            'В каком возрасте тебе хотелось бы выйти на пенсию?',
            reply_markup=ReplyKeyboardRemove())

        return self.retirement_age

    def get_retirement_age(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("Retirement age of %s %s", user.first_name, update.message.text)
        self.retirement_age = update.message.text

        reply_keyboard = [['Далее']]
        update.message.reply_text('К сожалению, я не могу рассказать, как именно заработать нужное для тебя количество'
                                  ' денег, но я могу помочь тебе поставить чёткие цели, благодаря которым, у тебя будет'
                                  ' ясность в голове по поводу нужного количества денег.\n\n'
                                  'Я хотел бы предложить тебе стратегию, которая разделена на 3 этапа:\n'
                                  '1) Стратегия, рассчитанная на 2 года, начиная с сегодняшнего дня\n'
                                  '2) Стратегия, рассчитанная на 6-8 лет, начиная с сегодняшнего дня\n'
                                  f'3) Стратегия, которая поможет выйти на пенсию в {self.retirement_age} лет',
                                  reply_markup=ReplyKeyboardMarkup(
                                      reply_keyboard, one_time_keyboard=True,
                                      input_field_placeholder='Погнали дальше?',
                                      resize_keyboard=True))

        return self.financial_safety_cushion

    def get_financial_safety_cushion(self, update: Update, context: CallbackContext) -> int:
        # Делаем красивую запись для X
        self.x_to_print = f'{self.x:,.0f}'.replace(',', ' ')
        self.financial_safety_cushion = 6 * self.x
        # Аналогично делаем красивую запись для финансовой подушки безопасности
        financial_safety_cushion_to_print = f'{self.financial_safety_cushion:,.0f}'.replace(',', ' ')

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
                                  ' чем больше срок инвестирования, тем меньше вероятность потерять все деньги. '
                                  'Из данных выше можно сделать вывод, что в среднем рынок растёт на 12% в год, что '
                                  'означает, что вложенные 100$ будут приность по 1$ каждый месяц. (12 % делим на 12 '
                                  'месяцев, полчучаем 1% в месяц. 1% от 100$ = 1$)\n\n',
                                  reply_markup=ReplyKeyboardRemove())

        time.sleep(7)
        update.message.reply_text(
            'Самое важное перед началом инвестирования — отсутсвтие долгов. У тебя не должно быть '
            'кредитов, рассрочек и всего такого. Лучше всё это закрыть.\n\n'
            'Вторым этапом будет формирование подушки безопасности. Она должна равняться полугодовому'
            ' заработку. Или 6X в нашем случае, т.к. X — минимально допустимая сумма денег, на '
            f'которую мы можем прожить в случае чего. В твоём случае '
            f'6X = {financial_safety_cushion_to_print} ₽', reply_markup=ReplyKeyboardRemove())

        time.sleep(7)
        update.message.reply_text('Эту подушку безопасности следует создать за ближайшие 2 года. '
                                  f'То есть, к моменту, когда тебе будет {self.age + 2}, у тебя она уже должна быть',
                                  reply_markup=ReplyKeyboardMarkup(
                                      reply_keyboard, one_time_keyboard=True,
                                      input_field_placeholder='Погнали дальше?',
                                      resize_keyboard=True))

        return self.small_capital

    def get_strategy_for_small_capital(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        self.x_to_print = f'{self.x:,.0f}'.replace(',', ' ')
        self.small_capital = self.x * 100
        self.small_capital_to_print = f'{self.small_capital:,.0f}'.replace(',', ' ')
        reply_keyboard = [['Далее']]

        update.message.reply_text(
            'Ну а теперь переходим к самому вкусному. Какого размера капитал нужен, чтобы ежемесячно '
            f'получать сумму равную X ({self.x_to_print} ₽)?\n\n'
            f'Математика тут простая. Т.к. среднемесячная доходность равна 1%, то, значит, наш X ~ '
            f'1%, а искомый капитал (обозначим его буквой sm = small capital) sm ~ 100%. '
            f'Решая пропорцию 6-го класса получаем, что sm = {self.small_capital_to_print} ₽',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                input_field_placeholder='Погнали дальше?',
                resize_keyboard=True))

        return self.big_capital

    def get_strategy_for_big_capital(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        self.big_capital = self.y * 100
        self.big_capital_to_print = f'{self.big_capital:,.0f}'.replace(',', ' ')
        reply_keyboard = [['Далее']]

        update.message.reply_text(
            f'Представляешь, можно накопить всего лишь {self.small_capital_to_print} и больше никогда не '
            f'работать! С натяжечкой, конечно, но всё же...',
            reply_markup=ReplyKeyboardRemove())
        time.sleep(4)

        update.message.reply_text(
            f'Это вторая часть плана. То есть, сначала нужно к возрасту {self.age + 2} создать подушку '
            f'безопасности, а к моменту, когда тебе будет уже {self.age + 6}-{self.age + 8} лет, у тебя должно '
            f'быть {self.small_capital_to_print} ₽', reply_markup=ReplyKeyboardRemove())

        time.sleep(4)
        update.message.reply_text(
            'Теперь нам наконец-то предстоить ответить на вопрос: "Сколько денег нужно для счастья? '
            'Конечно, всё не так просто, но благодаря числу, которое мы сейчас найдём, у тебя будет '
            'понимание, сколько денег просить у волшебника с именем "Жизнь".',
            reply_markup=ReplyKeyboardRemove())
        time.sleep(5)

        update.message.reply_text(
            'Нам нужно опять решить пропорция 6-го класса, только теперь, мы в месяц хотим получать '
            f'не {self.x_to_print} ₽, а уже {self.y_to_print} ₽. Аналогично 1% ~ {self.y_to_print} ₽, 100% ~ bg (big '
            f'capital). Решаем пропорцию и получаем, что наш bg = {self.big_capital_to_print} ₽',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                input_field_placeholder='Погнали дальше?',
                resize_keyboard=True))

        return self.risk_profile_friends_characteristic_1

    def get_risk_profile_friends_characteristic_1(self, update: Update, context: CallbackContext):

        update.message.reply_text('А теперь, давай пройдём набольшой тестик на риск профиль. Вопрос 1 из 9: '
                                  '"Как характерезуют тебя друзья?"\n\n'
                                  'А: Крайне осторожный и мнительный \n'
                                  'B: Осторожный человек \n'
                                  'C: Готов пойти на риск, но только после анализа последствий\n'
                                  'D: Игрок',
                                  reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                   one_time_keyboard=True,
                                                                   input_field_placeholder='Кто ты?',
                                                                   resize_keyboard=True))

        return self.risk_profile_opinion_2

    def get_risk_profile_opinion_2(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 1 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text(
            'Вопрос 2 из 9: "При любых инвестициях бывают взлёты и падения стоимости активов. Что ты'
            ' об этом думаешь?"\n\n'
            'A: Это меня останавливает, когда думаю об инвестициях\n'
            'B: Меня это беспокоет, но я понимаю, что так работает финансовый рынок\n'
            'C: Так устроен рынок, я не нервничаю\n'
            'D: Это хорошо, на этом как раз и можно заработать',
            reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                             one_time_keyboard=True,
                                             resize_keyboard=True))

        return self.risk_profile_travel_3

    def get_risk_profile_travel_3(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 2 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text('Вопрос 3 из 9: "Вы накопили на путешествие своей мечты, но за 2 недели до поездки '
                                  'потеряли работу. Как вы поступите?"\n\n'
                                  'A: Отменю путешествие\n'
                                  'B: Сделаю план путешествия скромнее, но поеду\n'
                                  'C: Ничего не буду менять\n'
                                  'D: Продлю отпуск',
                                  reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

        return self.risk_profile_losses_4

    def get_risk_profile_losses_4(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 3 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text(
            'Вопрос 4 из 9: "Вы хотите получать высокий инвестиционный доход. Готовы ли вы принять '
            'возможные убытки?"\n\n'
            'A: Не готов, не буду спать ночами\n'
            'B: Готов, но буду немного переживать\n'
            'C: Готов. Чем больше риск, тем больше возможностей\n'
            'D: Готов! Кто не рискует, тот не пьёт шампаское',
            reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                             one_time_keyboard=True,
                                             resize_keyboard=True))

        return self.risk_profile_associations_5

    def get_risk_profile_associations_5(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 4 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text('Вопрос 5 из 9: "Какие ассоциации вызывает у вас слово «риск»?"\n\n'
                                  'A: Риск — это потери\n'
                                  'B: Риск — это неопределённость\n'
                                  'C: Риск — это возможности\n'
                                  'D: Риск — это азарт',
                                  reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

        return self.risk_profile_alternatives_6

    def get_risk_profile_alternatives_6(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 5 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text('Вопрос 6 из 9: "Какую из двух альтернатив вы предпочтете?"\n\n'
                                  'A: Получить гарантированно 50 000 рублей\n'
                                  'B: Получить 120 000 рублей с верояностью 50% и с вероятностью 50% ничего не '
                                  'заработать', reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                                 one_time_keyboard=True,
                                                                                 resize_keyboard=True))

        return self.risk_profile_type_of_assets_7

    def get_risk_profile_type_of_assets_7(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 6 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text(
            'Вопрос 7 из 9: "У вас есть 250 000 руб. В какой вид активов вы вложите основную долю? '
            'Помните, что больший риск связан с возможностью получения большего дохода."\n\n'
            'A: В низкорискованные активы\n'
            'B: В среднерискованные активы\n'
            'C: В высокорискованные активы',
            reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                             one_time_keyboard=True,
                                             resize_keyboard=True))

        return self.risk_profile_portfolio_decline_8

    def get_risk_profile_portfolio_decline_8(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 7 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text('Вопрос 8 из 9: "Мировой финансовый рынок имеет особенность расти и снижаться. '
                                  'Что ты будешь делать, если стоимость вашего инвестиционного портфеля снизится '
                                  'на 10%?"\n\nA: Продам всё и положу на депозит\n'
                                  'B: Ничего не буду менять\n'
                                  'C: Продам часть портфеля\n'
                                  'D: Займу денег и прикуплю ещё',
                                  reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

        return self.risk_profile_experience_9

    def get_risk_profile_experience_9(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 8 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        update.message.reply_text('Вопрос 9 из 9: "Какой у тебя опыт инвестирования на фондовом рынке?"\n\n'
                                  'A: Нет опыта\n'
                                  'B: Есть, менее 1 года\n'
                                  'C: Есть, 1 — 3 года\n'
                                  'D: Есть, более 3-ёх лет',
                                  reply_markup=ReplyKeyboardMarkup(self.risk_profile_keyboard,
                                                                   one_time_keyboard=True,
                                                                   resize_keyboard=True))

        return self.risk_profile_result

    def get_risk_profile_result(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("Answer 9 of %s %s", user.first_name, update.message.text)
        self.risk_profile_sum += switch(update.message.text)
        logger.info("Risk profile sum of %s %s", user.first_name, self.risk_profile_sum)

        # А тут мы уже выводим риск профиль
        update.message.reply_text(risk_profile(self.risk_profile_sum), reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def get_cancel(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        logger.info("User %s canceled the conversation", user.first_name)

        update.message.reply_text('Пока-пока! Надесь, мы ещё скоро поболтаем!', reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END


bot = Bot(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(Constants.API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, NAME...
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.get_start)],
        states={
            bot.gender: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), bot.get_gender)],
            bot.name: [MessageHandler(Filters.text, bot.get_name)],
            bot.age: [MessageHandler(Filters.text, bot.get_age)],
            bot.x: [MessageHandler(Filters.text, bot.get_number_x)],
            bot.y: [MessageHandler(Filters.text, bot.get_number_y)],
            bot.retirement_age: [MessageHandler(Filters.text, bot.get_retirement_age)],
            bot.financial_safety_cushion: [MessageHandler(Filters.regex('^(Далее)$'),
                                                          bot.get_financial_safety_cushion)],
            bot.small_capital: [MessageHandler(Filters.regex('^(Далее)$'), bot.get_strategy_for_small_capital)],
            bot.big_capital: [MessageHandler(Filters.regex('^(Далее)$'), bot.get_strategy_for_big_capital)],
            bot.risk_profile_friends_characteristic_1: [
                MessageHandler(Filters.text, bot.get_risk_profile_friends_characteristic_1)],
            bot.risk_profile_opinion_2: [MessageHandler(Filters.text, bot.get_risk_profile_opinion_2)],
            bot.risk_profile_travel_3: [MessageHandler(Filters.text, bot.get_risk_profile_travel_3)],
            bot.risk_profile_losses_4: [MessageHandler(Filters.text, bot.get_risk_profile_losses_4)],
            bot.risk_profile_associations_5: [MessageHandler(Filters.text, bot.get_risk_profile_associations_5)],
            bot.risk_profile_alternatives_6: [MessageHandler(Filters.text, bot.get_risk_profile_alternatives_6)],
            bot.risk_profile_type_of_assets_7: [MessageHandler(Filters.text, bot.get_risk_profile_type_of_assets_7)],
            bot.risk_profile_portfolio_decline_8: [MessageHandler(Filters.text,
                                                                  bot.get_risk_profile_portfolio_decline_8)],
            bot.risk_profile_experience_9: [MessageHandler(Filters.text, bot.get_risk_profile_experience_9)],
            bot.risk_profile_result: [MessageHandler(Filters.text, bot.get_risk_profile_result)],
        },
        fallbacks=[CommandHandler('cancel', bot.get_cancel)],
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
