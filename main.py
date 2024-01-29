import pygame
import math


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


bullets = []


class Player:
    def __init__(self, gun):
        self.position = [screen.get_height()/2, screen.get_width()/2]
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

        pygame.draw.circle(screen, black, (self.position[0], self.position[1]), self.size)
        pygame.draw.circle(screen, red, (pygame.mouse.get_pos()), self.cursorsize, width=2)


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
        theta = math.atan(ydiff/(xdiff + 0.00001))
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


default_gun = Gun(1, 60, 10, 150)
player = Player(default_gun)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.scoping = True
        if event.type == pygame.MOUSEBUTTONUP:
            player.gun.gun_fired(player)
            player.scoping = False

    # thisis calculations
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False
    if keys[pygame.K_w]:  # up
        player.position[1] -= player.speed * dt
    if keys[pygame.K_s]:  # downsd
        player.position[1] += player.speed * dt
    if keys[pygame.K_a]:  # left
        player.position[0] -= player.speed * dt
    if keys[pygame.K_d]:  # right
        player.position[0] += player.speed * dt

    for bullet in bullets:
        bullet.update()

    # thisis screen boundary
    if player.position[0] > screen.get_width():
        player.position[0] = screen.get_width()
    elif player.position[0] < 0:
        player.position[0] = 0
    if player.position[1] > screen.get_height():
        player.position[1] = screen.get_height()
    elif player.position[1] < 0:
        player.position[1] = 0
    for bullet in bullets[:]:
        if bullet.position[0] > screen.get_width():
            bullets.remove(bullet)
        elif bullet.position[0] < 0:
            bullets.remove(bullet)
        elif bullet.position[1] > screen.get_height():
            bullets.remove(bullet)
        elif bullet.position[1] < 0:
            bullets.remove(bullet)

    # thisis rendering
    screen.fill(white)
    player.update()
    for bullet in bullets:
        pygame.draw.rect(screen, red, (bullet.position[0], bullet.position[1], 4, 10))  # bullet
    pygame.display.flip()

    dt = clock.tick(FPS) / 1000
