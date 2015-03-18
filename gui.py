import maze, image
import Tkinter, ImageTk
import random
from drawer import MazeDrawer, Canvas
from maze import Maze
from game import Game
import math
TAU = math.pi*2

class CanvasCanvas(Canvas):
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_line(self, coords, fill, tag):
        self.canvas.create_line(*coords, fill=fill, tag=tag)

    def draw_point(self, coords, fill, tag):
        x, y = coords
        self.canvas.create_line(x, y, x+1, y+1, fill=fill, tag=tag)


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


class App(Tkinter.Frame):
    def __init__(self, master, game, viewangle=TAU/6, viewslices=300, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.game = game
        self.width = self.game.width
        self.height = self.game.height
        self.blocksize = self.game.blocksize
        self.viewangle = viewangle
        self.viewslices = viewslices
        self.sliceangle = self.viewangle/self.viewslices
        self.canvas_width = self.width*self.blocksize + 1
        self.canvas_height = self.height*self.blocksize + 1
        self.block = (0, 0)
        self.selected_seeds = []
        self.create_widgets()
        self.maze = Maze(self.width, self.height)
        self.draw_canvas = CanvasCanvas(self.canvas)
        self.drawer = MazeDrawer(self.draw_canvas, self.maze, self.blocksize)
        self.create_player()
        self.create_seeds()

    def create_widgets(self):
        self.canvas = Tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind('<Button-1>', self.click)        

        self.threedcanvas = Tkinter.Canvas(self, width=self.viewslices, height=self.viewslices)
        self.threedcanvas.grid(row=0, column=1)

        self.buttonframe = Tkinter.Frame(self)
        self.buttonframe.grid(row=1, column=0)

        self.forward_button = Tkinter.Button(self.buttonframe, text='Forward',
                                             command=self.forward)
        self.forward_button.grid(row=0, column=0, columnspan=2)

        self.back_button = Tkinter.Button(self.buttonframe, text='Back',
                                          command=self.back)
        self.back_button.grid(row=2, column=0, columnspan=2)

        self.left_button = Tkinter.Button(self.buttonframe, text='Left',
                                          command=self.left)
        self.left_button.grid(row=1, column=0)

        self.right_button = Tkinter.Button(self.buttonframe, text='Right',
                                           command=self.right)
        self.right_button.grid(row=1, column=1)

        self.chromosomeframe = Tkinter.Frame(self)
        self.chromosomeframe.grid(row=1, column=1)

        self.chromosomevar = Tkinter.StringVar()
        self.chromosomevar.trace('w', self.check_chromosome)
        self.chromosomeentry = Tkinter.Entry(self.chromosomeframe,
                                             textvariable=self.chromosomevar,
                                             width=Seed.CHROMOSOMELENGTH)
        self.chromosomeentry.grid(row=0, column=0)

        self.chromosomelabel = Tkinter.Label(self.chromosomeframe, text='')
        self.chromosomelabel.grid(row=1, column=0)

    def create_player(self):
        self.player = Player(self.blocksize/2., self.blocksize/2., TAU/8)
        self.create_viewlines()
        self.create_3d_lines()
        x1, y1, x2, y2 = self.get_player_line_coords()
        self.player_line = self.canvas.create_line(x1, y1, x2, y2, fill='red')

    def update_player(self):
        angles = self.get_viewangles()
        endpoints = [self.get_next_wall(self.player.x, self.player.y, a) for a in angles]
        relangles = self.get_relative_angles()
        for i in range(self.viewslices):
            (x, y), distance, direction = endpoints[i]
            self.canvas.coords(self.viewlines[i], self.player.x, self.player.y, x, y)

            wallheight = self.viewslices/(distance*math.tan(self.viewangle)*math.cos(relangles[i])*2)
            color = {(1,0):'green', (0,1):'blue', (-1,0):'yellow', (0,-1):'red'}[direction]
            self.threedcanvas.coords(self.threedlines[i], i, self.viewslices/2-wallheight,
                                     i, self.viewslices/2+wallheight)
            self.threedcanvas.itemconfig(self.threedlines[i], fill=color)

        x1, y1, x2, y2 = self.get_player_line_coords()
        self.canvas.coords(self.player_line, x1, y1, x2, y2)

    def create_viewlines(self):
        angles = self.get_viewangles()
        endpoints = [self.get_view_line_endpoints(a) for a in angles]
        self.viewlines = [self.canvas.create_line(self.player.x, self.player.y, x, y, fill='black') for x, y in endpoints]

    def create_3d_lines(self):
        self.threedlines = []
        for i in range(self.viewslices):
            self.threedlines.append(self.threedcanvas.create_line(i, 0, i, self.viewslices))

    def create_seeds(self):
        self.seeds = []
        self.seed_map = [[[] for y in range(self.height)] for x in range(self.width)]
        self.create_seed(random.randint(0, self.width-1),
                         random.randint(0, self.height-1))

    def create_seed(self, x, y, chromosome=None):
        newseed = Seed(x, y, item=None, chromosome=chromosome)
        item = self.canvas.create_rectangle(x*self.blocksize+2,
                                            y*self.blocksize+2,
                                            (x+1)*self.blocksize-2,
                                            (y+1)*self.blocksize-2,
                                            fill=newseed.color,
                                            outline=newseed.color,
                                            tag='seed')
        newseed.item = item
        self.seeds.append(newseed)
        self.seed_map[x][y].append(newseed)

    def remove_seed(self, seed):
        self.seeds.remove(seed)
        self.seed_map[seed.x][seed.y].remove(seed)
        self.canvas.delete(seed.item)

    def get_relative_angles(self):
        angles = []
        for i in range(self.viewslices):
            angles.append(-self.viewangle/2 + self.sliceangle*i)
        return angles

    def get_viewangles(self):
        angles = [a+self.player.angle for a in self.get_relative_angles()]
        return angles

    def get_view_line_endpoints(self, angle):
        return self.get_next_wall(self.player.x, self.player.y, angle)[0]

    def get_player_line_coords(self):
        point, distance, direction = self.get_next_wall(self.player.x, self.player.y, self.player.angle)
        x, y = point
        return self.player.x, self.player.y, x, y

    def get_next_wall(self, x, y, angle, blockx=None, blocky=None):
        angle = angle%TAU
        if blockx==None: blockx = int(x/self.blocksize)
        if blocky==None: blocky = int(y/self.blocksize)
        wall_point, direction, distance = self.get_wall_point(x, y, angle)
        nextx = blockx + direction[0]
        nexty = blocky + direction[1]
        if not self.block_in_range(nextx, nexty):
            return wall_point, distance, direction

        cell = self.maze.cells[blockx][blocky]
        nextcell = self.maze.cells[nextx][nexty]
        if nextcell in cell.connected_neighbors:
            wall_point, newdist, direction =  self.get_next_wall(wall_point[0], wall_point[1],
                                                      angle, nextx, nexty)
            distance += newdist

        return wall_point, distance, direction

    def get_wall_point(self, x, y, angle):
        blockx = x/self.blocksize
        blocky = y/self.blocksize
        distance = 2
        wallx = None
        wally = None

        if angle < TAU/4 or angle > TAU*3/4:
            direction = (1, 0)
            wallx = math.ceil(blockx)
            if wallx == blockx: wallx += 1
        elif angle > TAU/4 and angle < TAU*3/4:
            direction = (-1, 0)
            wallx = math.floor(blockx)
            if wallx == blockx: wallx -= 1

        if wallx != None:
            distance = abs((wallx-blockx)/math.cos(angle))
            point = (wallx*self.blocksize, (blocky+distance*math.sin(angle))*self.blocksize)

        if angle > 0 and angle < TAU/2:
            ydirection = 1
            wally = math.ceil(blocky)
            if wally == blocky: wally += 1
        elif angle > TAU/2 and angle < TAU:
            wally = math.floor(blocky)
            ydirection = -1
            if wally == blocky: wally -= 1

        if wally != None:
            ydistance = abs((wally-blocky)/math.sin(angle))
            if ydistance < distance:
                direction = (0, ydirection)
                distance = ydistance
                point = ((blockx+distance*math.cos(angle))*self.blocksize, wally*self.blocksize)

        return point, direction, distance

    def draw_path(self, coords):
        self.canvas.delete('path')
        self.drawer.draw_path(*coords)

    def seed_step(self):
        self.eat_seeds()
        seedenergy = 0.1/len(self.seeds)
        for seed in self.seeds[:]:
            seed.energy += seedenergy
            if seed.energy >= 1:
                while True:
                    newx = seed.x + random.randint(-3, 3)
                    newy = seed.y + random.randint(-3, 3)
                    if self.block_in_range(newx, newy):
                        break
                seed.energy -= 1
                self.create_seed(newx, newy, chromosome=seed.chromosome)

    def eat_seeds(self):
        blockx = self.mouse_to_block(self.player.x)
        blocky = self.mouse_to_block(self.player.y)
        seeds = self.seed_map[blockx][blocky]
        if seeds:
            print '%d seeds eaten' %len(seeds)
            for seed in seeds[:]:
                self.remove_seed(seed)

    def mouse_to_block(self, x):
        return int(math.floor(((x)/self.blocksize)))

    def block_in_range(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        else:
            return True

    def event_block(self, event):
        blockx = self.mouse_to_block(event.x)
        blocky = self.mouse_to_block(event.y)
        if not self.block_in_range(blockx, blocky):
            return
        else:
            return blockx, blocky

    def click(self, event):
        block = self.event_block(event)
        if not block: return
        self.draw_path((self.block[0], self.block[1], block[0], block[1]))
        self.block = block
        self.seed_info()

    def seed_info(self):
        seeds = self.seed_map[self.block[0]][self.block[1]]
        if seeds:
            print '*****'
            for seed in seeds:
                print 'Seed:'
                print '-chromosome:', seed.chromosome
                print '-color:', seed.color
                print '-mutation rate: %d/16' %seed.mutability
        self.selected_seeds = seeds
        self.check_chromosome()

    def move_player(self, *args, **kwargs):
        if not self.player_can_move(*args, **kwargs): return
        self.player.move(*args, **kwargs)
        self.seed_step()
        self.update_player()

    def player_can_move(self, *args, **kwargs):
        x, y, angle = self.player.relative_point(*args, **kwargs)
        newblockx = self.mouse_to_block(x)
        newblocky = self.mouse_to_block(y)
        if not self.block_in_range(newblockx, newblocky):
            return False

        oldblockx = self.mouse_to_block(self.player.x)
        oldblocky = self.mouse_to_block(self.player.y)
        oldcell = self.maze.cells[oldblockx][oldblocky]
        newcell = self.maze.cells[newblockx][newblocky]
        if newcell == oldcell or newcell in oldcell.connected_neighbors:
            return True
        else:
            return False

    def forward(self):
        self.move_player(distance=5)

    def back(self):
        self.move_player(distance=-5)

    def left(self):
        self.move_player(dangle=-TAU/16)

    def right(self):
        self.move_player(dangle=TAU/16)

    def xor(self, stra, strb):
        if len(stra) != len(strb): raise ValueError('mismatched length')
        result = ''
        for a, b in zip(stra, strb):
            if a == b:
                result += '0'
            else:
                result += '1'
        return result

    def check_chromosome(self, *args):
        chromosome = self.chromosomevar.get()
        if self.valid_chromosome(chromosome):
            scores = []
            for seed in self.selected_seeds:
                match = self.xor(seed.chromosome, chromosome)
                score = match.count('1')
                scores.append(str(score))
            self.chromosomelabel['text'] = ', '.join(scores)
        else:
            self.chromosomelabel['text'] = ''

    def valid_chromosome(self, chromosome):
        return len(chromosome)==Seed.CHROMOSOMELENGTH and all([c in '01' for c in chromosome])


def main():
    global exitFlag
    exitFlag = False
    def on_quit():
        global exitFlag
        exitFlag = True
        rt.destroy()

    rt = Tkinter.Tk()
    rt.protocol("WM_DELETE_WINDOW", on_quit)
    game = Game()
    app = App(rt, game)
    app.grid()
    while not exitFlag:
        try:
            rt.mainloop()
        except KeyboardInterrupt:
            print 'Are you sure you want to quit?'
            response = response = raw_input('Type "Quit" to quit ')
            if response == 'Quit': break


if __name__ == '__main__':
    main()
