from player import *
import pygame

#Function - Load Sprites
def spritesheet(path, tag):
    sprite_images = [pygame.image.load(path + "/{}".format(i)).convert_alpha()
                    for i in os.listdir(path) if i.startswith("{}".format(tag))]
    return sprite_images

#Function - Checks Collision
def collision_check(player, objects, counter):
    if player.rect.colliderect(objects.body1_rect):
        return True

# Not sure if i'm going to keep this in
def front_layer(player, screen_res, surface1, surface2):
    surface1.blit(surface2, (0 - player.scroll[0], 0 - player.scroll[1]))
    #pygame.draw.circle(surface1, (98,19,18), (0+radius, screen_res[1] - radius), radius, width=0)
    #pygame.draw.rect(surface1, player.HP_color, (0, screen_res[1] - 200, player.current_HP, 200))

#Function - Normalize width and height so sprites blit pos are synonymous
def sprite_offset(sprites, sprites2=[]):
    x_offset, y_offset = [], []
    if len(sprites2) == 0:
        for sprite in sprites:
             if sprite.get_width() > sprites[0].get_width():
                 x_offset.append(sprite.get_width() - sprites[0].get_width())
             elif sprite.get_width() < sprites[0].get_width():
                 x_offset.append(-1*(sprites[0].get_width() - sprite.get_width()))
             else:
                 x_offset.append(0)

        for sprite in sprites:
            if sprite.get_height() != sprites[0].get_height():
                y_offset.append(sprite.get_height() - sprites[0].get_height())
            else:
                y_offset.append(0)

        return x_offset, y_offset
    else:
        for sprite in sprites2:
             if sprite.get_width() > sprites[0].get_width():
                 x_offset.append(sprite.get_width() - sprites[0].get_width())
             elif sprite.get_width() < sprites[0].get_width():
                 x_offset.append(-1*(sprites[0].get_width() - sprite.get_width()))
             else:
                 x_offset.append(0)

        for sprite in sprites2:
            if sprite.get_height() != sprites[0].get_height():
                y_offset.append(sprite.get_height() - sprites[0].get_height())
            else:
                y_offset.append(0)

        return x_offset, y_offset
