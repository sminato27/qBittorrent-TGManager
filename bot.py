import os
import time
import zipfile
import psutil
from qbittorrentapi import Client
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pyrogram import Client as PyroClient
from dotenv import load_dotenv

load_dotenv()

# Configurações do Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configurações do qBittorrent
QB_USERNAME = os.getenv("QB_USERNAME")
QB_PASSWORD = os.getenv("QB_PASSWORD")
QB_HOST = os.getenv("QB_HOST")

# Inicialização do bot e cliente do qBittorrent
bot = Bot(token=BOT_TOKEN)
qbt = Client(host=QB_HOST, username=QB_USERNAME, password=QB_PASSWORD)

def send_message(bot, message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def start_download(update: Update, context: CallbackContext):
    torrents = qbt.torrents_info()
    for torrent in torrents:
        if torrent.state == "downloading":
            message = f"""\
Name: {torrent.name}
Status: {torrent.state}
[{int(torrent.progress * 10) * "▰"}{(10 - int(torrent.progress * 10)) * "▱"}] {torrent.progress * 100:.2f}%
Processed: {torrent.size_downloaded / (1024 ** 3):.2f}GB of {torrent.total_size / (1024 ** 3):.2f}GB
Speed: {torrent.dlspeed / (1024 ** 2):.2f} MB/s | ETA: {torrent.eta} s
Time Elapsed: {torrent.time_active} s

CPU: {psutil.cpu_percent()}% | FREE: {psutil.virtual_memory().available / (1024 ** 3):.2f}GB
RAM: {psutil.virtual_memory().percent}% | UPTIME: {time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))}
DL: {torrent.dlspeed / (1024 ** 2):.2f} MB/s | UL: {torrent.upspeed / (1024 ** 2):.2f} MB/s
"""
            send_message(bot, message)

def on_complete(torrent):
    if torrent.progress == 1:
        zip_and_send(torrent)

def zip_and_send(torrent):
    # Dividindo e compactando em pedaços de 2GB
    part_size = 2 * 1024 * 1024 * 1024  # 2GB
    with zipfile.ZipFile(f"{torrent.name}.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(torrent.save_path)

    # Enviando para o Telegram
    with PyroClient("my_account") as app:
        app.send_document(CHAT_ID, f"{torrent.name}.zip")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_download))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()