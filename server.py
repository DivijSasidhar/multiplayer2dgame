import socket
import math
import struct
import random
import pygame
from _thread import start_new_thread

# https://realpython.com/python-sockets/
# https://www.dunebook.com/creating-a-python-socket-server-with-multiple-clients/


# thisis socket init
host = socket.gethostbyname(socket.gethostname())
port = 42069
ThreadCount = 0  # number of connections
players = []

# thisis pygame init
running = True
pygame.init()
clock = pygame.time.Clock()
FPS = 240
dt = 0

max_game_width = 1000
max_game_height = 1000

red = (255, 0, 0)
blue = (0, 255, 0)
green = (0, 0, 255)
white = (255, 255, 255)
gray = (128, 128, 128)
black = (0, 0, 0)

bullets = []


class Player:
    def __init__(self, username, gun):
        self.username = username
        self.position = [random.randint(-200, 200), random.randint(-200, 200)]
        self.gun = gun
        self.size = 30
        self.speed = 300
        self.cursorsize = 6
        self.scoping = False

    def update(self):
        if self.scoping:
            self.speed = self.gun.scoping_speed
            self.cursorsize = 4
        else:
            self.speed = 300
            self.cursorsize = 6


class Gun:
    def __init__(self, firerate, bulletspeed, damage, scoping_speed):
        self.firerate = firerate
        self.bulletspeed = bulletspeed
        self.damage = damage
        self.scoping_speed = scoping_speed

    def gun_fired(self, player):
        i = 0
        while self.firerate > i:
            bullets.append(
                Bullet(player, self)
            )
            i += 1


class Bullet:
    def __init__(self, player, gun):
        xdiff = (pygame.mouse.get_pos()[0] - player.position[0])
        ydiff = (pygame.mouse.get_pos()[1] - player.position[1])
        theta = math.atan(ydiff / (xdiff + 0.00001))
        self.position = player.position[:]
        self.size = gun.damage / 2.5
        self.speed = gun.bulletspeed
        if xdiff < 0:
            self.angle = [
                self.speed * -math.cos(theta),
                self.speed * -math.sin(theta)
            ]
        else:
            self.angle = [
                self.speed * math.cos(theta),
                self.speed * math.sin(theta)
            ]

    def update(self):
        self.position[0] += self.angle[0] * self.speed * dt
        self.position[1] += self.angle[1] * self.speed * dt
        if self.position[0] > max_game_width:
            bullets.remove(self)
        elif self.position[0] < 0:
            bullets.remove(self)
        elif self.position[1] > max_game_height:
            bullets.remove(self)
        elif self.position[1] < 0:
            bullets.remove(self)


def start_server(host, port):
    s = socket.socket()
    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Your server (IP {host}) is listening on Port ({port}).')
    s.listen()
    while True:
        accept_connections(s)


def accept_connections(s):
    Client, address = s.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client,))


def client_handler(connection):
    dt = 0
    player = Player(connection, default_gun)
    players.append(player)
    while connection:
        # thisis boundaries
        if player.position[0] > max_game_width:
            player.position[0] = max_game_width
        elif player.position[0] < 0:
            player.position[0] = 0
        if player.position[1] > max_game_height:
            player.position[1] = max_game_height
        elif player.position[1] < 0:
            player.position[1] = 0

        # thisis sockets
        received = connection.recv(1024)
        if len(received) < 1:
            players.remove(player)
            break
        if received[0] == 1:
            player.position[1] -= player.speed * dt
        if received[1] == 1:
            player.position[1] += player.speed * dt
        if received[2] == 1:
            player.position[0] -= player.speed * dt
        if received[3] == 1:
            player.position[0] += player.speed * dt
        if received[4] == 1:
            bullets.append(Bullet(player, player.gun))

        packet = bytearray(struct.pack('<2f', player.position[0], player.position[1]))
        for p in players:
            if p is not player:  # append all other players that are not the current client in this  # optimize
                packet.extend(b'\FF')
                packet.extend(struct.pack('<2f', p.position[0], p.position[1]))
        connection.sendall(bytes(packet))
        dt = clock.tick(FPS) / 1000


default_gun = Gun(1, 60, 10, 150)
start_server(host, port)
