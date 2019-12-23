import pygame
import numpy as np
from numpy import *
from pygame import gfxdraw
import random

pygame.init()
gameDisplay = pygame.display.set_mode((400, 300))
lifespan = 400
count = 0
target = pygame.Vector2(gameDisplay.get_size()[0] / 2, 50)
mutation_rate = 0.01
max_force = 0.2


class Rocket:

    def __init__(self, game_display, dna=None):
        width, height = game_display.get_size()
        self.completed = False
        self.dead = False
        self.pos = pygame.Vector2(width/2, height - 20)
        self.vel = pygame.Vector2()
        self.acc = pygame.Vector2()
        self.dna = dna if dna is not None else DNA()
        self.fitness = 0
        self.display = game_display

    def apply_force(self, force):
        self.acc = self.acc + force

    def update(self):
        dist = self.pos.distance_to(target)
        if dist <= 10:
            self.completed = True
            self.pos = pygame.Vector2(target.x, target.y)

        if rect_x < self.pos.x < rect_x + rect_w and rect_y < self.pos.y < rect_y + rect_h:
            self.dead = True

        width, height = self.display.get_size()
        # check if 2 polygons intersect!! + implement time and tweak other things
        if self.pos.x > width or self.pos.x < 0 or self.pos.y > height or self.pos.y < 0:
            self.dead = True

        if not self.completed and not self.dead:
            self.apply_force(self.dna.genes[count])
            self.vel = self.vel + self.acc
            self.pos = self.pos + self.vel
            self.acc = 0 * self.acc
            if self.vel.magnitude() > 4:
                self.vel.scale_to_length(4.0)

    def show(self):
        centre = pygame.Vector2(self.pos.x, self.pos.y)
        height = 5.0
        height = height / 2
        width = 25.0
        width = width / 2

        v1 = pygame.Vector2(-width, -height)
        v2 = pygame.Vector2(width, -height)
        v3 = pygame.Vector2(width, height)
        v4 = pygame.Vector2(-width, height)

        death_colour = (160, 186, 170, 100)

        pygame.gfxdraw.aapolygon(self.display, [pygame.Vector2(centre + v.rotate(self.vel.as_polar()[1]))
                                                for v in [v1, v2, v3, v4]], teal if not self.dead else death_colour)
        pygame.gfxdraw.filled_polygon(self.display, [pygame.Vector2(centre + v.rotate(self.vel.as_polar()[1]))
                                      for v in [v1, v2, v3, v4]], teal if not self.dead else death_colour)

    def get_fitness(self):
        dist = self.pos.distance_to(target)
        self.fitness = np.interp(dist, [0, self.display.get_size()[0]], [self.display.get_size()[0], 0])
        if self.completed:
            self.fitness *= 4
            # self.fitness *= np.interp(lifespan - count, [lifespan/2, lifespan], [1, 2])
            count2 = np.interp(count, [lifespan/3, lifespan], [0.5, 2])
            count2 = 2 / count2
            self.fitness *= count2
        if self.dead:
            if self.pos.y < rect_y:
                self.fitness /= 5
            else:
                self.fitness /= 10


class Population:
    def __init__(self, display):
        self.display = display
        self.mating_pool = []
        self.pop_size = 50
        self.rockets = [Rocket(display) for i in range(self.pop_size)]
        self.mating_pool = []

    def run(self):
        for i in range(self.pop_size):
            self.rockets[i].update()
            self.rockets[i].show()

    def eval_fitness(self):
        max_fitness = 0
        for i in range(self.pop_size):
            self.rockets[i].get_fitness()
            if self.rockets[i].fitness > max_fitness:
                max_fitness = self.rockets[i].fitness

        for i in range(self.pop_size):
            self.rockets[i].fitness /= max_fitness

        self.mating_pool = []

        for i in range(self.pop_size):
            n = self.rockets[i].fitness * 100
            for j in range(math.floor(n)):
                self.mating_pool.append(self.rockets[i])

    def selection(self):
        new_rockets = []
        for i in range(len(self.rockets)):
            mom = random.choice(self.mating_pool).dna
            dad = random.choice(self.mating_pool).dna
            child = mom.reproduce_with(dad)
            child.mutation()
            new_rockets.append(Rocket(self.display, child))

        self.rockets = new_rockets


class DNA:
    def __init__(self, genes=None):
        if genes is not None:
            self.genes = genes
        else:
            self.genes = []
            for i in range(lifespan):
                theta = np.random.uniform(0, 2.0 * math.pi)
                self.genes.append(pygame.Vector2(math.cos(theta), math.sin(theta)))
                self.genes[i].scale_to_length(max_force)

    def reproduce_with(self, partner):
        new_genes = []
        mid = math.floor(random.uniform(0, len(self.genes)))
        # child's genes are a random mix of mother's genes and father's genes
        for i in range(len(self.genes)):
            new_genes.append(self.genes[i] if i > mid else partner.genes[i])

        return DNA(new_genes)

    def mutation(self):
        for i in range(len(self.genes)):
            if random.uniform(0, 1) < mutation_rate:
                theta = np.random.uniform(0, 2.0 * math.pi)
                self.genes[i] = pygame.Vector2(math.cos(theta), math.sin(theta))
                self.genes[i].scale_to_length(max_force)


gameExit = False
bg = (200, 177, 255)
teal = (67, 224, 146, 150)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

r = Rocket(gameDisplay)
clock = pygame.time.Clock()

pop = Population(gameDisplay)

rect_x = 100
rect_y = 150
rect_w = 200
rect_h = 10

obstacle = pygame.rect.Rect(rect_x, rect_y, rect_w, rect_h)
drag_rect = False
drag_target = False

offset_x, offset_y = 0, 0
offset_x_t, offset_y_t = 0, 0

while not gameExit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if obstacle.collidepoint(event.pos):
                    drag_rect = True
                    mouse_x, mouse_y = event.pos
                    offset_x = obstacle.x - mouse_x
                    offset_y = obstacle.y - mouse_y

                if target.distance_to(event.pos) < 8:
                    drag_target = True
                    mouse_x, mouse_y = event.pos
                    offset_x_t = target.x - mouse_x
                    offset_y_t = target.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drag_rect = False
                drag_target = False

        elif event.type == pygame.MOUSEMOTION:
            if drag_rect:
                mouse_x, mouse_y = event.pos
                obstacle.x = mouse_x + offset_x
                obstacle.y = mouse_y + offset_y
            if drag_target:
                mouse_x, mouse_y = event.pos
                target.x = mouse_x + offset_x_t
                target.y = mouse_y + offset_y_t

    rect_x, rect_y = obstacle.x, obstacle.y

    gameDisplay.fill((50, 50, 50))
    pygame.gfxdraw.aacircle(gameDisplay, int(target.x), int(target.y), 8, (200, 200, 200, 150))
    pygame.gfxdraw.filled_circle(gameDisplay, int(target.x), int(target.y), 8, (200, 200, 200, 150))
    pop.run()
    count += 1

    if count == lifespan:
        pop.eval_fitness()
        pop.selection()
        # pop = Population(gameDisplay)
        count = 0

    pygame.draw.rect(gameDisplay, (200, 200, 200, 130), obstacle)

    clock.tick(60)

    pygame.display.update()
