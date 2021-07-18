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
            price = (js['data'][0]['p'])
            print(price)
            q.put(item = price, block=True, timeout= None)

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

def starter():
    print('here')
    print(threading.main_thread)
    print(threading.current_thread())
    active = []
    actives = []
    last_prices = []
    while True:
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
            print(id)
            q = None
            for ii in range(len(active)):
                print(ii)
                if active[ii][0] == db[i][1]:
                    q = active[ii][1]
        
        
            
            list = []
            while True:
                if q is not None:
                    try:
                        item = int(q.get(timeout = 0.5))
                        list.append(item)
                    except queue.Empty:
                        break
            
            price = list[-1]
            diff = price - last_prices[i]
            if diff > 0:
                word = "higher"
            else:
                word = "lower"
                diff = str(diff).pop(0)
            last_prices[i] = price
            message = ">>> current price of " + str(db[i][1]) + " is " + str(price) + ". \n That's " + diff + " " + word + " than the last price."
            channel = client.get_channel(id)
            send(channel, message)
            
            async def send(channel, message):
                await channel.send(message)
            
            time.sleep(10)

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
        print('we are a go')
        threading.Thread(target = starter).start()
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
    client.run("NzM4NTIyNjI1ODg1ODY0MTAw.XyNIyw.RzPp2rCmlYYPuoGQaswbXC_zy80")