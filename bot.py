import os
import json
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

TOKEN = "8300690595:AAH-AGD79G5iS2YlBBUnD-gfh2M_OEXoXTw"
ARCHIVO = "respuestas.json"
USUARIO_ADMIN = 7090513256  # Reemplaza con tu ID de Telegram (@userinfobot)

# Configuración inicial
if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, "w") as f:
        json.dump({}, f)

def cargar_respuestas():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def guardar_respuestas(data):
    with open(ARCHIVO, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Filtro para comandos admin
def comando_admin(update: Update):
    return update.effective_user.id == USUARIO_ADMIN

# Estados para la conversación
ESPERANDO_RESPUESTA = 1

### --- COMANDOS --- ###
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if comando_admin(update):
        await update.message.reply_text(
            "🤖 **Bot de Respuestas (Modo Admin)**\n\n"
            "Comandos disponibles:\n"
            "/add <clave> - Añadir nueva respuesta\n"
            "/list - Listar claves\n"
            "/delete <clave> - Eliminar clave"
        )
    else:
        await update.message.reply_text("Escribe cualquier palabra y te responderé si la reconozco")

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not comando_admin(update):
        await update.message.reply_text("❌ Solo el admin puede usar este comando")
        return ConversationHandler.END

    if not context.args:
        await update.message.reply_text("⚠️ Uso: /add <clave>\nEjemplo: /add zapatillas")
        return ConversationHandler.END

    clave = " ".join(context.args).lower().strip()
    context.user_data['clave'] = clave
    await update.message.reply_text(f"✍️ Envía el texto para asociar a '{clave}':")
    return ESPERANDO_RESPUESTA

async def add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not comando_admin(update):
        return ConversationHandler.END

    clave = context.user_data.get('clave')
    if not clave:
        await update.message.reply_text("❌ Error. Usa /add <clave> primero.")
        return ConversationHandler.END

    texto = update.message.text
    data = cargar_respuestas()
    data[clave] = texto
    guardar_respuestas(data)
    await update.message.reply_text(f"✅ Texto guardado para '{clave}'.")
    return ConversationHandler.END

async def list_respuestas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not comando_admin(update):
        await update.message.reply_text("❌ Solo el admin puede usar este comando")
        return

    data = cargar_respuestas()
    if not data:
        await update.message.reply_text("ℹ️ No hay respuestas guardadas.")
        return

    mensaje = "📋 **Claves guardadas:**\n\n" + "\n".join(f"• {clave}" for clave in data.keys())
    await update.message.reply_text(mensaje)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not comando_admin(update):
        await update.message.reply_text("❌ Solo el admin puede usar este comando")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Uso: /delete <clave>\nEjemplo: /delete zapatillas")
        return

    clave = " ".join(context.args).lower().strip()
    data = cargar_respuestas()

    if clave in data:
        del data[clave]
        guardar_respuestas(data)
        await update.message.reply_text(f"✅ Clave '{clave}' eliminada.")
    else:
        await update.message.reply_text(f"❌ Clave '{clave}' no encontrada.")

### --- RESPUESTA PARA TODOS --- ###
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text.lower()
    data = cargar_respuestas()
    respuestas = []

    for respuesta in data.values():
        palabras_texto = [
            palabra.strip(".,;!¡¿?()[]{}'\"")
            for palabra in respuesta.lower().split()
            if len(palabra) > 2
        ]

        if any(palabra in texto_usuario for palabra in palabras_texto):
            respuestas.append(respuesta)

    if respuestas:
        await update.message.reply_text("\n\n――――――\n\n".join(respuestas))
    # else: No responder si no hay coincidencias

### --- CONFIGURACIÓN PRINCIPAL --- ###
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Configuración de handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_start, filters=filters.User(USUARIO_ADMIN))],
        states={
            ESPERANDO_RESPUESTA: [MessageHandler(filters.TEXT & filters.User(USUARIO_ADMIN), add_text)],
        },
        fallbacks=[]
    )

    # Comandos protegidos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("list", list_respuestas, filters=filters.User(USUARIO_ADMIN)))
    application.add_handler(CommandHandler("delete", delete, filters=filters.User(USUARIO_ADMIN)))

    # Responder a todos los usuarios
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # Manejo de errores
    application.add_error_handler(lambda _, ctx: print(f"⚠️ Error: {ctx.error}"))

    print("🟢 Bot iniciado - Comandos protegidos activos")
    application.run_polling()

if __name__ == "__main__":
    main()

