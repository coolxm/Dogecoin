#https://pypi.org/project/websocket_client/
import websocket
import pprint
import json
ptp = pprint.PrettyPrinter(width= 50, compact= True)

def on_message(ws, message):
    js = json.loads(message)
    if js['type'] != 'ping':
        print("\n cool")
        print(js['data'][0]['p'])

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"BINANCE:DOGEUSDT"}')

if __name__ == "__main__":
    websocket.enableTrace(True) 
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=c2i0532ad3idsa35ckk0",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()