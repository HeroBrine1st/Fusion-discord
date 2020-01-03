import asyncio
import json
import random
import socket
import threading
import discord

from collections import Awaitable
from typing import Dict, Optional, Union

from core.bot import Bot
from libraries import logger as logging
from params import *
from core.exceptions import *


def jsonToBytes(json_data):
    return bytes(json.dumps(json_data) + "\r\n", encoding=encoding)


whois = jsonToBytes({"error": "whois"})
nonexistent = jsonToBytes({"error": "service_not_exists"})
need_auth = jsonToBytes({"error": "need_authorization"})
auth_exist = jsonToBytes({"error": "authorized_user_exists"})
json_error = jsonToBytes({"error": "json_decoding_failed"})
encoding = "UTF-8"


class RemoteResponse:
    response: list
    has_error: bool

    def __init__(self, resp):
        self.response = resp["response"]
        self.has_error = True if "error" in resp and resp["error"] else False

    def raise_if_error(self):
        if self.has_error is True:
            raise OpenComputersError(self.response[0])


class RemoteRequest(asyncio.Event):
    hash: str
    result: RemoteResponse

    def __init__(self, hash: str):
        super().__init__()
        self.hash = hash

    def resolve(self, response: Union[dict, RemoteResponse]):
        super().set()
        if type(response) == dict:
            self.result = RemoteResponse(response)
        else:
            self.result = response


class Client:
    requests: Dict[str, RemoteRequest] = {}
    pings: list = []
    listeners = []
    remote_socket: Optional[socket.socket] = None
    auth_token: str
    channel: discord.TextChannel
    client: Bot

    def __init__(self, auth_token, channel, client):
        self.channel = channel
        self.auth_token = auth_token
        self.client = client

    def clean(self):
        self.requests = {}
        self.pings = []
        self.remote_socket = None

    def process_message(self, message: Union[dict, str]):
        if type(message) == str:
            asyncio.ensure_future(self.channel.send(message))
        elif type(message) == dict:
            embed = self.client.get_embed(title=message["title"], description=message["description"])
            if "color" in message:
                embed.colour = message["color"]
            asyncio.ensure_future(self.channel.send(embed=embed))


clients: Dict[str, Client] = dict()  # name: client - позволяет иметь несколько клиентов, подключенных одновременно


class SocketHandlerThread(threading.Thread):
    logger = None
    addr = None
    conn: socket.socket = None
    authorized = False
    name = None
    client: Client = None

    def __init__(self, conn, addr):
        super().__init__(name="Socket Handler", daemon=True)
        self.logger = logging.Logger(thread="Socket", app="%s:%s" % addr)
        self.addr = addr
        self.conn = conn

    def check_access(self):
        if self.client.remote_socket is not None:
            self.logger.info("Service denied: another authorized client already connected")
            self.conn.send(auth_exist)
            # Согласно протоколу, удаленный хост должен сам отключиться
            return True
        return False

    def run(self) -> None:
        self.logger.info("Connected. Waiting information...")
        self.conn.send(whois)
        while True:
            try:
                data = str(self.conn.recv(4096), encoding=encoding)
            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError, OSError) as e:
                self.logger.error("%s: %s" % (type(e).__name__, e))
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
            if self.name is None:
                if "name" in received_data:
                    if received_data["name"] in clients:
                        self.logger.info("this client uses service \"%s\"")
                        self.name = received_data["name"]
                        self.client = clients[self.name]
                        if self.check_access():
                            return
                    else:
                        self.conn.send(nonexistent)
                else:
                    self.conn.send(whois)
                continue
            if not self.authorized:
                if "auth" in received_data and received_data["auth"] == self.client.auth_token:
                    if self.check_access():
                        return
                    self.authorized = True
                    self.client.remote_socket = self.conn
                    self.conn.send(jsonToBytes({"authorized": True}))
                    self.client.process_message({"title": "Статус корабля",
                                                 "description": "Подключен авторизованный корабль"})
                    self.logger.info("Authorized")
                else:
                    self.conn.send(need_auth)
                continue
            if "ping_response" in received_data and "hash" in received_data:
                pings.remove(received_data["hash"])
            elif "message" in received_data:
                self.logger.debug("Processing message from remote host")
                self.client.process_message(received_data["message"])
            elif "response" in received_data and "hash" in received_data:
                self.logger.debug("Response #%s received" % received_data["hash"])
                self.client.requests[received_data["hash"]].resolve(received_data)
        if self.authorized:
            self.client.process_message({"title": "Статус корабля",
                                         "description": "Авторизованный корабль отключен",
                                         "color": 0xFF4C4C})
            self.client.clean()
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
    event = asyncio.Event()
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
