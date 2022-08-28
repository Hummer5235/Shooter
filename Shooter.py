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

#Переменные действия игрока
moving_left = False
moving_right = False
shoot = False


#load images
#bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()

BG = (144,201,120)
RED = (255,0,0)



def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen,RED,(0,400),(SCREEN_WIDTH,400),3)

class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.star_ammo = ammo
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
            bullet = Bullet(self.rect.centerx + (self.rect.width * 0.3 * self.direction), self.rect.centery, self.direction)
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
            
        #Проверить столкновение с персонажами
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 25
                self.kill()
                print(player.health)
                
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                print(enemy.health)
                self.kill()


#Создание групп спрайтов
bullet_group = pygame.sprite.Group()



player = Soldier("player", 200, 300, 2, 5, 20)
enemy = Soldier("enemy", 300, 300, 2, 5, 20)

run = True
while run:
    draw_bg()
    player.draw()
    enemy.draw()
    player.update()
    enemy.update()

    #Обновление и отрисовка групп
    bullet_group.update()
    bullet_group.draw(screen)

    # Обновление действий игрока
    if player.alive:
        #Выстрелы пуль
        if shoot:
            player.shoot()

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
            if event.key == pygame.K_w and player.alive :
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()


        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False


    pygame.display.update()
    clock.tick(FPS)




