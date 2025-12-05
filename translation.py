DEFAULT_LOCALE = 'ru'

TRANSLATIONS = {
    "ru": {
        # ==== Базовые сообщения / команды ====
        "START_MESS": "Привет, пиши /menu для начала работы",
        "NOT_USER": "Ты не зарегистрирован в системе, напиши /start для регистрации",

        "HELP": (
            "Привет, я бот для управления конфигами AmneziaVPN.\n"
            "Вот список доступных команд:\n"
            "/start - начать работу с ботом\n"
            "/menu - открыть главное меню\n"
            "/help - показать это сообщение\n"
            "/referal <код> - стать рефералом другого пользователя\n"
        ),
        "ADMIN_HELP": (
            "\nКоманды администратора:\n"
            "/a - показать список активных оплат и т.п.\n"
            "/sendall <text> - отправить сообщение всем пользователям\n"
        ),
        "ACESS_ERR": "У вас нет доступа к этой команде",
        "CMD_NOT_FOR_YOU": "Эта команда не для тебя",

        # ==== Главное меню ====
        "MENU_MESS": "Твой баланс: {balance}руб\nКоличество твоих конфигов: {count}шт",
        "My configs": "Мои конфиги",
        "Account": "Личный кабинет",
        "Information": "Информация",
        "Buy config": "Купить конфиг",
        "Пополнить баланс": "Пополнить баланс",
        "LANG_CHANGE" : "Сменить язык / Change language",
        "LANG_SET_SUCCESS" : "Язык успешно изменен",

        # ==== Работа с конфигами / оплата ====
        "CONFIG_HELP": (
            "Спасибо за оплату!\n"
            "Для использования конфига скачай любое из следующих приложений:\n"
            "Android: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "Apple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "Windows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>"
        ),

        "Vpn duration": "Выбери длительность ключа",

        "NO_CONFIGS": "У тебя нет конфигов в данный момент",
        "CHOOSE_CONFIG": "Выбери конфиг",

        "CONFIG_MENU": (
            "Название: {name}\n"
            "Действителен до: {valid_until}\n"
            "Описание: {description}"
        ),

        "BTN_SHOW_QR": "Отобразить qr код",
        "BTN_GET_FILE": "Получить файл конфигурации",
        "BTN_EXTEND_CONFIG": "Продлить конфиг",
        "BTN_EDIT_CONFIG": "Изменить конфиг",

        "CHOOSE_LOCATION": "Выбери локацию",
        "BTN_SOON": "Скоро...",
        "CHOOSE_CONFIG_TARIFF": "Выбери тариф конфига",

        "PAY_SUMMARY": "Сумма оплаты: {amount}руб\nВаш баланс: {balance}руб",
        "PAY_FROM_BALANCE": "Сумма к оплате: {amount}руб\n\nВаш баланс: {balance}руб",

        "CONFIG_EXTEND_SUCCESS": "Конфиг {name} был успешно продлен",
        "CONFIG_VALID_UNTIL": "Действителен до: {date}(GMT+3)",
        
        "CONFIG_SETTINGS_PROMPT": "Что ты хочешь изменить в конфиге {config}:",

        "CHANGING_CONFIG_NAME": (
            "Ты хочешь изменить название конфига с\n"
            "{old_name}\n"
            "на\n"
            "{new_name}"
        ),
        "TOO_LONG_NAME": "Слишком длинное название! Максимальная длина - 32 символа.",
        "CHANGING_CONFIG_DESC": (
            "Ты хочешь изменить описание конфига с\n"
            "{old_desc}\n"
            "на\n"
            "{new_desc}"
        ),
        "TOO_LONG_DESC": "Слишком длинное описание! Максимальная длина - 255 символов.",
        "SET_CONFIG_DESC": "Ты хочешь поставить описание конфига\n{new_desc}",

        "CONFIG_NAME_CHANGED": (
            "Название конфига\n"
            "{code_name}\n"
            "успешно изменено на\n"
            "{text}"
        ),
        "CONFIG_DESC_CHANGED": (
            "Описание конфига\n"
            "успешно изменено на\n"
            "{text}"
        ),

        "CONFIG_EXPIRED_DELETED": "Твой конфиг {code_name} закончился и был удален",

        # ==== Рефералка ====
        "REFERAL_BECAME": "Вы стали рефералом {user}",
        "INPUT_REFERAL": "Введите реферальный код",
        "REFERAL_ERR": "Вы уже являетесь рефералом другого пользователя или такого кода не существует",

        "REFERRAL_PROGRAM": "Реферальная программа",
        "REFERRAL_MENU_TITLE": "Рефералы",
        "REFERRAL_ENTER_CODE": "Введите реферальный код",

        "BTN_MY_REF_CODE": "Мой реферальный код",
        "BTN_INPUT_REF_CODE": "Ввести реферальный код",
        "BTN_COPY_CODE": "Скопировать код",
        "BTN_COPY_LINK": "Скопировать ссылку",
        "REF_CODE_TEXT": "Твой реферальный код:\n<code>{code}</code>",

        # ==== Баланс / пополнение ====
        "SEND_INT": "Отправь целое число",
        "MIN_AMOUNT": "Минимальная сумма - {min}руб",
        "ASK_DEPOSIT_SUM": "Напиши сумму пополнения в рублях(от 80 руб.):",
        "DEPOSIT_CANCELED": "Пополнение отменено",
        "BALANCE_DEPOSIT_SUCCESS": "Баланс успешно пополнен на {amount}руб.",

        # ==== Информация о боте / прочее ====
        "ACCOUNT_MENU_TITLE": "Личный кабинет",
        "BOT_CHANNEL": "Канал бота",
        "BOT_INFO": "Это впн бот",

        "SOON_FUNC": "Функция в данный момент не работает, возможно я сделаю её позже...",
        "PRECHECKOUT_ERROR": "Ошибка, попробуй ещё раз или напиши в группу бота",

        # ==== Кнопки-иконки ====
        "YES": "Да✅",
        "CANCEL": "Отмена❌",
        "BACK": "Назад",
        "Оплатить": "Оплатить",
        "Отмена": "Отмена",
    },

    "en": {
        # ==== Basic ====
        "START_MESS": "Hello, send /menu to start",
        "NOT_USER": "You are not registered in the system, send /start for registration",

        "HELP": (
            "Hello, I am a bot for managing AmneziaVPN configs.\n"
            "Here is the list of available commands:\n"
            "/start - start working with the bot\n"
            "/menu - open the main menu\n"
            "/help - show this message\n"
            "/referal <code> - become another user's referral\n"
        ),
        "ADMIN_HELP": (
            "\nAdministrator commands:\n"
            "/a - show the list of active payments and so on\n"
            "/sendall <text> - send a message to all users\n"
        ),
        "ACESS_ERR": "You do not have access to this command",
        "CMD_NOT_FOR_YOU": "This command is not for you",

        # ==== Main menu ====
        "MENU_MESS": "Your balance: {balance}rub\nConfigs count: {count}",
        "My configs": "My configs",
        "Account": "Account",
        "Information": "Information",
        "Buy config": "Buy config",
        "Пополнить баланс": "Top up balance",
        "LANG_CHANGE" : "Сменить язык / Change language",
        "LANG_SET_SUCCESS" : "Language successfully changed",

        # ==== Configs / payments ====
        "CONFIG_HELP": (
            "Thank you for your payment!\n"
            "To use the config, download any of the following apps:\n"
            "Android: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "Apple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "Windows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>"
        ),

        "Vpn duration": "Choose VPN key duration",

        "NO_CONFIGS": "You don't have any configs",
        "CHOOSE_CONFIG": "Choose config",

        "CONFIG_MENU": (
            "Name: {name}\n"
            "Valid until: {valid_until}\n"
            "Description: {description}"
        ),

        "BTN_SHOW_QR": "Show QR code",
        "BTN_GET_FILE": "Get config file",
        "BTN_EXTEND_CONFIG": "Extend config",
        "BTN_EDIT_CONFIG": "Edit config",

        "CHOOSE_LOCATION": "Choose location",
        "BTN_SOON": "Soon...",
        "CHOOSE_CONFIG_TARIFF": "Choose config tariff",

        "PAY_SUMMARY": "Payment amount: {amount}rub\nYour balance: {balance}rub",
        "PAY_FROM_BALANCE": "Amount to pay: {amount}rub\n\nYour balance: {balance}rub",

        "CONFIG_EXTEND_SUCCESS": "Config {name} was successfully extended",
        "CONFIG_VALID_UNTIL": "Valid until: {date}(GMT+3)",
        
        "CONFIG_SETTINGS_PROMPT": "What do you want to change in config {config}:",

        "CHANGING_CONFIG_NAME": (
            "You want to change config name from\n"
            "{old_name}\n"
            "to\n"
            "{new_name}"
        ),
        "TOO_LONG_NAME": "Name is too long! Maximum length is 32 characters.",
        "CHANGING_CONFIG_DESC": (
            "You want to change config description from\n"
            "{old_desc}\n"
            "to\n"
            "{new_desc}"
        ),
        "TOO_LONG_DESC": "Description is too long! Maximum length is 255 characters.",
        "SET_CONFIG_DESC": "You want to set config description to\n{new_desc}",

        "CONFIG_NAME_CHANGED": (
            "Config name\n"
            "{code_name}\n"
            "was successfully changed to\n"
            "{text}"
        ),
        "CONFIG_DESC_CHANGED": (
            "Config description\n"
            "was successfully changed to\n"
            "{text}"
        ),

        "CONFIG_EXPIRED_DELETED": "Your config {code_name} has expired and was deleted",

        # ==== Referrals ====
        "REFERAL_BECAME": "You are {user}'s referral now",
        "INPUT_REFERAL": "Enter referral code",
        "REFERAL_ERR": "You are already a referral of another user or this code does not exist",

        "REFERRAL_PROGRAM": "Referral program",
        "REFERRAL_MENU_TITLE": "Referrals",
        "REFERRAL_ENTER_CODE": "Enter referral code",

        "BTN_MY_REF_CODE": "My referral code",
        "BTN_INPUT_REF_CODE": "Enter referral code",
        "BTN_COPY_CODE": "Copy code",
        "BTN_COPY_LINK": "Copy link",
        "REF_CODE_TEXT": "Your referral code:\n<code>{code}</code>",

        # ==== Balance ====
        "SEND_INT": "Send an integer",
        "MIN_AMOUNT": "Minimum amount - {min}rub",
        "ASK_DEPOSIT_SUM": "Send deposit amount in rubles (from 80 rub):",
        "DEPOSIT_CANCELED": "Deposit cancelled",
        "BALANCE_DEPOSIT_SUCCESS": "Your balance has been credited with {amount}rub.",

        # ==== Bot info ====
        "ACCOUNT_MENU_TITLE": "Account",
        "BOT_CHANNEL": "Bot channel",
        "BOT_INFO": "This is a VPN bot",

        "SOON_FUNC": "Function isn't working now, maybe I will do it soon...",
        "PRECHECKOUT_ERROR": "Error, try again or write to the bot's group",

        # ==== Buttons ====
        "YES": "Yes✅",
        "CANCEL": "Cancel❌",
        "BACK": "Back",
        "Оплатить": "Pay",
        "Отмена": "Cancel",
    },
}


async def tr(words: str, locale: str | None = None) -> str:
    locale = locale or DEFAULT_LOCALE
    lang_dict = TRANSLATIONS.get(locale) or TRANSLATIONS[DEFAULT_LOCALE]
    return lang_dict.get(words, words)
