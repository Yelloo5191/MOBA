import math
import pygame
from pygame.locals import *
from sys import exit

pygame.init()

screen = pygame.display.set_mode((640, 480), 0, 32)
display = pygame.Surface((320, 240))

clock = pygame.time.Clock()
FPS = 60

class World:
    def __init__(self):
        self.map_path = "Assets/Maps/1.txt"
        self.map = []
        self.load_map()
        self.assets = [
            pygame.image.load("Assets/World/grass.png").convert(),
        ]
    
    def load_map(self):
        with open(self.map_path) as f:
            for line in f:
                self.map.append(line.strip())

        print(self.map)
    
    def draw(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == "0":
                    display.blit(self.assets[0], (x * 16, y * 16))
        

class Player:
    # top down mobalike player
    def __init__(self, x, y, cooldowns_max = [2, 2, 2, 2]):
        self.x = x
        self.y = y
        self.speed = 1
        self.rect = pygame.Rect(self.x + 16, self.y + 32, 16, 16)
        self.state = "idle"
        self.cooldowns = [0, 0, 0, 0]
        self.cooldowns_max = cooldowns_max

        self.health_bar_image = pygame.image.load("Assets/UI/Health/healthbar.png").convert()
        self.health_bar_image.set_colorkey((0, 0, 0))
        self.health_bar_image = pygame.transform.scale(self.health_bar_image, (32, 8))
        self.health_bar = pygame.Surface((32, 8), pygame.SRCALPHA)
        self.health_bar.blit(self.health_bar_image, (0, 0))
        self.health_bar.set_alpha(128)
        self.health_cover = pygame.Surface((32, 8), pygame.SRCALPHA)
        self.health_cover.set_alpha(128)
        self.health_cover.fill((255, 0, 0))

        self.health = 800
        self.max_health = 1000


        self.ability_sheet = pygame.image.load("Assets/Characters/1/attacks1.png").convert_alpha()
        self.ability_sheet.set_colorkey((0, 0, 0))
        self.abilities = [pygame.Surface((32, 32)), pygame.Surface((32, 32)), pygame.Surface((32, 32)), pygame.Surface((32, 32))]
        self.abilities[0].blit(self.ability_sheet, (0, 0), (0, 0, 32, 32))
        self.abilities[1].blit(self.ability_sheet, (0, 0), (32, 0, 32, 32))
        self.abilities[2].blit(self.ability_sheet, (0, 0), (64, 0, 32, 32))
        self.abilities[3].blit(self.ability_sheet, (0, 0), (96, 0, 32, 32))

        # Q ability
        self.q_images = []
        for i in range(4):
            self.q_images.append(pygame.image.load(f"Assets/Characters/1/q/q{i + 1}.png").convert())
            self.q_images[i].set_colorkey((0, 0, 0))
        self.q_anim_frame = 0
        self.q_anim_timer = 0
        self.vine_dest = (0, 0)
        self.vine_start = (0, 0)

        # W ability
        self.w_images = []
        for i in range(4):
            self.w_images.append(pygame.image.load(f"Assets/Characters/1/w/w{i + 1}.png").convert())
            self.w_images[i] = self.w_images[i].convert_alpha()
            self.w_images[i].set_alpha(200)
            self.w_images[i].set_colorkey((0, 0, 0))
        self.w_anim_frame = 0
        self.w_time = 2 * FPS
        self.timer = 0
        self.w_circle = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.w_circle.set_alpha(128)
        self.w_size = 32
        self.w_max_size = 64

        # sprite sheet of 4 32x32 sprites in a row featuring a character facing up, right, down, and left respectively
        self.sprite_sheet = pygame.image.load("Assets/Characters/1/sprite1.png").convert()
        self.image = pygame.Surface((32, 32))
        self.image.blit(self.sprite_sheet, (0, 0), (0, 0, 32, 32))
        self.image.set_colorkey((0, 0, 0))
        
    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # normalize mouse positions from scaled screen to 320x240
        mouse_x = mouse_x * 320 / 640
        mouse_y = mouse_y * 240 / 480
    
        # move towards mouse right click
        if pygame.mouse.get_pressed()[2]:

            # get angle between player and mouse
            self.m_angle = math.atan2(mouse_y - self.y, mouse_x - self.x)

            # play click animation
            clickFX.x = mouse_x - 16
            clickFX.y = mouse_y - 16
            clickFX.update()

            # set player state to moving towards mouse
            self.state = "moving"
            self.target_x = mouse_x
            self.target_y = mouse_y
        
        keys = pygame.key.get_pressed()


        if keys[K_q] and self.state != "Q" and self.cooldowns[0] == 0:
            self.state = "Q"
            self.vine_dest = (mouse_x, mouse_y)
            self.vine_start = (self.x, self.y)
            self.vine_length = 0
        if keys[K_w] and self.state != "W" and self.cooldowns[1] == 0:
            self.state = "W"
        if keys[K_e] and self.state != "E" and self.cooldowns[2] == 0:
            self.state = "E"
        if keys[K_r] and self.state != "R" and self.cooldowns[3] == 0:
            self.state = "R"

        # manage player state
        if self.state == "moving":
            # set player sprite to match movement direction

            # up
            if self.m_angle > -math.pi / 4 and self.m_angle < math.pi / 4:
                self.image = pygame.Surface((32, 32))
                self.image.blit(self.sprite_sheet, (0, 0), (32, 0, 32, 32))
                self.image.set_colorkey((0, 0, 0))

            # right
            elif self.m_angle > math.pi / 4 and self.m_angle < math.pi * 3 / 4:
                self.image = pygame.Surface((32, 32))
                self.image.blit(self.sprite_sheet, (0, 0), (64, 0, 32, 32))
                self.image.set_colorkey((0, 0, 0))

            # down
            elif self.m_angle > math.pi * 3 / 4 or self.m_angle < -math.pi * 3 / 4:
                self.image = pygame.Surface((32, 32))
                self.image.blit(self.sprite_sheet, (0, 0), (96, 0, 32, 32))
                self.image.set_colorkey((0, 0, 0))

            # left
            elif self.m_angle < -math.pi / 4 and self.m_angle > -math.pi * 3 / 4:
                self.image = pygame.Surface((32, 32))
                self.image.blit(self.sprite_sheet, (0, 0), (0, 0, 32, 32))
                self.image.set_colorkey((0, 0, 0))

            # move player towards mouse
            self.x += math.cos(self.m_angle) * self.speed
            self.y += math.sin(self.m_angle) * self.speed

            # check if player has reached mouse
            if self.x > self.target_x - 1 and self.x < self.target_x + 1:
                if self.y > self.target_y - 1 and self.y < self.target_y + 1:
                    self.state = "idle"
        
        if self.state == "Q":
            self.cooldowns[0] = self.cooldowns_max[0] * FPS

            # Animate the vine
            self.q_anim_timer += 1
            
            if self.q_anim_timer >= 4 and self.q_anim_frame < 3:
                self.q_anim_timer = 0
                self.q_anim_frame += 1
            
            if self.q_anim_frame >= 3:
                self.q_anim_frame = 3
                if self.q_anim_timer >= 4:
                    self.state = "idle"
                    self.q_anim_frame = 0
                    self.q_anim_timer = 0

            self.q_sprite = pygame.Surface((192, 4))
            self.q_sprite.blit(self.q_images[self.q_anim_frame], (96, 0))
            self.q_sprite.set_colorkey((0, 0, 0))

            # Perform Q attack (vine hook)
            self.draw_vine(self.vine_start, self.vine_dest, self.vine_length)
        
        if self.state == "E":
            self.cooldowns[2] = self.cooldowns_max[2] * FPS

            self.health += 100

            if self.health > self.max_health:
                self.health = self.max_health

            self.state = "idle"

        
        if self.state == "W":
            self.cooldowns[1] = self.cooldowns_max[1] * FPS

            self.timer += 2
            if self.timer >= self.w_time:
                self.timer = 0
                self.w_size = 32
                self.w_anim_frame = 0
                self.state = "idle"

            # every 24 frames, increment animation frame by 1
            if self.timer % 30 == 0:
                self.w_anim_frame += 1
                if self.w_anim_frame >= 4:
                    self.w_anim_frame = 0

            # draw W animation
            display.blit(self.w_images[self.w_anim_frame], (self.x - 32, self.y - 36))
            
            # draw circle
            self.w_circle = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.w_circle.set_alpha(128)
            # pygame.draw.circle(self.w_circle, (255, 0, 0), (32, 32), self.w_size // 2)
            display.blit(self.w_circle, (self.x - 32, self.y - 36))
            circle_rect = self.w_circle.get_rect(center=(self.x, self.y - 4))
            # pygame.draw.rect(display, (255, 255, 255), circle_rect, 1)


            # increase circle size
            self.w_size += 3
            if self.w_size > self.w_max_size:
                self.w_size = self.w_max_size
        else:
            self.timer = 0
            self.w_size = 32

        
        # update cooldowns
        for i in range(4):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] -= 1
        
                

        self.draw()

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, 16, 16)
        # pygame.draw.circle(display, (255, 0, 0), (self.x, self.y), 2)
        display.blit(self.image, (self.x - 16, self.y - 32))

        # draw health bar
        self.health_cover.blit(self.health_bar, (0, 0), (0, 0, 32 * self.health / self.max_health, 8))
        display.blit(self.health_cover, (self.x - 16, self.y - 40))

        # draw shadow
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        s.set_alpha(100)
        pygame.draw.circle(s, (0, 0, 0), (16, 16), 6)
        display.blit(s, (self.x - 16, self.y - 20))

        # draw abilities
        # draw on bottom center of screen
        for i in range(4):
            display.blit(self.abilities[i], (116 - 32 + i * 32 + i * 8, 208))
            if self.cooldowns[i] > 0:
                s = pygame.Surface((32, 32))
                s.set_alpha(128)
                pygame.draw.rect(s, (0, 0, 0), (116 - 32 + i * 32 + i * 8, 208, 32, 32))
                pygame.draw.rect(display, (255, 255, 255), (116 - 32 + i * 32 + i * 8, 208, 32, 32), 1)
                display.blit(s, (116 - 32 + i * 32 + i * 8, 208))
    
    def draw_vine(self, start, end, length):
        angle = (180 / math.pi) * -math.atan2(end[1] - start[1], end[0] - start[0])
        rotated_vine = pygame.transform.rotate(self.q_sprite, int(angle))
        rotated_rect = rotated_vine.get_rect(center=start)

        # Calculate the endpoint of the vine based on the length
        end_line = (
            start[0] + length * math.cos(math.radians(angle)),
            start[1] - length * math.sin(math.radians(angle)),
        )

        # Draw the rotated vine image
        display.blit(rotated_vine, rotated_rect.topleft)

        # Draw the vine line
        # pygame.draw.line(display, (255, 0, 0), start, end_line, 2)
    
class FX:
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.images = self.setup_images(images)
        self.timer = 0
        self.frame = 0
    
    def setup_images(self, images):
        new_images = []
        for image in images:
            new_images.append(pygame.image.load(image).convert())
            new_images[-1].set_colorkey((0, 0, 0))
        return new_images

    def update(self):
        self.timer += 1
        if self.timer >= 2:
            self.timer = 0
            self.frame += 1
            if self.frame >= len(self.images):
                self.reset()
        display.blit(self.images[self.frame], (self.x, self.y))
    
    def reset(self):
        self.timer = 0
        self.frame = 0

player = Player(100, 100, cooldowns_max=[2, 2, 2, 2])
world = World()
clickFX = FX(0, 0, ["Assets/Effects/Click/click1.png", "Assets/Effects/Click/click2.png", "Assets/Effects/Click/click3.png", "Assets/Effects/Click/click4.png"])


while True:
    display.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    world.draw()
    player.update()

    screen.blit(pygame.transform.scale(display, (640, 480)), (0, 0))
    pygame.display.update()
    clock.tick(FPS)