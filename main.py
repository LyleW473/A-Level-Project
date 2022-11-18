import pygame, sys, os, random
from pygame.locals import *
from pygame import mixer
from MAP import *
import pickle


# Setup
pygame.display.set_caption('Space Platformer')

clock = pygame.time.Clock()
fps = 60
time_counter = 0

# initialising
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.font.init()

# score counter variables
one_second = 1000
last_time = pygame.time.get_ticks()
last_timer_count = pygame.time.get_ticks()

# menu variables
main_menu = True
pause_menu = False
level_complete = False


# game variables
tile_size = 50
GRAVITY = 0.75
SCROLL_THRESH = 490 # 500 - 10
screen_scroll = 0
scrolled_distance = 0
bg_scroll = 0
double_jump = 0
game_over = 0
score = 0


# Enemy 3 variables
enemy_shoot_cooldown = 1000
last_shot = pygame.time.get_ticks()
countdown = 0 # implement countdown later on 
last_count = pygame.time.get_ticks()


# Orb trap variables
orb_shoot_cooldown = 2000
last_orb_shot = pygame.time.get_ticks()
last_orb_count = pygame.time.get_ticks()

# screen measurements
screen_width = 1000 #len(world_data) * tile_size
screen_height = 800

WINDOW_SIZE = (screen_width, screen_height) # SIZE OF WINDOW
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

# action variables
moving_left = False
moving_right = False

# colours
BLACK = (0,0,0)
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLUE = (0,0,255)

# define fonts
font = pygame.font.SysFont('Amasis MT Pro Black', 70)
font_score = pygame.font.SysFont('Calibri', 30)

# load images
Space_background_img = pygame.image.load('graphics/background/bg2.png')
width = Space_background_img.get_width()
height = Space_background_img.get_height()
Space_background_img = pygame.transform.scale(Space_background_img,(int(width * 4), int(height * 4)))



# button images
start_img = pygame.image.load('graphics/buttons/start_btn.png')
continue_img = pygame.image.load('graphics/buttons/continue_btn.png')
quit_img = pygame.image.load('graphics/buttons/quit_btn.png')
quit_2_img = pygame.image.load('graphics/buttons/quit_btn_2.png')
quit_3_img = pygame.image.load('graphics/buttons/quit_btn_3.png')
quit_4_img = pygame.image.load('graphics/buttons/quit_btn_4.png')
title_img = pygame.image.load('graphics/buttons/title_btn.png')
controls_img = pygame.image.load('graphics/buttons/controls_btn.png')
replay_img = pygame.image.load('graphics/buttons/replay_btn.png')
replay_2_img = pygame.image.load('graphics/buttons/replay_btn_2.png')
replay_3_img = pygame.image.load('graphics/buttons/replay_btn_3.png')
level_complete_img = pygame.image.load('graphics/buttons/level_complete_btn.png')
game_over_img = pygame.image.load('graphics/buttons/game_over_btn.png')
paused_img = pygame.image.load('graphics/buttons/paused_btn.png')
 

# load sounds
coin_fx = pygame.mixer.Sound('sounds/coin.wav')
health_up_fx = pygame.mixer.Sound('sounds/health_up.wav')
health_down_fx = pygame.mixer.Sound('sounds/health_down.wav')
jump_fx = pygame.mixer.Sound('sounds/jump.wav')
lava_fx = pygame.mixer.Sound('sounds/lava.wav')
level_completed_fx = pygame.mixer.Sound('sounds/level_completed.wav')
game_over_fx = pygame.mixer.Sound('sounds/game_over.wav')

# play once variables
game_over_fx_played = False
level_completed_fx_played = False



# change sound volume
coin_fx.set_volume(0.15) #15%
health_up_fx.set_volume(0.15) #15%
health_down_fx.set_volume(0.15) # 15%
jump_fx.set_volume(0.3) # 30%
lava_fx.set_volume(0.15) # 15%
level_completed_fx.set_volume(0.1)# 10%
game_over_fx.set_volume(0.05) # 5%




def draw_bg():

    screen.fill(BLACK)
    width = Space_background_img.get_width()
    for x in range(20):
        screen.blit(Space_background_img,((x * width) - bg_scroll,-200))
    
    #pygame.draw.line(screen, RED, (0,700), (screen_width, 700)) draws lines

def reset_game():
    global screen_scroll
    global bg_scroll
    global time_counter
    global last_time
    global score # num of coins
    global game_over
    global game_over_fx_played
    global level_completed_fx_played
    
    screen_scroll += bg_scroll
    bg_scroll = 0
    player.rect.y = 750
    time_counter = 0
    last_time = pygame.time.get_ticks()
    score = 0
    game_over = 0
    player.health_start = 3
    player.health_remaining = 3
    game_over_fx_played = False
    level_completed_fx_played = False
    
    return screen_scroll
    return bg_scroll
    return time_counter
    return last_time
    return score
    return game_over
    return game_over_fx_played
    return level_completed_fx_played


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
    
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):

        action = False
        
        #get mouse position
        pos = pygame.mouse.get_pos()

        # check mouse-over and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #pygame.mouse.get_pressed()[0] , [0] = left mouse btn
                action = True
                self.clicked = True
                
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        #draw button
        screen.blit(self.image, self.rect)

        return action    
    

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.vel_y = 0
        self.direction = 1 #( -1 = left, 1 = right)
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # ( 0 = idle, 1 = run)
        self.update_time = pygame.time.get_ticks()
        self.can_jump = True # Player is stationary and spawns on the ground 
        self.can_doublejump = False
        self.in_air = False
        self.on_ground = True
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks


        
        
        # load all images for players
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            # reset the temporary list of images
            temporary_list = []
            # find how many images in folder
            number_of_frames = len(os.listdir(f'graphics/{self.char_type}/{animation}'))
            for i in range(number_of_frames): # value = how many images in folder
                img = pygame.image.load(f'graphics/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img,(int(img.get_width()* scale), int(img.get_height()* scale)))
                temporary_list.append(img)
            self.animation_list.append(temporary_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0
        collision_threshold = 20
        

        global game_over
        global score
        global level_complete

        if game_over == 0:
        
            # assign movement variables if moving_left or moving_right
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
                
            if moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

            
            
            # apply gravity
            self.vel_y += GRAVITY
            if self.vel_y > 19: # limit velocity to 10
                self.vel_y = 19
            dy += self.vel_y


            # check for collision with grounded enemies
            if pygame.sprite.spritecollide(self, enemy_group, False, pygame.sprite.collide_mask):
                game_over = -1
               

            # check for collision with UFO
            if pygame.sprite.spritecollide(self, enemy3_group, False, pygame.sprite.collide_mask):
                game_over = -1
            
            # check for collision with spike
            if pygame.sprite.spritecollide(self, spike_group, False, pygame.sprite.collide_mask):
                game_over = -1
            
            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False, pygame.sprite.collide_mask):
                lava_fx.play()
                game_over = -1
              

            # check for collision with coins
            if pygame.sprite.spritecollide(self, coin_group, True, pygame.sprite.collide_mask): # True indicates that the coin disappears
                score += 1
                coin_fx.play() 
            draw_text('X ' + str(score), font_score, WHITE, tile_size - 10, 10)

            # check for collision with collectible hearts
            if self.health_remaining < 3: # if HP is less than 3 
                if pygame.sprite.spritecollide(self, heart_group, True, pygame.sprite.collide_mask): # consume heart
                    health_up_fx.play()
                    self.health_remaining += 1 # increase hp
                    
            if self.health_remaining == 3:
                if pygame.sprite.spritecollide(self, heart_group, False, pygame.sprite.collide_mask):
                    pass
                

                
                
            # check for collision with platforms
            for platform in platform_group:
                #collision in the x-direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #collision in the y-direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below platform
                    if abs((self.rect.top + dy) - (platform.rect.bottom)) < collision_threshold:
                        dy = platform.rect.bottom - self.rect.top
                        self.vel_y = 0
                    #check if above platform
                    elif abs((self.rect.bottom + dy) - (platform.rect.top)) < collision_threshold:
                        self.rect.bottom = platform.rect.top  # 1 pixel above so that player can move in x direction
                        self.on_ground = True
                        self.vel_y = 0
                        self.can_double_jump = True
                        self.can_jump = True
                        dy = 0

                    # move sideways with platform
                    self.rect.x += platform.move_direction
                    
                
            # check for collision with portal
            if pygame.sprite.spritecollide(self, portal_group, False, pygame.sprite.collide_mask):
                level_complete = True


            # check for collision with tiles
            
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if on the ground (jumping)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0 #makes sure he isn't floating for a bit after colliding with tile with head
                    # check if above the ground (falling)
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        self.can_double_jump = True
                        self.can_jump = True
                        self.in_air = False
                        self.on_ground = True
                        dy = tile[1].top - self.rect.bottom
                        

            # update rectangle position / player co-ord
            self.rect.x += dx
            self.rect.y += dy

            # draw health bar
            pygame.draw.rect(screen, WHITE, ((screen_width - 355),(10) ,310, 25)) # + 10 to y co-ord to make the border around HP
            pygame.draw.rect(screen, RED, ((screen_width - 350), (15), 300, 15)) # display, x, y, width, height
            
            if self.health_remaining > 0:
                pygame.draw.rect(screen, GREEN, ((screen_width - 350), (15), int(300 * (self.health_remaining / self.health_start)),15))
            elif self.health_remaining <= 0:
                self.kill()
                game_over = -1
            
            # update scroll based on player position
            if self.char_type == 'player':
                if self.rect.right > screen_width - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                    self.rect.x -= dx

                    screen_scroll = -dx # equal to speed of the player, if player is trying to go right (dx is positive), screen goes left      

        return screen_scroll
        return game_over
        return score
        return level_complete
     

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image based on current frame index
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks() # reset update time
            self.frame_index += 1
        # reset animation
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        #check if new action is different to previous one
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def jump(self):
        self.vel_y = 0
        if self.can_jump == True:
            self.on_ground = False
            #self.can_jump = False
            self.vel_y -= 19
            
        elif self.can_doublejump == True: #and double_jump <= 2:
            self.on_ground = False
            #self.can_double_jump = False
            self.vel_y -= 19
            

            

        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self, data):
        self.tile_list = []


        # load images
        floor2_img = pygame.image.load('graphics/tiles/floor2.png')
        floor1_img = pygame.image.load('graphics/tiles/floor1.png')
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    floor2_image = pygame.transform.scale(floor2_img, (tile_size, tile_size))
                    floor2_image_rect = floor2_image.get_rect()
                    floor2_image_rect.x = col_count * tile_size
                    floor2_image_rect.y = row_count * tile_size
                    tile = (floor2_image, floor2_image_rect)
                    self.tile_list.append(tile)
                    
                if tile == 2:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                    
                if tile == 3:
                    enemy1 = Enemy(col_count * tile_size, row_count * tile_size - 15)
                    enemy_group.add(enemy1)
                    
                if tile == 4:
                    spike = Spike(col_count * tile_size, row_count * tile_size)
                    spike_group.add(spike)
                    
                if tile == 5:
                    enemy2 = Enemy2(col_count * tile_size, row_count * tile_size - 15)
                    enemy_group.add(enemy2)

                if tile == 6:
                    heart = Heart(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size //2))
                    heart_group.add(heart)
                    
                    
                if tile == 7:
                    lava = Lava(col_count * tile_size, row_count * tile_size)
                    lava_group.add(lava)
                    
                if tile == 8: # Change last 2 parameters to 1 or 0 to change to different type of platform
                    platform = Platform(col_count * tile_size, row_count * tile_size , 1, 0)
                    platform_group.add(platform)
                    

                if tile == 9: # Shooting enemy
                    enemy3 = Enemy3(col_count * tile_size, row_count * tile_size - 15)
                    enemy3_group.add(enemy3)

                if tile == 10: # Orb trap
                    orb = Orb(col_count * tile_size, row_count * tile_size)
                    orb_group.add(orb)

                if tile == 11: # AI enemy
                    enemy4 = Enemy4(col_count * tile_size, row_count * tile_size - 15)
                    enemy_group.add(enemy4)
                    
                if tile == 12: # Portal
                    portal = Portal(col_count * tile_size, row_count * tile_size - 50)
                    portal_group.add(portal)
                    
                col_count += 1
            row_count += 1
            
    def draw(self):
        for tile in self.tile_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)  (draw white outlines)  
           
# Enemy (Type 1)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.move_counter = 0
        # animation
        self.move_direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0 = walk / run
        self.update_time = pygame.time.get_ticks()

        # load all enemy images
        animation_types = ['walk']
        for animation in animation_types:
            # reset the temporary list of images
            temporary_list = []
            # find how many images in folder
            number_of_frames = len(os.listdir(f'graphics/enemy/type1/{animation}'))
            for i in range(number_of_frames): # value = how many images in folder
                img = pygame.image.load(f'graphics/enemy/type1/{animation}/{i}.png')
                img = pygame.transform.scale(img,(75,75))
                temporary_list.append(img)
            self.animation_list.append(temporary_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += self.move_direction + screen_scroll
        self.move_counter += 0.5
        if abs(self.move_counter) > 27:
            self.move_direction *= -1
            self.move_counter *= -1

        # Flipping image direction
        if self.move_direction == -1: # should face left
            self.flip = True
        if self.move_direction == 1: # should face right
            self.flip = False

            
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image based on current frame index
        if self.flip == False:
            self.image = self.animation_list[self.action][self.frame_index]
        if self.flip == True:
            self.image = self.animation_list[self.action][self.frame_index]
            flipped_image = pygame.transform.flip(self.image,True,False)
            self.image = flipped_image
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks() # reset update time
            self.frame_index += 1
        # reset animation
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0


# Enemy (Type 2)

class Enemy2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.move_counter = 0
        # animation
        self.move_direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0 = walk / run
        self.update_time = pygame.time.get_ticks()

        # load all enemy images
        animation_types = ['walk']
        for animation in animation_types:
            # reset the temporary list of images
            temporary_list = []
            # find how many images in folder
            number_of_frames = len(os.listdir(f'graphics/enemy/type2/{animation}'))
            for i in range(number_of_frames): # value = how many images in folder
                img = pygame.image.load(f'graphics/enemy/type2/{animation}/{i}.png')
                img = pygame.transform.scale(img,(75,75))
                temporary_list.append(img)
            self.animation_list.append(temporary_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += self.move_direction + screen_scroll
        self.move_counter += 0.5
        if abs(self.move_counter) > 27:
            self.move_direction *= -1
            self.move_counter *= -1

        # Flipping image direction
        if self.move_direction == -1: # should face left
            self.flip = True
        if self.move_direction == 1: # should face right
            self.flip = False

            
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image based on current frame index
        if self.flip == False:
            self.image = self.animation_list[self.action][self.frame_index]
        if self.flip == True:
            self.image = self.animation_list[self.action][self.frame_index]
            flipped_image = pygame.transform.flip(self.image,True,False)
            self.image = flipped_image
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks() # reset update time
            self.frame_index += 1
        # reset animation
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
 

# Shooting UFO Enemy

class Enemy3(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('graphics/enemy/type3/UFO' + str(random.randint(1, 5)) + '.png'), (128, 128))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.y += self.move_direction
        self.rect.x += screen_scroll
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= self.move_direction
        
class Enemy_3_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('graphics/enemy/type3/bullet/enemy_bullet.png'), (32,32))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.center = (x, y)

    def update(self):
        global game_over
        
        self.rect.x += screen_scroll
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, player_group, False, pygame.sprite.collide_mask):
            self.kill()
            health_down_fx.play()
            # damage player
            player.health_remaining -= 1

        # Looks at tile inside world tile list
        for tile in world.tile_list:
            # if the orb collides with a tile then delete the object
            if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.kill()

        return game_over


# Enemy (Type 4)

class Enemy4(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # enemy behaviour variables
        self.detect = pygame.Rect(0, 0, 500, 40)  
        self.move_counter = 0
        
        # animation
        self.move_direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0 = walk / run
        self.update_time = pygame.time.get_ticks()

        # load all enemy images
        animation_types = ['walk']
        for animation in animation_types:
            # reset the temporary list of images
            temporary_list = []
            # find how many images in folder
            number_of_frames = len(os.listdir(f'graphics/enemy/type4/{animation}'))
            for i in range(number_of_frames): # value = how many images in folder
                img = pygame.image.load(f'graphics/enemy/type4/{animation}/{i}.png')
                img = pygame.transform.scale(img,(75,75))
                temporary_list.append(img)
            self.animation_list.append(temporary_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

    def update(self):
        
        move_distance_x = 0

        # draw detection rect
        self.detect.center = (self.rect.centerx + 280 * self.move_direction, self.rect.centery)
        #pygame.draw.rect(screen,RED, self.detect) #Used to show the detection rect on screen

        # check if player is within detection rect
        if self.detect.colliderect(player.rect):
            if self.move_direction == -1:
                # is facing left
                move_distance_x = 6
            if self.move_direction == 1:
                # is facing right
                move_distance_x = -6
                
        else:

            self.move_counter += 0.5
        
            if abs(self.move_counter) > 27:
                self.move_direction *= -1
                self.move_counter *= -1

            # Flipping image direction
            if self.move_direction == -1: # should face left
                self.flip = True
                    
            if self.move_direction == 1: # should face right
                self.flip = False
    
        self.rect.x += self.move_direction + screen_scroll - move_distance_x

                
                

            
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image based on current frame index
        if self.flip == False:
            self.image = self.animation_list[self.action][self.frame_index]
        if self.flip == True:
            self.image = self.animation_list[self.action][self.frame_index]
            flipped_image = pygame.transform.flip(self.image,True,False)
            self.image = flipped_image
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks() # reset update time
            self.frame_index += 1
        # reset animation
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

            
    

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/spike.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        self.rect.x += screen_scroll

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        self.rect.x += screen_scroll
        

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/coin.png')
        self.image = pygame.transform.scale(img, (int(tile_size // 1.5), (int(tile_size // 1.5)))) # half a tile size
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) # midpoint instead of top left of tile

    def update(self):
        self.rect.x += screen_scroll
        

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/platform.png')
        self.image = pygame.transform.scale(img, (int(tile_size * 1.5),int(tile_size * 1.25)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.center = (x, y)
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y
        
        
    def update(self):
        self.rect.x += self.move_direction * self.move_x + screen_scroll
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/heart.png')
        self.image = pygame.transform.scale(img, (int(tile_size // 1.5), (int(tile_size // 1.5)))) # half a tile size
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) # midpoint instead of top left of tile

    def update(self):
        self.rect.x += screen_scroll


class Orb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/orb_trap.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
    def update(self):
        self.rect.x += screen_scroll


class Orb_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('graphics/tiles/orb_bullet.png'), (32,32))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        global game_over
        
        self.rect.x += screen_scroll
        self.rect.x -= 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, player_group, False, pygame.sprite.collide_mask):
            self.kill()
            health_down_fx.play()
            # damage player
            player.health_remaining -= 1
    
        # Looks at tile inside world tile list
        for tile in world.tile_list:
            # if the orb collides with a tile then delete the object
            if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.kill()


        return game_over


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('graphics/tiles/portal.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += screen_scroll       
    
    
# Instances
        
player = Player('player', 550,750, 3, 8, 3)



# groups

enemy_group = pygame.sprite.Group()
enemy3_group = pygame.sprite.Group()
enemy_3_bullets_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
orb_group = pygame.sprite.Group()
orb_bullets_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
heart_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_group.add(player)
portal_group = pygame.sprite.Group()




# dummy coin (for score)
coin_image = pygame.transform.scale(pygame.image.load('graphics/tiles/coin.png'), (30,30))
world = World(world_data)

title_btn = Button(150,30, title_img) # main menu
start_btn = Button(340,300, start_img) # main menu
controls_btn = Button(340, 450, controls_img) # main menu
quit_btn = Button(340, 600, quit_img) # main menu


paused_btn = Button(150,30, paused_img) # pause menu
continue_btn = Button(340,300, continue_img) # pause menu
replay_btn = Button(340,450, replay_img) # pause menu
quit_btn_2 = Button(340,600, quit_2_img) # pause menu


game_over_btn = Button(150,30, game_over_img) # game over menu
replay_btn_2 = Button(340,350, replay_2_img) # game over menu
quit_btn_3 = Button(340,500, quit_3_img) # game over menu


level_complete_btn = Button(150,30, level_complete_img) # level complete menu
replay_btn_3 = Button(340,350, replay_3_img) # level complete menu
quit_btn_4 = Button(340,500, quit_4_img) # level complete menu



run = True
while run == True:

    
    clock.tick(fps)


    if main_menu == True:
        title_btn.draw()
        if quit_btn.draw():
            run = False
        if controls_btn.draw():
            draw_text('W - Move forward', font_score, WHITE, 700,400)
            draw_text('A - Move left', font_score, WHITE, 700,440)
            draw_text('D - Move right', font_score, WHITE, 700,480)
            draw_text('Space - Jump', font_score, WHITE, 700,520)
            
        if start_btn.draw():
            main_menu = False
            
    if level_complete == False:
        if pause_menu == False:
            if main_menu == False:
                # if in-game and player isn't dead
                if game_over == 0:
                    
                    draw_bg()        
                    world.draw()
                    player.update_animation()
                    player.draw()
                        
                    enemy_group.update()
                    enemy3_group.update()
                    enemy_3_bullets_group.update()
                    spike_group.update()
                    orb_group.update()
                    orb_bullets_group.update()
                    lava_group.update()
                    coin_group.update()
                    heart_group.update()
                    platform_group.update()
                    portal_group.update()
                        
                    enemy_group.draw(screen)
                    enemy3_group.draw(screen)
                    enemy_3_bullets_group.draw(screen)
                    spike_group.draw(screen)
                    orb_group.draw(screen)
                    orb_bullets_group.draw(screen)
                    lava_group.draw(screen)
                    coin_group.draw(screen)
                    heart_group.draw(screen)
                    platform_group.draw(screen)
                    portal_group.draw(screen)

                    screen.blit(coin_image,(10,8))

                    # update time counter
                    time_now = pygame.time.get_ticks()
                    # increment the time counter
                    # last time = 0 at first, time_now would count up till it reaches one_second
                    if time_now - last_time > one_second:
                        time_counter += 1 # increment time counter by 1.
                        last_time = time_now # last_time would be set to the current time
                    # draw timer text
                    draw_text("Time: "+ str(time_counter) +" s", font_score, WHITE, 10, 50)
                        
                        
                    # create random enemy bullets
                    # record current time
                    time_now = pygame.time.get_ticks()
                    #shoot
                    if time_now - last_shot > enemy_shoot_cooldown and len(enemy_3_bullets_group) < 5 and len(enemy3_group) > 0:
                        attacking_enemy = random.choice(enemy3_group.sprites())
                        bullet = Enemy_3_Bullets(attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
                        enemy_3_bullets_group.add(bullet)
                        last_shot = time_now

                    time_now = pygame.time.get_ticks()
                    if time_now - last_orb_shot > orb_shoot_cooldown:
                        for orb in orb_group:
                            orb_trap = orb
                            orb_bullet = Orb_Bullets(orb_trap.rect.centerx - 30, orb_trap.rect.centery)
                            orb_bullets_group.add(orb_bullet)
                            last_orb_shot = time_now


                # update player actions as long as the player is alive
                    if player.in_air:
                        player.update_action(2) # changes player action to jump
                    elif moving_left or moving_right:
                        player.update_action(1) # changes player action to run
                    else:
                        player.update_action(0) # changes player action to idle
                    screen_scroll = player.move(moving_left, moving_right)
                    bg_scroll -= screen_scroll

                    
                if game_over == -1:
                    if game_over_fx_played == False:
                        game_over_fx.play()
                        game_over_fx_played = True
                        
                    draw_bg()
                    player.update_animation()
                    player.draw()
                    
                    #plays death animation once dead
                    player.update_action(3)
                    player.rect.y -= 5                
                    
                    game_over_btn.draw()
                    #screen.fill(BLACK)
                    draw_text("Duration: "+ str(time_counter) +" s", font_score, WHITE, 380, 300)
                    draw_text("Coins: " + str(score), font_score, WHITE, 380, 260)
                    if quit_btn_3.draw():
                        run = False
                    if replay_btn_2.draw():
                        main_menu = False
                        pause_menu = False
                        reset_game()
                

        else:
            screen.fill(BLACK)
            paused_btn.draw()
            if quit_btn_2.draw():
                run = False
                
            if continue_btn.draw():
                pause_menu = False
                
            if replay_btn.draw():
                main_menu = False
                pause_menu = False
                reset_game()
                
    else:
        screen.fill(BLACK)
        if level_completed_fx_played == False:
            level_completed_fx.play()
            level_completed_fx_played = True
            
        
        level_complete_btn.draw()
        draw_text("Time completed: "+ str(time_counter) +" s", font_score, WHITE, 380, 300)
        draw_text("Coins collected: " + str(score), font_score, WHITE, 380, 260)
        if quit_btn_4.draw():
            run = False
        if replay_btn_3.draw():
            
            main_menu = False
            pause_menu = False
            level_complete = False
            reset_game()
    
        
    for event in pygame.event.get():
        # leave game
        if event.type == pygame.QUIT:
            run = False
        # get key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
                
            if event.key == pygame.K_d:
                moving_right = True
                
            if event.key == K_SPACE and game_over != -1:
                if player.on_ground == True:
                    player.jump()
                    jump_fx.play()
                    player.can_doublejump = True
                elif player.can_doublejump == True:
                    player.jump()
                    jump_fx.play()
                    player.can_doublejump = False

                
            if event.key == pygame.K_ESCAPE:
                if main_menu == False and game_over == 0:
                    pause_menu = True

        # once keyboard button is released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            
   
    pygame.display.update()

    
pygame.quit()
