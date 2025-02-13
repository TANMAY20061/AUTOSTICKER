import random
import time
import requests
import pytz
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio

# --- Configuration ---
BOT_TOKEN = '7368044652:AAHm4E1UCfsmz1LAhloQh3MIN-JTRVIEnpk'
CHANNEL_ID = '@GODPREDICTION69'
API_URL = 'https://api.bdg88zf.com/api/webapi/GetNoaverageEmerdList'

# Stickers
START_STICKER = "CAACAgUAAxkBAAENyMRnri6zY_YpcVxWkuORxC9wGir21AACmA0AAnNHiVdAAwjfmDuppjYE"
END_STICKER = "CAACAgUAAxkBAAENyMZnri69VRRm0k3Zjbfukj1_LIVuZQACgAUAAgJ4EFaJpBQ_KTV_uTYE"
WIN_STICKER = "CAACAgIAAxkBAAENsKFnnk4PchJ4r5Pld96cCtpPd6ki_gACRjwAAgOpCEvYbLyS2BY3EjYE"
LOSS_STICKER = "CAACAgQAAxkBAAENyMJnri54Sf8c862VllKbXI0DsYJ3kwACvgwAArecmFAOdAvmzdNxwjYE"

# Active times (IST)
active_times = [
    {'start': '09:00', 'end': '09:30'},
    {'start': '12:00', 'end': '12:30'},
    {'start': '15:00', 'end': '15:30'},
    {'start': '18:00', 'end': '18:30'},
    {'start': '20:00', 'end': '21:00'},
    {'start': '22:00', 'end': '22:30'}
]

# Global variables
current_prediction = ''
active_session = False  # Tracks if an active session is ongoing
bot = Bot(token=BOT_TOKEN)


def is_within_active_time():
    """Check if the current IST time is within an active period."""
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    for period in active_times:
        start_time = datetime.strptime(period['start'], "%H:%M").time()
        end_time = datetime.strptime(period['end'], "%H:%M").time()
        if start_time <= now.time() <= end_time:
            return True
    return False


async def send_start_sticker():
    """Send the start sticker at the beginning of the active session."""
    await bot.send_sticker(chat_id=CHANNEL_ID, sticker=START_STICKER)


async def send_end_sticker():
    """Send the end sticker at the end of the active session."""
    await bot.send_sticker(chat_id=CHANNEL_ID, sticker=END_STICKER)


def generate_prediction(period):
    """Generate a prediction message."""
    r = random.randint(0, 9)
    𝘽𝙄𝙂_pairs = ["𝟱+𝟳", "𝟲+𝟵", "𝟴+𝟵", "𝟱+𝟴", "𝟳+𝟵", "𝟲+𝟴", "𝟱+𝟲", "𝟳+𝟴"]
    𝙎𝙈𝘼𝙇𝙇_pairs = ["𝟘+𝟚", "𝟙+𝟛", "𝟚+𝟜", "𝟘+𝟜", "𝟙+𝟚", "𝟛+𝟜", "𝟘+𝟙", "𝟚+𝟛"]

    if r < 5:
        pair = random.choice(𝙎𝙈𝘼𝙇𝙇_pairs)
        predicted_type = "𝙎𝙈𝘼𝙇𝙇"
    else:
        pair = random.choice(𝘽𝙄𝙂_pairs)
        predicted_type = "𝘽𝙄𝙂"

    global current_prediction
    current_prediction = f"{pair} {predicted_type}"

    return (f"🕒 **𝕻ᴇʀɪᴏᴅ:** `{period}`\n"
            f"🎯 **ₚᵣₑDᵢCₜᵢₒₙ:** `{current_prediction}`\n"
            "⚡️ **ʀᴇꜱᴜʟᴛ:** ᴡᴀɪᴛɪɴɢ... ⏳\n\n"
            "🔥 **ℂℝ𝔼𝔻𝕀𝕋𝕊:** 𝕄𝕒𝕕𝕖 𝕨𝕚𝕥𝕙 ❤️ 𝕓𝕪 [@TANMAYPAUL21] 🔥")

def check_prediction_match(predicted, number):
    """Check if the prediction is correct."""
    try:
        predicted_numbers_str, predicted_type = predicted.split()
        predicted_numbers = [int(x) for x in predicted_numbers_str.split('+')]
    except Exception as e:
        print("Error parsing predicted string:", e)
        return False

    actual_type = "𝘽𝙄𝙂" if int(number) >= 5 else "𝙎𝙈𝘼𝙇𝙇"
    type_match = predicted_type.lower() == actual_type.lower()
    number_match = int(number) in predicted_numbers

    return type_match or number_match


async def fetch_latest_period():
    """Fetch the latest period from the API."""
    try:
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 1,
            'language': 0,
            'random': "4a0522c6ecd8410496260e686be2a57c",
            'signature': "334B5E70A0C9B8918B0B15E517E2069C",
            'timestamp': int(time.time())
        }
        response = requests.post(API_URL, json=data, headers=headers)
        results = response.json().get('data', {}).get('list', [])
        latest_period = results[0]['issueNumber'] if results else None
        return int(latest_period) if latest_period else None
    except Exception as e:
        print(f"Error fetching latest period: {e}")
        return None


async def verify_prediction(period, sent_message_ids):
    """Verify the prediction result and update the message."""
    try:
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 1,
            'language': 0,
            'random': "4a0522c6ecd8410496260e686be2a57c",
            'signature': "334B5E70A0C9B8918B0B15E517E2069C",
            'timestamp': int(time.time())
        }
        response = requests.post(API_URL, json=data, headers=headers)
        results = response.json().get('data', {}).get('list', [])
        result = next((item for item in results if item['issueNumber'] == str(period)), None)

        if result:
            actual_number = result['number']
            is_win = check_prediction_match(current_prediction, actual_number)

            final_message = (
                "🎰 **Bᴇᴛ Rᴇsᴜʟᴛs!** 🎰\n\n"
                f"🕒 **Pᴇʀɪᴏᴅ:** `{str(period)[-3:]}`\n"
                f"🎯 **Sɪɢɴᴀʟ:** `{current_prediction}`\n"
                f"{'🏆 **Rᴇsᴜʟᴛ:** ✅ WIN' if is_win else '💥 **RESULT:** ❌ LOSS'} ({actual_number})\n\n"
                "🔥 **Pᴏᴡᴇʀᴇᴅ ʙʏ:** [@TANMAYPAUL21] 🔥"
            )

            await bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=sent_message_ids[CHANNEL_ID],
                text=final_message,
                parse_mode='Markdown'
            )

            await bot.send_sticker(chat_id=CHANNEL_ID, sticker=WIN_STICKER if is_win else LOSS_STICKER)
            return True
        else:
            print(f"No result found for PERIOD {period}")
            return False
    except Exception as e:
        print(f"Error verifying prediction: {e}")
        return False


async def schedule_predictions():
    """Continuously check for new periods and send predictions."""
    global active_session
    last_predicted_period = None

    while True:
        if is_within_active_time():
            if not active_session:
                active_session = True
                await send_start_sticker()

            new_period = await fetch_latest_period()
            if new_period and new_period != last_predicted_period:
                last_predicted_period = new_period
                next_period = new_period + 1
                prediction_message = generate_prediction(next_period)
                message = await bot.send_message(CHANNEL_ID, text=prediction_message, parse_mode='Markdown')
                while not await verify_prediction(next_period, {CHANNEL_ID: message.message_id}):
                    await asyncio.sleep(5)
            else:
                await asyncio.sleep(5)
        else:
            if active_session:
                active_session = False
                await send_end_sticker()
            await asyncio.sleep(60)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("💎✨Bot is running..💎⏳")))
    asyncio.run(schedule_predictions())


if __name__ == "__main__":
    main()
