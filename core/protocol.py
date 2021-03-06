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
from core import logger as logging
from bot.settings import listen_port, protocol_encoding, listen_ip
from core.exceptions import *
from core.lua_serialization import to_lua


def jsonToBytes(json_data):
    return bytes(json.dumps(json_data) + "\r\n", encoding=protocol_encoding)


whois = jsonToBytes({"error": "whois"})
nonexistent = jsonToBytes({"error": "service_not_exists"})
need_auth = jsonToBytes({"error": "need_authorization"})
auth_exist = jsonToBytes({"error": "authorized_user_exists"})
json_error = jsonToBytes({"error": "json_decoding_failed"})
start_event = threading.Event()


class OCInterface:
    method = ()
    client: 'ProtocolService'

    def __init__(self, client: 'ProtocolService', method=()):
        self.client = client
        self.method = method

    def __getattr__(self, item):
        return OCInterface(self.client, method=(self.method + (item,)))

    def __call__(self, *args, **kwargs) -> Awaitable:
        oc_args = args
        if kwargs:
            oc_args += (kwargs,)
        return self.client.method(".".join(self.method), oc_args)


class RemoteResponse:
    response: list
    has_error: bool

    def __init__(self, resp):
        self.response = resp["data"]
        self.has_error = True if "error" in resp and resp["error"] else False

    def raise_if_error(self):
        if self.has_error is True:
            raise OpenComputersError(self.response[0])


class RemoteRequest(asyncio.Event):
    hash: str
    result: RemoteResponse

    def __init__(self, cl, hash: str):
        super().__init__()
        self.create_time = time.time()
        self.client = cl
        self.hash = hash

    def resolve(self, response: Union[dict, RemoteResponse]):
        super().set()
        if type(response) == dict:
            self.result = RemoteResponse(response)
        else:
            self.result = response

    def __await__(self) -> RemoteResponse:
        yield from self.wait()
        del self.client.requests[self.hash]
        return self.result


class ProtocolService:
    requests: Dict[str, RemoteRequest] = {}
    pings: list = []
    listeners: Dict[str, list] = {}
    remote_socket: Optional[socket.socket] = None
    auth_token: str
    channel: discord.TextChannel
    bot_client: Bot
    name: str

    def __init__(self, auth_token, channel, bot_client, name):
        self.channel = channel
        self.auth_token = auth_token
        self.bot_client = bot_client
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
            embed = self.bot_client.get_embed(title="Говорит клиент %s" % self.name,
                                              description=message)
            asyncio.run_coroutine_threadsafe(self.channel.send(embed=embed), self.bot_client.loop)
        elif type(message) == dict:
            embed = self.bot_client.get_embed(title=message["title"], description=message["description"])
            if "color" in message:
                embed.colour = message["color"]
            asyncio.run_coroutine_threadsafe(self.channel.send(embed=embed), self.bot_client.loop)

    def add(self):
        if self.name in services:
            return
        services[self.name] = self

    @property
    def connected(self) -> bool:
        return self.remote_socket is not None

    async def execute(self, code):
        if self.remote_socket is None:
            raise SocketClosedException()
        _hash = str(random.randint(0, 2 ** 32 - 1))
        while _hash in self.requests:
            _hash = str(random.randint(0, 2 ** 32 - 1))
        self.remote_socket.send(jsonToBytes({"hash": _hash, "request": "execute", "data": code}))
        response: RemoteResponse = await self.create_request(_hash)
        response.raise_if_error()
        return response.response

    def method(self, method, args):
        code = "return package.loaded.%s(%s)" % (method, ",".join(to_lua(elem) for elem in args))
        return self.execute(code)

    def disconnect(self):
        if self.connected:
            self.remote_socket.send(jsonToBytes({"request": "exit"}))

    def get_interface(self) -> OCInterface:
        return OCInterface(self)


services: Dict[
    str, ProtocolService] = dict()  # name: service - позволяет иметь несколько клиентов, подключенных одновременно


class SocketHandlerThread(threading.Thread):
    logger = None
    addr = None
    conn: socket.socket = None
    authorized = False
    service_name = None
    client: ProtocolService = None

    def __init__(self, conn, addr):
        super().__init__(name="Handler")
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
                data = str(self.conn.recv(4096), encoding=protocol_encoding)
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
            if self.service_name is None:
                if "name" in received_data:
                    if received_data["name"] in services:
                        self.logger.info("That client uses service \"%s\"" % received_data["name"])
                        self.service_name = received_data["name"]
                        self.client = services[self.service_name]
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
                    self.client.process_message({"title": "Сервисные сообщения протокола",
                                                 "description": "Клиент %s:%s подключился к сервису %s." %
                                                                (self.addr[0], self.addr[1], self.service_name),
                                                 "color": 0x6AAF6A})
                    self.logger.info("Authorized")
                else:
                    self.conn.send(need_auth)
                continue
            if "message" in received_data:
                self.logger.debug("Processing message from remote host")
                self.client.process_message(received_data["message"])
            if "response" in received_data:
                if received_data["response"] == "ping":
                    self.client.pings.clear()
                elif received_data["response"] == "execute" and "hash" in received_data \
                        and received_data["hash"] in self.client.requests:
                    req = self.client.requests[received_data["hash"]]
                    self.logger.debug("Response #%s received (%ss)" % (received_data["hash"],
                                                                       time.time() - req.create_time))
                    req.resolve(received_data)
        if self.authorized:
            self.client.process_message({"title": "Сервисные сообщения протокола",
                                         "description": "Клиент %s:%s отключился от сервиса %s." %
                                                        (self.addr[0], self.addr[1], self.service_name),
                                         "color": 0x6AAF6A})
            self.client.clean()
        self.conn.close()


class ClientPinger(threading.Thread):
    def __init__(self):
        super().__init__(name="ClientPinger", daemon=True)
        self.logger = logging.Logger(app="Pinger")

    def run(self):
        while True:
            for client in services.values():
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
                        print(client.pings)
                        self.logger.info("ProtocolService %s isn't responding, closing connection.." % client.name)
                        try:
                            client.remote_socket.close()
                            client.remote_socket = None
                            client.clean()
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
        sock.bind((listen_ip, listen_port))
        sock.listen()
        self.logger.info("Start listening %s port" % listen_port)
        start_event.set()
        while True:
            conn, addr = sock.accept()
            addr: tuple  # Пичарм: СПАСИБО МИЛ ЧЕЛОВЕК Я И НЕ ДОГАДЫВАЛСЯ ЧТО ТУТ ЕБАНЫЙ TUPLE
            self.logger.info("Connecting to %s:%s" % addr)
            SocketHandlerThread(conn, addr).start()


def deploy():
    if start_event.is_set():
        return
    TCPListener().start()
    ClientPinger().start()
    start_event.wait()
