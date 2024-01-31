import socket
import pygame
import struct
from _thread import start_new_thread

# thisis socket init
IP = "10.16.69.5"
PORT = 42069
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_data = bytearray()


def connection(IP):
    try:
        s.connect((IP, PORT))
    except Exception as e:
        exit(e)


# thisis pygame init
running = True
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
FPS = 240
dt = 0
pygame.mouse.set_visible(False)
players = []

red = (255, 0, 0)
blue = (0, 255, 0)
green = (0, 0, 255)
white = (255, 255, 255)
gray = (128, 128, 128)
black = (0, 0, 0)


class Player:
    def __init__(self):
        self.position = [0, 0]
        self.size = 30
        self.speed = 300
        self.cursorsize = 6
        self.scoping = False
        self.offsetx = 0
        self.offsety = 0

    def update(self):
        pygame.draw.circle(screen, black, (self.position[0] + self.offsetx, self.position[1] + self.offsety), self.size)


player = Player()
connection(IP)


def network_handling():
    while running:
        global server_data
        server_data = s.recv(1024)


start_new_thread(network_handling, ())
request = [False, False, False, False,  # w, a, s, d pushed    # optimize by only updating what has changed
           False,  # button down / button up
           False, False, False]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            request[4] = True
        if event.type == pygame.MOUSEBUTTONUP:
            # todo gun fired
            request[5] = False

    # thisis inputs
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False
    request[0] = keys[pygame.K_w]
    request[1] = keys[pygame.K_s]
    request[2] = keys[pygame.K_a]
    request[3] = keys[pygame.K_d]

    # thisis socket info
    s.sendall(bytes(request))
    try:
        player.position = struct.unpack('<2f', (server_data[0:8]))
    except struct.error as e:
        print(e)
        pass
    server_data_1 = server_data[8:].split(b"\FF")
    for i in server_data_1[1:]:
        players.append(Player())
        players[-1].position = struct.unpack('<2f', i)
    # thisis rendering
    screen.fill(white)
    player.update()  # todo make a camera that offsets everything in the world
    #                    ie make a "real" coordinates and a rendered coordinates
    for p in players:
        p.update()
    players = []
    pygame.draw.circle(screen, red, (pygame.mouse.get_pos()), player.cursorsize, width=2)
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
