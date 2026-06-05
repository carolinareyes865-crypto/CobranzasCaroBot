"""
envio_masivo.py
---------------
Envía el mensaje de cobranza a TODOS los clientes registrados.
Ejecutar manualmente o programar con APScheduler / cron.

Uso:
    python envio_masivo.py

Agrega IDs de clientes en CLIENTES o carga desde un archivo CSV.
"""

import asyncio
import os
import csv
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ["BOT_TOKEN"]

# ─────────────────────────────────────────────
# Opción 1: lista manual de IDs
# ─────────────────────────────────────────────
CLIENTES = [
    # 123456789,
    # 987654321,
]

# ─────────────────────────────────────────────
# Opción 2: cargar desde clientes.csv
#   Formato: chat_id,nombre
# ─────────────────────────────────────────────
def cargar_clientes_csv(ruta="clientes.csv"):
    ids = []
    try:
        with open(ruta, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ids.append(int(row["chat_id"]))
                except (ValueError, KeyError):
                    pass
    except FileNotFoundError:
        logger.warning("clientes.csv no encontrado, usando lista manual.")
    return ids


async def enviar_a_todos():
    bot = Bot(token=TOKEN)
    ids = CLIENTES or cargar_clientes_csv()

    if not ids:
        logger.error("No hay clientes registrados. Agrega IDs en CLIENTES o en clientes.csv")
        return

    teclado = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ SI", callback_data="si"),
            InlineKeyboardButton("❌ NO", callback_data="no"),
        ]
    ])
    texto = (
        "Estimado cliente:\n\n"
        "Por favor, ayúdenos con la cancelación del monto pendiente "
        "correspondiente al servicio prestado.\n\n"
        "*¿Va a realizar el pago?*"
    )

    enviados, fallidos = 0, 0
    for chat_id in ids:
        try:
            await bot.send_message(chat_id, texto, reply_markup=teclado, parse_mode="Markdown")
            enviados += 1
            logger.info(f"✅ Enviado a {chat_id}")
            await asyncio.sleep(0.3)  # evitar flood
        except TelegramError as e:
            fallidos += 1
            logger.warning(f"❌ Error con {chat_id}: {e}")

    logger.info(f"\n📊 Resultado: {enviados} enviados, {fallidos} fallidos de {len(ids)} total")


if __name__ == "__main__":
    asyncio.run(enviar_a_todos())
