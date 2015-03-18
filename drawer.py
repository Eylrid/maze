class MazeDrawer:
    def __init__(self, canvas, maze, blocksize,
                 wallcolor='black', linecolor='red'):
        self.canvas = canvas
        self.maze = maze
        self.width = self.maze.width
        self.height = self.maze.height
        self.blocksize = blocksize

        self.image_width = self.width*blocksize+1
        self.image_height = self.height*blocksize+1

        self.wallcolor = wallcolor
        self.linecolor = linecolor

        self.draw_maze()

    def draw_maze(self):
        self.draw_outside_walls()
        self.draw_inside_walls()

    def draw_outside_walls(self):
        self.canvas.draw_line((0, 0, self.image_width-1, 0), fill=self.wallcolor, tag='outside')
        self.canvas.draw_line((0, self.image_height-1, self.image_width-1, self.image_height-1),
                              fill=self.wallcolor, tag='outside')
        self.canvas.draw_line((0, 0, 0, self.image_height), fill=self.wallcolor, tag='outside')
        self.canvas.draw_line((self.image_width-1, 0, self.image_width-1, self.image_height-1), 
                              fill=self.wallcolor, tag='outside')

    def draw_inside_walls(self):
        for x in range(self.width-1):
            for y in range(self.height-1):
                self.canvas.draw_point(((x+1)*self.blocksize, (y+1)*self.blocksize),
                                       fill=self.wallcolor, tag='wall')

        for y in range(self.height):
            for x in range(self.width):
                cell = self.maze.cells[x][y]
                if y < self.height-1:
                    below = self.maze.cells[x][y+1]
                    if below not in cell.connected_neighbors:
                        self.canvas.draw_line((x*self.blocksize, (y+1)*self.blocksize,
                                               (x+1)*self.blocksize, (y+1)*self.blocksize), 
                                              fill=self.wallcolor, tag='wall')

                if x < self.width-1:
                    right = self.maze.cells[x+1][y]
                    if right not in cell.connected_neighbors:
                        self.canvas.draw_line(((x+1)*self.blocksize, y*self.blocksize,
                                               (x+1)*self.blocksize, (y+1)*self.blocksize), 
                                              fill=self.wallcolor, tag='wall')


    def draw_path(self, x1, y1, x2, y2):
        path = self.maze.astar((x1, y1), (x2, y2))

        lastcell = path[0]
        for cell in path[1:]:
            self.canvas.draw_line((int((lastcell.x+0.5)*self.blocksize),
                                   int((lastcell.y+0.5)*self.blocksize),
                                   int((cell.x+0.5)*self.blocksize),
                                   int((cell.y+0.5)*self.blocksize)),
                                  fill=self.linecolor, tag='path')
            lastcell = cell


class Canvas:
    '''
    An object for drawing on various things.
    This is a stub to be subclassed.'''
    def __init__(self):
        pass

    def draw_line(self, coords, fill, tag=''):
        pass

    def draw_point(self, coords, fill, tag=''):
        pass

