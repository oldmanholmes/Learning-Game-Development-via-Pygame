import pygame, time, random, secrets, config, logging, option, sys, os, json

# initialize pygame settings
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)
pygame.display.set_caption("Map Editor")
clock = pygame.time.Clock()

# global constants
global VOLUME
global WINDOW_SIZE
global RESOLUTION
global CHANGED
VOLUME = 0.1
CHANGED = False

# initialize window and surfaces
WINDOW_SIZE = (1024, 768)
camera = pygame.display.set_mode(WINDOW_SIZE)
screen = pygame.display.set_mode(WINDOW_SIZE)
RESOLUTION = (1920, 1080)
display = pygame.Surface(RESOLUTION)
surface = pygame.Surface((1920, 1080))
background_image = pygame.image.load('../Project_01_Game/map/image/entrance.png').convert()
background_image.set_colorkey((0, 0, 0))
background_width = background_image.get_width()
background_height = background_image.get_height()
background = pygame.Surface((background_width, background_height))
option_menu = pygame.display.set_mode((WINDOW_SIZE[0] + 300, WINDOW_SIZE[1]))

# cursor variables
cursor = pygame.image.load('../Project_01_Game/ui/image/cursor/normal.gif').convert()
cursor.set_colorkey((0, 255, 0))
cursor_click = pygame.image.load('../Project_01_Game/ui/image/cursor/click.gif').convert()
cursor_click.set_colorkey((0, 255, 0))
pygame.mouse.set_visible(False)
cursor_rect = cursor.get_rect()
cursor_click_sound = pygame.mixer.Sound('../Project_01_Game/ui/audio/cursor/MouseClick.wav')
cursor_over_sound = pygame.mixer.Sound('../Project_01_Game/ui/audio/cursor/MouseOver.wav')

# player variables
player_x = 50
player_y = 50
moving_right = False
moving_left = False
direction = ''
player_movement = [0, 0]
WALK = 0
IDLE = 0
REVERSE = 0

# button variable
img_normal = pygame.image.load('../Project_01_Game/ui/image/button/normal.png')
img_hovered = pygame.image.load('../Project_01_Game/ui/image/button/hovered.png')


# create Surface objects
def create_surface(width, height, color, transparent=False):
    surface = pygame.surface.Surface((width, height)).convert_alpha()
    if transparent == False:
        surface.fill(color)
    else:
        surface.fill((color) + (230,), special_flags=pygame.BLEND_RGBA_MULT)
    return surface

def Menu():
    global VOLUME
    global WINDOW_SIZE
    global RESOLUTION
    global CHANGED
    pygame.mixer.music.load('../Project_01_Game/ui/audio/map_editor/38. Blue Destination.mp3')
    pygame.mixer.music.set_volume(VOLUME)
    pygame.mixer.music.play(-1)
    click_timer = 0
    button_1 = option.Button('EDIT', True, WINDOW_SIZE[0]+50,
                            0, int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.YELLOW,
                            img_normal, img_hovered)
    buttons = [button_1]
    running = True
    while running:
        option_menu.fill(config.BLACK)
        if CHANGED == True:
            buttons = button_function()
            CHANGED = False

        for button in buttons:
            button.draw(option_menu)

        logging.info('Menu ON!')

        # click cooldown
        if click_timer != 0:
            cursor_rect.center = pygame.mouse.get_pos()
            screen.blit(cursor_click, cursor_rect)
            click_timer -= 1

        elif click_timer == 0:
            cursor_rect.center = pygame.mouse.get_pos()
            screen.blit(cursor, cursor_rect)

        # process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                mouse_position = event.pos
                for b in buttons:
                    b.handleMouseOver(mouse_position)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if click_timer == 0:
                        click_timer = 10

                mouse_position = event.pos
                for b in range(len(buttons)):
                    if buttons[b].mouseIsOver(mouse_position):
                        if b == 0:
                            cursor_click_sound.play()
                            running = False
                            Game()
                        elif b == 1:
                            cursor_click_sound.play()
                        elif b == 2:
                            cursor_click_sound.play()
                            Options()
                        elif b == 3:
                            cursor_click_sound.play()
                            pygame.quit()
                            sys.exit()

        pygame.display.update()
        clock.tick(config.FPS)
def Game():
    # movement
    jump = False
    # pygame.mixer.music.load('../Project_01_Game/ui/audio/map_editor/38. Blue Destination.mp3')
    # pygame.mixer.music.set_volume(VOLUME)
    # pygame.mixer.music.play(-1)

    button_2 = option.Button('MAP', True, WINDOW_SIZE[0]+50,
                            int(WINDOW_SIZE[1]/14.4), int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.YELLOW,
                            img_normal, img_hovered)

    button_3 = option.Button('Tile', True, WINDOW_SIZE[0]+50,
                            int(WINDOW_SIZE[1]/14.4)*2.5, int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.BLUE,
                            img_normal, img_hovered)

    button_4 = option.Button('Rope', True, WINDOW_SIZE[0]+50,
                            int(WINDOW_SIZE[1]/14.4)*4, int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.YELLOW,
                            img_normal, img_hovered)

    button_5 = option.Button('Stair', True, WINDOW_SIZE[0]+50,
                            int(WINDOW_SIZE[1]/14.4)*5.5, int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.LIGHT_BLUE,
                            img_normal, img_hovered)

    button_6 = option.Button('Save', True, WINDOW_SIZE[0]+50,
                            int(WINDOW_SIZE[1]/14.4)*7, int(WINDOW_SIZE[0]/5.12),
                            int(WINDOW_SIZE[1]/14.4), config.BLACK, config.LIGHT_BLUE,
                            img_normal, img_hovered)

    buttons = [button_2, button_3, button_4, button_5, button_6]

    def spritesheet(path, tag):
        sprite_images = [pygame.image.load(path + "/{}".format(i)).convert_alpha()
                        for i in os.listdir(path) if i.startswith("{}".format(tag))]
        return sprite_images

    def gravity_function(object, gravity, tiles, tiles2, jump):

        gravity_rect = object.copy()
        gravity_check = False

        stair_rect = object.copy()
        stair_check = False

        if free_roam != True:
            gravity_rect.y += gravity
            for tile in tiles:
                if gravity_rect.colliderect(tile):
                    gravity_check = True
            if gravity_check == True:
                jump = False

            stair_rect.y += gravity
            for tile in tiles2:
                if (stair_rect.x, stair_rect.y) in tiles2 and gravity > -4:
                    jump = False

        return jump, gravity

    def movement(object, direction, jump, rope, tiles, rope_rects, stair_rects, free_roam, gravity, movement_x=3):
        global WALK
        global IDLE

        dummy_rect = object.copy()
        dummy_check = False

        gravity_rect = object.copy()
        gravity_check = False

        stair_rect = object.copy()
        stair_check = False

        if free_roam != True:
            for tile in rope_rects:
                if tile.collidepoint(object.center):
                    if moving_up:
                        object.x = tile.x - object.width//2
                        object.y -= 3
                        rope = True
                    elif moving_down:
                        object.x = tile.x - object.width//2
                        object.y += gravity
                        rope = True
                    object.y -= gravity

            gravity_rect.y += gravity
            for tile in tiles:
                if gravity_rect.colliderect(tile):
                    gravity_check = True
            if gravity_check == False:
                object.y += gravity

        IDLE += 1

        if IDLE  == 320:
            IDLE = 0

        if direction == 'Left':
            movement_state = idle_image[IDLE//80]

        elif direction == 'Right':
            movement_state = pygame.transform.flip(idle_image[IDLE//80], True, False)

        if WALK + 1 >= 40:
            WALK = 0
        if moving_right and object.x < background_width - object.width:
            direction = 'Right'
            dummy_rect.x += movement_x
            for tile in tiles:
                if dummy_rect.colliderect(tile):
                    dummy_check = True
            if dummy_check == False:
                object.x += movement_x
            else:
                object.x += 0
            movement_state = pygame.transform.flip(movement_image[WALK//8], True, False)
            WALK += 1

        elif moving_right and object.x == background_width - object.width:
            direction = 'Right'
            object.x += 0
            movement_state = pygame.transform.flip(movement_image[WALK//8], True, False)
            WALK += 1


        if moving_left and object.x > 0:
            direction = 'Left'
            dummy_rect.x -= movement_x
            for tile in tiles:
                if dummy_rect.colliderect(tile):
                    dummy_check = True
            if dummy_check == False:
                object.x -= movement_x
            else:
                object.x -= 0
            movement_state = movement_image[WALK//8]
            WALK += 1


        elif moving_left and object.x == 0:
            direction = 'Left'
            object.x -= 0
            movement_state = movement_image[WALK//8]
            WALK += 1

        if free_roam == True:
            if moving_up and object.y > 0:
                dummy_rect.y -= movement_x
                for tile in tiles:
                    if dummy_rect.colliderect(tile):
                        dummy_check = True
                if dummy_check == False:
                    object.y -= movement_x
                else:
                    object.y -= 0

            if moving_down and object.y < background_height - object.height:
                dummy_rect.y += movement_x
                for tile in tiles:
                    if dummy_rect.colliderect(tile):
                        dummy_check = True
                if dummy_check == False:
                    object.y += movement_x
                else:
                    object.y -= 0

        if movement_state.get_width() > movement_image[0].get_width() and direction == 'Left' and jump != True and down != True:
            background.blit(movement_state, (object.x - (movement_state.get_width() - movement_image[0].get_width()), object.y))
        elif movement_state.get_width() < movement_image[0].get_width() and direction == 'Left' and jump != True and down != True:
            background.blit(movement_state, (object.x - (-1*(movement_image[0].get_width() - movement_state.get_width())), object.y))

        elif jump != True and down != True:
            background.blit(movement_state, (object.x, object.y))
        elif jump == True:
            if direction == 'Left':
                background.blit(jump_image[0], (object.x, object.y))
            else:
                background.blit(pygame.transform.flip(jump_image[0], True, False), (object.x, object.y))
        elif down == True and jump != True:
            if direction == 'Left':
                background.blit(down_image[0], (object.x, object.y + (movement_state.get_height() - down_image[0].get_height())))
            elif direction == 'Right':
                background.blit(pygame.transform.flip(down_image[0], True, False), (object.x, object.y + (movement_state.get_height() - down_image[0].get_height())))
        elif rope == True:
            background.blit(movement_state, (object.x, object.y))


    font = pygame.font.SysFont(None, 50)
    menu_text = font.render('Map Editor', True, config.BLACK)
    floor_inactive = font.render('Floor: Inactive', True, config.RED)
    floor_active = font.render('Floor: Active', True, config.BLUE)
    delete_inactive = font.render('Delete: Inactive', True, config.RED)
    delete_active = font.render('Delete: Active', True, config.BLUE)
    delete_check = False
    floor_check = False

    start_coord = [0, 0]
    portal = []
    spawn = []

    idle_image = spritesheet("../Project_01_Game/player/image", "stand")
    movement_image = spritesheet("../Project_01_Game/player/image", "walk")
    jump_image = spritesheet("../Project_01_Game/player/image", "jump")
    down_image = spritesheet("../Project_01_Game/player/image", "prone")

    player = idle_image[0]
    player_rect = pygame.Rect(start_coord[0], start_coord[1], player.get_width(), player.get_height())

    map_image = [pygame.image.load("../Hell Knight Revamped/data/map/images/{}".format(i)).convert_alpha() for i in os.listdir("../Hell Knight Revamped/data/map/images/")]
    map_file_name = [i for i in os.listdir("../Hell Knight Revamped/data/map/images/")]
    jump_sound = pygame.mixer.Sound('../Hell Knight/Sounds/Jump.wav')
    portal_img = pygame.image.load("../Project_01_Game/map/portal/portal01.png").convert_alpha()
    spawn_img = pygame.Surface((100, 1))
    spawn_img.fill((255,0 ,0))

    start = player
    start = pygame.transform.flip(start, True, False)
    portal_img = pygame.transform.scale(portal_img, (200, 150))
    # player_rect = pygame.Rect(starting_coord[0], starting_coord[1], 32, 32)
    direction = 'Right'
    moving_right = False
    moving_left = False
    moving_up = False
    moving_down = False
    down = False
    jump = False
    rope = False
    player_y_momentum = 0
    free_roam = True

    tile_coord = {}
    tiles = []
    tile = create_surface(player.get_width(), player.get_height()//10, config.BLUE, False)
    pixel = 6

    true_scroll = [0 , 0]
    menu = create_surface(300, WINDOW_SIZE[1], config.WHITE, False)
    map_buttons = []
    for i in range(len(map_image)):
        map_image[i] = pygame.transform.scale(map_image[i], (300, 300))
        map_buttons.append(option.Button('', True, 300*(i), 0, 300, 300, config.BLACK, config.YELLOW, map_image[i], map_image[i]))

    square = pygame.Surface((pixel,pixel))
    square.fill(config.BLUE)
    square2 = pygame.Surface((pixel, pixel))
    square2.fill(config.YELLOW)
    square3 = pygame.Surface((pixel, pixel))
    square3.fill(config.LIGHT_BLUE)


    def draw_grid(screen):
        for i in range(0, background_width, pixel):
            pygame.draw.line(screen, (255, 255, 255), (0, i), (background_width, i))
            pygame.draw.line(screen, (255, 255, 255), (i, 0), (i, background_width))

    # cursor
    click_timer = 0
    hold = False
    mx = [0]
    drag = False
    recording = False
    delete = False
    show_grid = False
    mouse_check = 1

    # map
    background_images_list = [i for i in os.listdir("../Project_01_Game/map/image/")]
    background_images = [pygame.image.load("../Project_01_Game/map/image/{}".format(i)).convert_alpha() for i in background_images_list]
    map_index = 0
    background_image = background_images[map_index]
    background_width = background_image.get_width()
    background_height = background_image.get_height()
    background = pygame.Surface((background_width, background_height))
    map_id = background_images_list[map_index]

    map_menu_on = False
    absolute = False
    stair = False
    rope = False

    for maps in map_file_name:
        map_text = font.render('{}'.format(maps), True, config.BLACK)
    tile_rects = []
    rope_rects = []
    stair_rects = []
    tile_map = {}
    corrected_map = {}
    tile_1 = []
    tile_2 = []
    tile_3 = []
    count = 0

    for y in range(background_height//(pixel)):
        for x in range(background_width//(pixel)):
            tile_map[(x, y)] = 0

    row = (background_width//(pixel))
    col = (background_height//(pixel))

    running = True
    while running:
        background.fill(config.BLACK)

        true_scroll[0] += (player_rect.x - true_scroll[0] - (round(WINDOW_SIZE[0]/2) - round(32/2))) / 20
        true_scroll[1] += (player_rect.y - true_scroll[1] - (round(WINDOW_SIZE[1]/2) - round(32/2))) / 20
        if true_scroll[0] < 0:
            true_scroll[0] = 0
        if true_scroll[0] > background_width - WINDOW_SIZE[0]:
            true_scroll[0] = background_width - WINDOW_SIZE[0]
        if true_scroll[1] < 0:
            true_scroll[1] = 0
        if true_scroll[1] > background_height - WINDOW_SIZE[1]:
            true_scroll[1] = background_height - WINDOW_SIZE[1]

        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        jump, player_y_momentum = gravity_function(player_rect, player_y_momentum, tile_rects, rope_rects, jump)

        player_y_momentum += 0.2
        if player_y_momentum > 3.0:
            player_y_momentum = 3.0

        background.blit(background_image, (0, 0))
        background.blit(start, (start_coord))
        for x in portal:
            background.blit(portal_img, x)
        for x in spawn:
            background.blit(spawn_img, x)

        tile_rects = []
        rope_rects = []
        stair_rects = []
        corrected_map = {}

        for k, v in tile_map.items():
            if v == 1:
                background.blit(square, (k[0]*(background_width//row), k[1]*(background_height//col)))
                tile_rect = pygame.Rect(k[0]*(background_width//row),k[1]*(background_height//col), square.get_width(), square.get_height())
                tile_rects.append(tile_rect)
            if v == 2:
                background.blit(square2, (k[0]*(background_width//row), k[1]*(background_height//col)))
                tile_rect = pygame.Rect(k[0]*(background_width//row),k[1]*(background_height//col), square2.get_width(), square2.get_height())
                rope_rects.append(tile_rect)
            if v == 3:
                background.blit(square3, (k[0]*(background_width//row), k[1]*(background_height//col)))
                tile_rect = pygame.Rect(k[0]*(background_width//row),k[1]*(background_height//col), square3.get_width(), square3.get_height())
                stair_rects.append(tile_rect)
            if v != 0:
                corrected_map[k] = v

        movement(player_rect, direction, jump, rope, tile_rects, rope_rects, stair_rects, free_roam, player_y_momentum)
        if show_grid == True:
            draw_grid(background)

        screen.blit(background, (0 - scroll[0], 0 - scroll[1]))
        FPS_text = pygame.font.SysFont('Ariel', 50).render(str(int(clock.get_fps())), 1, config.YELLOW)
        screen.blit(FPS_text, (WINDOW_SIZE[0] - FPS_text.get_width(), 0))

        option_menu.blit(menu, (WINDOW_SIZE[0], 0))
        option_menu.blit(menu_text, (WINDOW_SIZE[0] + 60, 0))

        pos = pygame.mouse.get_pos()
        x = (pos[0] + scroll[0]) // (pixel)
        y = (pos[1] + scroll[1]) // (pixel)

        #300, WINDOW_SIZE[1]

        for button in buttons:
            button.draw(option_menu)

        if hold == True:
            if absolute == True:
                if mouse_check == 1:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 1
                elif mouse_check == 2:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 0

            elif rope == True:
                if mouse_check == 1:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 2
                elif mouse_check == 2:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 0

            elif stair == True:
                if mouse_check == 1:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 3
                elif mouse_check == 2:
                    if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                        tile_map[(x, y)] = 0

        if map_menu_on == True:
            for b in map_buttons:
                b.draw(screen)

        # click cooldown
        if click_timer != 0:
            cursor_rect = pygame.mouse.get_pos()
            screen.blit(cursor_click, cursor_rect)
            if hold == False:
                click_timer -= 2

        elif click_timer == 0 and hold == False:
            cursor_rect = pygame.mouse.get_pos()
            screen.blit(cursor, cursor_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                mouse_position = event.pos
                for b in buttons:
                    b.handleMouseOver(mouse_position)
                if map_menu_on == True:
                    for b in map_buttons:
                        b.handleMouseOver(mouse_position)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    if absolute == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 1
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 1

                    elif rope == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 1
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 2

                    elif stair == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 1
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 3

                    mouse_position = event.pos
                    for b in range(len(buttons)):
                        if buttons[b].mouseIsOver(mouse_position):
                            if b == 0:
                                absolute = False
                                rope = False
                                stair = False
                                cursor_click_sound.play()
                                if map_menu_on != True:
                                    map_menu_on = True
                                else:
                                    map_menu_on = False

                            elif b == 1:
                                cursor_click_sound.play()
                                rope = False
                                stair = False
                                if absolute == True:
                                    absolute = False
                                else:
                                    absolute = True

                            elif b == 2:
                                cursor_click_sound.play()
                                absolute = False
                                stair = False
                                if rope == True:
                                    rope = False
                                else:
                                    rope = True

                            elif b == 3:
                                cursor_click_sound.play()
                                absolute = False
                                rope = False
                                if stair == True:
                                    stair = False
                                else:
                                    stair = True
                            elif b == 4:
                                cursor_click_sound.play()
                                for k,v in corrected_map.items():
                                    if v == 1:
                                        tile_1.append(list(k))
                                    elif v == 2:
                                        tile_2.append(list(k))
                                    elif v == 3:
                                        tile_3.append(list(k))

                                with open("../Project_01_Game/map/data/config.json", "w")as f:
                                    print('{"map":', file=f)
                                    print('{"Entrance":{"img":' + '"{}","tile_1":'.format(map_id) + "[" + "{}".format(tile_1), file=f)
                                    print(']', file=f)
                                    print(',"tile_2":' + "[" + "{}".format(tile_2), file=f)
                                    print(']', file=f)
                                    print(',"tile_3":' + "[" + "{}".format(tile_3), file=f)
                                    print(']', file=f)
                                    print(',"start_pos":' + "[{}]".format(start_coord), file=f)
                                    print(',"portals":' + "{}".format(portal), file=f)
                                    print(',"spawn":' + "{}".format(spawn), file=f)
                                    # print('start_coord:{}'.format(start_coord), file=f)
                                    print("}}}", file=f)

                    if map_menu_on == True:
                        for b in map_buttons:
                            if b.mouseIsOver(mouse_position):
                                cursor_click_sound.play()

                if event.button == 3:
                    if absolute == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 2
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 0

                    elif rope == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 2
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 0

                    elif stair == True:
                        if click_timer == 0:
                            click_timer = 10
                        hold = True
                        mouse_check = 2
                        if pos[0] + scroll[0] <= screen.get_width() + scroll[0] - 300:
                            tile_map[(x, y)] = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag = False
                    hold = False
                elif event.button == 3:
                    drag = False
                    hold = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LEFT:
                    direction = 'Left'
                    moving_left = True
                if event.key == pygame.K_RIGHT:
                    direction = 'Right'
                    moving_right = True
                if event.key == pygame.K_UP:
                    moving_up = True
                if event.key == pygame.K_DOWN:
                    moving_down = True
                if event.key == pygame.K_f:
                    start_coord = [player_rect.x, player_rect.y]
                if event.key == pygame.K_g:
                    portal.append([player_rect.x, player_rect.y])
                if event.key == pygame.K_h:
                    if len(portal) > 0:
                        portal.pop()
                if event.key == pygame.K_t:
                    spawn.append([player_rect.x, player_rect.y+player_rect.height])
                if event.key == pygame.K_y:
                    if len(spawn) > 0:
                        spawn.pop()
                if event.key == pygame.K_z:
                    show_grid = True
                if event.key == pygame.K_SPACE:
                    if player_y_momentum == 3.0 and jump != True:
                        jump_sound.play()
                        jump_sound.set_volume(0.1)
                        jump = True
                        player_y_momentum = -6
                if event.key == pygame.K_x:
                    if free_roam != True:
                        free_roam = True
                    else:
                        free_roam = False


            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    moving_left = False
                if event.key == pygame.K_RIGHT:
                    moving_right = False
                if event.key == pygame.K_UP:
                    moving_up = False
                if event.key == pygame.K_DOWN:
                    moving_down = False
                if event.key == pygame.K_z:
                    show_grid = False
                if event.key == pygame.K_x:
                    delete = False

        clock.tick(config.FPS)
        pygame.display.update()

Menu()
