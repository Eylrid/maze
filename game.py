import random
import math
TAU = math.pi*2

class Seed:
    CHROMOSOMELENGTH = 28
    def __init__(self, x, y, item, energy=0., chromosome=None):
        self.x = x
        self.y = y
        self.item = item
        self.energy = energy
        self.process_chromosome(chromosome)

    def process_chromosome(self, chromosome):
        if chromosome:
            if len(chromosome) != Seed.CHROMOSOMELENGTH:
                raise ValueError('Chromosome Wrong Length')

            self.chromosome = chromosome
        else:
            self.chromosome = ''.join([random.choice(('0','1')) for i in range(Seed.CHROMOSOMELENGTH)])

        self.mutability = int(self.chromosome[24:], 2)+1
        if random.randint(0,16) < self.mutability:
            mutationpoint = random.randint(0, Seed.CHROMOSOMELENGTH-1)
            mutation = random.choice(('0','1'))
            self.chromosome = self.chromosome[:mutationpoint] + mutation + self.chromosome[mutationpoint+1:]

        self.color = '#' + hex(int(self.chromosome[:24], 2))[2:].rjust(6, '0')


class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

    def relative_point(self, distance=0, dx=0, dy=0, dangle=0):
        angle = (self.angle + dangle) % TAU
        x = self.x + dx + distance*math.cos(angle)
        y = self.y + dy + distance*math.sin(angle)
        return x, y, angle

    def move(self, *args, **kwargs):
        self.x, self.y, self.angle = self.relative_point(*args, **kwargs)


class Game:
    def __init__(self, width=25, height=25, blocksize=20):
        self.width = width
        self.height = height
        self.blocksize = blocksize
        self.block = (0, 0)
        self.selected_seeds = []
        #self.maze = Maze(self.width, self.height)
        #self.create_player()
        #self.create_seeds()
