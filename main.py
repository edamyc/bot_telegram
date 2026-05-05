import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# --- Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Registro_Personal").sheet1

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Bot ---
TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    botones = [
        ["Entrada", "Inicio Comida"],
        ["Fin Comida", "Salida"],
        ["Tiempo Adicional"]
    ]
    update.message.reply_text(
        "Selecciona una opción:",
        reply_markup=ReplyKeyboardMarkup(botones, resize_keyboard=True)
    )

def registrar_evento(update, evento):
    update.message.reply_text(
        "Envíame tu ubicación GPS",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Enviar ubicación", request_location=True)]],
            resize_keyboard=True
        )
    )
    update.user_data["evento"] = evento

def recibir_ubicacion(update: Update, context: CallbackContext):
    user = update.message.from_user
    evento = context.user_data.get("evento", "Desconocido")

    lat = update.message.location.latitude
    lon = update.message.location.longitude

    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")

    sheet.append_row([user.id, user.first_name, evento, fecha, hora, lat, lon])

    update.message.reply_text(f"Registro guardado: {evento}")

def texto(update: Update, context: CallbackContext):
    msg = update.message.text

    if msg == "Entrada":
        registrar_evento(update, "Entrada")
    elif msg == "Inicio Comida":
        registrar_evento(update, "Inicio Comida")
    elif msg == "Fin Comida":
        registrar_evento(update, "Fin Comida")
    elif msg == "Salida":
        registrar_evento(update, "Salida")
    elif msg == "Tiempo Adicional":
        registrar_evento(update, "Tiempo Adicional")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, texto))
    dp.add_handler(MessageHandler(Filters.location, recibir_ubicacion))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()