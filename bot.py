import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Token desde variables de entorno (asegúrate de tener TOKEN en Render)
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("ERROR: La variable de entorno TOKEN no está configurada.")
    exit(1)

bot = Bot(token=TOKEN)
app = Flask(__name__)

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
    print("Comando /start recibido")
    await update.message.reply_text("¡Hola! Pregúntame por zapatillas (ej: 'zapatillas nike').")

# Responder a mensajes de texto
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower().strip()
    print(f"Mensaje recibido: {texto}")
    if texto in RESPUESTAS:
        links = "\n".join(RESPUESTAS[texto])
        await update.message.reply_text(f"Estas son todas las {texto}:\n{links}")
    else:
        await update.message.reply_text("No tengo esa información aún. Prueba con 'zapatillas nike' o 'adidas'.")

# Configuración del bot
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# Ruta webhook para recibir updates de Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print(f"Update recibido: {data}")
    update = Update.de_json(data, bot)
    application.process_update(update)
    print("Update procesado correctamente")
    return "ok"

# Ruta principal para test de servidor
@app.route("/")
def home():
    return "Bot funcionando en Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Arrancando servidor en el puerto {port}")
    app.run(host="0.0.0.0", port=port)


