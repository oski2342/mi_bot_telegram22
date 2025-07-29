import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import threading

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

