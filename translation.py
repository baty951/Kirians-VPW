DEFAULT_LOCALE = 'en'

TRANSLATIONS = {
    "ru": {
        # ==== Базовые сообщения / команды ====
        "START_MESS": "👋 Привет! Пиши /menu, чтобы начать работу. Перед покупкой рекомендую проверить работоспособность бесплатного ключа.",
        "NOT_USER": "⚠️ Ты не зарегистрирован в системе. Напиши /start для регистрации.",

        "HELP": (
            "🤖 <b>Я бот для управления ключами AmneziaVPN.</b>\n\n"
            "📌 <b>Доступные команды:</b>\n"
            "• /start — начать работу с ботом\n"
            "• /menu — открыть главное меню\n"
            "• /help — показать это сообщение\n"
            "• /referal &lt;код&gt; — стать рефералом другого пользователя\n"
        ),
        "ADMIN_HELP": (
            "\n👨‍💻 <b>Команды администратора:</b>\n"
            "• /a — показать список активных оплат и изменений\n"
            "• /sendall &lt;text&gt; — отправить сообщение всем пользователям\n"
        ),
        
        "ACESS_ERR": "⛔ У вас нет доступа к этой команде.",

        # ==== Главное меню ====
        "MENU_MESS": (
            "💰 <b>Баланс:</b> {balance}₽\n"
            "🔑 <b>Твоих ключей:</b> {count} шт."
        ),
        "MY_CFGS": "🔑 Мои ключи",
        "FREE_PRESENT": "🎁 Бесплатный ключ",
        "ACCOUNT": "👤 Личный кабинет",
        "INFO": "ℹ️ Информация",
        "BUY_CFG": "🛒 Купить ключ",
        "DEPOSIT": "💳 Пополнить баланс",
        "LANG_CHANGE": "🌐 язык / language",
        "LANG_SET_SUCCESS": "✅ Язык успешно изменён.",

        # ==== Работа с ключами / оплата ====
        "CONFIG_HELP": (
            "✅ <b>Спасибо за оплату!</b>\n\n"
            "Чтобы использовать ключ, скачай любое из следующих приложений:\n\n"
            "📱 <b>Android:</b> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> · "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "🍏 <b>Apple:</b> "
            "<a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> · "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "💻 <b>Windows:</b> "
            "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>"
        ),

        "CFG_DURATION": "⏱ Выбери длительность ключа:",

        "NO_CONFIGS": "📭 У тебя пока нет активных ключей.",
        "CHOOSE_CONFIG": "🔑 Выбери ключ из списка:",

        "CONFIG_MENU": (
            "📄 <b>Название:</b> {name}\n"
            "⏰ <b>Действителен до:</b> {valid_until}\n"
            "📝 <b>Описание:</b> {description}"
        ),

        "BTN_SHOW_QR": "🔳 Показать QR-код ключа",
        "BTN_GET_FILE": "📄 Получить файл ключа",
        "BTN_EXTEND_CONFIG": "🔁 Продлить ключ",
        "BTN_EDIT_CONFIG": "⚙️ Изменить ключ",

        "CHOOSE_LOCATION": "🌍 Выбери локацию:",
        "BTN_SOON": "🚧 Скоро...",
        "CHOOSE_CONFIG_TARIFF": "💳 Выбери тариф ключа:",

        "PAY_SUMMARY": (
            "💵 <b>Сумма к оплате:</b> {amount}₽\n"
            "💰 <b>Ваш баланс:</b> {balance}₽"
        ),
        "PAY_FROM_BALANCE": (
            "💵 <b>Сумма к оплате:</b> {amount}₽\n\n"
            "💰 <b>Ваш баланс:</b> {balance}₽"
        ),

        "INVOICE_DEPOSIT_TITLE" : "💳 Пополнение баланса бота на {amount}₽ для {name}",
        "INVOICE_DEPOSIT_DESC" : "{amount}₽ будут зачислены на внутренний баланс бота {name}({id}) и могут быть использованы для покупки ключей доступа и других сервисов.",
        "INVOCE_DEPOSIT_DESC" : "Пополнение внутреннего баланса {name}({id}) на {summ}руб для оплаты цифровых услуг",
        "INVOICE_CONFIG_TITLE" : "🔑 Покупка ключа доступа на {duration}",
        "INVOICE_CONFIG_DESC" : "Оплата цифрового ключа для защищённого подключения через сервер {location} на {duration}. После оплаты вы получите файл и QR-код для подключения.",
        "INVOICE_EXTEND_TITLE": "🔁 Продление ключа {name} на {duration}",
        "INVOICE_EXTEND_DESC": "Оплата продления срока действия твоего цифрового ключа {name} на {duration}. После оплаты время действия будет увеличено автоматически.",
        "CONFIG_EXTEND_SUCCESS": "✅ Ключ <b>{name}</b> был успешно продлён.",
        "CONFIG_VALID_UNTIL": "⏰ Действителен до: {date} (GMT+3)",
        
        "CONFIG_EXPIRES": "⏳ Срок действия ключа {code_name} истекает в течение двух суток.",
        "CONFIGS_EXPIRES": "⏳ Срок действия ключей {code_name} истекает в течение двух суток.",
        
        "CONFIG_INFO" : "Название: {name}\nОписание: {description}\nДействителен до: {valid_until}",
        
        "CONFIG_SETTINGS_PROMPT": "⚙️ Что ты хочешь изменить в ключе <b>{config}</b>?",
        
        "ASK_CONFIG_NAME": "✏️ Введи новое название ключа (макс. 32 символа):",
        "CHANGING_CONFIG_NAME": (
            "✏️ Ты хочешь изменить название ключа:\n"
            "• <b>Сейчас:</b> {old_name}\n"
            "• <b>Будет:</b> {new_name}\n\n"
            "Подтвердить изменение?"
        ),
        "TOO_LONG_NAME": "⚠️ Слишком длинное название! Максимальная длина — 32 символа.",
        "CONFIG_NAME_CHANGED": (
            "✅ Название ключа\n"
            "<code>{code_name}</code>\n"
            "успешно изменено на:\n"
            "<b>{text}</b>"
        ),
        
        "ASK_CONFIG_DESC": "✏️ Введи новое описание ключа (макс. 255 символов):",
        "CHANGING_CONFIG_DESC": (
            "✏️ Ты хочешь изменить описание ключа:\n"
            "• <b>Сейчас:</b> {old_desc}\n"
            "• <b>Будет:</b> {new_desc}\n\n"
            "Подтвердить изменение?"
        ),
        "TOO_LONG_DESC": "⚠️ Слишком длинное описание! Максимальная длина — 255 символов.",
        "SET_CONFIG_DESC": (
            "✏️ Ты хочешь установить следующее описание ключа:\n"
            "{new_desc}\n\n"
            "Подтвердить?"
        ),
        "CONFIG_DESC_CHANGED": (
            "✅ Описание ключа успешно изменено на:\n"
            "<b>{text}</b>"
        ),

        "CONFIG_EXPIRED_DELETED": (
            "⏳ Срок действия твоего ключа <code>{code_name}</code> истёк, "
            "и он был удалён."
        ),

        # ==== Рефералка ====
        "REFERAL_BECAME": "🤝 Вы стали рефералом пользователя <b>{user}</b>.",
        "INPUT_REFERAL": "🔑 Введите реферальный код:",
        "ALREADY_REFERAL" : "⚠️ Вы уже являетесь рефералом другого пользователя.",
        "REFERAL_ERR": "⚠️ Такого кода не существует.",

        "REFERRAL_PROGRAM": "👥 Реферальная программа",
        "REFERRAL_MENU_TITLE": "👥 Рефералы",
        "REFERRAL_ENTER_CODE": "🔑 Введите реферальный код:",

        "BTN_MY_REF_CODE": "🧾 Мой реферальный код",
        "BTN_INPUT_REF_CODE": "✏️ Ввести реферальный код",
        "BTN_COPY_CODE": "📋 Скопировать код",
        "BTN_COPY_LINK": "🔗 Скопировать ссылку",
        "REF_CODE_TEXT": "🧾 Твой реферальный код:\n<code>{code}</code>",

        # ==== Баланс / пополнение ====
        "SEND_INT": "🔢 Отправь целое число.",
        "MIN_AMOUNT": "⚠️ Минимальная сумма — {min}₽.",
        "ASK_DEPOSIT_SUM": "💳 Напиши сумму пополнения в рублях (от 80₽):",
        "DEPOSIT_CANCELED": "❌ Пополнение отменено.",
        "BALANCE_DEPOSIT_SUCCESS": "✅ Баланс успешно пополнен на {amount}₽.",
        "BALANCE_PAY" : "💰Баланс(-10%)",
        "BALANCE" : "💰Баланс",

        # ==== Информация о боте / прочее ====
        "ACCOUNT_MENU_TITLE": "👤 Личный кабинет",
        "BOT_CHANNEL": "📢 Канал бота",
        "BOT_SITE" : "🌐 Сайт",
        "BOT_INFO": (
            "🔐 <b>Kirians-VPW</b> — бот для управления цифровыми ключами доступа к интернет-сервисам.\n\n"
            "С его помощью ты можешь:\n\n"
            "• получать и продлевать цифровые ключи доступа 🗝\n"
            "• подключаться к удалённым серверам через удобные приложения 📱💻\n"
            "• пользоваться онлайн-сервисами, которые могут быть недоступны из твоего региона 🌍\n\n"
            "📂 Все ключи хранятся в твоём личном кабинете — ты в любой момент можешь:\n"
            "• скачать конфигурационный файл\n"
            "• отсканировать QR-код\n"
            "• продлить срок действия ключа\n\n"
            "<b>Поддерживаемые приложения</b>\n"
            "📱 <b>Android:</b> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> · "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "🍏 <b>Apple:</b> "
            "<a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> · "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "💻 <b>Windows:</b> "
            "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN\n\n</a>"
            "⚠️ <b>Важно</b>\n\n"
            "Один цифровой ключ предназначен для <b>одного активного подключения</b>.\n"
            "Нельзя использовать один и тот же ключ одновременно на нескольких устройствах.\n\n"
            "При этом ты можешь подключаться с разных устройств <b>поочерёдно</b> — просто отключайся на одном устройстве перед подключением на другом."
        ),
        "PRECHECKOUT_ERROR": "⚠️ Ошибка. Попробуй ещё раз или напиши в группу бота.",
        "MIN" : "минут",
        "H" : "",
        "D" : "дней",
        "M" : "месяц",

        # ==== Кнопки-иконки ====
        "YES": "✅ Да",
        "CANCEL": "❌ Отмена",
        "BACK": "⬅️ Назад",
        "PAY": "💳 Оплатить",
        "RUB": "₽"
    },

    "en": {
        # ==== Basic ====
        "START_MESS": "👋 Hello! Send /menu to get started. Before buying, I recommend checking the functionality of the free key.",
        "NOT_USER": "⚠️ You are not registered. Send /start to register.",

        "HELP": (
            "🤖 <b>I am a bot for managing AmneziaVPN keys.</b>\n\n"
            "📌 <b>Available commands:</b>\n"
            "• /start — start working with the bot\n"
            "• /menu — open the main menu\n"
            "• /help — show this message\n"
            "• /referal &lt;code&gt; — become another user's referral\n"
        ),
        "ADMIN_HELP": (
            "\n👨‍💻 <b>Administrator commands:</b>\n"
            "• /a — show the list of active payments and changes\n"
            "• /sendall &lt;text&gt; — send a message to all users\n"
        ),
        
        "ACESS_ERR": "⛔ You do not have access to this command.",

        # ==== Main menu ====
        "MENU_MESS": (
            "💰 <b>Your balance:</b> {balance}rub\n"
            "🗂 <b>Configs count:</b> {count}"
        ),
        "MY_CFGS": "🔑 My configs",
        "FREE_PRESENT": "🎁 Free key",
        "ACCOUNT": "👤 Account",
        "INFO": "ℹ️ Information",
        "BUY_CFG": "🛒 Buy config",
        "DEPOSIT": "💳 deposit",
        "LANG_CHANGE": "🌐 язык / language",
        "LANG_SET_SUCCESS": "✅ Language successfully changed.",

        # ==== Configs / payments ====
        "CONFIG_HELP": (
            "✅ <b>Thank you for your payment!</b>\n\n"
            "To use the config, download any of the following apps:\n\n"
            "📱 <b>Android:</b> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> · "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "🍏 <b>Apple:</b> "
            "<a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> · "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "💻 <b>Windows:</b> "
            "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>"
        ),

        "CFG_DURATION": "⏱ Choose key duration:",

        "NO_CONFIGS": "📭 You don't have any active configs yet.",
        "CHOOSE_CONFIG": "📂 Choose a config from the list:",

        "CONFIG_MENU": (
            "📄 <b>Name:</b> {name}\n"
            "⏰ <b>Valid until:</b> {valid_until}\n"
            "📝 <b>Description:</b> {description}"
        ),

        "BTN_SHOW_QR": "🔳 Show QR code",
        "BTN_GET_FILE": "📄 Get config file",
        "BTN_EXTEND_CONFIG": "🔁 Extend config",
        "BTN_EDIT_CONFIG": "⚙️ Edit config",

        "CHOOSE_LOCATION": "🌍 Choose location:",
        "BTN_SOON": "🚧 Soon...",
        "CHOOSE_CONFIG_TARIFF": "💳 Choose config tariff:",

        "PAY_SUMMARY": (
            "💵 <b>Payment amount:</b> {amount}rub\n"
            "💰 <b>Your balance:</b> {balance}rub"
        ),
        "PAY_FROM_BALANCE": (
            "💵 <b>Amount to pay:</b> {amount}rub\n\n"
            "💰 <b>Your balance:</b> {balance}rub"
        ),
        
        "INVOICE_DEPOSIT_TITLE" : "💳 Bot balance top-up: {amount}rub for {name}",
        "INVOICE_DEPOSIT_DESC" : "{amount}rub will be credited to {name}({id}) in-bot balance and can be used to buy access keys and other services.",
        "INVOICE_CONFIG_TITLE" : "🔑 Access key purchase for {duration}",
        "INVOICE_CONFIG_DESC" : "Payment for a digital access key via server {location} for {duration}. After payment you will receive a file and a QR code to connect.",
        "INVOICE_EXTEND_TITLE": "🔁 Extend key {name} for {duration}",
        "INVOICE_EXTEND_DESC": "Payment for extending the validity of your digital access key {name} for {duration}. After payment the validity period will be extended automatically.",
        "CONFIG_EXTEND_SUCCESS" : "✅ Config <b>{name}</b> was successfully extended.",
        "CONFIG_VALID_UNTIL": "⏰ Valid until: {date} (GMT+3)",
        
        "CONFIG_EXPIRES": "⏳ The validity period of your key {code_name} expires within two days.",
        "CONFIGS_EXPIRES": "⏳ The validity period of your keys {code_name} expires within two days.",

        "CONFIG_SETTINGS_PROMPT": "⚙️ What do you want to change in config <b>{config}</b>?",
        "ASK_CONFIG_NAME": "✏️ Enter new config name (max. 32 characters):",
        "CHANGING_CONFIG_NAME": (
            "✏️ You want to change the config name:\n"
            "• <b>Current:</b> {old_name}\n"
            "• <b>New:</b> {new_name}\n\n"
            "Confirm change?"
        ),
        "TOO_LONG_NAME": "⚠️ Name is too long! Maximum length is 32 characters.",
        "CONFIG_NAME_CHANGED": (
            "✅ Config name\n"
            "<code>{code_name}</code>\n"
            "was successfully changed to:\n"
            "<b>{text}</b>"
        ),
        
        "ASK_CONFIG_DESC": "✏️ Enter new config description (max. 255 characters):",
        "CHANGING_CONFIG_DESC": (
            "✏️ You want to change the config description:\n"
            "• <b>Current:</b> {old_desc}\n"
            "• <b>New:</b> {new_desc}\n\n"
            "Confirm change?"
        ),
        "TOO_LONG_DESC": "⚠️ Description is too long! Maximum length is 255 characters.",
        "SET_CONFIG_DESC": (
            "✏️ You want to set the following config description:\n"
            "{new_desc}\n\n"
            "Confirm?"
        ),
        "CONFIG_DESC_CHANGED": (
            "✅ Config description was successfully changed to:\n"
            "<b>{text}</b>"
        ),

        "CONFIG_EXPIRED_DELETED": (
            "⏳ The validity period of your config <code>{code_name}</code> has expired "
            "and it was deleted."
        ),

        # ==== Referrals ====
        "REFERAL_BECAME": "🤝 You are now {user}'s referral.",
        "INPUT_REFERAL": "🔑 Enter referral code:",
        "REFERAL_ERR": "⚠️ You are already a referral of another user or this code does not exist.",

        "REFERRAL_PROGRAM": "👥 Referral program",
        "REFERRAL_MENU_TITLE": "👥 Referrals",
        "REFERRAL_ENTER_CODE": "🔑 Enter referral code:",

        "BTN_MY_REF_CODE": "🧾 My referral code",
        "BTN_INPUT_REF_CODE": "✏️ Enter referral code",
        "BTN_COPY_CODE": "📋 Copy code",
        "BTN_COPY_LINK": "🔗 Copy link",
        "REF_CODE_TEXT": "🧾 Your referral code:\n<code>{code}</code>",

        # ==== Balance ====
        "SEND_INT": "🔢 Send an integer number.",
        "MIN_AMOUNT": "⚠️ Minimum amount — {min}rub.",
        "ASK_DEPOSIT_SUM": "💳 Send deposit amount in rubles (from 80 rub):",
        "DEPOSIT_CANCELED": "❌ Deposit cancelled.",
        "BALANCE_DEPOSIT_SUCCESS": "✅ Your balance has been credited with {amount}rub.",
        "BALANCE" : "Balance(-5%)",

        # ==== Bot info ====
        "ACCOUNT_MENU_TITLE": "👤 Account",
        "BOT_CHANNEL": "📢 Bot channel",
        "BOT_SITE" : "🌐 Website",
        "BOT_INFO": (
            "🔐 <b>Kirians-VPW</b> is a bot for managing digital access keys to online services.\n\n"
            "With its help, you can:\n\n"
            "• obtain and renew digital access keys 🗝\n"
            "• connect to remote servers using convenient applications 📱💻\n"
            "• access online services that may be unavailable in your region 🌍\n\n"
            "📂 All your keys are stored in your personal dashboard — at any time you can:\n"
            "• download a configuration file\n"
            "• scan a QR code\n"
            "• extend the validity period of a key\n\n"
            "<b>Supported applications</b>\n"
            "📱 <b>Android:</b> "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> · "
            "<a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
            "🍏 <b>Apple:</b> "
            "<a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> · "
            "<a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
            "💻 <b>Windows:</b> "
            "<a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>\n\n"
            "⚠️ <b>Important</b>\n\n"
            "Each digital access key is intended for <b>one active connection</b>.\n"
            "You cannot use the same key on multiple devices at the same time.\n\n"
            "However, you may use the key on different devices <b>one at a time</b> — "
            "just disconnect on one device before connecting on another."
        ),

        "SOON_FUNC": "🚧 This function isn't available now. I may add it later...",
        "PRECHECKOUT_ERROR": "⚠️ Error. Try again or write to the bot's group.",
        "MIN" : "minutes",
        "H" : "",
        "D" : "days",
        "M" : "month",

        # ==== Buttons ====
        "YES": "✅ Yes",
        "CANCEL": "❌ Cancel",
        "BACK": "⬅️ Back",
        "Оплатить": "💳 Pay",
        "Отмена": "❌ Cancel",
        "RUB": "rub"
    },
}



async def tr(words: str, locale: str | None = None) -> str:
    locale = locale or DEFAULT_LOCALE
    lang_dict = TRANSLATIONS.get(locale) or TRANSLATIONS[DEFAULT_LOCALE]
    return lang_dict.get(words, words)
