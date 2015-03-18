import maze

width = int(raw_input('width? '))
height = int(raw_input('height? '))

m = maze.Maze(width, height)

output = ''

for x in range(width):
    output += ' _'
output += '\n'

for y in range(height):
    output += '|'
    for x in range(width):
        cell = m.cells[x][y]
        if y < height-1:
            below = m.cells[x][y+1]
            if below not in cell.connected_neighbors:
                output += '_'
            else:
                output += ' '
        else:
            output += '_'

        if x < width-1:
            right = m.cells[x+1][y]
            if right not in cell.connected_neighbors:
                output += '|'
            else:
                output += ' '
        else:
            output += '|\n'

print output
