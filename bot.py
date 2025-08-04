import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# Configuración
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USUARIO_ADMIN = int(os.getenv('TELEGRAM_ADMIN_ID', 0))
ARCHIVO = os.path.join(os.getenv('RENDER_DISK_PATH', './data'), 'respuestas.json')

# Inicialización del archivo de respuestas
def init_respuestas():
    os.makedirs(os.path.dirname(ARCHIVO), exist_ok=True)
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, 'w') as f:
            json.dump({"ejemplo": "Esta es una respuesta de ejemplo"}, f)

def cargar_respuestas():
    try:
        with open(ARCHIVO, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        init_respuestas()
        return cargar_respuestas()

def guardar_respuestas(data):
    with open(ARCHIVO, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == USUARIO_ADMIN:
        await update.message.reply_text(
            "🤖 Bot de Respuestas (Modo Admin)\n\n"
            "Comandos:\n"
            "/add <clave> - Añadir respuesta\n"
            "/list - Listar claves\n"
            "/delete <clave> - Eliminar clave"
        )
    else:
        await update.message.reply_text("Escribe algo y veré si tengo respuesta")

# (Aquí incluirías los demás handlers: add_start, add_text, list_respuestas, delete, responder)
# ... [Los handlers que ya tenías funcionan igual, solo cambian las funciones cargar/guardar]

def main():
    # Inicializar archivo si no existe
    init_respuestas()
    
    # Crear aplicación
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Configurar handlers (igual que antes)
    # ...
    
    print("🟢 Bot iniciado con persistencia en Render Disk")
    application.run_polling()

if __name__ == "__main__":
    main()
