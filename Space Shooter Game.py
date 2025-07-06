import pygame 
from os.path import join
from random import randint, uniform

# Player class to handle the spaceship logic
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('space shooter', 'images', 'player.png')).convert_alpha()  # load the player image
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))  # place it in the middle of screen
        self.direction = pygame.Vector2()  # default no movement
        self.speed = 300  # movement speed

        # shooting cooldown setup
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400  # ms

        # mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        # check if enough time passed to shoot again
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        # player movement
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])  
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt  # apply movement

        # shooting lasers
        recent_keys = pygame.key.get_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))  # spawn laser
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

# just some background stars for aesthetics
class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = (randint(0, WINDOW_WIDTH),randint(0, WINDOW_HEIGHT)))

# laser class for bullets that go upward
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_rect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt  # move up
        if self.rect.bottom < 0:  # delete if off screen
            self.kill()

# meteors that fall from the top of the screen
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000  # how long meteor lasts in ms
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)  # mostly down, a bit sideways
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt  # move
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()  # time’s up, remove meteor

        # spin the meteor
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

# shows animation when laser hits meteor
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames  # list of images
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 20 * dt  # speed up animation
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()  # done animating, remove sprite

# collision detection for player and laser
def collisions():
    global running 

    # check if player collides with any meteors
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False  # end game
    
    # check if any lasers hit meteors
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

# shows timer on screen
def display_score():
    current_time = pygame.time.get_ticks() // 100  # makes it shorter
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

# --- main game setup ---

# initialize pygame
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Timbit travels')
running = True
clock = pygame.time.Clock()

# load images and audio
star_surf = pygame.image.load(join('space shooter', 'images', 'star.png' )).convert_alpha()
meteor_surf = pygame.image.load(join('raccoonhead.png')).convert_alpha()
laser_surf = pygame.image.load(join('timbit.png')).convert_alpha()
font = pygame.font.Font(join('space shooter', 'images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('space shooter', 'images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('space shooter', 'audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('space shooter', 'audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('space shooter', 'audio', 'game_music.wav'))
game_music.set_volume(0.4)
# game_music.play(loops= -1)  # uncomment to play music

# sprite groups to manage things
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# make 20 stars to look cool :p
for i in range(20):
    Star(all_sprites, star_surf) 

# make player
player = Player(all_sprites)

# meteor spawner event (fires every 200ms)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 200)

# --- main game loop ---
while running:
    dt = clock.tick() / 1000  # get delta time

    # check for events like quit or spawn meteor
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)  # spawn off-screen top
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # update all sprites
    all_sprites.update(dt)

    # check for c  o llisions
    collisions()   

    # draw everything
    display_surface.fill("#150053")  # dark purple bg
    display_score()  # show score
    all_sprites.draw(display_surface)
    pygame.display.update()

# exit the game
pygame.quit()
 