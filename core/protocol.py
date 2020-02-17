import asyncio
import json
import random
import socket
import threading
import time
import discord

from collections import Awaitable
from typing import Dict, Optional, Union
from core.bot import Bot
from libraries import logger as logging
from params import listen_port
from core.exceptions import *


def jsonToBytes(json_data):
    return bytes(json.dumps(json_data) + "\r\n", encoding=encoding)


whois = jsonToBytes({"error": "whois"})
nonexistent = jsonToBytes({"error": "service_not_exists"})
need_auth = jsonToBytes({"error": "need_authorization"})
auth_exist = jsonToBytes({"error": "authorized_user_exists"})
json_error = jsonToBytes({"error": "json_decoding_failed"})
encoding = "UTF-8"


class OCInterface:
    args = ()
    client: 'Client'

    def __init__(self, client: 'Client', args=()):
        self.client = client
        self.args = tuple(args)

    def __getattr__(self, item):
        return OCInterface(self.client, args=(self.args + (item,)))

    def __call__(self, *args, **kwargs) -> Awaitable:
        oc_args = self.args + args
        return self.client.method(self.client, *oc_args)


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

    def __init__(self, cl, hash: str):
        super().__init__()
        self.client = cl
        self.hash = hash

    def resolve(self, response: Union[dict, RemoteResponse]):
        super().set()
        if type(response) == dict:
            self.result = RemoteResponse(response)
        else:
            self.result = response

    def __await__(self) -> RemoteResponse:
        self.wait()
        del self.client.requests[self.hash]
        return self.result


class Client:
    requests: Dict[str, RemoteRequest] = {}
    pings: list = []
    listeners: Dict[str, list] = {}
    remote_socket: Optional[socket.socket] = None
    auth_token: str
    channel: discord.TextChannel
    bot_client: Bot
    name: str

    def __init__(self, auth_token, channel, client, name):
        self.channel = channel
        self.auth_token = auth_token
        self.bot_client = client
        self.name = name

    def create_request(self, hash) -> RemoteRequest:
        if hash in self.requests:
            raise RequestObtainException
        ev = RemoteRequest(self, hash)
        self.requests[hash] = ev
        return ev

    def clean(self):
        self.requests = {}
        self.pings = []
        self.remote_socket = None

    def process_message(self, message: Union[dict, str]):
        if type(message) == str:
            asyncio.ensure_future(self.channel.send(message))
        elif type(message) == dict:
            embed = self.bot_client.get_embed(title=message["title"], description=message["description"])
            if "color" in message:
                embed.colour = message["color"]
            asyncio.ensure_future(self.channel.send(embed=embed))

    def add(self):
        if self.name in clients:
            return
        clients[self.name] = self

    async def method(self, *args):
        if self.remote_socket is None:
            raise SocketClosedException()
        _hash = str(random.randint(0, 2 ** 32 - 1))
        while _hash in self.requests:
            _hash = str(random.randint(0, 2 ** 32 - 1))
        self.remote_socket.send(jsonToBytes({"hash": _hash, "request": list(args)}))
        response: RemoteResponse = await self.create_request(_hash)
        response.raise_if_error()
        return response.response

    def component_method(self, *args) -> Awaitable:
        args = ("component",) + args
        return self.method(self, *args)

    def get_interface(self) -> OCInterface:
        return OCInterface(self)


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
            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError,
                    OSError, UnicodeDecodeError) as e:
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
                        self.logger.info("That client uses service \"%s\"")
                        self.name = received_data["name"]
                        self.client = clients[self.name]
                        if self.check_access():
                            break
                        self.conn.send(need_auth)
                    else:
                        self.conn.send(nonexistent)
                else:
                    self.conn.send(whois)
                continue
            if not self.authorized:
                if "auth" in received_data and received_data["auth"] == self.client.auth_token:
                    if self.check_access():
                        break
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
                # self.client.pings.remove(received_data["hash"])
                self.client.pings = []
            elif "message" in received_data:
                self.logger.debug("Processing message from remote host")
                self.client.process_message(received_data["message"])
            elif "response" in received_data and "hash" in received_data \
                    and received_data["hash"] in self.client.requests:
                self.logger.debug("Response #%s received" % received_data["hash"])
                self.client.requests[received_data["hash"]].resolve(received_data)
        if self.authorized:
            self.client.process_message({"title": "Статус корабля",
                                         "description": "Авторизованный корабль отключен",
                                         "color": 0xFF4C4C})
            self.client.clean()
        self.conn.close()


class ClientPinger(threading.Thread):
    def __init__(self):
        super().__init__(name="ClientPinger", daemon=True)
        self.logger = logging.Logger(app="Pinger")

    def start(self):
        while True:
            for client in clients.values():
                if client.remote_socket is not None:
                    if len(client.pings) in range(3):
                        hsh = str(random.randint(0, 2 ** 32 - 1))
                        try:
                            client.remote_socket.send(jsonToBytes({"request": "ping", "hash": hsh}))
                        except OSError as e:
                            self.logger.error("%s: %s" % (type(e).__name__, e))
                        else:
                            client.pings.append(hsh)
                    else:
                        self.logger.info("Client %s isn't responding, closing connection.." % client.name)
                        try:
                            client.remote_socket.close()
                        except OSError as e:
                            self.logger.error("%s: %s" % (type(e).__name__, e))
                            self.logger.info("This is normal situation - remote peer already closed connection")
            time.sleep(5)


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
            addr: tuple  # Пичарм: СПАСИБО МИЛ ЧЕЛОВЕК Я И НЕ ДОГАДЫВАЛСЯ ЧТО ТУТ ЕБАНЫЙ TUPLE
            self.logger.info("Connecting to %s:%s" % addr)
            SocketHandlerThread(conn, addr).start()


# Сработает один раз. Не используйте importlib и все будет збс
TCPListener().start()
ClientPinger().start()
