FROM python:3.10

# Instala pacotes
RUN pip install python-telegram-bot qbittorrent-api psutil pyrogram tgcrypto

# Copia o script e as variáveis de ambiente para o contêiner
WORKDIR /bot
COPY bot.py .
COPY .env .

# Executa o script
CMD ["python", "bot.py"]