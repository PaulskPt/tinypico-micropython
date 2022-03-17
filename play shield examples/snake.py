"""
   The contents of this file taken out of main.py (snake game)
   to have this Snake class in a separate file

"""
import random, math
from defs import pskDEFS  # get various definitions

n = pskDEFS()

my_debug = n.get_debug()
hori = n.get_hor()
vert = n.get_vert()

rt = n.get_rot()
rot_000 = rt[0]
rot_090 = rt[1]
rot_180 = rt[2]
rot_270 = rt[3]

dr = n.get_dir()
dir_0 = dr[0]
dir_1 = dr[1]
dir_2 = dr[2]
dir_3 = dr[3]

dir_dict = n.get_dir_dict()

class Snake:
    def reset(self, x, y, len, dir):
        self._moves = 0
        self._dead = False
        self._length = len
        self._dir = dir
        self._speed = 0.12
        self._score = 0
        self._fruit = []
        self._x = x  # added by @Paulskpt
        self._y = y  # idem
        self.ul = n.get_ul()  # snake disp limit upper-left
        self.lr = n.get_lr()  # snake disp limit lower-right
        if my_debug:
            print("Snake (reset) starts at position hor: {}, vert: {}, length: {}, direction: {}".format(self._x,
            self._y, len, dir_dict[self._rotation][dir]))
        # set snake head position
        self._list = [ [self._x, self._y] ]
        # dynamically create snake body based on starting position
        for i in range( self._length-1 ):

            if self._dir == dir_0:
                self._y += 2
            elif self._dir == dir_1:
                self._x -= 2
            elif self._dir == dir_2:
                self._y -= 2
            elif self._dir == dir_3:
                self._x += 2
            
            self._list.append( [self._x, self._y] )
        
        self.add_fruit()

    # Parameters dw and dh added by @Paulskpt
    def __init__(self, dw, dh, x, y, len, dir, disp_rotation):
        self._dw = dw  # display width
        self._dh = dh  # display height
        self._rotation = disp_rotation
        self.reset( x, y, len, dir )

    def set_dir(self, dir):
        # Chnage directiom
        self._dir += dir

        # Wrap direction
        if self._dir < 0:
            self._dir = 3
        elif self._dir > 3:
            self. _dir = 0

    def move(self):
        # Increase snake length every 10 moves
        # self._moves += 1
        # if self._moves == 10:
        #     self._moves = 0
        #     self._length += 1
        if self._dh > self._dw:  # if the height > width then reverse their values
            t = self._dw
            self._dw = self._dh
            self._dh = t
            if my_debug:
                print("Snake::move() dimensions after being reversed: dw,dh: ({},{}), dir: {}".format(self._dw, self._dh, dir_dict[self._rotation][self._dir]))
        else:
            if my_debug:
                print("Snake::move(): dw,dh: ({},{})".format(self._dw, self._dh ))
        remove_tail = [0,0,0,0]
        # renamed x,y into tx,ty to signify tail (mod by @Paulskpt)
        if len( self._list ) == self._length:
            tx,ty = self._list[ self._length-1 ]
            remove_tail[0] = tx
            remove_tail[1] = ty
            del self._list[ self._length-1 ]

        # renamed x,y into hx,hy to signify head (mod by @Paulskpt)
        # Grab the x,y of the head
        hx, hy = self._list[0]

        # move the head based on the current direction
        if self._dir == dir_0:   # (move on contrary as defined reset() ?)
            hy -= 2
        elif self._dir == dir_1:
            hx += 2
        elif self._dir == dir_2:
            hy += 2
        elif self._dir == dir_3:
            hx -= 2
            
            
        """

           Snake display move limits (for the 160x80 ST7735 display model)
           
                  6                        160
                  |                         |
           26  ---+-------------------------+---      (6,26)...(160,104)
                  |                         |
                  |                         |
                  |                         |
                  |                         |
                  |                         |
          104  ---+-------------------------+---             
                  |                         |

        """

        # Empirically determined values
        # ul = (6, 26)    # ul = upper-left
        # lr = (160, 104) # dr = lower-right
        
        # Did we hit the outer bounds of the level?
        #hit_bounds = self._x < 1 or self._y < 1 or self._x > 125 or self._y > 61
        #hit_bounds = hx < 1 or hy < 1 or hx > self._dw-1 or hy > self._dh-1
        hit_bounds = hx < self.ul[hori] or hy < self.ul[vert] or hx > self.lr[hori] or hy > self.lr[vert]

        # Is the x,y position already in the list? If so, we hit ourselves and died - we also died if we hit the edge of the level 
        self._dead = self._list.count( [hx, hy] ) > 0 or hit_bounds

        # Add the next position as the head of the snake
        self._list.insert( 0, [hx, hy] )

        # Did we eat any fruit?
        for f in self._fruit:
            fx,fy = f

            if self._x >= fx-2 and self._x <= fx+1 and self._y >= fy-2 and self._y <= fy+1:
                remove_tail[2] = fx
                remove_tail[3] = fy
                self.eat_food()
                self._fruit.remove( f )
                self.add_fruit()
                
        if my_debug:
            print("Snake::move(): pos hx,hy: ({},{}), dir: {}".format(hx, hy, dir_dict[self._rotation][self._dir]))
            print("All fruit positions: ", self._fruit)
            print("Fruit position: ({},{})".format(self._fruit[0][hori], self._fruit[0][vert]))

        return remove_tail

    def is_dead(self):
        return self._dead

    def get_positions(self):
        return self._list

    def get_speed(self):
        return self._speed

    def get_score(self):
        return self._score

    def eat_food(self):
        self._score += 1
        self._length += 2
        # reduce the speed time delay, burt clamped between 0.05 and 0.12
        self._speed = max(0.01, min( self._speed - 0.01, 0.12))

        # print("Score {}, Speed {}".format( self._score, self._speed))

    def add_fruit(self):
        fx = random.randrange(2,60) * 2
        if fx > self.lr[hori]:  # was > self._dw:   # if block added by @Paulskpt
            fx = self.lr[hori] # self._dw
        fy = random.randrange(2,30) * 2
        if fy > self.lr[vert]:  # was > self._dh:  # if block added by @Paulskpt
            fy = self.lr[vert] #self._dh
        self._fruit.append( (fx, fy) )

    def get_fruit_positions(self):
        return self._fruit