import pygame, sys, os, settings, time, random
from pygame._sdl2 import Window, WINDOWPOS_CENTERED
from player import *
from functions import *
from enemy import *
from map import *

# initialize pygame settings
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)
pygame.display.set_caption("{}".format(settings.title))
clock = pygame.time.Clock()
FPS = settings.FPS
TARGET_FPS = settings.FPS
screen = pygame.display.set_mode(settings.WINDOW_SIZE)
WINDOW_SIZE = settings.WINDOW_SIZE
screen_width = screen.get_width()
screen_height = screen.get_height()

counter = 0
prev_time = time.time()
dt = 0

# initialize Window and Secret modules
window = Window.from_display_module()
map = Map()
player = Player(map.start_pos)
number = 1
unique_id = []
while len(unique_id) < number:
    num = random.randint(0,2000)
    if num not in unique_id:
        unique_id.append(num)

enemies = [(unique_id[i],Enemy(map.spawn)) for i in range(number)]
menu = Menu(settings.WINDOW_SIZE)
game_instance = map.background
# collision_l = [0]*len(monsters)

running = True
while running:
    clock.tick(FPS)
    dt = time.time() - prev_time
    dt *= TARGET_FPS
    prev_time = time.time()
    if dt < 0.9 or dt > 1.1:
        #average dt over many trials
        dt = 1

    death_list = []
    map.update(player.rect, player.true_scroll)
    player.update(dt, False, WINDOW_SIZE, map.map_res, map.tile_1, map.tile_3, map.portals)
    if enemies:
        for enemy in enemies:
            map.objects_pos(enemy[0], (player.rect.colliderect(enemy[1].rect)))
            map.enemy_position(enemy[0], enemy[1].rect, enemy[1].name)
            enemy[1].update(dt, game_instance, map.map_res, map.tile_1, map.tile_3, enemy[0], player.single_hit)
            if enemy[1].death:
                map.cleanup_pos(enemy[0])
            if enemy[1].cleanup == 0:
                if enemy[1] not in death_list:
                    death_list.append(enemy)
    if death_list:
        enemies.remove(death_list[0])
        num = random.randint(0,2000)
        if num not in unique_id:
            enemies.append((num, Enemy(map.spawn)))

    player.collision(map.hit, map.enemy_check)
    player.draw(game_instance)
    screen.fill(settings.BLACK)
    front_layer(player, WINDOW_SIZE, screen, game_instance)
    map.draw(screen)
    player.globe(screen, WINDOW_SIZE)
    player.user_interface(screen, WINDOW_SIZE)
    #menu.run(screen)

    FPS_text = pygame.font.SysFont('Ariel', 50).render(str(int(clock.get_fps())), 1, settings.YELLOW)
    screen.blit(FPS_text, (settings.WINDOW_SIZE[0] - FPS_text.get_width(), 0))

    pygame.display.update()
