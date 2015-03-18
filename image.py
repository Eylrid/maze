import Image, ImageDraw
import time, os
from drawer import MazeDrawer, Canvas
from maze import Maze

class ImageCanvas(Canvas):
    def __init__(self, im):
        self.im = im
        self.draw = ImageDraw.Draw(self.im)

    def draw_line(self, coords, fill, tag):
        self.draw.line(coords, fill=fill)

    def draw_point(self, coords, fill, tag):
        self.draw.point(coords, fill=fill)


class MazeImage:
    def __init__(self, width, height, blocksize,
                 background='white', wallcolor='black', linecolor='red'):
        self.width = width
        self.height = height
        self.blocksize = blocksize

        self.im_width = width*blocksize+1
        self.im_height = height*blocksize+1

        self.maze = Maze(self.width, self.height)
        self.im = Image.new('RGB', (self.im_width, self.im_height), background)
        self.canvas = ImageCanvas(self.im)
        self.mazedrawer = MazeDrawer(self.canvas, self.maze, self.blocksize,
                                     wallcolor='black', linecolor='red')

    def draw_path(self, x1, y1, x2, y2):
        self.mazedrawer.draw_path(x1, y1, x2, y2)

    def save(self, *args, **kwargs):
        self.im.save(*args, **kwargs)


def savepath():
    return os.path.join('out', str(time.time())+'.png')

def main():
    width = int(raw_input('width? '))
    height = int(raw_input('height? '))
    blocksize = int(raw_input('blocksize? '))
    x1 = int(raw_input('x1? '))
    y1 = int(raw_input('y1? '))
    x2 = int(raw_input('x2? '))
    y2 = int(raw_input('y2? '))
    mazeimage = MazeImage(width, height, blocksize)
    mazeimage.draw_path(x1, y1, x2, y2)
    mazeimage.save(savepath())

if __name__ == '__main__':
    main()
