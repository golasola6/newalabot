from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from pyrogram import Client, filters

@Client.on_message(filters.command('buy_premium'))
async def buy_premium(_, message):
    text = """🎖 PREMIUM MEMBERSHIP LIVE! 🎖
🔥 LATEST MOVIES & SERIES — SAME DAY RELEASE
🚫 NO ADS | 🌐 ALL LANGUAGES | ❌ NO FREE TRIAL

🎯 OFFER ENDING 5 JUNE! 🎯

💸 NEW PRICES:
✨ 1 Month – ₹100 (Quick access, no commitment)
🔥 3 Month – ₹225 (₹75/mo — Save ₹225)
⚡️ 6 Month – ₹375 (₹62/mo — Save ₹375)
⭐️ 9 Month – ₹450 (₹50/mo — Save ₹450)
🏆 12 Month – ₹550 (₹45/mo — Save ₹550)

⚠️ LIMITED SLOTS!
💬 DM 👉 @Simplifytuber2 TO BUY NOW!
"""
    keyboard = InlineKeyboardMarkup([[  
        InlineKeyboardButton("🫰 Buy Premium 💸", url="https://t.me/Simplifytuber2")],  
        [InlineKeyboardButton("Cancel Premium", callback_data="close_data")]])
    await message.reply_text(text=text, reply_markup=keyboard)
