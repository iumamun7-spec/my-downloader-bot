import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Render-এর জন্য ডামি HTTP Server (২৪/৭ রাখার জন্য)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"All Social Media Downloader Bot is Running!")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# টেলিগ্রামের মূল বার্তা ও কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **স্বাগতম!**\n\n"
        "আমি একটি অল-ইন-ওয়ান সোশ্যাল মিডিয়া ডাউনলোডার বট।\n"
        "যেকোনো ভিডিওর লিঙ্ক (YouTube, Facebook, Instagram, TikTok ইত্যাদি) পাঠালেই আমি তা ডাউনলোড করে দেব।"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ **লিংক প্রসেস করা হচ্ছে এবং ভিডিও ডাউনলোড শুরু হয়েছে...**")
    
    # yt-dlp সেটআপ
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_media.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,  # Render ফ্রি ভার্সনে ৫০ MB সীমাবদ্ধতা
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 **ডাউনলোড সম্পন্ন! ভিডিও টেলিগ্রামে আপলোড করা হচ্ছে...**")
        
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="✅ আপনার ভিডিও প্রস্তুত!")

        # কাজ শেষ হলে সার্ভার থেকে ভিডিও মুছে ফেলা
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        error_text = str(e)
        if "File is larger than" in error_text:
            await status_msg.edit_text("❌ ভিডিওটির সাইজ ৫০ MB-এর চেয়ে বড়। Render ফ্রি প্ল্যানে এটি ডাউনলোড করা সম্ভব নয়।")
        else:
            await status_msg.edit_text("❌ ভিডিও ডাউনলোড করতে সমস্যা হয়েছে। দয়া করে সঠিক ও পাবলীক ভিডিও লিঙ্ক পাঠান।")

if __name__ == '__main__':
    # আপনার আসল বট টোকেন
    TOKEN = "8893716569:AAEVseUecLvH7mxqOpCAUfKU73NiYGeSbm8"
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    logging.info("Downloader Bot status: Running")
    app.run_polling()
