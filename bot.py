import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# এখানে আপনার BotFather-এর আসল API Token বসান
TOKEN = 'YOUR_BOT_TOKEN_HERE'

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Terabox", callback_data='platform_terabox'),
         InlineKeyboardButton("▶️ YouTube", callback_data='platform_youtube')],
        [InlineKeyboardButton("📸 Instagram", callback_data='platform_instagram'),
         InlineKeyboardButton("🎵 TikTok", callback_data='platform_tiktok')],
        [InlineKeyboardButton("🌐 Other Websites", callback_data='platform_others')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 **Welcome to Universal Downloader Bot!**\n\nআপনি কোন প্ল্যাটফর্ম থেকে ডাউনলোড করতে চান? নিচের বাটন সিলেক্ট করুন:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    platform = query.data.split('_')[1].capitalize()
    await query.message.reply_text(f"✅ আপনি **{platform}** সিলেক্ট করেছেন।\n\nএখন লিঙ্কটি সেন্ড করুন:")

async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("🔎 **High Quality Download Link প্রসেস করা হচ্ছে...**")

    if "terabox" in url or "1024tera" in url or "teraboxapp" in url:
        await status_msg.edit_text("⚡ **Terabox Link Found!**\n\nDirect High-Speed Download Link তৈরি হচ্ছে...")
        terabox_direct_link = f"https://terabox-dl.qt0.workers.dev/?url={url}" 
        download_btn = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download HD Video", url=terabox_direct_link)]])
        await update.message.reply_text("এখানে ক্লিক করে ফাইলটি ডাউনলোড করুন:", reply_markup=download_btn)
        return

    ydl_opts = {'format': 'best', 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url', None)
            title = info.get('title', 'High Quality Media')

            if download_url:
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Direct High-Quality Download", url=download_url)]])
                await status_msg.edit_text(f"🎬 **Title:** {title}\n\nআপনার ডাউনলোড লিঙ্ক তৈরি হয়ে গেছে:", reply_markup=btn)
            else:
                await status_msg.edit_text("❌ সরাসরি ডাউনলোড লিঙ্ক পাওয়া যায়নি।")

    except Exception as e:
        await status_msg.edit_text("❌ লিঙ্কটি প্রসেস করতে সমস্যা হয়েছে।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
    app.run_polling()

if __name__ == '__main__':
    main()
  
