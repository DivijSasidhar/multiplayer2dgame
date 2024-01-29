import socket
import pygame
import struct
from _thread import start_new_thread

# thisis socket init
IP = "10.16.69.5"
PORT = 42069
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_data = bytearray()


def connection(IP, username):
    try:
        s.connect((IP, PORT))
        s.sendall(bytes(username, 'utf-8'))
    except Exception as e:
        exit(e)


# thisis pygame init
running = True
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
FPS = 240
dt = 0

red = (255, 0, 0)
blue = (0, 255, 0)
green = (0, 0, 255)
white = (255, 255, 255)
gray = (128, 128, 128)
black = (0, 0, 0)


class Player:
    def __init__(self, gun):
        self.position = [0, 0]
        self.gun = gun
        self.size = 30
        self.speed = 300
        self.cursorsize = 6
        self.scoping = False
        self.offsetx = 0
        self.offsety = 0

    def update(self):
        pygame.draw.circle(screen, black, (self.position[0] + self.offsetx, self.position[1] + self.offsety), self.size)


player = Player([300, 300])
connection(IP, "Player")


def network_handling():
    while running:
        global server_data
        server_data = s.recv(1024)


start_new_thread(network_handling, ())
request = [False, False, False, False,  # w, a, s, d pushed    # todo optimize by only updating what has changed
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
    print(server_data, '\n')
    try:
        player.position = struct.unpack('<2f', server_data)
    except struct.error:
        pass
    # thisis rendering
    screen.fill(white)
    player.update()  # todo make a camera that offsets everything in the world
    #                    ie make a "real" coordinates and a rendered coordinates
    pygame.draw.circle(screen, red, (pygame.mouse.get_pos()), player.cursorsize, width=2)
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
