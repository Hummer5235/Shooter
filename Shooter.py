import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = (SCREEN_WIDTH*0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

#Установить частоту кадров
clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
TILE_SIZE = 40

#Переменные действия игрока
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


#load images
#bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
#grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
#pick up boxes
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade' :grenade_box_img
}


BG = (144,201,120)
RED = (255,0,0)

#Шрифт
font = pygame.font.Font('fonts/ChareInk/ChareInk-Bold.ttf', 30)




def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen,RED,(0,400),(SCREEN_WIDTH,400),3)

class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed, ammo , grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.star_ammo = ammo
        self.grenades = grenades
        self.shoot_cooldown = 0
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
        animation_types = ["Idle","Run","Jump","Death"]
        
        for animation in animation_types:
            temp_list = []
            #Найти количество объектов в папке
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img,(img.get_width() * scale,img.get_height()*scale  ))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center  = (x,y)

    def update_animation(self):
        #Обновление анимации
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self,new_action):
        # Если новое действие не равно старому, тогда поменять
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)
        # pygame.draw.rect(screen,RED,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),3)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.width * 0.6 * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #вычитание патронов
            self.ammo -= 1
            
            
        elif self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
    def update(self):
        self.update_animation()
        self.check_alive()
        
        

    def move(self,moving_left,moving_right):
        #Обнулить переменные перемещения
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.direction = -1
            self.flip = True

        if moving_right:
            dx = self.speed
            self.direction = 1
            self.flip = False

        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        dy += self.vel_y

        # Проверка столкновения с полом
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_air = False

        #Обновление позиции игрока
        self.rect.x += dx
        self.rect.y += dy
    
    
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.direction = 1
            self.update_action(3)
            

            
        
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type , x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[ self.item_type ]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2 , y + (TILE_SIZE - self.image.get_height()) )


    def update(self):
        #Проверить столкновение героя с боксами
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':

                player.health += 25
                if player.health >= player.max_health:
                    player.health = player.max_health


            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        #Движение пуль
        self.rect.x += self.speed * self.direction
        # Проверить зашла ли пуля за экран
        if self.rect.x < 0 or self.rect.x > 800:
            self.kill()
            
        #Проверить столкновение с главным игроком
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 25
                self.kill()
                print(player.health)
                
        #Проверить столкновение с врагами
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    print(enemy.health)
                    self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -13
        self.speed = 8
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        self.vel_y += GRAVITY
        
        dx = self.speed * self.direction
        dy = self.vel_y

        # Проверка столкновения с полом
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.speed = 0
            
            
        # Проверка столкновения со стенами
        if self.rect.x + dx <= 0 or self.rect.x + dx >= 800:
            self.direction *= -1
            
        
        # Применить смещение
        self.rect.x += dx
        self.rect.y += dy
        
        #Уменьшение таймера
        self.timer -= 1
        
        #Время кончилась, граната взрывается
        if self.timer <= 0 :
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)

            #Нанести урон , если кто-либо в области поражения
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2 and \
            abs(self.rect.centery - player.rect.centery) < TILE_SIZE*2 :
                #Отнять здоровье игрока
                player.health -= 50
                
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    # Отнять здоровье врага
                    enemy.health -= 50
                    
                    
            
        
    

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img,(img.get_width()*scale, img.get_height()*scale))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        
    def update(self):
        EXPLOSION_SPEED = 5
        
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            
        if self.frame_index >= len(self.images):
            self.kill()
        else:
            self.image = self.images[self.frame_index]
        
            
        
        
        

#Создание групп спрайтов
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()


item_box = ItemBox('Health' , 100, 360)
item_box_group.add(item_box)
item_box = ItemBox('Ammo' , 300, 360)
item_box_group.add(item_box)
item_box = ItemBox('Grenade' , 500, 360)
item_box_group.add(item_box)



player = Soldier("player", 200, 300, 2, 5, 20,3)
enemy = Soldier("enemy", 300, 300, 2, 5, 40, 0)
enemy_group.add(enemy)
enemy = Soldier("enemy", 600, 300, 2, 5, 40, 0)
enemy_group.add(enemy)



run = True
while run:

    draw_bg()
    player.draw()
    player.update()


    for enemy in enemy_group:
        enemy.update()
        enemy.draw()
    

    #Обновление и отрисовка групп
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)

    # Обновление действий игрока
    if player.alive:
        #Выстрелы пуль
        if shoot:
            player.shoot()
        elif grenade and grenade_thrown == False and player.grenades > 0 :
            # Создать гранату
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0]* player.direction),\
                                player.rect.top, player.direction)
            grenade_group.add(grenade)

            player.grenades -= 1 # Уменьшить количество гранат
            grenade_thrown = True
            

        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

        player.move(moving_left,moving_right)
    


    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive :
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()


        # Отпустили нажатые клавиши
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade= False
                grenade_thrown = False
                
        
        
        

    pygame.display.update()
    clock.tick(FPS)



