import random

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frontier = False
        self.closed = False

    def __repr__(self):
        return '<cell (%d, %d)>' %(self.x, self.y)

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
        self.neighbors_map = [[[] for y in range(self.height)] for x in range(self.width)]
        self.connected_neighbors_map = [[[] for y in range(self.height)] for x in range(self.width)]
        self.connectable_neighbors_map = [[[] for y in range(self.height)] for x in range(self.width)]
        self.create_cells()
        self.add_neighbors()
        self.connect()

    def add_neighbor(self, cella, cellb):
        self.neighbors_map[cella.x][cella.y].append(cellb)
        self.connectable_neighbors_map[cella.x][cella.y].append(cellb)

    def connect_neighbor(self, cella, cellb):
        if cellb not in self.connectable_neighbors_map[cella.x][cella.y]:
            raise IndexError('other not in connectable neighbors')

        self.connectable_neighbors_map[cella.x][cella.y].remove(cellb)
        self.connected_neighbors_map[cella.x][cella.y].append(cellb)

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
                    self.add_neighbor(cell1, cell2)

    def connect(self):
        cell = random.choice(self.all_cells)
        frontier = [cell]
        cell.frontier = True
        closed = []
        while frontier:
            expand = frontier[-1]
            if self.connectable_neighbors_map[expand.x][expand.y]:
                other = random.choice(self.connectable_neighbors_map[expand.x][expand.y])
                if other.frontier or other.closed:
                    self.connectable_neighbors_map[expand.x][expand.y].remove(other)
                else:
                    self.connect_neighbor(expand, other)
                    self.connect_neighbor(other, expand)
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
        status_map[start_cell.x][start_cell.y] = 'f'
        endfound = False
        while frontier:
            frontier.sort(key=lambda x: x.t)
            loc = frontier.pop()
            cell = loc.object
            status_map[cell.x][cell.y] = 'c'
            newf = loc.f + 1
            for neighbor in self.connected_neighbors_map[cell.x][cell.y]:
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

