
# File: defs.py
# Used in main.py and snake.py
# Created 2022-03-16 by @Paulskpt


class pskDEFS:
    
    def __init__(self):
    
        self.my_debug = True

        self.hor = 0
        self.vert = 1

        self.rot_000 = 0
        self.rot_090 = 1
        self.rot_180 = 2
        self.rot_270 = 3

        self.dir_0 = 0
        self.dir_1 = 1
        self.dir_2 = 2
        self.dir_3 = 3

        self.dir_dict = {self.rot_000: {0: "left",  1: "up",    2: "right", 3: "down" },  # outer key = display rotation
                         self.rot_090: {0: "down",  1: "left",  2: "up",    3: "right"},  # inner key = snake direction
                         self.rot_180: {0: "right", 1: "down",  2: "left",  3: "up"   },
                         self.rot_270: {0: "up",    1: "right", 2: "down",  3: "left" }}
    
    
        # Snake display limits
        self.ul = (6, 26)    # ul = upper-left
        self.lr = (160, 104) # dr = lower-right
    
    
    def get_debug(self):
        return self.my_debug
    
    def get_hor(self):
        return self.hor
    
    def get_vert(self):
        return self.vert
    
    def get_rot(self):
        return (self.rot_000, self.rot_090, self.rot_180, self.rot_270)
    
    def get_dir(self):
        return (self.dir_0, self.dir_1, self.dir_2, self.dir_3)
    
    def get_dir_dict(self):
        return self.dir_dict
    
    def get_ul(self):  # get upper-left display boundary
        return self.ul
    
    def get_lr(self):  # get lower-right display boundary
        return self.lr 