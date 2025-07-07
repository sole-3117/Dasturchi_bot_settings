import telebot
from telebot.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
import json
import os

# === Sozlamalar ===
API_TOKEN = '7733746139:AAF9OpkPEXDqObRIC23YbNOJrNmEW6On590'  # ← Bot tokeningizni bu yerga yozing
ADMIN_ID = 6887251996         # ← Faqat siz snippet qo‘sha olasiz

bot = telebot.TeleBot(API_TOKEN)

# === JSON faylga snippet yozish ===
SNIPPETS_FILE = "code_snippets.json"

def load_snippets():
    if not os.path.exists(SNIPPETS_FILE):
        return []
    with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_snippets(snippets):
    with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=2, ensure_ascii=False)

# === Start komandasi ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    web_app_url = "https://yourdomain.com/app"  # ← Web App sahifangizni bu yerga qo‘ying
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("👨‍💻 Mashqni boshlash", web_app=WebAppInfo(url=web_app_url))
    )
    bot.send_message(message.chat.id, f"Assalomu alaykum, {message.from_user.first_name}! 👋\nMashqni boshlash uchun tugmani bosing:", reply_markup=markup)

# === Snippet qo‘shish uchun vaqtinchalik holat saqlovchi o‘zgaruvchi ===
user_states = {}

# === /add_snippet komandasi (faqat admin uchun) ===
@bot.message_handler(commands=['add_snippet'])
def add_snippet_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Sizda bu buyruqni ishlatish huquqi yo‘q.")
        return

    user_states[message.from_user.id] = {'step': 'language'}
    markup = InlineKeyboardMarkup()
    langs = ['Python', 'JavaScript', 'C++']
    for lang in langs:
        markup.add(InlineKeyboardButton(lang, callback_data=f"lang_{lang.lower()}"))
    bot.send_message(message.chat.id, "📚 Kod snippet uchun dasturlash tilini tanlang:", reply_markup=markup)

# === Callback tugmalarni qayta ishlash ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_") or call.data.startswith("level_"))
def callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return

    state = user_states[user_id]

    if call.data.startswith("lang_"):
        lang = call.data.split("_")[1]
        user_states[user_id]['language'] = lang
        user_states[user_id]['step'] = 'text'
        bot.send_message(call.message.chat.id, f"✅ Til tanlandi: {lang.title()}\n\n✍️ Endi kod snippetni yozib yuboring (bir yoki bir nechta qatorda):")

    elif call.data.startswith("level_"):
        level = call.data.split("_")[1]
        state = user_states[user_id]
        snippet = {
            "id": len(load_snippets()) + 1,
            "language": state['language'],
            "text": state['text'],
            "level": level
        }
        snippets = load_snippets()
        snippets.append(snippet)
        save_snippets(snippets)

        bot.send_message(call.message.chat.id, "✅ Kod snippet muvaffaqiyatli saqlandi!")
        del user_states[user_id]

# === Kod matni yuborilsa ===
@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id]['step'] == 'text')
def snippet_text_handler(message):
    user_states[message.from_user.id]['text'] = message.text
    user_states[message.from_user.id]['step'] = 'level'
    markup = InlineKeyboardMarkup()
    for level in ['easy', 'medium', 'hard']:
        markup.add(InlineKeyboardButton(level.title(), callback_data=f"level_{level}"))
    bot.send_message(message.chat.id, "🔢 Qiyinlik darajasini tanlang:", reply_markup=markup)

# === Botni ishga tushirish ===
print("🤖 Bot ishga tushdi...")
bot.infinity_polling()
