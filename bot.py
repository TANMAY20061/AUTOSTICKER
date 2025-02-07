import random
import time
import requests
import pytz
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio
from flask import Flask
from multiprocessing import Process

# Flask App Initialization
app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running successfully!"

# Function to Start the Flask App
def start_flask():
    app.run(host="0.0.0.0", port=10000)

API_URL = 'https://api.bdg88zf.com/api/webapi/GetNoaverageEmerdList'
AUTH_TOKEN = 'YOUR_BEARER_TOKEN'
BOT_TOKEN = '7368044652:AAFKI2a7lcJWmicReoCfMlSkGsm-bzV0YbQ'

CHANNEL_FILE = 'god.txt'

def load_channels():
    try:
        with open(CHANNEL_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

def save_channels(channels):
    with open(CHANNEL_FILE, 'w') as file:
        for channel in channels:
            file.write(f"{channel}\n")
            
CHANNEL_IDS = load_channels()

current_prediction = ''
is_manual_trigger = False  

IST = pytz.timezone('Asia/Kolkata')
bot = Bot(token=BOT_TOKEN)

active_times = [
    {'start': '09:00', 'end': '09:30'},
    {'start': '12:00', 'end': '12:30'},
    {'start': '15:00', 'end': '15:30'},    
    {'start': '18:00', 'end': '18:30'},
    {'start': '20:00', 'end': '20:30'},
    {'start': '22:00', 'end': '22:30'}
]

def is_within_active_time():
    now = datetime.now(IST)
    current_time = now.strftime('%H:%M')  # Get current time in HH:MM format
    
    for time_range in active_times:
        if time_range['start'] <= current_time <= time_range['end']:
            return True
    return False

def generate_prediction(period):
    𝘽𝙄𝙂_pairs = ["5+7", "6+9", "8+9", "5+8", "7+9", "6+8", "5+6", "7+8"]  # Only 𝘽𝙄𝙂 numbers (5-9)
    𝙎𝙈𝘼𝙇𝙇_pairs = ["0+2", "1+3", "2+4", "0+4", "1+2", "3+4", "0+1", "2+3"]  # Only 𝙎𝙈𝘼𝙇𝙇 numbers (0-4)

    is_𝘽𝙄𝙂 = random.choice([True, False])  # 50% chance for 𝘽𝙄𝙂 or 𝙎𝙈𝘼𝙇𝙇
    selected_pair = random.choice(𝘽𝙄𝙂_pairs if is_𝘽𝙄𝙂 else 𝙎𝙈𝘼𝙇𝙇_pairs)  # Randomly pick from the respective list

    result = f"[{selected_pair}] {'𝘽𝙄𝙂' if is_𝘽𝙄𝙂 else '𝙎𝙈𝘼𝙇𝙇'}"  

    global current_prediction
    current_prediction = result
    return f"🕒 **Pᴇʀɪᴏᴅ:** `{str(period)[-3:]}` ➟ {result}"

async def fetch_latest_period():
    try:
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': f'Bearer {AUTH_TOKEN}'}
        data = {
            'pageSize': 10, 'pageNo': 1, 'typeId': 1, 'language': 0,
            'random': "4a0522c6ecd8410496260e686be2a57c",
            'signature': "334B5E70A0C9B8918B0B15E517E2069C", 'timestamp': int(time.time())
        }
        response = requests.post(API_URL, json=data, headers=headers)
        results = response.json().get('data', {}).get('list', [])
        latest_period = results[0]['issueNumber'] if results else None
        return int(latest_period) if latest_period else None
    except Exception as e:
        print(f"Error fetching latest period: {e}")
        return None

def check_prediction_match(predicted, number):
    try:
        predicted_numbers, predicted_type = predicted.split()
        predicted_numbers = predicted_numbers.strip("[]").split("+")
        predicted_numbers = [int(num) for num in predicted_numbers]
    except ValueError:
        return False

    actual_type = "𝘽𝙄𝙂" if int(number) >= 5 else "𝙎𝙈𝘼𝙇𝙇"
    type_match = predicted_type == actual_type
    number_match = int(number) in predicted_numbers
    return type_match or number_match

async def verify_prediction(period, sent_message_ids):
    try:
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': f'Bearer {AUTH_TOKEN}'}
        data = {
            'pageSize': 10, 'pageNo': 1, 'typeId': 1, 'language': 0,
            'random': "4a0522c6ecd8410496260e686be2a57c",
            'signature': "334B5E70A0C9B8918B0B15E517E2069C", 'timestamp': int(time.time())
        }
        response = requests.post(API_URL, json=data, headers=headers)
        results = response.json().get('data', {}).get('list', [])

        result = next((item for item in results if item['issueNumber'] == str(period)), None)

        if result:
            number = int(result['number'])
            actual_result = "𝘽𝙄𝙂" if number >= 5 else "𝙎𝙈𝘼𝙇𝙇"
            is_win = check_prediction_match(current_prediction, number)

            outcome_message = (
                "🎰 **Bᴇᴛ Rᴇsᴜʟᴛs!** 🎰\n\n"
                f"🕒 **Pᴇʀɪᴏᴅ:** `{str(period)[-3:]}`\n"
                f"🎯 **Sɪɢɴᴀʟ:** `{current_prediction}`\n"
                f"{'🏆 **Rᴇsᴜʟᴛ:** ✅ 𝗪𝗜𝗡' if is_win else '💥 **Rᴇsᴜʟᴛ:** ❌ 𝗟𝗢𝗦𝗦'}  ({number})\n\n"
                "🔥 **Pᴏᴡᴇʀᴇᴅ ʙʏ:** [@TANMAYPAUL21] 🔥"
            )

            # Send the outcome message to all channels and update the message
            for channel, message_id in sent_message_ids.items():
                await bot.edit_message_text(chat_id=channel, message_id=message_id, text=outcome_message, parse_mode='Markdown')
                
                if is_win:
                    # Send verification sticker ONLY if the prediction was correct
                    await bot.send_sticker(chat_id=channel, sticker="CAACAgUAAxkBAAKNfGdM_PCbhz0WbKqCIKwV8uLhmO0JAAJgDQACdp7xVeArWYhcjh2eNgQ")

            return True
        else:
            print(f"No result found for PERIOD {period}")
            return False
    except Exception as e:
        print(f"Error verifying prediction: {e}")
        return False

async def schedule_predictions():
    global is_manual_trigger
    last_predicted_period = None
    while True:
        if is_manual_trigger:
            await asyncio.sleep(60)
            continue

        if is_within_active_time():
            new_period = await fetch_latest_period()

            if new_period and new_period != last_predicted_period:
                last_predicted_period = new_period
                next_period = new_period + 1

                # Send sticker before starting prediction
                for channel in CHANNEL_IDS:
                    await bot.send_sticker(chat_id=channel, sticker="CAACAgUAAxkBAAENu29npcKaHRGQaDDN7dooo1p07njiNAACFQ8AAjuEAAFVPAKVzG-_rMU2BA")

                prediction_message = generate_prediction(next_period)
                sent_message_ids = {}

                # Send prediction to all channels and save message ids
                for channel in CHANNEL_IDS:
                    message = await bot.send_message(
                        chat_id=channel,
                        text=(
                            f"{prediction_message}\n\n"
                            "⚡️ **Rᴇsᴜʟᴛ:** Wᴀɪᴛɪɴɢ... ⏳\n\n"
                            "🔥 **Cʀᴇᴅɪᴛs:** Mᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ [@TANMAYPAUL21] 🔥"
                        ),
                        parse_mode='Markdown'
                    )
                    sent_message_ids[channel] = message.message_id  # Save message_id for editing

                verified = False
                while not verified:
                    verified = await verify_prediction(next_period, sent_message_ids)
                    if not verified:
                        await asyncio.sleep(5)
                        print(f"Retrying verification for PERIOD {next_period}...")
                        
                # Send sticker after prediction time ends
                for channel in CHANNEL_IDS:
                    await bot.send_sticker(chat_id=channel, sticker="CAACAgUAAxkBAAENt89no0nLuZPOJvr7vbdhqZe9kemtRQACTAwAAsCAAAFVTpIwwoGAFb02BA")

        else:
            print("Outside active time, prediction not made.")
        await asyncio.sleep(60)

async def start(update, context):
    await update.message.reply_text("Prediction Bot is running...")

async def add_channel(update, context):
    if len(context.args) == 1:
        channel_id = context.args[0]
        if channel_id not in CHANNEL_IDS:
            CHANNEL_IDS.append(channel_id)
            save_channels(CHANNEL_IDS)
            await update.message.reply_text(f"Channel {channel_id} added successfully.")
        else:
            await update.message.reply_text(f"Channel {channel_id} is already in the list.")
    else:
        await update.message.reply_text("Usage: /add @channel")

async def remove_channel(update, context):
    if len(context.args) == 1:
        channel_id = context.args[0]
        if channel_id in CHANNEL_IDS:
            CHANNEL_IDS.remove(channel_id)
            save_channels(CHANNEL_IDS)
            await update.message.reply_text(f"Channel {channel_id} removed successfully.")
        else:
            await update.message.reply_text(f"Channel {channel_id} not found in the list.")
    else:
        await update.message.reply_text("Usage: /remove @channel")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    add_channel_handler = CommandHandler("add", add_channel)
    remove_channel_handler = CommandHandler("remove", remove_channel)

    application.add_handler(start_handler)
    application.add_handler(add_channel_handler)
    application.add_handler(remove_channel_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(schedule_predictions())

    # Start Flask in a separate process
    flask_process = Process(target=start_flask)
    flask_process.start()

    application.run_polling()

if __name__ == "__main__":
    main()
