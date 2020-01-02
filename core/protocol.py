import asyncio
import json
import random
import socket
import threading
from collections import Awaitable

from libraries import logger as logging
from params import *
from core.exceptions import *


def jsonToBytes(json_data):
    return bytes(json.dumps(json_data) + "\r\n", encoding=encoding)


need_auth = jsonToBytes({"error": "need_authorization"})
auth_exist = jsonToBytes({"error": "authorized_user_exists"})
json_error = jsonToBytes({"error": "json_decoding_failed"})
encoding = "UTF-8"

messages = []
responses = {}
pings = []
listeners = {}
connected = False
remote_socket = None


class SocketHandlerThread(threading.Thread):
    logger = None
    addr = None
    conn: socket.socket = None
    authorized = False

    def __init__(self, conn, addr):
        super().__init__(name="Socket Handler", daemon=True)
        self.logger = logging.Logger(thread="Socket", app="%s:%s" % addr)
        self.addr = addr
        self.conn = conn

    def run(self) -> None:
        global messages
        global responses
        global pings
        global listeners
        global connected
        global remote_socket
        if connected:
            self.logger.info("Connection denied: another authorized client already connected")
            self.conn.send(auth_exist)
            # Согласно протоколу, удаленный хост должен сам отключиться
            return
        self.logger.info("Connected. Waiting authorization...")
        self.conn.send(need_auth)
        while True:
            try:
                data = str(self.conn.recv(4096), encoding=encoding)
            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError, OSError) as e:
                self.logger.error("%s: %s" % (type(e).__name__, e))
                # noinspection PyBroadException
                try:
                    self.conn.close()
                except Exception as e:
                    self.logger.error("Error closing connection:\n%s: %s" % (type(e).__name__, e))
                else:
                    self.logger.info("Closed connection")
                break
            if not data:
                break
            try:
                received_data = json.loads(data)
            except json.JSONDecodeError:
                self.conn.send(json_error)
                continue
            if type(received_data) != dict:
                self.conn.send(json_error)
                continue
            if not self.authorized:
                if "auth" in received_data and received_data["auth"] == auth_token:
                    self.authorized = True
                    connected = True
                    remote_socket = self.conn
                    self.conn.send(jsonToBytes({"authorized": True}))
                    messages.append({"title": "Статус корабля",
                                     "description": "Подключен авторизованный корабль"})
                    self.logger.info("Authorized")
                else:
                    self.conn.send(need_auth)
                continue
            if "ping_response" in received_data and "hash" in received_data:
                pings.remove(received_data["hash"])
            elif "message" in received_data:
                self.logger.debug("Processing message from remote host")
                messages.append(received_data["message"])
            elif "response" in received_data and "hash" in received_data:
                self.logger.debug("Response #%s received" % received_data["hash"])
                responses[received_data["hash"]] = {
                    "response": received_data["response"],
                    "error": True if "error" in received_data and received_data["error"] else False
                }

        if self.authorized:
            messages.append({"title": "Статус корабля",
                             "description": "Авторизованный корабль отключен",
                             "color": 0xFF4C4C})
            connected = False
            remote_socket = None
            pings = []
        self.conn.close()


async def ship_pinger() -> None:
    logger = logging.Logger(app="Pinger")
    while True:
        if connected and len(pings) < 4:
            hsh = str(random.randint(0, 2 ** 32 - 1))
            pings.append(hsh)
            try:
                remote_socket.send(jsonToBytes({"request": "ping", "hash": hsh}))
            except OSError as e:
                logger.error("%s: %s" % (type(e).__name__, e))
                pings.remove(hsh)
            if len(pings) > 0:
                logger.warning("Ping warning: %s/4" % len(pings))
        elif len(pings) > 3:
            logger.info("Ping failed, closing connection..")
            try:
                remote_socket.close()
            except OSError as e:
                logger.error("%s: %s" % (type(e).__name__, e))
                logger.info("This is normal situation - remote peer already closed connection")
        await asyncio.sleep(5)


class TCPListener(threading.Thread):
    def __init__(self):
        super().__init__(name="TCPListener", daemon=True)
        self.logger = logging.Logger(thread="Socket", app="Listener")

    def run(self) -> None:
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", listen_port))
        sock.listen()
        self.logger.info("Start listening %s port" % listen_port)
        while True:
            conn, addr = sock.accept()
            # НЕТ ТУТ БЛЯДЬ ОШИБКИ, ТАМ АЙПИ + ПОРТ СУКА В TUPLE
            # noinspection PyStringFormat
            self.logger.info("Connecting to %s:%s" % addr)
            SocketHandlerThread(conn, addr).start()


async def method(*args):
    _hash = str(hash(args))
    if not remote_socket:
        raise SocketClosedException()
    remote_socket.send(jsonToBytes({"hash": _hash, "request": list(args)}))
    while _hash not in responses:
        await asyncio.sleep(0.1)
    res = responses[_hash]
    del responses[_hash]
    if res["error"]:
        raise OpenComputersError(res["response"][0])
    return res["response"]


def component_method(*args) -> Awaitable:
    args = ("component",) + args
    return method(*args)


class OCMethod:
    args = ()

    def __init__(self, args=None):
        if args is None:
            args = ()
        self.args = tuple(args)

    def __getattr__(self, item):
        return OCMethod(args=(self.args + (item,)))

    def __call__(self, *args, **kwargs) -> Awaitable:
        oc_args = self.args + args
        return method(*oc_args)
