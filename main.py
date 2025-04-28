import pgzrun
import random

WIDTH = 800
HEIGHT = 600
TITLE = "KILL ENEMIES ONLY"
FPS = 30

MENU = 0
PLAYING = 1
VICTORY = 2
game_state = MENU

music.play("background_music")
music.set_volume(0.5)
shoot_sound = sounds.load("shoot.wav")
enemy_death_sound = sounds.load("enemy_death.wav")

player = None
enemies = []
bullets = []
platforms = []
music_enabled = True
jump_pressed = False

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.actor = Actor("platform_image") 
        self.actor.x = self.x + self.width // 2
        self.actor.y = self.y + self.height // 2

    def colliderect(self, actor):
        return (actor.right > self.x and actor.left < self.x + self.width and
                actor.bottom > self.y and actor.top < self.y + self.height)

    def draw(self):
        self.actor.draw()

class Player(Actor):
    def __init__(self):
        super().__init__("player_idle_right")
        self.direction = "right"
        self.speed = 5
        self.gravity = 0.5
        self.velocity_y = 0
        self.jump_speed = -12
        self.animation_frames = {
            "idle": {"right": ["player_idle_right"], "left": ["player_idle_left"]},
            "walk": {"right": ["walk1_right", "walk2_right"], "left": ["walk1_left", "walk2_left"]},
            "jump": {"right": ["player_jump_right"], "left": ["player_jump_left"]}
        }
        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0

    def update(self):
        if keyboard.left:
            self.direction = "left"
            self.x -= self.speed
            if self.on_ground():
                self.current_animation = "walk"
        elif keyboard.right:
            self.direction = "right"
            self.x += self.speed
            if self.on_ground():
                self.current_animation = "walk"
        else:
            if self.on_ground():
                self.current_animation = "idle"

        self.animation_timer += 1
        if self.animation_timer >= 5:
            frames = self.animation_frames[self.current_animation][self.direction]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.animation_timer = 0

        self.y += self.velocity_y
        self.velocity_y += self.gravity

        landed = False
        for platform in platforms:
            if platform.colliderect(self):
                if self.velocity_y > 0 and self.bottom < platform.y + platform.height:
                    self.bottom = platform.y
                    self.velocity_y = 0
                    landed = True

        if not self.on_ground() and not landed:
            self.current_animation = "jump"
            self.image = self.animation_frames["jump"][self.direction][0]

    def jump(self):
        if self.on_ground():
            self.velocity_y = self.jump_speed
            self.current_animation = "jump"
            self.image = self.animation_frames["jump"][self.direction][0]

    def on_ground(self):
        for platform in platforms:
            if (self.bottom >= platform.y - 5 and self.bottom <= platform.y + 5 and
                self.right > platform.x and self.left < platform.x + platform.width):
                return True
        return False

class Enemy(Actor):
    def __init__(self, x, y):
        super().__init__("enemy_idle_right")
        self.direction = "right"
        self.speed = 2
        self.x = x
        self.y = y
        self.path_left = self.x - 50
        self.path_right = self.x + 50
        self.animation_frames = {
            "walk": {"right": ["enemy_walk1_right", "enemy_walk2_right"],
                     "left": ["enemy_walk1_left", "enemy_walk2_left"]}
        }
        self.current_animation = "walk"
        self.frame_index = 0
        self.animation_timer = 0

    def update(self):
        if self.direction == "right":
            self.x += self.speed
            if self.x > self.path_right:
                self.direction = "left"
        else:
            self.x -= self.speed
            if self.x < self.path_left:
                self.direction = "right"

        self.animation_timer += 1
        if self.animation_timer >= 5:
            frames = self.animation_frames[self.current_animation][self.direction]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.animation_timer = 0

class Bullet(Actor):
    def __init__(self, x, y, direction):
        super().__init__("bullet")
        self.direction = direction
        self.speed = 8
        self.x = x
        self.y = y

    def update(self):
        if self.direction == "right":
            self.x += self.speed
        else:
            self.x -= self.speed
        if self.x < 0 or self.x > WIDTH:
            bullets.remove(self)

def setup_game():
    global player, enemies, platforms
    
    player = Player()
    player.x = 160  
    player.y = 60 

    platforms = [
        Platform(50, 90, 120, 40),     
        Platform(30, 270, 170, 40),    
        Platform(300, 300, 170, 30),   
        Platform(530, 140, 220, 40),   
        Platform(520, 400, 170, 40)    
    ]

    enemies = [
        Enemy(120, 270),   
        Enemy(360, 295),   
        Enemy(610, 140),   
        Enemy(610, 400)    
    ]

def update():
    global game_state, enemies, jump_pressed

    if game_state == PLAYING:
        if keyboard.up and not jump_pressed:
            player.jump()
            jump_pressed = True
        if not keyboard.up:
            jump_pressed = False

        player.update()
        
        if player.bottom > HEIGHT:
            game_state = MENU

        for enemy in enemies:
            enemy.update()

        if keyboard.space:
            direction = player.direction
            bullet = Bullet(player.x, player.y, direction)
            bullets.append(bullet)
            shoot_sound.play()

        for bullet in bullets[:]:
            bullet.update()
            for enemy in enemies[:]:
                if bullet.colliderect(enemy):
                    enemy_death_sound.play()
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    break

        for enemy in enemies:
            if player.colliderect(enemy):
                game_state = MENU

        if len(enemies) == 0:
            music.stop()
            music.play("victory")
            game_state = VICTORY

    elif game_state == MENU:
        if keyboard.RETURN:
            setup_game()
            game_state = PLAYING
        if keyboard.m:
            toggle_music()
        if keyboard.ESCAPE:
            exit()

    elif game_state == VICTORY:
        global can_start
        if keyboard.v:
            music.stop()
            music.play("background_music")
            setup_game()
            game_state = MENU
            can_start = False
            
        if not keyboard.v:
            can_start = True

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        music.unpause()
    else:
        music.pause()

def draw():
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == VICTORY:
        draw_victory()

def draw_menu():
    screen.clear()
    screen.blit("forest_background", (0, 0))
    screen.draw.text("KILL ENEMIES ONLY", 
                    center=(WIDTH//2, HEIGHT//4), 
                    fontsize=60, 
                    color="red", 
                    shadow=(1, 1), 
                    scolor="black")
    
    menu_options = [
        ("START GAME - Press Enter", "white", 40),
        (f"MUSIC: {'ON' if music_enabled else 'OFF'} - Press M", "yellow", 30),
        ("EXIT GAME - Press Esc", "red", 40)
    ]
    
    y_pos = HEIGHT//2 - 50
    for text, color, size in menu_options:
        screen.draw.text(text, 
                        center=(WIDTH//2, y_pos), 
                        fontsize=size, 
                        color=color)
        y_pos += 50
    
    screen.draw.text("CONTROLS:", 
                    midtop=(WIDTH//2, y_pos + 20), 
                    fontsize=30, 
                    color="cyan")
    
    controls = [
        "Move: Arrow Keys Left/Right",
        "Jump: Up Arrow",
        "Shoot: Spacebar"
    ]
    
    y_pos += 60
    for control in controls:
        screen.draw.text(control, 
                        midtop=(WIDTH//2, y_pos), 
                        fontsize=25, 
                        color="white")
        y_pos += 30

def draw_game():
    screen.fill((0, 0, 0))
    screen.blit("forest_background", (0, 0))

    for platform in platforms:
        platform.draw()
    
    player.draw()

    for enemy in enemies:
        enemy.draw()

    for bullet in bullets:
        bullet.draw()
        
def draw_victory():
    screen.clear()
    screen.fill((20, 60, 20)) 

    screen.draw.text("YOU WIN!", 
                    center=(WIDTH//2, HEIGHT//3), 
                    fontsize=80, 
                    color="lime",
                    shadow=(2, 2),
                    scolor="black")

    screen.draw.text("All enemies defeated!", 
                    center=(WIDTH//2, HEIGHT//2), 
                    fontsize=40, 
                    color="white")

    screen.draw.text("Press v to Return to Menu", 
                    center=(WIDTH//2, HEIGHT//2 + 100), 
                    fontsize=30, 
                    color="yellow")

pgzrun.go()