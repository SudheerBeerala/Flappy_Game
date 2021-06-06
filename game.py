import pygame as pg
import sys
import random


def bottom_move():
    screen.blit(bottom_image, (bottom_image_x, 540))
    screen.blit(bottom_image, (bottom_image_x + 336, 540))


def create_pipe_rect():
    pipe_height = random.choice([230, 330, 430])
    pipe_rect_bottom = pipe_image_bottom.get_rect(midtop=(350, pipe_height))
    pipe_rect_top = pipe_image_bottom.get_rect(midbottom=(350, pipe_height - 150))
    return pipe_rect_bottom, pipe_rect_top


def move_pipes(pipe_rect_list):
    for pipe_rect in pipe_rect_list:
        pipe_rect.centerx -= 2
    return pipe_rect_list


def draw_pipes(pipe_rect_list):
    for pipe_rect in pipe_rect_list:
        if pipe_rect.bottom >= 550:
            screen.blit(pipe_image_bottom, pipe_rect)
        else:
            screen.blit(pipe_image_top, pipe_rect)


def check_collision(pipe_rect_list):
    for pipe_rect in pipe_rect_list:
        if bird_rect.colliderect(pipe_rect):
            death_sound.play()
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= 540:
        return False
    return True


def rotate_bird(bird_image):
    new_bird_image = pg.transform.rotozoom(bird_image, bird_movement * 3, 1)
    return new_bird_image


def bird_animation():
    new_bird_image = bird_image_list[bird_image_index]
    new_bird_rect = bird_image.get_rect(center=(100, bird_rect.centery))
    return new_bird_image, new_bird_rect


def score_display(game_status):
    if game_status == 'main_game':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(180, 50))
        screen.blit(score_surface, score_rect)

    elif game_status == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(180, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(180, 500))
        screen.blit(high_score_surface, high_score_rect)


# pg.mixer.pre_init(frequency=44100, size=16, channels=1, buffer=512)
pg.init()

# Game variables
gravity = 0.2
bird_movement = 0
game_active = True
game_font = pg.font.Font('04B_19.ttf', 30)
score = 0
high_score = 0
score_count = 100

running = True
screen = pg.display.set_mode((360, 640))
clock = pg.time.Clock()
background_image = pg.image.load('resources/background-day.png').convert()
background_image = pg.transform.scale(background_image, (360, 640))

bottom_image = pg.image.load('resources/base.png').convert()
bottom_image_x = 0

# bird_image = pg.image.load('resources/bluebird-midflap.png').convert_alpha()
bird_image_downflap = pg.image.load('resources/bluebird-downflap.png').convert_alpha()
bird_image_midflap = pg.image.load('resources/bluebird-midflap.png').convert_alpha()
bird_image_upflap = pg.image.load('resources/bluebird-upflap.png').convert_alpha()
bird_image_list = [bird_image_downflap, bird_image_midflap, bird_image_upflap]
bird_image_index = 0
bird_image = bird_image_list[bird_image_index]
bird_rect = bird_image.get_rect(center=(100, 320))

pipe_image_bottom = pg.image.load('resources/pipe-green.png').convert()
pipe_image_top = pg.transform.flip(pipe_image_bottom, False, True)
pipe_rect_list = []

game_over_image = pg.image.load('resources/message.png').convert_alpha()
game_over_rect = game_over_image.get_rect(center=(180, 300))

# Sounds
flap_sound = pg.mixer.Sound('audio/sfx_wing.wav')
death_sound = pg.mixer.Sound('audio/sfx_die.wav')
score_sound = pg.mixer.Sound('audio/sfx_point.wav')

SPAWNPIPE = pg.USEREVENT
pg.time.set_timer(SPAWNPIPE, 1200)

BIRDFLAP = pg.USEREVENT + 1
pg.time.set_timer(BIRDFLAP, 200)

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
                flap_sound.play()

            if event.key == pg.K_SPACE and not(game_active):
                game_active = True
                bird_movement = 0
                bird_rect = bird_image.get_rect(center=(100, 320))
                pipe_rect_list.clear()
                score = 0

        if event.type == SPAWNPIPE:
            pipe_rect_list.extend(create_pipe_rect())

        if event.type == BIRDFLAP:
            if bird_image_index >= 2:
                bird_image_index = 0
            else:
                bird_image_index += 1

            bird_image, bird_rect = bird_animation()


# Background
    screen.blit(background_image, (0, 0))

    if(game_active):

        # Bird
        bird_movement += gravity
        bird_rect.centery += bird_movement
        rotated_bird = rotate_bird(bird_image)
        screen.blit(rotated_bird, bird_rect)

        game_active = check_collision(pipe_rect_list)

    # Pipes
        pipe_rect_list = move_pipes(pipe_rect_list)
        draw_pipes(pipe_rect_list)
        score += .01
        score_count -= 1

        if score_count <= 0:
            score_sound.play()
            score_count = 100

        score_display('main_game')
    else:
        if score > high_score:
            high_score = score
        screen.blit(game_over_image, game_over_rect)
        score_display('game_over')

# Floor
    bottom_image_x -= 1
    bottom_move()
    if bottom_image_x < -235:
        bottom_image_x = 0

    pg.display.update()
    clock.tick(120)
