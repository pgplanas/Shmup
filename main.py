# Shmup! game
import pygame
import random
from os import path
import math

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 480
HEIGHT = 600
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
POWERUP_TIME = 5000

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shmup!')
clock = pygame.time.Clock()

#font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    # font = pygame.font.Font(font_name, size)
    font = pygame.font.Font(path.join(img_dir, 'Gameover.ttf'), size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surface, x, y, shield_value):
    color = GREEN
    if shield_value < 0:
        shield_value = 0
    elif shield_value < 25:
        color = RED
    elif shield_value < 50:
        color = YELLOW
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = shield_value / 100 * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 1)

def draw_lives(surface, x, y, lives, img):
    for i in range (lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 54))
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius )
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hidden_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        # check powerup timer
        if self.power >= 2 and pygame.time.get_ticks() - self.power_timer > POWERUP_TIME:
            self.power -= 1
            if self.power < 1:
                self.power = 1
            self.power_timer = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hidden_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_LEFT] and keystate[pygame.K_RIGHT]:
            self.speedx = 0
        if self.rect.right + self.speedx > WIDTH:
            self.rect.right = WIDTH
            self.speedx = 0
        if self.rect.left + self.speedx < 0:
            self.rect.left = 0
            self.speedx = 0
        self.rect.x += self.speedx
        if keystate[pygame.K_SPACE]:
            self.shoot()

    def powerup(self):
        self.power += 1
        self.power_timer = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
            elif self.power >= 3:
                bullet1 = Bullet(self.rect.centerx, self.rect.y)
                bullet2 = Bullet(self.rect.right, self.rect.centery, 0.5, 0.866)
                bullet3 = Bullet(self.rect.left, self.rect.centery, -0.5, 0.866)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet3)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet3)
                shoot_sound.play()


    def hide(self):
        self.hidden = True
        self.hidden_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
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
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-160, -120)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed =  random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left > WIDTH + 20 or self.rect.right < -25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-160, -120)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=0, vy=1):
        pygame.sprite.Sprite.__init__(self)
        self.angle = math.atan(vx / vy) / math.pi * 180
        self.image = pygame.transform.scale(bullet_img, (13, 54))
        self.image = pygame.transform.rotate(bullet_img, -self.angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10
        self.speedy = -self.speed * vy
        self.speedx = self.speed * vx

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # kill it if it goes out of the screen
        if self.rect.bottom < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        # kill it if it goes out of the screen
        if self.rect.bottom > HEIGHT:
            self.kill()

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHUMP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys to move, space to fire", 24, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 24, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# load all game graphics
background = pygame.image.load(path.join(img_dir, 'bg.png')).convert()
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_dir, 'X-Wing_Top_View.png')).convert_alpha()
print(player_img.get_width())
player_mini_img = pygame.transform.scale(player_img, (25, 27)).convert_alpha()

meteor_images = []
meteor_list = ['meteorBrown_big1.png',
               'meteorBrown_big2.png',
               'meteorBrown_med1.png',
               'meteorBrown_med3.png',
               'meteorBrown_small1.png',
               'meteorBrown_small2.png',
               'meteorBrown_tiny1.png'
               ]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert_alpha())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = f'regularExplosion0{i}.png'
    img = pygame.image.load(path.join(img_dir, filename)).convert_alpha()
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    filename = f'sonicExplosion0{i}.png'
    img = pygame.image.load(path.join(img_dir, filename)).convert_alpha()
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert_alpha()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert_alpha()

bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert_alpha()

# load all sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'Laser_Shoot.wav'))
shoot_sound.set_volume(0.2)
expl_sounds = []
for snd in ['Explosion1.wav', 'Explosion2.wav']:
    tmp_snd = pygame.mixer.Sound(path.join(snd_dir, snd))
    tmp_snd.set_volume(0.3)
    expl_sounds.append(tmp_snd)
pygame.mixer.music.load(path.join(snd_dir, 'music.wav'))
pygame.mixer.music.set_volume(0.4)


pygame.mixer.music.play(loops=-1)

# game loop
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        score = 0

        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()


    # keep loop running at the right speed
    clock.tick(FPS)

    # process input
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # update
    all_sprites.update()

    # check collisions
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()
        random.choice(expl_sounds).play()

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            expl_sounds[1].play()
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    # check to see if player got the powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += 20
            if player.shield >= 100:
                player.shield = 100

        if hit.type == 'gun':
            player.powerup()


    # if the player dies and the explosion has finish
    if player.lives == 0 and not death_explosion.alive():
        game_over = True


    # draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    """for sprite in all_sprites:
        pygame.draw.rect(screen, WHITE, sprite.rect, 3)"""
    draw_text(screen, str(score), 36, WIDTH / 2, 10)
    pygame.display.flip()

pygame.quit()