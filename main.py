import sys
import pygame
import os

explosion_list = []
img_folder = os.path.join(os.path.dirname(__file__), "exp")
HEIGHT = 800 
WITDH = 800 
bullets = pygame.sprite.Group()

class Game:

    def __init__(self):
        self.run = True
        self.screen_width = WITDH
        self.screen_height = HEIGHT
        self.image = pygame.image.load("sprites/background/background1.png")
        self.image = pygame.transform.scale(
            self.image, (self.screen_width, self.screen_height))
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))

        # all_sprites is used to update and draw all sprites together.
        self.all_sprites = pygame.sprite.Group()
        self.tanks = pygame.sprite.Group()

        # for collision detection with enemies.

        self.tank = Tank(100,100,0)
        self.tank1 = Tank(200,200,1)
        self.tanks.add(self.tank)
        self.tanks.add(self.tank1)
        self.all_sprites.add(self.tank)
        self.all_sprites.add(self.tank1)

        # загрузка ресурсов для игры
        for i in range(1, 9):
            filename = "explosion_{:d}.png".format(i)
            image = pygame.image.load(
                os.path.join(img_folder, filename)).convert()
            image.set_colorkey((0, 0, 0))
            explosion_list.append(image)

        # обнаружение столкновений
        hits = pygame.sprite.spritecollide(self.tank, bullets, False)
        if hits:
            player_explosion = Explosion(
                self.tank.rect.centerx, self.tank.rect.centery)
            self.all_sprites.add(player_explosion)
            self.tank.kill()

        hits = pygame.sprite.spritecollide(self.tank1, bullets, False)
        if hits:
            player_explosion = Explosion(
                self.tank1.rect.centerx, self.tank1.rect.centery)
            self.all_sprites.add(player_explosion)
            self.tank1.kill()

        # определяем окончание игры
        if not (self.tank.alive() or self.tank1.alive()) and not player_explosion.alive():
            self.run = False

    def handle_events(self):
        keys = pygame.key.get_pressed()
        self.tank.handle_events()
        self.tank1.handle_events()
        if self.tank1.k == 1: 
          if keys[pygame.K_UP]:
              self.tank1.move(-5)
          if keys[pygame.K_DOWN]:
              self.tank1.move(5)
        if self.tank.k == 0: 
          if keys[pygame.K_w]:
              self.tank.move(-5)
          if keys[pygame.K_s]:
              self.tank.move(5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.run = False
                if event.key == pygame.K_SPACE:
                    b = self.tank.shoot()
                    self.all_sprites.add(b)
                    bullets.add(b)
                if event.key == pygame.K_RCTRL:
                    b = self.tank1.shoot()
                    self.all_sprites.add(b)
                    bullets.add(b)
                    

    def update(self):
        # Calls `update` methods of all contained sprites.
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.image, (0, 0))
        self.all_sprites.draw(self.screen)  # Draw the contained sprites.
        pygame.display.update()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = explosion_list[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.index = 0
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 100:
            self.index += 1
            if self.index >= len(explosion_list):
                self.kill()
            else:
                self.image = explosion_list[self.index]


class Tank(pygame.sprite.Sprite):

    def __init__(self, x, y, k):
        self.k = k
        self.bullet_group = pygame.sprite.Group()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/player/player_tank{:d}.png".format(self.k))
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.org_image = self.image.copy()

        # A nicer way to set the start pos with `get_rect`.
        self.rect = self.image.get_rect(center=( x, y))

        self.angle = 0
        self.direction = pygame.Vector2(1, 0)
        self.pos = pygame.Vector2(self.rect.center)

    def handle_events(self):
        pressed = pygame.key.get_pressed()
        if self.k == 0:
          if pressed[pygame.K_a]:
              self.angle += 3
          if pressed[pygame.K_d]:
              self.angle -= 3

        if self.k == 1:
          if pressed[pygame.K_LEFT]:
              self.angle += 3
          if pressed[pygame.K_RIGHT]:
              self.angle -= 3

        self.image = pygame.transform.rotate(self.org_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, velocity):
        direction = pygame.Vector2(0, velocity).rotate(-self.angle)
        if (self.pos + direction)[0] > 0 and (self.pos + direction)[0] < WITDH:
            if (self.pos + direction)[1] > 0 and (self.pos + direction)[1] < HEIGHT:
                self.pos += direction

        self.rect.center = round(self.pos[0]), round(self.pos[1])

    def shoot(self):
      bullet = Bullet(self)
      self.bullet_group.add(bullet)
      return bullet

class Bullet(pygame.sprite.Sprite):

    def __init__(self, tank):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/bullet/bullet{:d}.png".format(tank.k))
        self.image = pygame.transform.scale(self.image, (16, 48))
        self.rect = self.image.get_rect()
        self.angle = tank.angle
        self.pos = pygame.Vector2(tank.pos)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.direction = pygame.Vector2(0, -10).rotate(-self.angle)
        self.image = pygame.transform.rotate(self.image, self.angle)
        
    def update(self):
        self.pos += self.direction
        self.rect.center = round(self.pos.x), round(self.pos.y)
        if self.rect.left < 0:
            self.kill()
            #self.direction.x *= -1
            #self.rect.left = 0
            #self.pos.x = self.rect.centerx
        if self.rect.right > WITDH:
            self.kill()
            #self.direction.x *= -1
            #self.rect.right = 800
            #self.pos.x = self.rect.centerx
        if self.rect.top < 0:
            self.kill()
            #self.direction.y *= -1
            #self.rect.top = 0
            #self.pos.y = self.rect.centery
        if self.rect.bottom > HEIGHT:
            self.kill()
            #self.direction.y *= -1
            #self.rect.right = 800
            #self.pos.y = self.rect.centery

def main():
    pygame.init()
    pygame.display.set_caption('Tank Game')
    clock = pygame.time.Clock()
    game = Game()

    while game.run:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)

if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()
