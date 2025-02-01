from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio
import ast  # Python literal değerlendirmesi için
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv

# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce

# from alpaca.trading.client import TradingClient

# from pybit.unified_trading import HTTP
# session = HTTP(testnet=True)
# print(session.get_kline(
#     category="inverse",
#     symbol="BTCUSD",
#     interval=60,
#     start=1670601600000,
#     end=1670608800000,
# ))
app = Flask(__name__)

# Discord bot istemcisi
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)



client = Client("WgXTEAHnnkM9soZvxIwIxCf1AJfjeRWpFgAnbBN63q5gog7kNXJDLerrtFfwDTlu", "ArakDsk7LKmoXBBaTNAvTjfRND06WePK4KUl9T3oZ8ZrDKL8fDeOiVm3XoHeOsNp", testnet=True)

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1258161138496045096  # Mesaj göndermek istediğiniz kanalın ID'si

# Discord bot başlatıcı
@bot.event
async def on_ready():
    print(f"Bot başarıyla giriş yaptı: {bot.user.name}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🚀 Test: Bybit botu çalışmaya başladı!")

# Discord'da mesaj göndermek için bir yardımcı coroutine
async def send_discord_message(message):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)

# Flask webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("=== Gelen Webhook ===")
        print("Headers:", request.headers)
        print("Body (raw):", request.data)

        # Gelen ham veriyi Python dict'e dönüştür
        raw_data = request.data.decode('utf-8')
        try:
            # Python dict formatında gelen string veriyi ayrıştır
            data = ast.literal_eval(raw_data)
        except (ValueError, SyntaxError) as e:
            print(f"Veriyi ayrıştırma hatası: {e}")
            return jsonify({"success": False, "message": "Geçersiz veri formatı"}), 400

        print("Parsed Data:", data)
        print("=====================")

        if data:
            
            # BUY işlemi kontrolü
            if data.get('action') == "BUY":
                order = client.order_market_buy(symbol='BTCUSDT',quantity=0.1)
                balance = client.get_asset_balance(asset='BTC')
                message = f"📈 **BUY Alert**\nBalance: {balance}\nSymbol: {data.get('symbol')}\nAmount: {data.get('amount')}\nStrategy: {data.get('strategy')}\nINVRSI: {data.get('INVRSI')}\nINVSTOCH: {data.get('INVSTOCH')}\nCCI: {data.get('CCI')}\nRSI: {data.get('RSI')}"
                # Discord botunun event loop'una mesaj gönder
                asyncio.run_coroutine_threadsafe(
                    send_discord_message(message), bot.loop
                )

            # SELL işlemi kontrolü
            elif data.get('action') == "SELL":
                order = client.order_market_sell(symbol='BTCUSDT',quantity=0.1)
                balance = client.get_asset_balance(asset='BTC')
                message = f"📈 **SELL Alert**\nBalance: {balance}\nSymbol: {data.get('symbol')}\nAmount: {data.get('amount')}\nStrategy: {data.get('strategy')}\nINVRSI: {data.get('INVRSI')}\nINVSTOCH: {data.get('INVSTOCH')}\nCCI: {data.get('CCI')}\nRSI: {data.get('RSI')}"
                # Discord botunun event loop'una mesaj gönder
                asyncio.run_coroutine_threadsafe(
                    send_discord_message(message), bot.loop
                )

        return jsonify({"success": True, "message": "Webhook işlendi"})

    except Exception as e:
        print("Hata:", str(e))
        return jsonify({"success": False, "message": str(e)}), 400

# Flask ve Discord'u aynı anda çalıştırmak için birleştirilmiş asenkron yapı
async def start():
    # Discord botunu başlat
    bot_task = asyncio.create_task(bot.start(DISCORD_TOKEN))

    # Flask uygulamasını başlat
    app_task = asyncio.to_thread(app.run, host="0.0.0.0", port=8080)

    # Her iki görevi aynı anda çalıştır
    await asyncio.gather(bot_task, app_task)

# Ana çalışma bloğu
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
