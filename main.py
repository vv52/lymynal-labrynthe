import pygame
from pygame.locals import *
from time import time
from datetime import datetime, timedelta
import json
import sys

# Define FPS
FPS = 60                            # Cap at 60 FPS

# Define screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Define physics values
ACC = 0.6                           # Set player acceleration constant
FRIC = -0.12                        # Set friction constant
GRAV = 0.45                         # Set gravitational acceleration constant
JUMP = -12                          # Set jump velocity constant
JUMP_MIN = -3                       # Set minimum jump velocity
JUMP_WINDOW = 6                     # Set frame window where jump can be performed after falling off platform
MAX_FALL_SPEED = 14                 # This prevents a glitch where player moves through floor before check

# Define RGB color primitives
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Define global arrays
TileArray = []                      # Define array that stores all bounding objects
HazardArray = []                    # Define array that stores objects dangerous to player
StageExitArray = []                 # Define array that stores stage_exit objects
CollectibleArray = []               # Define array that stores collectible objects
RespawnPointArray = []              # Define array that stores respawn point objects
SpikeArray = []                     # Define array that stores spikes that are harmful to falling player
SlowArray = []                      # Define array that stores objects that slow the player
DecorativeArray = []                # Define array that stores decorative objects
LockArray = []
LockLeafArray = []
KeyArray = []
SpecialKeyArray = []
SecretDoorArray = []
TombstoneArray = []
GutsArray = []
ChestArray = []
ReturnArray = []
FloatArray = []
EyeArray = []
RingArray = []
SwordArray = []
FinalDoorArray = []

# Definitions for convenience
vec = pygame.math.Vector2           # Defining simple reference to Vector2
SK1_COINS = 35
SK2_COINS = 94
FINAL_COINS = 158
has_sk1 = False
has_sk2 = False
has_ring = False
has_sword = False
has_xcancel = False
returned = False


# Overriding sprite class to make other classes more atomic
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, spawn_x, spawn_y):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = [spawn_x, spawn_y]
        self.num_jumps = 0

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/player.bmp", spawn_x, spawn_y)
        self.pos = vec((spawn_x, spawn_y))
        self.vel = vec((0, 0))
        self.acc = vec((0, 0))
        self.air = 0                    # Manual frame timer for forgiving jump mechanic [see: JUMP_WINDOW]

    def move(self):
        self.acc = vec(0, GRAV)

        # Check for LEFT / RIGHT key presses
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.acc.x = -ACC
        if keys[K_RIGHT]:
            self.acc.x = ACC
        if keys[K_DOWN]:
            if has_xcancel:
                self.vel.x = 0

        # Handle movement and gravity
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.pos.y += self.vel.y + 0.5 * self.acc.y

        # Handle bounds checking and screen wrap
        if self.pos.x + 24 > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH - 24
        if self.pos.x < 24:
            self.pos.x = 24
        if self.pos.y < 32:
            self.pos.y = 32
            self.vel.y = 0

        # Ensure rect is synced with player pos
        self.rect.midbottom = self.pos

    def jump(self, jump_fx):
        if self.air < JUMP_WINDOW:          # No double jumps
            self.vel.y = JUMP
            jump_fx.play()
            self.num_jumps += 1

    def cancel_jump(self):
        if self.air > 0:
            if self.vel.y < JUMP_MIN:       # Cap vertical velocity to cancel jump
                self.vel.y = JUMP_MIN

    def update(self, obstacles, hazards, stage_exit, collectibles, respawn_point,
               spikes, slow, keys, skeys, sdoors, chests, returns, rings, swords, fdoors):
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED
        self.move()
        on_ground = False

        # Handle jumping vertical collision detection
        hits = pygame.sprite.spritecollide(self, obstacles, False)   # Get all collisions (player->wall)
        if self.vel.y > 0:                                      # If player is falling
            if hits:                                            # && if collision is detected
                if self.pos.y < hits[0].rect.bottom:            # && player is beneath top edge of wall
                    self.pos.y = hits[0].rect.top + 1           # Move player above wall
                    self.vel.y = 0                              # Set player vertical velocity to zero
                    self.air = 0                                # Specify that player is no longer jumping
                    on_ground = True
        if not on_ground:                                       # Add to airtime frame counter
            self.air += 1

        hazard_hit = pygame.sprite.spritecollideany(self, hazards)
        if hazard_hit:
            return 1

        exit_hit = pygame.sprite.spritecollideany(self, stage_exit)
        if exit_hit:
            return 2

        coin_hit = pygame.sprite.spritecollide(self, collectibles, True)
        if coin_hit:
            return 3

        respawn_hit = pygame.sprite.spritecollide(self, respawn_point, True)
        if respawn_hit:
            return 4

        spike_hit = pygame.sprite.spritecollide(self, spikes, False)
        if self.vel.y > 0:
            if spike_hit:
                return 1

        slow_hit = pygame.sprite.spritecollide(self, slow, False)
        if slow_hit:
            return 5

        key_hit = pygame.sprite.spritecollide(self, keys, True)
        if key_hit:
            return 6

        skey_hit = pygame.sprite.spritecollide(self, skeys, True)
        if skey_hit:
            return 7

        chest_hit = pygame.sprite.spritecollide(self, chests, True)
        if chest_hit:
            return 8

        sdoor_hit = pygame.sprite.spritecollide(self, sdoors, False)
        if sdoor_hit:
            return 9

        return_hit = pygame.sprite.spritecollide(self, returns, False)
        if return_hit:
            return 10

        ring_hit = pygame.sprite.spritecollide(self, rings, True)
        if ring_hit:
            return 11

        sword_hit = pygame.sprite.spritecollide(self, swords, True)
        if sword_hit:
            return 12

        fdoor_hit = pygame.sprite.spritecollide(self, fdoors, False)
        if fdoor_hit and has_sword:
            return 13

        return 0


class Wall(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/wall.bmp", spawn_x, spawn_y)


class Wall2(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/wall2.bmp", spawn_x, spawn_y)


class Wall3(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/wall3.bmp", spawn_x, spawn_y)


class Platform(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/platform.bmp", spawn_x, spawn_y)


class BadLeaf(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/badleaf.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                   # Simple animation by swapping image every 30 frames
        if self.frame_timer == 30:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/badleaf.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/badleaf2.bmp")

            if self.ticker == 1000:             # Lazy insurance against overflow exception
                self.ticker = 0


class Exit(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/exit.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                   # Simple animation by swapping image every 15 frames
        if self.frame_timer == 30:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker == 1:
                self.image = pygame.image.load("res/img/exit.bmp")
            if self.ticker == 8:
                self.image = pygame.image.load("res/img/exit2.bmp")
                self.ticker = 0


class Coin(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/coin1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                         # Simple animation by swapping image every 5 frames
        if self.frame_timer == 5:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 4: self.ticker = 1
            self.image = pygame.image.load(f"res/img/coin{self.ticker}.bmp")


class Respawn(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/respawn1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                        # Simple animation by swapping image every 10 frames
        if self.frame_timer == 10:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 4: self.ticker = 1
            self.image = pygame.image.load(f"res/img/respawn{self.ticker}.bmp")


class Grass(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/grass.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                       # Simple animation by swapping image every 15 frames
        if self.frame_timer == 15:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/grass.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/grass2.bmp")

            if self.ticker == 1000:                 # Lazy insurance against overflow exception
                self.ticker = 0


class Bush(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/bush.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1                       # Simple animation by swapping image every 30 frames
        if self.frame_timer == 30:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/bush.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/bush2.bmp")

            if self.ticker == 1000:                 # Lazy insurance against overflow exception
                self.ticker = 0


class Spike(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/spike2.bmp", spawn_x, spawn_y)


class LockLeaf(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/lockleaf.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 30 frames
        if self.frame_timer == 30:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/lockleaf.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/lockleaf2.bmp")

            if self.ticker == 1000:  # Lazy insurance against overflow exception
                self.ticker = 0


class Lock(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/lock.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 30 frames
        if self.frame_timer == 30:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/lock.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/lock2.bmp")

            if self.ticker == 1000:  # Lazy insurance against overflow exception
                self.ticker = 0


class Key(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/key1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 10 frames
        if self.frame_timer == 10:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 5: self.ticker = 1
            self.image = pygame.image.load(f"res/img/key{self.ticker}.bmp")


class SecretDoor(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/secretdoorclosed.bmp", spawn_x, spawn_y)

    def update(self):
        if has_sk1:
            self.image = pygame.image.load("res/img/secretdooropen.bmp")


class SecretDoor2(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/secretdoorclosed.bmp", spawn_x, spawn_y)

    def update(self):
        if has_sk2:
            self.image = pygame.image.load("res/img/secretdooropen.bmp")


class SpecialKey(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/specialkey1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 10 frames
        if self.frame_timer == 10:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 4: self.ticker = 1
            self.image = pygame.image.load(f"res/img/specialkey{self.ticker}.bmp")


class SpecialKey2(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/specialkey1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 10 frames
        if self.frame_timer == 10:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 4: self.ticker = 1
            self.image = pygame.image.load(f"res/img/specialkey{self.ticker}.bmp")


class Chest(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/chest.bmp", spawn_x, spawn_y)


class Tombstone(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/rip.bmp", spawn_x, spawn_y)


class BrokenTombstone(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/broken.bmp", spawn_x, spawn_y)


class Guts(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/guts.bmp", spawn_x, spawn_y)


class ReturnDoor(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/returndoor.bmp", spawn_x, spawn_y)


class SWall(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/swall.bmp", spawn_x, spawn_y)


class FloatingPlatform(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/float.bmp", spawn_x, spawn_y)
        self.x = spawn_x
        self.y = spawn_y
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < 32:
            self.speed *= -1
        if self.rect.x > SCREEN_WIDTH - 48:
            self.speed *= -1


class EyeEnemy(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/eye.bmp", spawn_x, spawn_y)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT - 32:
            self.rect.y = SCREEN_HEIGHT / 2


class EyeEnemyInvert(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/eye.bmp", spawn_x, spawn_y)
        self.speed = 3

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 16:
            self.rect.y = SCREEN_HEIGHT - 32


class Ring(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/ring1.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 10 frames
        if self.frame_timer == 10:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker > 3: self.ticker = 1
            self.image = pygame.image.load(f"res/img/ring{self.ticker}.bmp")


class Sword(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/sword.bmp", spawn_x, spawn_y)
        self.frame_timer = 0
        self.ticker = 0

    def update(self):
        self.frame_timer += 1  # Simple animation by swapping image every 20 frames
        if self.frame_timer == 20:
            self.frame_timer = 0
            self.ticker += 1
            if self.ticker % 2 == 0:
                self.image = pygame.image.load("res/img/sword.bmp")
            if self.ticker % 2 == 1:
                self.image = pygame.image.load("res/img/sword2.bmp")

            if self.ticker == 1000:  # Lazy insurance against overflow exception
                self.ticker = 0


class FinalDoor(Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__("res/img/fdoorclosed.bmp", spawn_x, spawn_y)

    def update(self):
        if has_sword:
            self.image = pygame.image.load("res/img/fdoor3.bmp")

def load_names():
    with open("res/levels/names.json") as json_file:
        data = json.load(json_file)
    return data


def load_stage(filename, obstacles, hazards, stage_exit, collectibles, respawn,
               spikes, slow, decorative, locks, lockleafs, keys, skeys, sdoors,
               tombstones, chests, returns, floats, coins, current_stage, rings,
               swords, fdoors):
    with open(filename, 'r') as file:               # Open specified text file
        stage = file.read()
    x_count = 0                                     # Create coordinates to traverse screen
    y_count = 0
    x_pos_str = stage[0:3]
    y_pos_str = stage[3:6]
    global returned
    if stage[7] == 'x':
        return vec(-1, -1)
    else:
        for tile in stage[7:]:                              # Step through file and interpret delimiters
            if tile == ',':
                x_count += 16
                if x_count >= SCREEN_WIDTH:
                    x_count = 0
            if tile == '\n':
                y_count += 16
            if tile == '1':                             # Create wall at current (x,y) location
                if current_stage < 10:
                    new_wall = Wall(x_count + 8, y_count + 8)
                elif current_stage < 18:
                    new_wall = Wall2(x_count + 8, y_count + 8)
                else:
                    new_wall = Wall3(x_count + 8, y_count + 8)
                obstacles.append(new_wall)
            if tile == '2':                             # Create platform at current (x,y) location
                new_platform = Platform(x_count + 8, y_count + 8)
                obstacles.append(new_platform)
            if tile == '3':                             # Create hazard at current (x,y) location
                new_leaf = BadLeaf(x_count + 8, y_count + 8)
                hazards.append(new_leaf)
            if tile == '4':                             # Create stage exit at current (x,y) location
                new_exit = Exit(x_count + 8, y_count + 8)
                stage_exit.append(new_exit)
            if tile == '5' and not returned:                             # Create coin at current (x,y) location
                new_coin = Coin(x_count + 8, y_count + 8)
                collectibles.append(new_coin)
            if tile == '6':                             # Create respawn point at current (x,y) location
                new_respawn = Respawn(x_count + 8, y_count + 8)
                respawn.append(new_respawn)
            if tile == '7':                             # Create grass at current (x,y) location
                new_grass = Grass(x_count + 8, y_count + 8)
                decorative.append(new_grass)
            if tile == '8':                             # Create bush at current (x,y) location
                new_bush = Bush(x_count + 8, y_count + 8)
                slow.append(new_bush)
            if tile == '9':
                new_spike = Spike(x_count + 8, y_count + 8)
                spikes.append(new_spike)
            if tile == 'L':
                new_lock = Lock(x_count + 8, y_count + 8)
                locks.append(new_lock)
            if tile == 'l':
                new_lockleaf = LockLeaf(x_count + 8, y_count + 8)
                lockleafs.append(new_lockleaf)
            if tile == 'K':
                new_key = Key(x_count + 8, y_count + 8)
                keys.append(new_key)
            if tile == 's':
                if current_stage == 6 and coins >= SK1_COINS:
                    new_skey = SpecialKey(x_count + 8, y_count + 8)
                    skeys.append(new_skey)
                if current_stage > 6 and coins >= SK2_COINS:
                    new_skey = SpecialKey2(x_count + 8, y_count + 8)
                    skeys.append(new_skey)
            if tile == 'D':
                if current_stage == 7:
                    new_sdoor = SecretDoor(x_count + 8, y_count + 8)
                    sdoors.append(new_sdoor)
                if current_stage > 7:
                    new_sdoor = SecretDoor2(x_count + 8, y_count + 8)
                    sdoors.append(new_sdoor)
            if tile == 'r':
                new_rip = Tombstone(x_count + 8, y_count + 8)
                tombstones.append(new_rip)
            if tile == 'G':
                new_guts = Guts(x_count + 8, y_count + 8)
                slow.append(new_guts)
            if tile == 'C':
                new_chest = Chest(x_count + 8, y_count + 8)
                chests.append(new_chest)
            if tile == 'B':
                new_return = ReturnDoor(x_count + 8, y_count + 8)
                returns.append(new_return)
            if tile == 'w':
                new_swall = SWall(x_count + 8, y_count + 8)
                obstacles.append(new_swall)
            if tile == 'F':
                new_float = FloatingPlatform(x_count + 8, y_count + 8)
                floats.append(new_float)
            if tile == 'R':
                new_ring = Ring(x_count + 8, y_count + 8)
                rings.append(new_ring)
            if tile == 'E':
                new_eye = EyeEnemy(x_count + 8, y_count + 8)
                hazards.append(new_eye)
            if tile == 'I':
                new_eye = EyeEnemyInvert(x_count + 8, y_count + 8)
                hazards.append(new_eye)
            if tile == 'b':
                new_brip = BrokenTombstone(x_count + 8, y_count + 8)
                tombstones.append(new_brip)
            if tile == 'S':
                if has_ring:
                    new_sword = Sword(x_count + 8, y_count + 8)
                    swords.append(new_sword)
            if tile == 'f':
                new_fdoor = FinalDoor(x_count + 16, y_count + 24)
                fdoors.append(new_fdoor)
        return vec(int(x_pos_str), int(y_pos_str))


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=1)    # | pygame.SCALED
    bigscreen = False
    pygame.display.set_caption("Lymynal Labrynthe")   # Assign name to window
    game_icon = pygame.image.load("res/img/icon.png")
    pygame.display.set_icon(game_icon)
    clock = pygame.time.Clock()                     # Clock for syncing updates to frame rate
    stage_loaded = False                            # Defining bool to ensure stage is loaded
    current_stage = 0                               # Defining int to keep track of current stage
    player_deaths = 0                               # Defining int to keep track of player deaths
    coins = 0                                       # Defining int to keep track of collected coins
    total_jumps = 0
    spawn = vec(0, 0)                               # Set default spawn
    respawn = vec(0, 0)                             # Set default respawn
    screenshot_num = 0

    player = Player(spawn.x, spawn.y)               # Spawn player

    sprites = pygame.sprite.Group()                 # Create group for all game objects
    sprites.add(player)                             # Add player to master sprite group
    obstacles = pygame.sprite.Group()               # Create group for decorative and platform objects
    hazards = pygame.sprite.Group()                 # Create group for objects dangerous to player
    stage_exit = pygame.sprite.Group()              # Create group for stage exit objects
    collectibles = pygame.sprite.Group()            # Create group for collectible game objects
    respawn_point = pygame.sprite.Group()           # Create group for respawn objects
    spikes = pygame.sprite.Group()                  # Create group for spike objects
    slow = pygame.sprite.Group()                    # Create group for objects that slow the player
    decorative = pygame.sprite.Group()              # Create group for decorative objects
    lockleafs = pygame.sprite.Group()
    keys = pygame.sprite.Group()
    skeys = pygame.sprite.Group()
    sdoors = pygame.sprite.Group()
    chests = pygame.sprite.Group()
    returns = pygame.sprite.Group()
    floats = pygame.sprite.Group()
    rings = pygame.sprite.Group()
    swords = pygame.sprite.Group()
    fdoors = pygame.sprite.Group()

    special_timer = 0
    special_ticker = 1
    special_timer2 = 0
    special_ticker2 = 1

    global has_sk1
    global has_sk2
    global has_ring
    global has_sword
    global has_xcancel
    global returned

    font_color = WHITE
    font = pygame.font.Font("res/misc/Bitmgothic.ttf", 24)

    stage_names = load_names()

    start_time = time()

    ambient_fx = pygame.mixer.Sound("res/audio/background.ogg")
    ambient_fx.set_volume(0.6)
    title_fx = pygame.mixer.Sound("res/audio/title.wav")
    title_fx.set_volume(0.8)
    select_fx = pygame.mixer.Sound("res/audio/title2.wav")
    select_fx.set_volume(0.8)
    jump_fx = pygame.mixer.Sound("res/audio/jump.flac")
    jump_fx.set_volume(0.2)
    coin_fx = pygame.mixer.Sound("res/audio/coin.wav")
    coin_fx.set_volume(0.4)
    next_fx = pygame.mixer.Sound("res/audio/next.flac")
    next_fx.set_volume(1.0)
    death_fx = pygame.mixer.Sound("res/audio/death.wav")
    death_fx.set_volume(0.4)
    respawn_fx = pygame.mixer.Sound("res/audio/respawn.wav")
    respawn_fx.set_volume(1.0)
    chest_fx = pygame.mixer.Sound("res/audio/chest.wav")
    chest_fx.set_volume(0.3)
    skey1_fx = pygame.mixer.Sound("res/audio/specialkey1.wav")
    skey1_fx.set_volume(0.3)
    skey2_fx = pygame.mixer.Sound("res/audio/specialkey1.wav")
    skey2_fx.set_volume(0.3)
    sdoor_fx = pygame.mixer.Sound("res/audio/specialdoor.wav")
    sdoor_fx.set_volume(0.2)
    return_fx = pygame.mixer.Sound("res/audio/return.wav")
    return_fx.set_volume(0.2)
    open_fx = pygame.mixer.Sound("res/audio/open.wav")
    open_fx.set_volume(0.2)
    partial_fx = pygame.mixer.Sound("res/audio/partial.wav")
    partial_fx.set_volume(0.2)
    sbkgd1_fx = pygame.mixer.Sound("res/audio/sbkgd1.ogg")
    sbkgd1_fx.set_volume(0.5)
    sbkgd2_fx = pygame.mixer.Sound("res/audio/sbkgd2.ogg")
    sbkgd2_fx.set_volume(0.6)
    sbkgd3_fx = pygame.mixer.Sound("res/audio/sbkgd3.ogg")
    sbkgd3_fx.set_volume(0.5)
    ring_fx = pygame.mixer.Sound("res/audio/chest.wav")     # PUT A DIFFERENT SOUND HERE
    ring_fx.set_volume(0.3)
    sword_fx = pygame.mixer.Sound("res/audio/sword.wav")
    sword_fx.set_volume(0.3)

    title_fx.play()

    title = True
    quit_from_title = False
    while title:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # Handle window exit gracefully
                title = False
                quit_from_title = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    title = False
                if event.key == pygame.K_f:
                    if bigscreen:
                        bigscreen = False
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=1)
                    else:
                        bigscreen = True
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
                if event.key == pygame.K_ESCAPE:
                    title = False
                    quit_from_title = True
        title_image = pygame.image.load("res/img/title.bmp")
        screen.blit(title_image, title_image.get_rect())
        pygame.display.flip()

    select_fx.play()
    ambient_fx.play(-1)

    GameOver = False
    running = True
    while running and not quit_from_title:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # Handle window exit gracefully
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:        # Begin jump logic process
                    player.jump(jump_fx)
                if event.key == pygame.K_s:
                    pygame.image.save(screen, f"screenshot{screenshot_num}.jpeg")
                    screenshot_num += 1
                if event.key == pygame.K_f:
                    if bigscreen:
                        bigscreen = False
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=1)
                    else:
                        bigscreen = True
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:        # End jump logic process
                    player.cancel_jump()

        if not stage_loaded:                        # Load stage if not loaded
            spawn = load_stage(f"res/levels/level{current_stage}.txt",
                               TileArray, HazardArray, StageExitArray,
                               CollectibleArray, RespawnPointArray,
                               SpikeArray, SlowArray, DecorativeArray,
                               LockArray, LockLeafArray, KeyArray,
                               SpecialKeyArray, SecretDoorArray,
                               TombstoneArray, ChestArray, ReturnArray,
                               FloatArray, coins, current_stage, RingArray,
                               SwordArray, FinalDoorArray)
            if spawn == vec(-1, -1):
                end_time = time()
                GameOver = True
                running = False
            else:
                pygame.display.set_caption(f"Lymynal Labrynthe - {stage_names[str(current_stage)]}")
                if current_stage == 13:
                    sbkgd2_fx.play()
                sprites.empty()                         # Clear sprites, obstacles to make room for new stage
                obstacles.empty()
                for obj in TileArray:                   # Load new obstacles
                    obstacles.add(obj)
                    sprites.add(obj)
                TileArray.clear()                       # Clear array used for loading obstacles for next cycle
                hazards.empty()                         # Clear hazards
                for obj in HazardArray:                 # Load new hazards
                    hazards.add(obj)
                    sprites.add(obj)
                HazardArray.clear()                     # Clear array used for loading hazards for next cycle
                stage_exit.empty()                         # Clear stage_exit
                for obj in StageExitArray:                # Load new stage_exit objects
                    stage_exit.add(obj)
                    sprites.add(obj)
                StageExitArray.clear()                  # Clear array used for loading stage exit for next cycle
                collectibles.empty()                    # Clear collectibles
                for obj in CollectibleArray:            # Load new collectibles
                    collectibles.add(obj)
                    sprites.add(obj)
                CollectibleArray.clear()                # Clear array used for loading collectibles for next cycle
                respawn_point.empty()
                if RespawnPointArray:
                    for obj in RespawnPointArray:       # Load stage respawn point if one exists
                        respawn = vec(obj.rect.x + 8, obj.rect.y - 8)
                        respawn_point.add(obj)
                        sprites.add(obj)
                    RespawnPointArray.clear()           # Clear array used for loading respawn points for next cycle
                spikes.empty()
                if SpikeArray:
                    for obj in SpikeArray:
                        spikes.add(obj)
                        sprites.add(obj)
                    SpikeArray.clear()
                slow.empty()
                if SlowArray:
                    for obj in SlowArray:
                        slow.add(obj)
                        sprites.add(obj)
                    SlowArray.clear()
                decorative.empty()
                if DecorativeArray:
                    for obj in DecorativeArray:
                        decorative.add(obj)
                        sprites.add(obj)
                    DecorativeArray.clear()
                lockleafs.empty()
                if LockArray:
                    for obj in LockArray:
                        lockleafs.add(obj)
                        hazards.add(obj)
                        sprites.add(obj)
                    LockArray.clear()
                if LockLeafArray:
                    for obj in LockLeafArray:
                        lockleafs.add(obj)
                        hazards.add(obj)
                        sprites.add(obj)
                    LockLeafArray.clear()
                keys.empty()
                if KeyArray:
                    for obj in KeyArray:
                        keys.add(obj)
                        sprites.add(obj)
                    KeyArray.clear()
                skeys.empty()
                if SpecialKeyArray:
                    for obj in SpecialKeyArray:
                        skeys.add(obj)
                        sprites.add(obj)
                    SpecialKeyArray.clear()
                sdoors.empty()
                if SecretDoorArray:
                    for obj in SecretDoorArray:
                        sdoors.add(obj)
                        sprites.add(obj)
                    SecretDoorArray.clear()
                if TombstoneArray:
                    for obj in TombstoneArray:
                        decorative.add(obj)
                        sprites.add(obj)
                    TombstoneArray.clear()
                chests.empty()
                if ChestArray:
                    for obj in ChestArray:
                        chests.add(obj)
                        sprites.add(obj)
                    ChestArray.clear()
                returns.empty()
                if ReturnArray:
                    for obj in ReturnArray:
                        returns.add(obj)
                        sprites.add(obj)
                    ReturnArray.clear()
                floats.empty()
                if FloatArray:
                    for obj in FloatArray:
                        floats.add(obj)
                        obstacles.add(obj)
                        sprites.add(obj)
                    FloatArray.clear()
                rings.empty()
                if RingArray:
                    for obj in RingArray:
                        rings.add(obj)
                        sprites.add(obj)
                    RingArray.clear()
                swords.empty()
                if SwordArray:
                    for obj in SwordArray:
                        swords.add(obj)
                        sprites.add(obj)
                    SwordArray.clear()
                fdoors.empty()
                if FinalDoorArray:
                    for obj in FinalDoorArray:
                        fdoors.add(obj)
                        sprites.add(obj)
                    FinalDoorArray.clear()

                total_jumps += player.num_jumps
                player.kill()                           # Remove current instance of player
                player = Player(spawn.x, spawn.y)       # Spawn new player at spawn location specified for new stage
                sprites.add(player)
                stage_loaded = True                     # Confirm loading of stage

        pygame.event.pump()                         # Update current event log
        if current_stage == 8:                          # Handle special stage bg and animation
            special_image = pygame.image.load(f"res/img/special{special_ticker}.bmp")
            special_timer += 1
            if special_timer == 10:
                special_timer = 0
                special_ticker += 1
                if special_ticker > 3: special_ticker = 1
            screen.blit(special_image, special_image.get_rect())
        elif current_stage == 17:
            special_image2 = pygame.image.load(f"res/img/specialsecond{special_ticker}.bmp")
            special_timer2 += 1
            if special_timer2 == 10:
                special_timer2 = 0
                special_ticker2 += 1
                if special_ticker2 > 3: special_ticker2 = 1
            screen.blit(special_image2, special_image2.get_rect())
        elif current_stage == 20:
            special_image3 = pygame.image.load(f"res/img/win.bmp")
            screen.blit(special_image3, special_image3.get_rect())

        else:
            screen.fill(BLACK)                          # Fill window background with black

        if returned:
            returned = False

        check = player.update(obstacles, hazards,   # Update player
                              stage_exit, collectibles,
                              respawn_point, spikes, slow,
                              keys, skeys, sdoors, chests,
                              returns, rings, swords, fdoors)
        if check == 1:                              # Player death case
            total_jumps += player.num_jumps
            player.kill()
            player_deaths += 1
            player = Player(spawn.x, spawn.y)
            sprites.add(player)
            death_fx.play()
        if check == 2:                              # Player next stage case
            stage_loaded = False
            if current_stage == 7:
                current_stage = 9
            elif current_stage == 16:
                current_stage = 18
            else:
                current_stage += 1
            next_fx.play()
        if check == 3:                              # Player collect coin case
            coins += 1
            coin_fx.play()
        if check == 4:
            spawn = respawn
            respawn_fx.play()
        if check == 5:
            player.air = 0
            if player.vel.x > 2:
                player.vel.x = 2
            elif player.vel.x < -2:
                player.vel.x = -2
            if player.vel.y > 2:
                player.vel.y = 2
            elif player.vel.y < -5:
                player.vel.y = -5
        if check == 6:
            if not keys:
                for leaf in lockleafs:
                    leaf.kill()
                open_fx.play()
            else:
                partial_fx.play()
        if check == 7:
            if current_stage <= 6:
                has_sk1 = True
                skey1_fx.play()
            else:
                has_sk2 = True
                skey2_fx.play()
        if check == 8:
            has_xcancel = True
            chest_fx.play()
        if check == 9:
            if has_sk1:
                stage_loaded = False
                current_stage = 8
                sdoor_fx.play()
                ambient_fx.stop()
                sbkgd1_fx.play()
            if has_sk2:
                stage_loaded = False
                current_stage = 17
                sdoor_fx.play()
                ambient_fx.stop()
                sbkgd3_fx.play()
        if check == 10:
            if current_stage == 18:
                stage_loaded = False
                current_stage = 19
                next_fx.play()
                ambient_fx.stop()
            if current_stage == 20:
                stage_loaded = False
                current_stage = 19
                next_fx.play()
                ambient_fx.stop()
            else:
                returned = True
                stage_loaded = False
                current_stage -= 1
                has_sk1 = False
                has_sk2 = False
                return_fx.play()
                sbkgd1_fx.stop()
                sbkgd3_fx.stop()
                ambient_fx.play(-1)
        if check == 11:
            has_ring = True
            ring_fx.play()
        if check == 12:
            has_sword = True
            sword_fx.play()
        if check == 13:
            if has_sword:
                stage_loaded = False
                current_stage = 20
                ambient_fx.stop()


        for obj in sprites:                         # Render all game objects
            obj.draw(screen)
        for obj in hazards:                         # Handle hazard animations
            obj.update()
        for obj in collectibles:                    # Handle collectible animations
            obj.update()
        for obj in stage_exit:                      # Handle stage exit animations
            obj.update()
        if respawn_point:                           # Handle respawn point animations
            for obj in respawn_point:
                obj.update()
        if spikes:                                   # handle spikeable tile animations
            for obj in spikes:
                obj.update()
        if slow:                                    # Handle slowing tile animations
            for obj in slow:
                obj.update()
        if decorative:
            for obj in decorative:
                obj.update()
        if keys:
            for obj in keys:
                obj.update()
        if skeys:
            for obj in skeys:
                obj.update()
        if sdoors:
            for obj in sdoors:
                obj.update()
        if floats:
            for obj in floats:
                obj.update()
        if rings:
            for obj in rings:
                obj.update()
        if swords:
            for obj in swords:
                obj.update()
        if fdoors:
            for obj in fdoors:
                obj.update()
        pygame.display.flip()                       # Update window
        clock.tick(FPS)                             # Sync main loop to specified FPS

    while GameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # Handle window exit gracefully
                GameOver = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    GameOver = False
                if event.key == pygame.K_s:
                    pygame.image.save(screen, "score.jpeg")
                if event.key == pygame.K_f:
                    if bigscreen:
                        bigscreen = False
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=1)
                    else:
                        bigscreen = True
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
                if event.key == pygame.K_ESCAPE:
                    GameOver = False

        sec = timedelta(seconds=int(end_time - start_time))
        d = datetime(1, 1, 1) + sec
        time_text = font.render(f"Total time: %d:%d:%d" % (d.hour, d.minute, d.second), True, font_color)
        time_text_rect = time_text.get_rect(center=(SCREEN_WIDTH / 2, 96))
        deaths_text = font.render(f"Deaths: {player_deaths}", True, font_color)
        deaths_text_rect = deaths_text.get_rect(center=(SCREEN_WIDTH / 2, 192))
        coins_text = font.render(f"Coins: {coins}", True, font_color)
        coins_text_rect = coins_text.get_rect(center=(SCREEN_WIDTH / 2, 288))
        jumps_text = font.render(f"Jumps: {total_jumps}", True, font_color)
        jumps_text_rect = jumps_text.get_rect(center=(SCREEN_WIDTH / 2, 384))

        score_image = pygame.image.load("res/img/score.bmp")
        screen.blit(score_image, score_image.get_rect())
        screen.blit(time_text, time_text_rect)
        screen.blit(deaths_text, deaths_text_rect)
        screen.blit(coins_text, coins_text_rect)
        screen.blit(jumps_text, jumps_text_rect)

        pygame.display.flip()

    pygame.display.quit()                           # More graceful exit handling
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
