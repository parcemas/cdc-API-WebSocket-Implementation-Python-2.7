
from __future__ import print_function
import json
import base64
import hmac
import hashlib
import time
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
import zlib


class WebsocketClient(object):
    def __init__(self, url="wss://ws.crypto.com/kline-api/ws", event_type="sub",
                 should_print=True, params=None):
        self.url = url
        self.params = params
        self.type = event_type
        self.stop = False
        self.error = None
        self.ws = None
        self.thread = None
        self.should_print = should_print


    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.on_open()
        self.thread = Thread(target=_go)
        self.thread.start()

    def _connect(self):

        sub_params = {'event': self.event_type, 'params': self.params}

        self.ws = create_connection(self.url)

        self.ws.send(json.dumps(sub_params))

    def _listen(self):
        while not self.stop:
            try:
                start_t = 0
                if time.time() - start_t >= 30:
                    # Set a 30 second ping to keep connection alive
                    self.ws.ping("keepalive")
                    start_t = time.time()
                data = self.ws.recv()
		# HERE I STILL NEED TO FIND A WAY TO DECODE AND DECOMPRESS		
                decoded_data = data
		print (decoded_data)
#                msg = json.loads(decoded_data)
		msg = "new mex!"
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass

        self.on_close()

    def close(self):
        self.stop = True
        self.thread.join()

    def on_open(self):
        if self.should_print:
            print("-- Subscribed! --\n")

    def on_close(self):
        if self.should_print:
            print("\n-- Socket Closed --")

    def on_message(self, msg):
        if self.should_print:
            print(msg)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))
        


if __name__ == "__main__":
    import sys
    import time


    class MyWebsocketClient(WebsocketClient):
        def on_open(self):
            self.url = "wss://ws.crypto.com/kline-api/ws"
	    self.event_type = "sub"
            self.params = {"channel":"market_btcusdt_trade_ticker","cb_id":"btcusdt","top":150}
#            self.params = {"channel":"market_btcusdt_ticker","cb_id":"btcusdt"}
            self.message_count = 0
            print("Let's count the messages!")

        def on_message(self, msg):
            print(json.dumps(msg, indent=4, sort_keys=True))
            self.message_count += 1

        def on_close(self):
            print("-- Goodbye! --")


    wsClient = MyWebsocketClient()
    wsClient.start()
    print(wsClient.url)
    try:
        while True:
            print("\nMessageCount =", "%i \n" % wsClient.message_count)
            time.sleep(1)
    except KeyboardInterrupt:
        wsClient.close()

    if wsClient.error:
        sys.exit(1)
    else:
        sys.exit(0)
