
DEFAULT_LOCALE = 'ru'

TRANSLATIONS = {
    "ru" : {
        "START_MESS" : "Привет, пиши /menu для начала работы",
        "NOT_USER" : "Ты не зарегистрирован в системе, напиши /start для регистрации",
        "HELP" : (
            "Привет, я бот для управления конфигами AmneziaVPN.\n"
            "Вот список доступных команд:\n"
            "/start - начать работу с ботом\n"
            "/menu - открыть главное меню\n"
            "/help - показать это сообщение\n"
            "/referal <код> - стать рефералом другого пользователя\n"
        ),
        "ADMIN_HELP" : (
            "\nКоманды администратора:\n"
            "/a - показать список активных оплат и тп\n"
            "/sendall <text> - отправить сообщение всем пользователям\n"),
        "ACESS_ERR" : "У вас нет доступа к этой команде",
        "MENU_MESS" : "Твой баланс: {balance}руб\nКоличество твоих конфигов: {count}шт",
        "CONFIG_HELP" : "Спасибо за оплату!\nдля использования конфига скачай любое из следующих предложений\nAndroid: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> <a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\nApple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> <a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\nWindows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>",
        "REFERAL_BECAME" : "Вы стали рефералом {user}",
        "INPUT_REFERAL" : "Введите реферальный код",
        "REFERAL_ERR": "Вы уже являетесь рефералом другого пользователя или такого кода не существует",
        "My configs" : "Мои конфиги",
        "CHANGING_CONFIG_NAME" : "Ты хочешь изменить название конфига с\n{old_name}\nна\n{new_name}",
        "TOO_LONG_NAME" : "Слишком длинное название! Максимальная длина - 32 символа.",
        "CHANGING_CONFIG_DESC" : "Ты хочешь изменить описание конфига с\n{old_desc}\nна\n{new_desc}",
        "TOO_LONG_DESC" : "Слишком длинное описание! Максимальная длина - 255 символов.",
        "Account" : "Личный кабинет",
        "Information" : "Информация",
        "Buy config" : "Купить конфиг",
        "Vpn duration" : "Выбери длительность ключа",
        "YES" : "Да✅",
        "CANCEL" : "Отмена❌"
    },
    "en" : {
        "START_MESS" : "Hello, send /menu for start",
        "NOT_USER" : "You are not registered in the system, send /start for registration",
        "HELP" : (
            "Hello, I am a bot for managing AmneziaVPN configs.\n"
            "Here is the list of available commands:\n"
            "/start - start working with the bot\n"
            "/menu - open the main menu\n"
            "/help - show this message\n"
            "/referal <code> - become another user's referral\n"
        ),
        "ADMIN_HELP" : (
            "\nAdministrator commands:\n"
            "/a - show the list of active payments and so on\n"
            "/sendall <text> - send a message to all users\n"
        ),
        "ACESS_ERR" : "You do not have access to this command",
        "MENU_MESS" : "Your balance: {balance}rub\nConfigs count: {count}",
        "CONFIG_HELP" : "Thank you for your payment!\nTo use the config, download any of the following apps:\nAndroid: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> <a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\nApple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> <a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\nWindows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>",
        "REFERAL_BECAME" : "You are {user}'s referral now",
        "INPUT_REFERAL" : "Enter referral code",
        "REFERAL_ERR": "You are already a referral of another user or this code does not exist",
        "My configs" : "My configs",
        "CHANGING_CONFIG_NAME" : "You want to change config's name from\n{old_name}\nto\n{new_name}",
        "TOO_LONG_NAME" : "Name is too long! Maximum length is 32 characters.",
        "CHANGING_CONFIG_DESC" : "You want to change config's description from\n{old_desc}\nto\n{new_desc}",
        "TOO_LONG_DESC" : "Description is too long! Maximum length is 255 characters.",
        "Account" : "Account",
        "Information" : "Information",
        "Buy config" : "Buy config",
        "Vpn duration" : "Choose duration of vpn key",
        "YES" : "Yes✅",
        "CANCEL" : "Cancel❌"
    }
}

async def tr(words: str, locale: str | None = None):
    locale = locale or DEFAULT_LOCALE
    lang_dict = TRANSLATIONS.get(locale) or TRANSLATIONS[DEFAULT_LOCALE]
    return lang_dict.get(words, words)