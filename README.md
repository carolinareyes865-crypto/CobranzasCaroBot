# 🤖 Bot de Cobranza Telegram — Guía de despliegue

## Archivos del proyecto
```
cobranza_bot/
├── bot.py            ← lógica principal del bot
├── envio_masivo.py   ← script para mensajes mensuales
├── requirements.txt  ← dependencias
├── clientes.csv      ← lista de clientes (tú lo creas)
└── README.md
```

---

## PASO 1 — Crear el bot en Telegram

1. Abre Telegram y busca **@BotFather**
2. Escribe `/newbot`
3. Ponle un nombre (ej: "Cobranza Bot")
4. Ponle un usuario (ej: `cobranza_empresa_bot`)
5. BotFather te dará un **TOKEN** — guárdalo 🔑

---

## PASO 2 — Obtener tu Chat ID (la encargada)

1. Busca **@userinfobot** en Telegram
2. Escríbele cualquier mensaje
3. Te responderá con tu **ID numérico** — guárdalo 🔑

---

## PASO 3 — Crear clientes.csv

Formato del archivo:
```csv
chat_id,nombre
123456789,Juan Pérez
987654321,María López
```

Para obtener el chat_id de cada cliente:
- Pídeles que abran el bot y escriban /start una vez
- El bot puede registrarlos automáticamente (se puede ampliar)

---

## PASO 4 — Desplegar en Render (gratis)

1. Sube los archivos a un repositorio GitHub (privado)
2. Ve a https://render.com y crea cuenta
3. Clic en **New → Web Service**
4. Conecta tu repo de GitHub
5. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. En **Environment Variables** agrega:
   - `BOT_TOKEN` = el token de BotFather
   - `ENCARGADA_CHAT_ID` = el ID numérico de la encargada
7. Clic en **Deploy** ✅

---

## PASO 5 — Envío masivo mensual

### Opción A: Manual (ejecutar localmente)
```bash
BOT_TOKEN="tu_token" ENCARGADA_CHAT_ID="123" python envio_masivo.py
```

### Opción B: Programado en Render
Crea un **Cron Job** en Render:
- Schedule: `0 8 1 * *`  ← día 1 de cada mes a las 8am
- Command: `python envio_masivo.py`

---

## Flujo resumido

```
Mensaje masivo (día 1 del mes)
        ↓
Cliente responde SI → fecha → nombre → cédula → comprobante → encargada recibe todo
Cliente responde NO → motivo → encargada recibe reporte
        ↓
Mensaje de advertencia de suspensión
```

---

## Comandos del bot
- `/start` — inicia el flujo de cobranza
- `/cancelar` — cancela la conversación actual
