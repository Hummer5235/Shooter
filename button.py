import pygame

class Button():
    def __init__(self,x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image,((width * scale),(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False


    def draw(self, screen):
        action = False

        #Получить позицию мышки
        pos = pygame.mouse.get_pos()


        if self.rect.collidepoint(pos):
            #Рисовать выделение
            # pygame.draw.rect(screen,(0,0,0),(self.rect.x - 8, self.rect.y - 8, self.rect.width + 16, self.rect.height
            #                  +16 ))
            if pygame.mouse.get_pressed()[0] == True and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == False:
            self.clicked = False

        # Нарисовать кнопку
        screen.blit(self.image,(self.rect.x, self.rect.y))

        return action








