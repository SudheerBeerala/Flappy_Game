import pygame
import sys
import os
import random
import neat

pygame.font.init()

# Global variables
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
FLOOR = 630
BIRD_X = 230
BIRD_Y = 350
STAT_FONT = pygame.font.SysFont("comicsans", 50)
GRAVITY = 1
DRAW_LINES = False

gen = 0

# Screen
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load Images
#   Background
bg_img = pygame.image.load('resources/background-night.png').convert()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

#   Pipes
pipe_image_bottom = pygame.image.load('resources/pipe-green.png').convert()
pipe_image_top = pygame.transform.flip(pipe_image_bottom, False, True)

#   Bird
bird_image_downflap = pygame.image.load('resources/redbird-downflap.png').convert_alpha()
bird_image_midflap = pygame.image.load('resources/redbird-midflap.png').convert_alpha()
bird_image_upflap = pygame.image.load('resources/redbird-upflap.png').convert_alpha()
bird_images = [bird_image_downflap, bird_image_midflap, bird_image_upflap]

base_img = pygame.image.load('resources/base.png').convert()


class Bird:
    IMGS = bird_images
    ANIMATION_COUNT = 5  # for every ANIMATION_COUNT frames, next image is picked.

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.movement = 0
        self.img_tick = 0
        self.img = self.IMGS[0]
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def jump(self):
        self.movement = 0
        self.movement -= 6
        self.rect.centery += self.movement

    def move(self):
        self.movement += GRAVITY
        self.rect.centery += self.movement

    def rotate(self):
        self.img = pygame.transform.rotozoom(self.img, self.movement * 3, 1)

    def draw(self, screen):
        self.img_tick += 1

        if self.img_tick <= self.ANIMATION_COUNT:
            self.img = self.IMGS[0]
        elif self.img_tick <= self.ANIMATION_COUNT * 2:
            self.img = self.IMGS[1]
        elif self.img_tick <= self.ANIMATION_COUNT * 3:
            self.img = self.IMGS[2]
        elif self.img_tick <= self.ANIMATION_COUNT * 4:
            self.img = self.IMGS[1]
        else:
            self.img = self.IMGS[0]
            self.img_tick = 0

        self.rotate()

        screen.blit(self.img, self.rect)


class Pipe():
    GAP = 200
    MOVE_COUNT = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0

        self.img_pipe_top = pipe_image_top
        self.img_pipe_bottom = pipe_image_bottom

        self.passed = False

        self.set_height()

        self.add_rect()

    def set_height(self):
        self.height = random.randrange(350, 480)
        self.top = self.height
        self.bottom = self.height - self.GAP

    def add_rect(self):
        self.rect_pipe_top = self.img_pipe_top.get_rect(midbottom=(self.x, self.bottom))
        self.rect_pipe_bottom = self.img_pipe_bottom.get_rect(midtop=(self.x, self.top))

    def move(self):
        self.rect_pipe_bottom.centerx -= self.MOVE_COUNT
        self.rect_pipe_top.centerx -= self.MOVE_COUNT

    def draw(self, screen):
        screen.blit(self.img_pipe_top, self.rect_pipe_top)
        screen.blit(self.img_pipe_bottom, self.rect_pipe_bottom)


class Floor:
    MOVE_COUNT = 1
    IMG = base_img
    WIDTH = base_img.get_width()
    THRESHOLD = 300

    def __init__(self, y):
        self.y = y
        self.x = 0
        self.img = self.IMG

    def move(self):
        self.x -= self.MOVE_COUNT
        if self.x <= self.THRESHOLD:
            self.x = 0

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        screen.blit(self.img, (self.x + self.WIDTH, self.y))


def check_collission(pipe, bird):
    if pipe.rect_pipe_top.colliderect(bird.rect) or pipe.rect_pipe_bottom.colliderect(bird.rect):
        return True
    if bird.rect.top <= -50 or bird.rect.bottom >= FLOOR:
        return True
    return False


def update_screen(screen, birds, pipes, floor, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    screen.blit(bg_img, (0, 0))
    for pipe in pipes:
        pipe.draw(screen)

    floor.draw(screen)
    for bird in birds:
        bird.draw(screen)
        if DRAW_LINES:
            try:
                pygame.draw.line(screen, (255, 0, 0), bird.rect.midtop, pipe.rect_pipe_top.midbottom, 5)
                pygame.draw.line(screen, (255, 0, 0), bird.rect.midbottom, pipe.rect_pipe_bottom.midtop, 5)
            except:
                pass

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    screen.blit(score_label, (SCREEN_WIDTH - score_label.get_width() - 15, 10))

    gen_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    screen.blit(gen_label, (10, 10))

    alive_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    screen.blit(alive_label, (10, 50))

    pygame.display.update()


def evaluate_genomes(genomes, config):
    global SCREEN, gen
    gen += 1

    nets = []
    ge = []
    birds = []

    pipes = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(BIRD_X, BIRD_Y))
        ge.append(genome)

    pipes.append(Pipe(700))
    floor = Floor(FLOOR)
    score = 0

    clock = pygame.time.Clock()
    running = True

    while running and len(birds):
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].rect.left > pipes[0].rect_pipe_bottom.right:
            pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[x].activate((bird.rect.centery,
                                       abs(bird.rect.centery - pipes[pipe_ind].rect_pipe_bottom.top),
                                       abs(bird.rect.centery - pipes[pipe_ind].rect_pipe_top.bottom)))
            if output[0] > 0.5:
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            for x, bird in enumerate(birds):
                if check_collission(pipe, bird):
                    ge[x].fitness -= 1
                    nets.pop(x)
                    ge.pop(x)
                    birds.pop(x)

            if pipe.rect_pipe_top.right < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.rect_pipe_top.centerx < bird.rect.centerx:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(SCREEN_WIDTH))

        for r in rem:
            pipes.remove(r)

        floor.move()

        update_screen(SCREEN, birds, pipes, floor, score, gen, pipe_ind)


def neat_run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Population
    p = neat.Population(config)

    # Stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run upto 50 generations
    winner = p.run(evaluate_genomes, 50)

    # Show Final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    neat_run(config_path)
