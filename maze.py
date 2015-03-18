import random

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.connected_neighbors = []
        self.connectable_neighbors = []
        self.frontier = False
        self.closed = False

    def __repr__(self):
        return '<cell (%d, %d)>' %(self.x, self.y)

    def add_neighbor(self, other):
        self.neighbors.append(other)
        self.connectable_neighbors.append(other)

    def connect(self, other):
        if other not in self.connectable_neighbors:
            raise IndexError('other not in connectable neighbors')

        self.connectable_neighbors.remove(other)
        self.connected_neighbors.append(other)

    def dist(self, other):
        return abs(self.x-other.x) + abs(self.y-other.y)


class AStarLoc:
    def __init__(self, object, f, h, last=None):
        self.object = object
        self.f = f
        self.h = h
        self.t = self.f+self.h
        self.last = last


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.create_cells()
        self.add_neighbors()
        self.connect()

    def create_cells(self):
        self.cells = []
        self.all_cells = []
        for x in range(self.width):
            column = []
            for y in range(self.height):
                cell = Cell(x,y)
                column.append(cell)
                self.all_cells.append(cell)
            self.cells.append(column)

    def add_neighbors(self):
        directions = {'u':(0,-1),
                      'd':(0,1),
                      'l':(-1,0),
                      'r':(1,0),}
        for x in range(self.width):
            xds = []
            if x > 0:
                xds.append('l')
            if x < self.width-1:
                xds.append('r')
            for y in range(self.height):
                cell1 = self.cells[x][y]
                yds = []
                if y > 0:
                    yds.append('u')
                if y < self.height-1:
                    yds.append('d')
                for d in xds+yds:
                    dx, dy = directions[d]
                    x2 = x + dx
                    y2 = y + dy
                    cell2 = self.cells[x2][y2]
                    cell1.add_neighbor(cell2)

    def connect(self):
        cell = random.choice(self.all_cells)
        frontier = [cell]
        cell.frontier = True
        closed = []
        while frontier:
            expand = frontier[-1] #random.choice(frontier)
            if expand.connectable_neighbors:
                other = random.choice(expand.connectable_neighbors)
                if other.frontier or other.closed:
                    expand.connectable_neighbors.remove(other)
                else:
                    expand.connect(other)
                    other.connect(expand)
                    frontier.append(other)
                    other.frontier = True
            else:
                frontier.remove(expand)
                expand.frontier = False
                closed.append(expand)
                expand.closed = True

            if random.randint(0,100)==0:
                print 'frontier:', len(frontier)
                print 'closed:', len(closed)

    def astar(self, start, end):
        start_cell = self.cells[start[0]][start[1]]
        end_cell = self.cells[end[0]][end[1]]
        startloc = AStarLoc(start_cell, 0, start_cell.dist(end_cell))
        frontier = [startloc]
        status_map = [['o' for y in range(self.height)] for x in range(self.width)]
        #import pdb; pdb.set_trace()
        status_map[start_cell.x][start_cell.y] = 'f'
        endfound = False
        while frontier:
            frontier.sort(key=lambda x: x.t)
            loc = frontier.pop()
            cell = loc.object
            status_map[cell.x][cell.y] = 'c'
            newf = loc.f + 1
            for neighbor in cell.connected_neighbors:
                newloc = AStarLoc(neighbor, newf,
                                  neighbor.dist(end_cell),
                                  loc)
                if neighbor == end_cell:
                    endfound = True
                    loc = newloc
                    break

                if status_map[neighbor.x][neighbor.y] == 'o':
                    frontier.append(newloc)
                    status_map[neighbor.x][neighbor.y] = 'f'

            if endfound:
                break

        if endfound:
            path = [loc.object]
            while loc.last:
                loc = loc.last
                path.append(loc.object)
            path.reverse()
            return path

