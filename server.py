from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio
import ast  # For safely parsing literal data
from binance.client import Client
import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables
load_dotenv()

# Fetch API keys securely
TOKEN_BINANCEFIRST = os.getenv("TOKEN_BINANCEFIRST")
TOKEN_BINANCESECOND = os.getenv("TOKEN_BINANCESECOND")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))  # Ensure it's an integer
print(f"DISCORD_BOT_TOKEN: {DISCORD_BOT_TOKEN}")

# Verify tokens before starting
if not DISCORD_BOT_TOKEN:
    raise ValueError("ERROR: DISCORD_BOT_TOKEN is missing! Check your .env file.")

if not TOKEN_BINANCEFIRST or not TOKEN_BINANCESECOND:
    raise ValueError("ERROR: Binance API keys are missing! Check your .env file.")

# Initialize Flask app
app = Flask(__name__)

# Initialize Binance Client
client = Client(TOKEN_BINANCEFIRST, TOKEN_BINANCESECOND, testnet=True)

# Setup Discord bot with proper intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------- DISCORD BOT EVENTS ---------------------- #

@bot.event
async def on_ready():
    """Triggers when the bot starts."""
    print(f"✅ Bot is online: {bot.user.name}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🚀 Bot has started successfully!")

async def send_discord_message(message):
    """Helper function to send messages to Discord."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)

# ---------------------- FLASK WEBHOOK ---------------------- #

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handles incoming webhook data."""
    try:
        print("=== Incoming Webhook ===")
        print("Headers:", request.headers)
        print("Body (raw):", request.data)

        raw_data = request.data.decode('utf-8')

        # Safely parse incoming JSON data
        try:
            data = ast.literal_eval(raw_data)
        except (ValueError, SyntaxError) as e:
            print(f"❌ Error parsing data: {e}")
            return jsonify({"success": False, "message": "Invalid data format"}), 400

        print("Parsed Data:", data)

        if data:
            action = data.get("action")
            symbol = data.get("symbol", "BTCUSDT")
            amount = data.get("amount", 0.1)

            if action == "BUY":
                order = client.order_market_buy(symbol=symbol, quantity=amount)
                balance = client.get_asset_balance(asset=symbol[:-4])  # Extract asset symbol
                message = f"📈 **BUY Alert**\nBalance: {balance}\nSymbol: {symbol}\nAmount: {amount}"
                asyncio.run_coroutine_threadsafe(send_discord_message(message), bot.loop)

            elif action == "SELL":
                order = client.order_market_sell(symbol=symbol, quantity=amount)
                balance = client.get_asset_balance(asset=symbol[:-4])  # Extract asset symbol
                message = f"📉 **SELL Alert**\nBalance: {balance}\nSymbol: {symbol}\nAmount: {amount}"
                asyncio.run_coroutine_threadsafe(send_discord_message(message), bot.loop)

        return jsonify({"success": True, "message": "Webhook processed successfully"})

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400

# ---------------------- ASYNC SERVER RUNNER ---------------------- #

async def start():
    """Runs both Flask and Discord bot in parallel."""
    bot_task = asyncio.create_task(bot.start(DISCORD_BOT_TOKEN))
    app_task = asyncio.to_thread(app.run, host="0.0.0.0", port=8080)
    await asyncio.gather(bot_task, app_task)

# ---------------------- MAIN ENTRY POINT ---------------------- #

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
