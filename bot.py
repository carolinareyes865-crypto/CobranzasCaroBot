import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Variables de entorno (configura en Render)
# ─────────────────────────────────────────────
TOKEN = os.environ["BOT_TOKEN"]
ENCARGADA_ID = 6542830130

# Estados de la conversación
ESPERANDO_RESPUESTA, ESPERANDO_FECHA, ESPERANDO_NOMBRE, \
ESPERANDO_CEDULA, ESPERANDO_COMPROBANTE, ESPERANDO_MOTIVO = range(6)


# ─────────────────────────────────────────────
# INICIO DEL FLUJO
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_mensaje_cobranza(update, context)

async def enviar_mensaje_cobranza(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if update.message:
        await update.message.reply_text(texto, reply_markup=teclado, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(texto, reply_markup=teclado, parse_mode="Markdown")
    return ESPERANDO_RESPUESTA


# ─────────────────────────────────────────────
# RAMA: SI
# ─────────────────────────────────────────────
async def respuesta_si(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("¿Hasta qué *fecha* realizará la cancelación?\n\n_Ejemplo: 15/07/2025_", parse_mode="Markdown")
    return ESPERANDO_FECHA

async def recibir_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fecha"] = update.message.text
    await update.message.reply_text("Por favor ingrese su *nombre completo*:", parse_mode="Markdown")
    return ESPERANDO_NOMBRE

async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nombre"] = update.message.text
    await update.message.reply_text("Ingrese su *número de cédula*:", parse_mode="Markdown")
    return ESPERANDO_CEDULA

async def recibir_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cedula"] = update.message.text
    await update.message.reply_text("Por favor *suba una foto del comprobante de pago* 📎", parse_mode="Markdown")
    return ESPERANDO_COMPROBANTE

async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = context.user_data
    foto = update.message.photo[-1] if update.message.photo else None
    doc = update.message.document

    # Mensaje para la encargada
    resumen = (
        "📋 *NUEVO REPORTE DE PAGO*\n\n"
        f"👤 Nombre: {datos.get('nombre', 'N/A')}\n"
        f"🪪 Cédula: {datos.get('cedula', 'N/A')}\n"
        f"📅 Fecha prometida: {datos.get('fecha', 'N/A')}\n"
        f"✅ Estado: *VA A PAGAR*\n"
        f"📞 Chat ID cliente: `{update.effective_user.id}`\n"
        f"👤 Usuario: @{update.effective_user.username or 'sin_usuario'}"
    )
    await context.bot.send_message(ENCARGADA_ID, resumen, parse_mode="Markdown")

    if foto:
        await context.bot.send_photo(ENCARGADA_ID, foto.file_id, caption="🧾 Comprobante de pago")
    elif doc:
        await context.bot.send_document(ENCARGADA_ID, doc.file_id, caption="🧾 Comprobante de pago")

    # Mensaje final al cliente
    await update.message.reply_text(
        "✅ *¡Gracias!* Hemos recibido su información.\n\n"
        "Le recordamos que, en caso de no regularizar su pago dentro del "
        "plazo establecido, el servicio podría ser *suspendido*.",
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─────────────────────────────────────────────
# RAMA: NO
# ─────────────────────────────────────────────
async def respuesta_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "Por favor indique el *motivo* por el cual no realizará el pago:",
        parse_mode="Markdown"
    )
    return ESPERANDO_MOTIVO

async def recibir_motivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    motivo = update.message.text

    resumen = (
        "🚨 *REPORTE: NO VA A PAGAR*\n\n"
        f"👤 Chat ID: `{update.effective_user.id}`\n"
        f"👤 Usuario: @{update.effective_user.username or 'sin_usuario'}\n"
        f"❌ Estado: *NO VA A PAGAR*\n"
        f"📝 Motivo: {motivo}"
    )
    await context.bot.send_message(ENCARGADA_ID, resumen, parse_mode="Markdown")

    await update.message.reply_text(
        "Le recordamos que, en caso de no regularizar su pago dentro del "
        "plazo establecido, el servicio podría ser *suspendido*.\n\n"
        "Si cambia de opinión, puede comunicarse con nosotros.",
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─────────────────────────────────────────────
# CANCELAR
# ─────────────────────────────────────────────
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Proceso cancelado. Escribe /start para comenzar de nuevo.")
    return ConversationHandler.END


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
async def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ESPERANDO_RESPUESTA: [
                CallbackQueryHandler(respuesta_si, pattern="^si$"),
                CallbackQueryHandler(respuesta_no, pattern="^no$"),
            ],
            ESPERANDO_FECHA:       [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_fecha)],
            ESPERANDO_NOMBRE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            ESPERANDO_CEDULA:      [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cedula)],
            ESPERANDO_COMPROBANTE: [MessageHandler(filters.PHOTO | filters.Document.ALL, recibir_comprobante)],
            ESPERANDO_MOTIVO:      [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_motivo)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    logger.info("Bot iniciado ✅")
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
