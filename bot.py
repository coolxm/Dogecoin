##price - tracker
#https://pypi.org/project/websocket_client/
import websocket
import pprint
import json

import discord
import time
import queue
import threading
#log into discord
client = discord.Client()
q = queue.Queue()

ptp = pprint.PrettyPrinter(width= 50, compact= True)

running = False

def myfunc(q, t):
    def on_message(ws, message):
        js = json.loads(message)
        if js['type'] != 'ping' and js['type'] != 'error':
            print("\n cool")
            price = float(js['data'][-1]['p'])
            print(price)
            q.put(item = float(price), block=True, timeout= None)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        message = '{"type":"subscribe","symbol":"' + str(t) + '"}'
        ws.send(message)


    websocket.enableTrace(True) 
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=c2i0532ad3idsa35ckk0",
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

async def starter():
    active = []
    actives = []
    last_prices = []
    while True:
        print("hi")
        db = json.load(open("channels.json"))
        for i in range(len(db)):
            if not db[i][1] in actives:
                actives.append(db[i][1])
                active.append((db[i][1], queue.Queue()))
                last_prices.append(1)
                threading.Thread(target= myfunc, args = (active[i][1], db[i][1])).start()
        
        ptp.pprint(active)

        for i in range(len(db)):
            id = db[i][0]
            q = None
            for ii in range(len(active)):
                if active[ii][0] == db[i][1]:
                    q = active[ii][1]
        
            list = []
            x = True
            while x == True:
                if q is not None:
                    try:
                        item = float(q.get(timeout = 1))
                        list.append(item)
                    except queue.Empty:
                        x = False
            
            print(list)
            if list != []:
                price = list[-1]
                diff = price - last_prices[i]
                if diff > 0:
                    word = "higher"
                else:
                    word = "lower"
                    diff = abs(diff)
                last_prices[i] = price
                message = ">>> current price of " + str(db[i][1]) + " is " + str(price) + ". \n That's " + str(diff) + " " + word + " than the last price."
                channel = client.get_channel(id)
                await channel.send(message)

            
        time.sleep(3600)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global running
    print('recieved')
    if message.author == client.user:
        return
    if running == False:
        await starter()
        running = True

    if message.content.startswith('$program'):
        channel = message.channel
        await channel.send(">>> coin symbol? \n ie: <BINANCE:DOGEUSDT>")
    
        def check(m):
            return m.channel == channel
        
        msg = await client.wait_for('message', check=check)
        link = msg.content
        id = channel.id
        save = (id, link)
        db = json.load(open('channels.json'))
        db.append(save)

        with open('channels.json', 'w') as f:
            json.dump(db, f)

if __name__ == "__main__":
    client.run("NzM4NTIyNjI1ODg1ODY0MTAw.XyNIyw.dT59nua7GhEVpsbfth2w8ewJsI8")