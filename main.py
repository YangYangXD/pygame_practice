import random
import pygame
import os

FPS = 60

WIDTH = 500
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LBLUE = (0, 192, 255)
PINK = (255,0,224)

#初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("small game")
clock = pygame.time.Clock()

#載入圖片

os.chdir('sound')

bgimg = pygame.image.load(os.path.join("img", "background.png")).convert()

plimg = pygame.image.load(os.path.join("img", "player.png")).convert()

liveimg = pygame.transform.scale(plimg,(25,19))
liveimg.set_colorkey(BLACK)
pygame.display.set_icon(liveimg)

blimg = pygame.image.load(os.path.join("img", "bullet.png")).convert()

rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

expl_animation = {}
expl_animation['large'] = []
expl_animation['small'] = []
expl_animation['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_animation['large'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_animation['small'].append(pygame.transform.scale(expl_img,(40,40)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_animation['player'].append(player_expl_img)
    player_expl_img.set_colorkey(BLACK)

power_imgs = {}

power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()

power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

#載入音樂

os.chdir('sound')

shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
player_died = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [ pygame.mixer.Sound(os.path.join("sound","expl0.wav")) , pygame.mixer.Sound(os.path.join("sound","expl1.wav")) ]
pygame.mixer.music.load(os.path.join("sound","background.ogg"))
pygame.mixer.music.set_volume(0.5)

font_name = "font.ttf"

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(bgimg,(0,0))
    draw_text(screen, '太空生存戰!', 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, 'A D 移動飛船 空白鍵發射子彈~', 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, '按任意鍵開始遊戲~', 18, WIDTH/2, HEIGHT/4 *3)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


#飛船
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(plimg, (50,38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx


        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not(self.hidden):   
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx , self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left , self.rect.centery)
                bullet2 = Bullet(self.rect.right , self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT +500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()
#隕石
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0 , WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180 , -100)
        self.speedx = random.randrange(-3 , 3)
        self.speedy = random.randrange(2 , 5)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0 , WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100 , -40)
            self.speedx = random.randrange(-2 , 2)
            self.speedy = random.randrange(2 , 8)            
#子彈
class Bullet(pygame.sprite.Sprite):
    def __init__(self , x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = blimg
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top < 0:
            self.kill()
#爆炸動畫
class Explosion(pygame.sprite.Sprite):
    def __init__(self , center , size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_animation[self.size]):
                self.kill()
            else:
                self.image = expl_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
#掉落物
class Power(pygame.sprite.Sprite):
    def __init__(self , center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#bgm
pygame.mixer.music.play(-1)

#主迴圈
show_init = True
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(10):
            new_rock()
        score = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #畫面更新
    all_sprites.update()

    #rock bullet hit
    hits = pygame.sprite.groupcollide(rocks , bullets , True , True)
    for hit in hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'large')
        all_sprites.add(expl)
        if random.random() > 0.99:
            pows = Power(hit.rect.center)
            all_sprites.add(pows)
            powers.add(pows)
        new_rock() 

    #player rock hit
    hits = pygame.sprite.spritecollide(player , rocks , True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        player.health -= hit.radius * hit. speedy / 2
        expl = Explosion(hit.rect.center, 'small')
        all_sprites.add(expl)
        if player.health <= 0:
            dexpl = Explosion(player.rect.center, 'player')
            all_sprites.add(dexpl)
            player_died.play()
            player.lives -= 1
            player.health = 100
            player.hide()

    #player power hit
    hits = pygame.sprite.spritecollide(player , powers , True, pygame.sprite.collide_circle)
    for hit in hits:
        if hit.type == 'shield':
            player.health += 10
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play()


    if player.lives == 0 and not(dexpl.alive()):
        show_init = True

    #畫面
    screen.fill(BLACK)
    screen.blit(bgimg,(0,0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, liveimg, WIDTH - 100, 15)
    pygame.display.update()


pygame.quit()