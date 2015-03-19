import maze, image
import Tkinter, ImageTk
import random
import pickle, os
from drawer import MazeDrawer, Canvas
from maze import Maze
from game import Game, Seed
import math
TAU = math.pi*2
SAVEFILE = 'save.pkl'

class CanvasCanvas(Canvas):
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_line(self, coords, fill, tag):
        self.canvas.create_line(*coords, fill=fill, tag=tag)

    def draw_point(self, coords, fill, tag):
        x, y = coords
        self.canvas.create_line(x, y, x+1, y+1, fill=fill, tag=tag)


class App(Tkinter.Frame):
    VIEWANGLE = TAU/6
    VIEWSLICES = 300
    SLICEANGLE = VIEWANGLE/VIEWSLICES
    def __init__(self, master, game, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.game = game
        self.canvas_width = self.game.width*self.game.blocksize + 1
        self.canvas_height = self.game.height*self.game.blocksize + 1
        self.block = (0, 0)
        self.create_widgets()
        self.draw_canvas = CanvasCanvas(self.canvas)
        self.drawer = MazeDrawer(self.draw_canvas, self.game.maze, self.game.blocksize)
        self.create_player()
        self.create_seeds()

    def create_widgets(self):
        self.canvas = Tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind('<Button-1>', self.click)        

        self.threedcanvas = Tkinter.Canvas(self, width=App.VIEWSLICES, height=App.VIEWSLICES)
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

    def save(self):
        with open(SAVEFILE, 'w') as file:
            pickle.dump(self.game, file)

    def create_player(self):
        self.create_viewlines()
        self.create_3d_lines()
        x1, y1, x2, y2 = self.get_player_line_coords()
        self.player_line = self.canvas.create_line(x1, y1, x2, y2, fill='red')

    def update_player(self):
        angles = self.get_viewangles()
        endpoints = [self.get_next_wall(self.game.player.x, self.game.player.y, a) for a in angles]
        relangles = self.get_relative_angles()
        for i in range(App.VIEWSLICES):
            (x, y), distance, direction = endpoints[i]
            self.canvas.coords(self.viewlines[i], self.game.player.x, self.game.player.y, x, y)

            wallheight = App.VIEWSLICES/(distance*math.tan(App.VIEWANGLE)*math.cos(relangles[i])*2)
            color = {(1,0):'green', (0,1):'blue', (-1,0):'yellow', (0,-1):'red'}[direction]
            self.threedcanvas.coords(self.threedlines[i], i, App.VIEWSLICES/2-wallheight,
                                     i, App.VIEWSLICES/2+wallheight)
            self.threedcanvas.itemconfig(self.threedlines[i], fill=color)

        x1, y1, x2, y2 = self.get_player_line_coords()
        self.canvas.coords(self.player_line, x1, y1, x2, y2)

    def create_viewlines(self):
        angles = self.get_viewangles()
        endpoints = [self.get_view_line_endpoints(a) for a in angles]
        self.viewlines = [self.canvas.create_line(self.game.player.x, self.game.player.y, x, y, fill='black') for x, y in endpoints]

    def create_3d_lines(self):
        self.threedlines = []
        for i in range(App.VIEWSLICES):
            self.threedlines.append(self.threedcanvas.create_line(i, 0, i, App.VIEWSLICES))

    def create_seeds(self):
        self.seed_items = {}
        for seed in self.game.seeds:
            self.draw_seed(seed)


    def create_seed(self, x, y, chromosome=None):
        seed = self.game.create_seed(x, y, chromosome)
        self.draw_seed(seed)

    def draw_seed(self, seed):
        item = self.canvas.create_rectangle(seed.x*self.game.blocksize+2,
                                            seed.y*self.game.blocksize+2,
                                            (seed.x+1)*self.game.blocksize-2,
                                            (seed.y+1)*self.game.blocksize-2,
                                            fill=seed.color,
                                            outline=seed.color,
                                            tag='seed')
        self.seed_items[seed] = item

    def remove_seed(self, seed):
        self.game.remove_seed(seed)
        self.canvas.delete(self.seed_items[seed])

    def get_relative_angles(self):
        angles = []
        for i in range(App.VIEWSLICES):
            angles.append(-App.VIEWANGLE/2 + App.SLICEANGLE*i)
        return angles

    def get_viewangles(self):
        angles = [a+self.game.player.angle for a in self.get_relative_angles()]
        return angles

    def get_view_line_endpoints(self, angle):
        return self.get_next_wall(self.game.player.x, self.game.player.y, angle)[0]

    def get_player_line_coords(self):
        point, distance, direction = self.get_next_wall(self.game.player.x, self.game.player.y, self.game.player.angle)
        x, y = point
        return self.game.player.x, self.game.player.y, x, y

    def get_next_wall(self, x, y, angle, blockx=None, blocky=None):
        angle = angle%TAU
        if blockx==None: blockx = int(x/self.game.blocksize)
        if blocky==None: blocky = int(y/self.game.blocksize)
        wall_point, direction, distance = self.get_wall_point(x, y, angle)
        nextx = blockx + direction[0]
        nexty = blocky + direction[1]
        if not self.block_in_range(nextx, nexty):
            return wall_point, distance, direction

        cell = self.game.maze.cells[blockx][blocky]
        nextcell = self.game.maze.cells[nextx][nexty]
        if nextcell in self.game.maze.connected_neighbors_map[cell.x][cell.y]:
            wall_point, newdist, direction =  self.get_next_wall(wall_point[0], wall_point[1],
                                                      angle, nextx, nexty)
            distance += newdist

        return wall_point, distance, direction

    def get_wall_point(self, x, y, angle):
        blockx = x/self.game.blocksize
        blocky = y/self.game.blocksize
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
            point = (wallx*self.game.blocksize, (blocky+distance*math.sin(angle))*self.game.blocksize)

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
                point = ((blockx+distance*math.cos(angle))*self.game.blocksize, wally*self.game.blocksize)

        return point, direction, distance

    def draw_path(self, coords):
        self.canvas.delete('path')
        self.drawer.draw_path(*coords)

    def seed_step(self):
        self.eat_seeds()
        seedenergy = 0.1/len(self.game.seeds)
        for seed in self.game.seeds[:]:
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
        blockx = self.mouse_to_block(self.game.player.x)
        blocky = self.mouse_to_block(self.game.player.y)
        seeds = self.game.seed_map[blockx][blocky]
        if seeds:
            print '%d seeds eaten' %len(seeds)
            for seed in seeds[:]:
                self.remove_seed(seed)

    def mouse_to_block(self, x):
        return int(math.floor(((x)/self.game.blocksize)))

    def block_in_range(self, x, y):
        if x < 0 or x >= self.game.width or y < 0 or y >= self.game.height:
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
        seeds = self.game.seed_map[self.block[0]][self.block[1]]
        if seeds:
            print '*****'
            for seed in seeds:
                print 'Seed:'
                print '-chromosome:', seed.chromosome
                print '-color:', seed.color
                print '-mutation rate: %d/16' %seed.mutability
        self.game.selected_seeds = seeds
        self.check_chromosome()

    def move_player(self, *args, **kwargs):
        if not self.player_can_move(*args, **kwargs): return
        self.game.player.move(*args, **kwargs)
        self.seed_step()
        self.update_player()
        self.save()

    def player_can_move(self, *args, **kwargs):
        x, y, angle = self.game.player.relative_point(*args, **kwargs)
        newblockx = self.mouse_to_block(x)
        newblocky = self.mouse_to_block(y)
        if not self.block_in_range(newblockx, newblocky):
            return False

        oldblockx = self.mouse_to_block(self.game.player.x)
        oldblocky = self.mouse_to_block(self.game.player.y)
        oldcell = self.game.maze.cells[oldblockx][oldblocky]
        newcell = self.game.maze.cells[newblockx][newblocky]
        if newcell == oldcell or newcell in self.game.maze.connected_neighbors_map[oldcell.x][oldcell.y]:
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
            for seed in self.game.selected_seeds:
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
    if os.path.exists(SAVEFILE):
        with open(SAVEFILE, 'r') as file:
            game = pickle.load(file)
    else:
        game = Game()
        with open(SAVEFILE, 'w') as file:
            pickle.dump(game, file)

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
