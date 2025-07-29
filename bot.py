import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Respuestas predefinidas
RESPUESTAS = {
    "zapatillas nike": [
        "https://ejemplo.com/nike1",
        "https://ejemplo.com/nike2"
    ],
    "adidas": [
        "https://ejemplo.com/adidas1",
        "https://ejemplo.com/adidas2"
    ]
}

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Pregúntame por zapatillas (ej: 'zapatillas nike').")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower().strip()

    if texto in RESPUESTAS:
        links = "\n".join(RESPUESTAS[texto])
        await update.message.reply_text(f"Estas son todas las {texto}:\n{links}")
    else:
        await update.message.reply_text("No tengo esa información aún. Prueba con 'zapatillas nike' o 'adidas'.")

# Crear aplicación de Telegram
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# Iniciar el bot cuando Flask arranca
@app.before_first_request
def iniciar_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(application.start())
    print("Bot de Telegram iniciado")

# Webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return "ok"

# Home route
@app.route("/")
def home():
    return "Bot funcionando en Render!"

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
