from binance.client import Client

client = Client("WgXTEAHnnkM9soZvxIwIxCf1AJfjeRWpFgAnbBN63q5gog7kNXJDLerrtFfwDTlu", "ArakDsk7LKmoXBBaTNAvTjfRND06WePK4KUl9T3oZ8ZrDKL8fDeOiVm3XoHeOsNp", testnet=True)

test = client.get_asset_balance()
print(test)
