import telebot
from telebot import types
import json
import os

# ==================== НАСТРОЙКИ ====================
TOKEN = "8892309856:AAFvJROuKj-EPgbYSaDaAokwZ0Gxu4s96VQ"  # Твой токен
ADMIN_USERNAME = "@GSecho"  # Твоя техподдержка
SUPPORT_BOT = "@TRILLION_VIP_BOT" # Бот для сотрудничества

bot = telebot.TeleBot(TOKEN)

# --- БАЗА ТОВАРОВ (Мужское трико) ---
PRODUCTS = {
    "1": {"name_ru": "Трико Classic Black", "name_uz": "Klassik qora triko", "price": 450000, "desc_ru": "Классическое черное трико. 100% хлопок.", "desc_uz": "Klassik qora triko. 100% paxta.", "image": "https://via.placeholder.com/600x600.png?text=Classic+Black"},
    "2": {"name_ru": "Трико Sport Grey", "name_uz": "Sport kulrang triko", "price": 490000, "desc_ru": "Спортивное серое трико. Для тренировок.", "desc_uz": "Sport kulrang triko. Mashg'ulotlar uchun.", "image": "https://via.placeholder.com/600x600.png?text=Sport+Grey"},
    "3": {"name_ru": "Трико Premium Navy", "name_uz": "Premium to'q ko'k triko", "price": 520000, "desc_ru": "Премиальное темно-синее трико.", "desc_uz": "Premium to'q ko'k triko.", "image": "https://via.placeholder.com/600x600.png?text=Premium+Navy"},
}

# Хранилище корзин и данных
carts = {}
users_lang = {} # Храним выбранный язык для каждого юзера

def save_data():
    with open('trillion_data.json', 'w', encoding='utf-8') as f:
        json.dump({"carts": carts, "lang": users_lang}, f, ensure_ascii=False)

def load_data():
    global carts, users_lang
    if os.path.exists('trillion_data.json'):
        with open('trillion_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            carts = data.get("carts", {})
            users_lang = data.get("lang", {})

# ==================== ТЕКСТЫ (RU / UZ) ====================
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в *TRILLION*!\n\nПремиальное мужское трико.\nВыбери действие:",
        "catalog": "🛍 *Коллекция*",
        "cart": "🛒 *Корзина*",
        "empty_cart": "Твоя корзина пуста.",
        "order": "✅ Оформить заказ",
        "support": f"🆘 *Техподдержка*\n\nПо всем вопросам пиши: {ADMIN_USERNAME}",
        "coop": f"🤝 *Сотрудничество*\n\nПереходи в нашего бота: {SUPPORT_BOT}",
        "back": "⬅️ Назад",
        "add": "➕ Добавить в корзину",
        "del": "❌ Удалить",
        "total": "💰 *Итого:*",
        "checkout_text": "✍️ *Оформление заказа*\n\nНапиши свои данные одним сообщением:\nФИО\nТелефон\nАдрес",
        "success": "✅ *Заказ оформлен!* Менеджер свяжется с тобой.",
        "lang_btn": "🌐 Язык / Til"
    },
    "uz": {
        "welcome": "👋 *TRILLION* ga xush kelibsiz!\n\nPremium erkaklar trikosi.\nAmalni tanlang:",
        "catalog": "🛍 *Kolleksiya*",
        "cart": "🛒 *Savat*",
        "empty_cart": "Savatingiz bo'sh.",
        "order": "✅ Buyurtma berish",
        "support": f"🆘 *Qo'llab-quvvatlash*\n\nBarcha savollar uchun yozing: {ADMIN_USERNAME}",
        "coop": f"🤝 *Hamkorlik*\n\nBotimizga o'ting: {SUPPORT_BOT}",
        "back": "⬅️ Orqaga",
        "add": "➕ Savatga qo'shish",
        "del": "❌ O'chirish",
        "total": "💰 *Jami:*",
        "checkout_text": "✍️ *Buyurtma berish*\n\nMa'lumotlaringizni bitta xabarda yozing:\nF.I.Sh\nTelefon\nManzil",
        "success": "✅ *Buyurtma qabul qilindi!* Menejer tez orada bog'lanadi.",
        "lang_btn": "🌐 Язык / Til"
    }
}

def get_text(user_id, key):
    lang = users_lang.get(str(user_id), "ru")
    return TEXTS[lang][key]

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    lang = users_lang.get(str(user_id), "ru")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if lang == "ru":
        markup.add("🛍 Каталог", "🛒 Корзина")
        markup.add("🤝 Сотрудничать", "🆘 Техподдержка")
        markup.add("🌐 Язык / Til")
    else:
        markup.add("🛍 Kolleksiya", "🛒 Savat")
        markup.add("🤝 Hamkorlik", "🆘 Qo'llab-quvvatlash")
        markup.add("🌐 Язык / Til")
        
    return markup

def catalog_menu(user_id):
    lang = users_lang.get(str(user_id), "ru")
    markup = types.InlineKeyboardMarkup(row_width=1)
    for pid, item in PRODUCTS.items():
        name = item["name_ru"] if lang == "ru" else item["name_uz"]
        btn = types.InlineKeyboardButton(f"{name} — {item['price']} сум", callback_data=f"view_{pid}")
        markup.add(btn)
    return markup

def product_menu(pid, user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(get_text(user_id, "add"), callback_data=f"add_{pid}"))
    markup.add(types.InlineKeyboardButton(get_text(user_id, "back"), callback_data="back_catalog"))
    return markup

def cart_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    cart = carts.get(str(user_id), {})
    lang = users_lang.get(str(user_id), "ru")
    
    if not cart:
        markup.add(types.InlineKeyboardButton(get_text(user_id, "back"), callback_data="back_catalog"))
        return markup
        
    for pid, qty in cart.items():
        if pid in PRODUCTS:
            name = PRODUCTS[pid]["name_ru"] if lang == "ru" else PRODUCTS[pid]["name_uz"]
            markup.add(types.InlineKeyboardButton(f"{get_text(user_id, 'del')} {name}", callback_data=f"rem_{pid}"))
            
    markup.add(types.InlineKeyboardButton(get_text(user_id, "order"), callback_data="checkout"))
    markup.add(types.InlineKeyboardButton(get_text(user_id, "back"), callback_data="back_catalog"))
    return markup

# ==================== ХЕНДЛЕРЫ ====================

@bot.message_handler(commands=['start'])
def start(message):
    load_data()
    user_id = str(message.from_user.id)
    
    if user_id not in carts:
        carts[user_id] = {}
    if user_id not in users_lang:
        users_lang[user_id] = "ru" # По умолчанию русский
    save_data()
        
    bot.send_message(
        message.chat.id,
        get_text(user_id, "welcome"),
        parse_mode='Markdown',
        reply_markup=main_menu(user_id)
    )

# Переключение языка
@bot.message_handler(func=lambda message: message.text in ["🌐 Язык / Til", "🌐 Язык", "🌐 Til"])
def switch_lang(message):
    user_id = str(message.from_user.id)
    current = users_lang.get(user_id, "ru")
    users_lang[user_id] = "uz" if current == "ru" else "ru"
    save_data()
    
    bot.send_message(
        message.chat.id,
        get_text(user_id, "welcome"),
        parse_mode='Markdown',
        reply_markup=main_menu(user_id)
    )

# Обработка кнопок меню (учитываем оба языка)
@bot.message_handler(func=lambda message: message.text in ["🛍 Каталог", "🛍 Kolleksiya"])
def show_catalog(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, get_text(user_id, "catalog"), parse_mode='Markdown', reply_markup=catalog_menu(user_id))

@bot.message_handler(func=lambda message: message.text in ["🛒 Корзина", "🛒 Savat"])
def show_cart(message):
    user_id = str(message.from_user.id)
    cart = carts.get(user_id, {})
    
    if not cart:
        bot.send_message(message.chat.id, get_text(user_id, "empty_cart"), reply_markup=main_menu(user_id))
        return

    total = 0
    text = get_text(user_id, "cart") + "\n\n"
    lang = users_lang.get(user_id, "ru")
    
    for pid, qty in cart.items():
        if pid in PRODUCTS:
            item = PRODUCTS[pid]
            name = item["name_ru"] if lang == "ru" else item["name_uz"]
            item_total = item['price'] * qty
            total += item_total
            text += f"• {name} — {qty} шт. = {item_total} сум\n"
            
    text += f"\n{get_text(user_id, 'total')} {total} сум"
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=cart_menu(user_id))

@bot.message_handler(func=lambda message: message.text in ["🤝 Сотрудничать", "🤝 Hamkorlik"])
def coop(message):
    user_id = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Перейти в бот / Botga o'tish", url=f"https://t.me/{SUPPORT_BOT.replace('@', '')}")
    markup.add(btn)
    bot.send_message(message.chat.id, get_text(user_id, "coop"), parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["🆘 Техподдержка", "🆘 Qo'llab-quvvatlash"])
def support(message):
    user_id = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Написать / Yozish", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    markup.add(btn)
    bot.send_message(message.chat.id, get_text(user_id, "support"), parse_mode='Markdown', reply_markup=markup)

# ==================== CALLBACK КНОПКИ ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = str(call.from_user.id)
    lang = users_lang.get(user_id, "ru")
    
    if call.data.startswith("view_"):
        pid = call.data.split("_")[1]
        if pid in PRODUCTS:
            item = PRODUCTS[pid]
            name = item["name_ru"] if lang == "ru" else item["name_uz"]
            desc = item["desc_ru"] if lang == "ru" else item["desc_uz"]
            text = f"*{name}*\n\n{desc}\n\n💰 {item['price']} сум"
            bot.send_photo(call.message.chat.id, item['image'], caption=text, parse_mode='Markdown', reply_markup=product_menu(pid, user_id))
            bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data.startswith("add_"):
        pid = call.data.split("_")[1]
        if user_id not in carts:
            carts[user_id] = {}
        carts[user_id][pid] = carts[user_id].get(pid, 0) + 1
        save_data()
        bot.answer_callback_query(call.id, "✅ Добавлено / Qo'shildi!")
        
    elif call.data.startswith("rem_"):
        pid = call.data.split("_")[1]
        if user_id in carts and pid in carts[user_id]:
            del carts[user_id][pid]
            save_data()
            bot.answer_callback_query(call.id, "❌ Удалено / O'chirildi")
            show_cart(call.message)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass

    elif call.data == "back_catalog":
        bot.send_message(call.message.chat.id, get_text(user_id, "catalog"), parse_mode='Markdown', reply_markup=catalog_menu(user_id))
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass

    elif call.data == "checkout":
        cart = carts.get(user_id, {})
        if not cart:
            bot.answer_callback_query(call.id, "Пусто / Bo'sh!", show_alert=True)
            return
            
        msg = bot.send_message(call.message.chat.id, get_text(user_id, "checkout_text"), parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_order)

# ==================== ОФОРМЛЕНИЕ ЗАКАЗА ====================

def process_order(message):
    user_id = str(message.from_user.id)
    lang = users_lang.get(user_id, "ru")
    
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, get_text(user_id, "welcome"), reply_markup=main_menu(user_id))
        return
        
    cart = carts.get(user_id, {})
    total = 0
    order_summary = f"🛒 *Новый заказ TRILLION!*\n\n"
    order_summary += f"👤 Клиент: @{message.from_user.username or 'Нет'} (ID: {user_id})\n"
    order_summary += f"📋 Данные:\n{message.text}\n\n"
    order_summary += "📦 *Товары:*\n"
    
    for pid, qty in cart.items():
        if pid in PRODUCTS:
            item = PRODUCTS[pid]
            name = item["name_ru"] if lang == "ru" else item["name_uz"]
            item_total = item['price'] * qty
            total += item_total
            order_summary += f"• {name} — {qty} шт. = {item_total} сум\n"
            
    order_summary += f"\n💰 *Итого: {total} сум*"

    carts[user_id] = {}
    save_data()

    bot.send_message(message.chat.id, get_text(user_id, "success"), parse_mode='Markdown', reply_markup=main_menu(user_id))
    
    # Отправка тебе (Админу)
    ADMIN_ID = 7121055768 # Твой ID
    try:
        bot.send_message(ADMIN_ID, order_summary, parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, get_text(user_id, "welcome"), parse_mode='Markdown', reply_markup=main_menu(user_id))

if __name__ == '__main__':
    load_data()
    print("Бот TRILLION (Men's Trico Edition) запущен...")
    bot.infinity_polling()