import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Obtiene el token desde las variables de entorno en Render
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Diccionario de respuestas predefinidas
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

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Pregúntame por zapatillas (ej: 'zapatillas nike').")

# Mensajes de texto
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower().strip()

    if texto in RESPUESTAS:
        links = "\n".join(RESPUESTAS[texto])
        await update.message.reply_text(f"Estas son todas las {texto}:\n{links}")
    else:
        await update.message.reply_text("No tengo esa información aún. Prueba con 'zapatillas nike' o 'adidas'.")

# Configuración del bot
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# Ruta del webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Ruta principal para probar si está vivo
@app.route("/")
def home():
    return "Bot funcionando en Render!"

# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
