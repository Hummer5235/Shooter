#Сбор предметов
import pygame
import os
import random
import csv
import button

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH*0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),)
pygame.display.set_caption("Shooter")

#set framerate
clock = pygame.time.Clock()
FPS = 60

#Определим игровые переменны
SCROLL_THRESH = 200 # Начало прокрутки экрана
screen_scroll = 0 # Прокрутка экрана
bg_scroll = 0 # Прокрутка фона
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 0
start_game = False
MAX_LEVELS = 3



#player action variable
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#Загрузка изображений
#Изображения кнопок
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

#Изображения фона
pine1_img = pygame.image.load('img/background/pine1.png')
pine2_img = pygame.image.load('img/background/pine2.png')
mountain_img = pygame.image.load('img/background/mountain.png')
sky_img = pygame.image.load('img/background/sky_cloud.png')

#Список плиток для уровня
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)

#bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
#grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
#pick up boxes
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes = {
    "Health" : health_box_img,
    "Ammo"   : ammo_box_img,
    "Grenade": grenade_box_img
}


#define colours
BG = (144,201,120)
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)

#define font
font = pygame.font.SysFont("Futura",30)

def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))



def draw_bg():
    screen.fill((BG))
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img,((x*width)-bg_scroll*0.2,0))
        screen.blit(mountain_img,((x*width)-bg_scroll*0.3,200))
        screen.blit(pine1_img,((x*width)-bg_scroll*0.5,300))
        screen.blit(pine2_img,((x*width)-bg_scroll*0.7,350))
    # pygame.draw.line(screen,RED,(0,400),(SCREEN_WIDTH,400),3)

# Функция перезагрузки уровня
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #Создать пустой спиок
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo,grenades) :
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #ИИ специальные переменные
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False # Ожидание
        self.idle_counter = 0 # Счетчик ожидания

        animation_types = ["Idle","Run","Jump","Death"]

        for animation in animation_types:
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * scale , img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self,moving_left,moving_right):
        #Пересоздать переменные движения
        screen_scroll = 0
        dx = 0
        dy = 0
        #assign movement variables is moving left or right

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False :
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        dy += self.vel_y

        # #Проверить столкновение с полом
        # if self.rect.bottom + dy > 400:
        #     dy = 400 - self.rect.bottom
        #     self.in_air = False

        #Проверка столкновения со списком препятствий
        for tile in world.obstacle_list:
            #Проверим столкновение по x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y,self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0

            #Проверим столкновение по y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #Проверка касания земли снизу, прыжок вверх
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = 0
                # Проверка касания земли сверху , падение
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = 0

        #Ограничение края экрана для героя
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0


        #Обновить позицию прямоугольника
        self.rect.x += dx
        self.rect.y += dy

        #Проверка на столкновение с водой
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #Проверка на столкновение табличкой выхода
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #Проверка на падение ниже земли
        if self.rect.bottom > SCREEN_HEIGHT + 100:
            self.health = 0

        #Обновить scroll с помощью позиции игрока
        if self.char_type == 'player':
            if (self.rect.right >= SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE)-SCREEN_WIDTH   )\
                    or self.rect.left <= SCROLL_THRESH and bg_scroll > 0 :
                self.rect.x -= dx
                screen_scroll = -dx



        return screen_scroll, level_complete








    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            #if the animation has run out the reset back to the start
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action])-1
                else:
                    self.frame_index = 0


    def update_action(self,new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0 :
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo >0 :
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.width * 0.75 * self.direction), self.rect.centery+2,self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1

    def ai(self):
        if player.alive and self.alive:
            if self.idling==False and random.randint(1,200) == 1: # Если совпало число
                self.update_action(0) # Сменить анимацию
                self.idling = True  #Ожидание работает
                self.idle_counter = 50 # Установить счетчик

            # Если ИИ обнаружил игрока
            if self.vision.colliderect(player):

                #Остановиться
                self.update_action(0)
                #Стрелять
                self.shoot()


            else:
                if self.idling == False: #Ожидание выключено, враг бегает
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False

                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)

                    #Увеличиваем счетчик
                    self.move_counter += 1

                    if self.move_counter > TILE_SIZE:
                        self.move_counter *= -1
                        self.direction *= -1

                    self.update_action(1)

                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery )
                    # pygame.draw.rect(screen, BLACK,self.vision,1)

                # Ожидание включено, враг стоит на месте
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        print(self.level_length)# Узнаем длину одной строки
        #Переберем файл с информацией уровня
        for y, row in enumerate(data):
            for x, tile in enumerate(row):

                if tile>= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img, img_rect)

                    #Проверка значения плитки
                    #Если земля добавить в список препятствий
                    if tile >=0 and tile<=8:
                        self.obstacle_list.append(tile_data)

                    elif tile == 9 or tile == 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)

                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 4, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)

                    elif tile == 16:
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 0)
                        enemy_group.add(enemy)

                    elif tile == 17: # Создать Ammobox
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE  )
                        item_box_group.add(item_box)

                    elif tile == 18: # Создать Grenadebox

                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)


                    elif tile == 19:  # Создать Healthbox
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)


        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])



class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll




class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))



    def update(self):
        #check if the player has picked up the box
        #scroll
        self.rect.x += screen_scroll

        if pygame.sprite.collide_rect(self,player):
            #check what kind of box it was
            if self.item_type == "Health":

                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            if self.item_type == "Ammo":
                player.ammo+= 15
            if self.item_type == "Grenade":
                player.grenades += 3
            #delete the item box
            self.kill()

class HealthBar():
    def __init__(self,x,y,health,max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self,health):
        #update  with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(screen,RED,(self.x, self.y, 150, 20))
        pygame.draw.rect(screen,GREEN,(self.x, self.y, 150 * ratio, 20))






class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction*self.speed)
        #check if bullet has gone off screen
        if self.rect.right<0 or self.rect.left > SCREEN_WIDTH :
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self):
                self.kill()


        #check collision with characters
        if pygame.sprite.spritecollide(player,bullet_group,False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy,bullet_group,False):
                if enemy.alive:
                    enemy.health -= 25

                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.speed * self.direction
        dy = self.vel_y

        # # check collision with floor
        # if self.rect.bottom + dy > 400:
        #     dy = 400 - self.rect.bottom
        #     self.speed = 0

        # check collision with walls
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.speed * self.direction

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0

                # Проверка касания нижней части земли
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = 0
                # Проверка касания земли сверху , падение гранаты
                elif self.vel_y >= 0:
                    self.vel_y = 0





        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x,self.rect.y,1)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx-player.rect.centerx) < TILE_SIZE *2 and \
                abs(self.rect.centery-player.rect.centery) < TILE_SIZE *2:
                player.health -= 50

            for enemy in enemy_group:

                if abs(self.rect.centerx-enemy.rect.centerx) < TILE_SIZE *2 and \
                    abs(self.rect.centery-enemy.rect.centery) < TILE_SIZE *2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.rect.x += screen_scroll
        #update explosion animation
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]



#Создание кнопок
start_button = button.Button(SCREEN_WIDTH // 2 - 130 , SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110 , SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100 , SCREEN_HEIGHT // 2 - 50, restart_img, 2)


#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()








#Создадим пустой список плиток
world_data = []

for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#Загрузить данные уровня и создать мир
with open(f'level{level}_data.csv',newline='') as csvfile:
    reader = csv.reader(csvfile,delimiter = ',' )
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:
        # Если игра еще не началась, то рисуем главное меню
        if start_game == False:
            # Главное меню
            screen.fill(BG)
            # Кнопки

            if start_button.draw(screen):
                start_game = True
            if exit_button.draw(screen):
                run = False

        else:

            draw_bg()
            #show player health
            health_bar.draw(player.health)
            world.draw()
            #show ammo
            draw_text(f"AMMO:",font,WHITE,10,35)
            for x in range(player.ammo):
                screen.blit(bullet_img,(90 + (x * 10),35))

            # show grenades
            draw_text(f"GRENADES:", font, WHITE, 10, 60)
            for x in range(player.grenades):
                screen.blit(grenade_img,(135 + (x * 15), 60))

            player.update()
            player.draw()
            #Для каждого врага в группе
            for enemy in enemy_group:
                enemy.update()
                enemy.draw()
                enemy.ai()


            #update and draw groups
            bullet_group.update()
            grenade_group.update()
            explosion_group.update()
            item_box_group.update()
            decoration_group.update()
            water_group.update()
            exit_group.update()
            bullet_group.draw(screen)
            grenade_group.draw(screen)
            explosion_group.draw(screen)
            item_box_group.draw(screen)
            decoration_group.draw(screen)
            water_group.draw(screen)
            exit_group.draw(screen)


            if player.alive:
                #shoot bullets
                if shoot:
                    player.shoot()
                #throw grenades
                elif grenade and grenade_thrown == False and player.grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                                      player.rect.top,player.direction)
                    grenade_group.add(grenade)
                    #reduce grenades
                    player.grenades -= 1
                    grenade_thrown = True

                if player.in_air:
                    player.update_action(2)
                elif moving_left or moving_right:
                    player.update_action(1) #1 run
                else:
                    player.update_action(0) #0 idle

            #Игрок не жив
            else:
                screen_scroll= 0
                if restart_button.draw(screen):
                    bg_scroll = 0
                    world_data = reset_level()
                    # Загрузить данные уровня и создать мир
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)


            screen_scroll, level_complete = player.move(moving_left,moving_right)
            bg_scroll -= screen_scroll # Для перемещения фона

            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Загрузить данные уровня и создать мир
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)





        for event in pygame.event.get():
            #quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            #keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

            #keyboard button released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_q:
                    grenade = False
                    grenade_thrown = False


        pygame.display.update()
        clock.tick(FPS)


