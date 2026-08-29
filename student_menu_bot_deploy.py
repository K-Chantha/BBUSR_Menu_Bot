"""
Telegram Student Menu Bot (v2 — Deploy Version, Webhook on Render)
---------------------------------------------------------------------
ដូចគ្នាបេះបិទនឹង student_menu_bot_v2.py ខាងក្នុងទាំងអស់ (Menu, ចម្លើយ, Chat Menu
Button) លើកលែងតែផ្នែកចាប់ផ្តើម Bot ដែលប្តូរពី Polling ទៅ Webhook ដើម្បីអាច Deploy
លើ Render ឱ្យដំណើរការជាប់ជានិច្ច 24/7 ដោយមិនចាំបាច់បើក Terminal ខ្លួនឯង។

តម្រូវការ:
    pip install python-telegram-bot --upgrade
"""

import os
import logging
from telegram import (
    ReplyKeyboardMarkup,
    Update,
    KeyboardButton,
    BotCommand,
    MenuButtonDefault,
    LinkPreviewOptions,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==========================================================
# 1) កំណត់ TOKEN របស់ Bot
#    ⚠️ លើ Render កុំសរសេរ Token ត្រង់នេះ! ត្រូវដាក់ជា Environment Variable
#    ឈ្មោះ BOT_TOKEN នៅក្នុងផ្ទាំង Render (មិនដាក់ក្នុងកូដ ដើម្បីសុវត្ថិភាព)
# ==========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
# Render ផ្តល់ Domain ខាងក្រៅតាម Environment Variable នេះស្វ័យប្រវត្តិ
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
PORT = int(os.environ.get("PORT", 10000))

# ==========================================================
# 2) សារស្វាគមន៍ដែលបង្ហាញនៅពេលចាប់ផ្តើម Bot (ដូចសារភ្ជាប់ Pin ក្នុងរូបគំរូ)
# ==========================================================
WELCOME_MESSAGE = (
    "📌 សូមស្វាគមន៍មកកាន់ BBUSR Academic News\n\n"
    "សូមចុចប៊ូតុងខាងក្រោម ឬវាយ /menu ឬ /start 👇"
)

# ==========================================================
# 3) ទិន្នន័យ Menu — កែសម្រួល/បន្ថែម/លុបចំណុចនៅទីនេះបានទាំងអស់
#    key = ចំណងជើងលើប៊ូតុង (ត្រូវតែដូចគ្នាបេះបិទនឹងអ្វីអ្នកចង់ឱ្យគេចុច)
#    value = ចម្លើយដែលបង្ហាញ
# ==========================================================
MENU = {
    "📊 ពិន្ទុ": (
        "*ការមើលពិន្ទុ*\n\n"
        "1. ការជូនដំណឹងពិន្ទុប្រឡងជាផ្លូវការ ធ្វើឡើងតាមការជូនដំណឹងក្នុងក្រុម Telegram\n"
        "2. និស្សិតអាចចូលមើលពិន្ទុមុខវិជ្ជាទាំងអស់ដែលបានប្រឡងនៅក្នុង BBU App\n"
        "3. ពិន្ទុមុខវិជ្ជានីមួយៗ ចាប់ពី៦០ ឡើងទៅ សន្មត់ថា *ជាប់*\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា ឌី សុម៉ាវត្តី\n"
        "☎️ ទូរស័ព្ទ៖ 086 657 788\n"
        "📱 តេឡេក្រាម [@Mateydy](https://t.me/Mateydy)"
    ),
    "📝 ការស្នើសុំកែតម្រូវពិន្ទុ": (
        "*ការស្នើសុំកែតម្រូវពិន្ទុ*\n\n"
        "1. ដាក់ពាក្យស្នើសុំក្នុងរយៈពេល ៧ ថ្ងៃ បន្ទាប់ពីប្រកាសពិន្ទុ\n"
        "2. បំពេញទម្រង់ស្នើសុំកែតម្រូវពិន្ទុ ជាមួយហេតុផលច្បាស់លាស់\n"
        "3. ភ្ជាប់ភស្តុតាង (ប្រសិនបើមាន)\n"
        "4. ដាក់ជូនផ្នែកសេវានិស្សិត ដើម្បីពិនិត្យឡើងវិញ\n"
        "5. លទ្ធផលនឹងជូនដំណឹងវិញក្នុងរយៈពេលកំណត់\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា លី ច័ន្ទចរិយា\n"
        "☎️ ទូរស័ព្ទ៖ 011 292 212\n"
        "📱 តេឡេក្រាម [@ly_chanchakriya](https://t.me/ly_chanchakriya)"
    ),
    "📄 ការសុំច្បាប់": (
        "*ការសុំច្បាប់*\n\n"
        "1. មកយកទម្រង់សុំច្បាប់ពីផ្នែកសេវានិស្សិត\n"
        "2. ដាក់ស្នើមុនថ្ងៃសម្រាកយ៉ាងតិច ១ ថ្ងៃ (លើកលែងករណីបន្ទាន់)\n"
        "3. ភ្ជាប់ភស្តុតាង (ដូចជាលិខិតវេជ្ជបណ្ឌិត ក្នុងករណីឈឺ)\n"
        "4. ដាក់ជូនផ្នែកសេវានិស្សិត ដើម្បីឆ្លងការអនុម័ត\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា លី ច័ន្ទចរិយា\n"
        "☎️ ទូរស័ព្ទ៖ 011 292 212\n"
        "📱 តេឡេក្រាម [@ly_chanchakriya](https://t.me/ly_chanchakriya)"
    ),
    "📋 ការស្នើសុំកែអវត្តមាន": (
        "*ការស្នើសុំកែអវត្តមាន*\n\n"
        "1. ប្រើក្នុងករណីអវត្តមានត្រូវបានកត់ត្រាខុសឆ្គង\n"
        "2. បំពេញទម្រង់ស្នើសុំកែអវត្តមាន ជាមួយកាលបរិច្ឆេទ និងមុខវិជ្ជាដែលមានបញ្ហា\n"
        "3. ភ្ជាប់ភស្តុតាង (ឧ. រូបថតវត្តមាន, សារបញ្ជាក់ពីគ្រូ)\n"
        "4. ដាក់ជូនផ្នែកសេវានិស្សិតពិនិត្យ និងកែតម្រូវក្នុងប្រព័ន្ធ\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា លី ច័ន្ទចរិយា\n"
        "☎️ ទូរស័ព្ទ៖ 011 292 212\n"
        "📱 តេឡេក្រាម [@ly_chanchakriya](https://t.me/ly_chanchakriya)"
    ),
    "🔄 ការប្តូរវេន/វគ្គសិក្សា": (
        "*ការប្តូរវេន ឬវគ្គសិក្សា*\n\n"
        "1. ដាក់ពាក្យស្នើសុំប្តូរវេន/វគ្គសិក្សានៅផ្នែកកិច្ចការសិក្សា\n"
        "2. បុគ្គលិកជំនាញនឹងពិនិត្យមើលថាតើវេន/វគ្គសិក្សាអាចប្តូរបានដែរឬទេ\n"
        "3. រង់ចាំការអនុម័ត មុននឹងផ្លាស់ប្តូរជាផ្លូវការ\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងលោក សំ គុណថង\n "
        "☎️ ទូរស័ព្ទ៖ 087 750 600\n"
        "📱 តេឡេក្រាម [@Sam_Kunthang](https://t.me/Sam_Kunthang)"
    ),
    "🏫 ការប្តូរទីតាំងសិក្សា": (
        "*ការប្តូរទីតាំង/សាខាសិក្សា*\n\n"
        "1. ដាក់ពាក្យស្នើសុំនៅផ្នែកកិច្ចការសិក្សា\n"
        "2. ជ្រើសរើសសាខាដែលមានជំនាញដូចគ្នា\n"
        "3. រង់ចាំការបញ្ជាក់ការផ្ទេរឯកសារ\n"
        "4. ចាប់ផ្តើមសិក្សានៅសាខាថ្មីតាមកាលវិភាគប្រកាស\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា ម៉ាង ម៉ារ៉ា\n"
        "☎️ ទូរស័ព្ទ៖ 096 587 5802\n"
        "📱 តេឡេក្រាម [@Mara_Mang](https://t.me/Mara_Mang)"
    ),
    "🎓 ការប្តូរជំនាញ": (
        "*ការប្តូរជំនាញសិក្សា*\n\n"
        "1. ពិគ្រោះយោបល់ជាមួយបុគ្គលិកផ្នែកកិច្ចការសិក្សាមុនសិន\n"
        "2. បំពេញទម្រង់ស្នើសុំប្តូរជំនាញ\n"
        "3. ពិនិត្យលក្ខខណ្ឌក្នុងការផ្ទេរ (credit transfer)\n"
        "4. ការអនុម័តចេញផ្លូវការក្រោយពិនិត្យឯកសារ\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងលោក សំ គុណថង\n "
        "☎️ ទូរស័ព្ទ៖ 087 750 600\n"
        "📱 តេឡេក្រាម [@Sam_Kunthang](https://t.me/Sam_Kunthang)"
    ),
    "📜 លិខិតរដ្ឋបាល": (
        "*ការស្នើសុំលិខិតរដ្ឋបាល*\n\n"
        "1. បំពេញទម្រង់ស្នើសុំលិខិត (ឧ. លិខិតបញ្ជាក់ការសិក្សា, ព្រឹត្តិបត្រពិន្ទុ, វិញ្ញាបនបត្របណ្តោះអាសន្ន,...)\n"
        "2. បញ្ជាក់គោលបំណងប្រើប្រាស់លិខិត\n"
        "3. ដាក់ជូននៅផ្នែកកិច្ចការសិក្សា ព្រមទាំងបង់ថ្លៃសេវា (ប្រសិនបើមាន)\n"
        "4. បុគ្គលិកបំពេញថ្ងៃមកទទួលលិខិត\n\n"
        "❓ បើមានចម្ងល់ សូមទំនាក់ទំនងកញ្ញា នឿន ចំប៉ា\n"
        "☎️ ទូរស័ព្ទ៖ 081 762 926\n"
        "📱 តេឡេក្រាម [@NoeunChampa](https://t.me/NoeunChampa)"
    ),
    "☎️ ទំនាក់ទំនង": (
        "*ព័ត៌មានទំនាក់ទំនង*\n\n"
        "📚 ផ្នែកកិច្ចការសិក្សា៖\n"
        "   ☎️ លោក ព្រំ សុភាណុច នាយផ្នែក 098 550 005 ឬ [@PrumSopheanoch](https://t.me/PrumSopheanoch)\n"
        "   ☎️ លោក សំ គុណថង នាយរងផ្នែក 087 750 600 ឬ [@Sam_Kunthang](https://t.me/Sam_Kunthang)\n"
        "   ☎️ កញ្ញា ម៉ាង ម៉ារ៉ា នាយរងផ្នែក 096 587 5802 ឬ [@Mara_Mang](https://t.me/Mara_Mang)\n\n"
        "💼 ផ្នែកសេវានិស្សិត៖\n"
        "   ☎️ លោក នូ ពិសិដ្ឋ នាយផ្នែក 012 751 314 ឬ [@Piseth_Nou](https://t.me/Piseth_Nou)\n"
        "   ☎️ កញ្ញា លី ច័ន្ទចរិយា នាយរងផ្នែក 011 292 212 ឬ [@ly_chanchakriya](https://t.me/ly_chanchakriya)\n\n"
        "🎓 លោក កាំង ចន្ថា នាយករងសាខា 012 727 979 ឬ [@kaingchantha](https://t.me/kaingchantha)"
    ),
}

# សារនៅពេលមិនអាចយល់សំណួរដែលគេវាយចូល (ដូចក្នុងរូបគំរូ)
FALLBACK_MESSAGE = (
    "សូមអភ័យទោស ខ្ញុំមិនអាចឆ្លើយសំណួរបានទេ។\n\n"
    "📱 សូមសួរសំណួរជាមួយ [@BBU_SR_Chat_Bot](http://t.me/BBU_SR_Chat_Bot) វិញ។"
)


def build_keyboard() -> ReplyKeyboardMarkup:
    """បង្កើត Keyboard ជា 3 ជួរឈរ"""
    labels = list(MENU.keys())
    keyboard = [
        [KeyboardButton(label) for label in labels[i:i + 3]]
        for i in range(0, len(labels), 3)
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,   # ធ្វើឱ្យប៊ូតុងតូចល្មម មិនធំពេក
        # is_persistent=True មិនត្រូវដាក់ទេ — វាបង្ខំ Menu ឱ្យនៅជាប់ជានិច្ច
        # ធ្វើឱ្យ icon លាក់/បង្ហាញ (⊞) មិនលេចមកទាល់តែសោះ
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ពេលអ្នកប្រើវាយ /start (ឬចុច Start ដំបូងគេ) — បង្ហាញ Menu ភ្លាមៗ"""
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=build_keyboard(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ដោះស្រាយសារគ្រប់សារដែលអ្នកប្រើវាយចូល៖
    - បើត្រូវនឹងចំណងជើងណាមួយក្នុង Menu → ឆ្លើយតបចម្លើយនោះ
    - បើមិនត្រូវ → ឆ្លើយសារ fallback ជាមួយតំណភ្ជាប់ទៅ Bot ជំនួយបន្ថែម
    """
    text = update.message.text.strip()

    answer = MENU.get(text)
    if answer:
        await update.message.reply_text(
            answer,
            parse_mode="Markdown",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            reply_markup=build_keyboard(),
        )
    else:
        await update.message.reply_text(
            FALLBACK_MESSAGE,
            parse_mode="Markdown",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            reply_markup=build_keyboard(),
        )


async def post_init(application):
    """រត់ម្តងគត់ពេល Bot ចាប់ផ្តើម៖ លុប Chat Menu Button ចេញ (ត្រឡប់ទៅលំនាំដើម
    របស់ Telegram វិញ — គ្មានប៊ូតុងពិសេសខាងឆ្វេងបំផុតទៀតទេ)"""
    await application.bot.set_my_commands([
        BotCommand("start", "ចាប់ផ្តើម Bot / បង្ហាញ Menu"),
        BotCommand("menu", "បង្ហាញ Menu"),
    ])
    await application.bot.set_chat_menu_button(menu_button=MenuButtonDefault())


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler(["start", "menu"], start))
    # ចាប់សារអត្ថបទទាំងអស់ (លើកលែងតែពាក្យបញ្ជា ដូចជា /start)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    if RENDER_EXTERNAL_URL:
        # របៀប Webhook — ប្រើពេល Deploy លើ Render (Bot ដំណើរការជាប់ជានិច្ច)
        webhook_path = BOT_TOKEN  # ប្រើ Token ជា path សម្ងាត់ កុំឱ្យអ្នកដទៃស្មានឃើញ
        print(f"Bot កំពុងចាប់ផ្តើមជា Webhook លើ port {PORT}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=f"{RENDER_EXTERNAL_URL}/{webhook_path}",
        )
    else:
        # របៀប Polling — ប្រើពេលសាកល្បងក្នុងកុំព្យូទ័រផ្ទាល់ខ្លួន
        print("Bot កំពុងដំណើរការជា Polling... (Ctrl+C ដើម្បីបញ្ឈប់)")
        app.run_polling()


if __name__ == "__main__":
    main()
