FROM python:3.10

# Instala pacotes
RUN pip install python-telegram-bot qbittorrent-api psutil pyrogram tgcrypto python-dotenv

# Copia o script e as variáveis de ambiente para o contêiner
WORKDIR /bot
COPY bot.py /bot/
COPY .env /bot/

# Executa o script
CMD ["python", "/bot/bot.py"]