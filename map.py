import pygame, os, json, random
from pathlib import Path

class Map():
    def __init__(self):
        self.relative_path = Path().absolute().as_posix()
        with open("{}".format(self.relative_path) + "/map/data/config.json", encoding = 'utf-8' ) as f:
            self.data = json.load(f)

        self.current_map = self.data["map"]["0"]["img"]

        self.tile_1_dict = {}
        self.tile_1 = []
        self.pixel = 6
        for x in self.data["map"]["0"]["tile_1"][0]:
            self.tile_1_dict[tuple([i for i in x])] = 1
            self.tile_1.append(pygame.Rect(x[0]*self.pixel, x[1]*self.pixel, self.pixel, self.pixel))

        self.tile_3_dict = {}
        self.tile_3 = []
        for x in self.data["map"]["0"]["tile_3"][0]:
            self.tile_3_dict[tuple([i for i in x])] = 1
            self.tile_3.append(pygame.Rect(x[0]*self.pixel, x[1]*self.pixel, self.pixel, self.pixel))

        for x in self.data["map"]["0"]["start_pos"]:
            self.start_pos = x

        self.portals = {}
        for x in self.data["map"]["0"]["portals"]:
            self.portals[tuple([i for i in x])] = 1

        self.spawn = []
        for x in self.data["map"]["0"]["spawn"]:
            self.spawn.append(x)

        self.background_image = pygame.image.load("{}".format(self.relative_path) + "/map/image/{}".format(self.current_map)).convert_alpha()
        self.background_image.fill((0, 0, 128), special_flags=pygame.BLEND_RGB_ADD)
        self.map_res = (self.background_image.get_width(),self.background_image.get_height())
        self.background = pygame.Surface(self.map_res)
        self.hit = {}
        self.enemy_pos = {}
        self.enemy_check = {}

        self.moon = pygame.image.load("{}".format(self.relative_path) + "/map/misc/image/moon.png").convert_alpha()
        self.moon = pygame.transform.scale(self.moon, (150, 150))
        self.moon.fill((122,40,44), special_flags=pygame.BLEND_RGB_ADD)
        self.stars_n = 100
        self.stars = [[random.randint(0, self.map_res[0]), random.randint(0, self.map_res[1])] for x in range(self.stars_n)]

    def objects_pos(self, i, collision):
        self.hit[i] = collision


    def enemy_position(self, i, object, name):
        self.enemy_check[i] = (object.x, object.y, name)
        self.enemy_pos[i] = (object.x/(self.map_res[0]/self.width), object.y/(self.map_res[1]/self.height))
        self.enemy_width = object.width/(self.map_res[0]/self.width)
        self.enemy_height = object.height/(self.map_res[1]/self.height)

    def cleanup_pos(self, i):
        if i in self.hit:
            del self.hit[i]
        if i in self.enemy_check:
            del self.enemy_check[i]
        if i in self.enemy_pos:
            del self.enemy_pos[i]

    def mini_map(self, player):
        self.width = 200
        self.height = 100
        self.mini_map_background = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.mini_map_instance = pygame.Surface((self.map_res[0], self.map_res[1])).convert_alpha()
        self.mini_map_instance.set_colorkey((0,0,0))
        self.mini_map_instance = pygame.transform.scale(self.mini_map_instance, (self.width , self.height))
        self.player_x = (player.x/(self.map_res[0]/self.width))
        self.player_y = (player.y/(self.map_res[1]/self.height))
        self.player_width = player.width/(self.map_res[0]/self.width)
        self.player_height = player.height/(self.map_res[1]/self.height)

    def draw(self, surface):
        self.mini_map_instance.blit(self.mini_map_background, (0,0))
        # for tile in self.tile_1:
        #     pygame.draw.rect(self.mini_map_instance, (0,0,0), (tile.x/(self.map_res[0]/self.width), tile.y/(self.map_res[1]/self.height), 1, 1))
        # for tile in self.tile_3:
        #     pygame.draw.rect(self.mini_map_instance, (0,0,0), (tile.x/(self.map_res[0]/self.width), tile.y/(self.map_res[1]/self.height), 1, 1))
        for i in self.enemy_pos:
            pygame.draw.rect(self.mini_map_instance, (255,0,0), (self.enemy_pos[i][0], self.enemy_pos[i][1], self.player_width, self.enemy_height))
        pygame.draw.rect(self.mini_map_instance, (0,0,255), (self.player_x, self.player_y, self.player_width, self.player_height))
        surface.blit(self.mini_map_instance, (0, 0))

    def backdrop(self, scroll):
        self.scroll = scroll.copy()
        self.scroll[0] = int(self.scroll[0])//20
        self.scroll[1] = int(self.scroll[1])//20

        for star in self.stars:
            pygame.draw.line(self.background, (255, 255, 255), (star[0], star[1]), (star[0], star[1]), 2)
            star[0] = star[0] - 1
            if star[0] < 0:
                star[0] = self.map_res[0]
                star[1] = random.randint(0, self.map_res[1])
        self.background.blit(self.moon, (500, 200))

    def update(self, player, scroll):
        self.background.fill((0,0,0))
        self.backdrop(scroll)
        self.background.blit(self.background_image, (0,0))
        self.mini_map(player)
