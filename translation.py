
DEFAULT_LOCALE = 'ru'

TRANSLATIONS = {
    "ru" : {
        "START_MESS" : "Привет, пиши /menu для начала работы",
        "MENU_MESS" : "Твой баланс: {balance}руб\nКоличество твоих конфигов: {count}шт",
        "CONFIG_HELP" : "Спасибо за оплату!\nдля использования конфига скачай любое из следующих предложений\nAndroid: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> <a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\nApple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> <a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\nWindows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>",
        "My configs" : "Мои конфиги",
        "Account" : "Личный кабинет",
        "Information" : "Информация",
        "Buy config" : "Купить конфиг",
        "Vpn duration" : "Выбери длительность ключа"
    },
    "en" : {
        "START_MESS" : "Hello, send /menu for start",
        "MENU_MESS" : "Your balance: {balance}rub\nConfigs count: {count}",
        "CONFIG_HELP" : "Thank you for your payment!\nTo use the config, download any of the following apps:\nAndroid: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> <a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\nApple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> <a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\nWindows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>",
        "My configs" : "My configs",
        "Account" : "Account",
        "Information" : "Information",
        "Buy config" : "Buy config",
        "Vpn duration" : "Choose duration of vpn key"
    }
}

async def tr(words: str, locale: str | None = None):
    locale = locale or DEFAULT_LOCALE
    lang_dict = TRANSLATIONS.get(locale) or TRANSLATIONS[DEFAULT_LOCALE]
    return lang_dict.get(words, words)