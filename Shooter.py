import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = (SCREEN_WIDTH*0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

#Установить частоту кадров
clock = pygame.time.Clock()
FPS = 60

#Переменные действия игрока
moving_left = False
moving_right = False

BG = (144,201,120)

def draw_bg():
    screen.fill(BG)

class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(5):
            img = pygame.image.load(f"img/{self.char_type}/Idle/{i}.png").convert_alpha()
            img = pygame.transform.scale(img,(img.get_width() * scale,img.get_height()*scale  ))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(6):
            img = pygame.image.load(f"img/{self.char_type}/Run/{i}.png").convert_alpha()
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
                self.frame_index = 0

    def update_action(self,new_action):
        # Если новое действие не равно старому, тогда поменять
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

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

        #обновление позиции игрока
        self.rect.x += dx
        self.rect.y += dy




player = Soldier("player",200,300,2,5)
enemy = Soldier("enemy",300,300,2,5)

run = True
while run:
    draw_bg()
    player.draw()
    enemy.draw()

    # Обновление действий игрока
    if moving_left or moving_right:
        player.update_action(1)
    else:
        player.update_action(0)

    player.move(moving_left,moving_right)
    player.update_animation()


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
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False


    pygame.display.update()
    clock.tick(FPS)




