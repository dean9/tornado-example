#!venv/bin/python

'''web server. could exchange data between spec/esp/browser/robots
'''

from tornado import websocket, web, ioloop
import json
from pathlib import Path

abspath = Path(__file__).parent

clients_list = []
latest_data = {}
known_messages = ['example1', 'example2']

latest_data['example1'] = {'name': 'example1', 'value': '4.56'}


class IndexHandler(web.RequestHandler):
    # gets are called when you visit the url in a browser
    def get(self):
        self.render("index.html")


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    # send latest info to a new connection
    def open(self):
        if self not in clients_list:
            clients_list.append(self)

        # send data to the new client
        for d in latest_data.values():
            self.write_message(json.dumps(d))

    def on_message(self, message):
        print(f"got ws message: {message}")
        do_something_with_message(message)

    def on_close(self):
        if self in clients_list:
            clients_list.remove(self)


class ApiHandler(web.RequestHandler):
    '''API handler
        - Data can be requested from this server 
        - Data gets posted here from e.g. spec, esp 
        - Data is forwarded to browser (send_data_to_browser()) w/ websockets via SocketHandler
    '''

    def get(self, *args):
        # example get request coming in:
        # URL = 'localhost:7112/api'
        # data = {'name': 'example1'}
        # requests.get(URL, data)

        name = self.get_argument("name")
        try:
            self.finish(json.dumps(latest_data[name]))
        except: 
            self.finish('')

    def post(self):
        # example post data coming in:
        # URL = 'localhost:7112/api'
        # data = {'name': 'resistor_value', 'value': '1.23'}
        # requests.post(URL, data))

        name = self.get_argument("name")
        value = self.get_argument("value")
        data = {'name': name, 'value': value}
        print(f"got api post: {name}, {value}")

        if name not in known_messages: 
            print(f"Unknown name: {name}")
            return
        else:
            # store the new value (e.g. in case the browser page is refreshed)
            latest_data[name] = data 

            do_something_with_message(float(value))

            send_data_to_browser(data)

        self.finish()


def do_something_with_message(msg):
    print(msg)


def send_data_to_browser(data):
    '''
    Send data to websocket clients.
    '''
    print(f"forwarding data: {data['name']=}; {data['value']=}")
    json_data = json.dumps(data)
    for c in clients_list:
        c.write_message(json_data)
        print("wrote msg", data)


# define whatever static files you want to serve to the browser.
# map the routes that other software (spec/esp/etc) can use.
asset_path = f"{abspath}/assets/"
app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),  # endpoint and the class that will handle its requests
    (r'/api', ApiHandler),
    (r'/(styles.css)', web.StaticFileHandler, {'path': asset_path}),
    (r'/(bootstrap.css)', web.StaticFileHandler, {'path': asset_path}),
    (r'/(wshandler.js)', web.StaticFileHandler, {'path': asset_path}),
])

if __name__ == '__main__':
    print("server now listening on port 7112")
    app.listen(7112)
    ioloop.IOLoop.instance().start()
