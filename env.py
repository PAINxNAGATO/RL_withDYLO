# Imports:
import numpy as np  # To deal with data in form of matrices
import tkinter as tk  # To build GUI
import time  # Time is needed to slow down the agent and to see how he runs
from PIL import Image, ImageTk  # For adding images into the canvas widget
from itertools import permutations
import random
import math

# Setting the sizes for the environment
pixels = 64   # pixels
env_height, env_width = 10, 10  # grid dimentions

# Global variable for dictionary with coordinates for the final route
a = {}
flag = 1

obj_spaces = [(0, 2), (0, 4), (1, 7), (2, 9), (3, 1), (3, 3), (3, 5), (3, 9), (4, 1), (4, 3), (4, 6), (4, 9), (5, 0), (5, 1), (5, 6), (5, 7), (5, 9), (6, 0), (6, 3), (6, 6), (6, 7), (7, 4), (7, 6), (7, 7), (7, 9), (8, 0), (8, 1), (8, 2), (8, 4), (8, 6), (8, 7), (8, 8), (8, 9), (9, 1), (9, 3), (9, 6), (9, 7), (9, 8), (9, 9), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (7, 0), (8, 0), (0, 1), (1, 1), (2, 1), (6, 1), (7, 1), (8, 1), (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (0, 9), (1, 9), (6, 9)]

# cat_avail_space = [(9, 4), (9, 5), (8, 1), (8, 3), (8, 5), (7, 1), (7, 0), (7, 2), (7, 3), (6, 1), (6, 2), (6, 4), (6, 5), (5, 2), (5, 3), (5, 4), (5, 5), (4, 2), (4, 4), (4, 5), (3, 4), (3, 2), (2, 4), (2, 3), (2, 2), (9, 0), (9, 2)]

grid = permutations([i for i in range(env_width)], 2) # 0 to 9 taken 2 at a time: 10P2
cat_avail_space = [ item for item in grid if item not in obj_spaces ]
# print(cat_avail_space)

cat_collision = {} # {key: value} = {(2, 3): 6}
for pos in cat_avail_space:
    # pos = (0, 5) || (0 * 64, 5 * 64)
    pos = (pos[0] * pixels, pos[1] * pixels)
    # pos = (0, 320)
    cat_collision[pos] = 0
    #{(3, 4): 0, (4, 5): 0.........}
# print(cat_collision)

# list of avilable sq.
# dictionary of cat collisions

tcount1 = 0
tcount2 = 5
dy1, dx1 = 0, 0
dy2, dx2 = 0, 0

cat1_pos = {}
cat2_pos = {}
cat_pos = {} # cat1_pos + cat2_pos
for i in cat_avail_space:
    cat1_pos[i] = 0
    cat2_pos[i] = 0
    cat_pos[i] = 0

# Creating class for the environment
class Environment(tk.Tk, object):
    def __init__(self):
        super(Environment, self).__init__()
        self.action_space = ['up', 'down', 'left', 'right']
        self.n_actions = len(self.action_space)
        self.title('RL Q-learning')
        self.geometry('{0}x{1}'.format(env_height * pixels, env_height * pixels))
        self.build_environment()

        # Dictionaries to draw the final route
        self.d = {}
        self.f = {}

        # Key for the dictionaries
        self.i = 0

        # Writing the final dictionary first time
        self.c = True

        # Showing the steps for longest found route
        self.longest = 0

        # Showing the steps for the shortest route
        self.shortest = 0

        self.images = []

    # Function to build the environment
    def build_environment(self):
        global dy1, dx1, dy2, dx2, cat1_pos, cat2_pos

        self.canvas_widget = tk.Canvas(self,  bg='light green',
                                       height=env_height * pixels,
                                       width=env_width * pixels)

        # Uploading an image for background
        # img_background = Image.open("images/bg.png")
        # self.background = ImageTk.PhotoImage(img_background)
        # # Creating background on the widget
        # self.bg = self.canvas_widget.create_image(0, 0, anchor='nw', image=self.background)

        # Creating grid lines
        for column in range(0, env_width * pixels, pixels):
            x0, y0, x1, y1 = column, 0, column, env_height * pixels
            self.canvas_widget.create_line(x0, y0, x1, y1, fill='dark green')
        for row in range(0, env_height * pixels, pixels):
            x0, y0, x1, y1 = 0, row, env_height * pixels, row
            self.canvas_widget.create_line(x0, y0, x1, y1, fill='dark green')

        # Creating objects of Obstacles
        # Obstacle type 1 - road closed1
        img_obstacle1 = Image.open("images/trap_4.png")
        self.obstacle1_object = ImageTk.PhotoImage(img_obstacle1)
        # Obstacle type 2 - tree1
        img_obstacle2 = Image.open("images/trap_3.png")
        self.obstacle2_object = ImageTk.PhotoImage(img_obstacle2)
        # Obstacle type 3 - tree2
        img_obstacle3 = Image.open("images/trap_2.png")
        self.obstacle3_object = ImageTk.PhotoImage(img_obstacle3)
        # Obstacle type 4 - building1
        img_obstacle4 = Image.open("images/trap_1.png")
        self.obstacle4_object = ImageTk.PhotoImage(img_obstacle4)
        # Obstacle type 5 - building2
        img_obstacle5 = Image.open("images/cheese.png")
        self.obstacle5_object = ImageTk.PhotoImage(img_obstacle5)
        # Obstacle type 6 - road closed2
        img_obstacle6 = Image.open("images/cat_1.png")
        self.obstacle6_object = ImageTk.PhotoImage(img_obstacle6)
        # Obstacle type 7 - road closed3
        img_obstacle7 = Image.open("images/cat_2.png")
        self.obstacle7_object = ImageTk.PhotoImage(img_obstacle7)

        # Creating obstacles themselves
        # Obstacles 1
        self.obstacle1 = self.canvas_widget.create_image(pixels * 5, 0, anchor='nw', image=self.obstacle1_object)
        # Obstacle 2
        self.obstacle2 = self.canvas_widget.create_image(pixels * 6, 0, anchor='nw', image=self.obstacle1_object)
        # Obstacle 3
        self.obstacle3 = self.canvas_widget.create_image(pixels * 8, 0, anchor='nw', image=self.obstacle1_object)
        # Obstacle 4
        self.obstacle4 = self.canvas_widget.create_image(0, pixels * 2, anchor='nw', image=self.obstacle1_object)
        # Obstacle 5
        self.obstacle5 = self.canvas_widget.create_image(0, pixels * 4, anchor='nw', image=self.obstacle1_object)
        # Obstacle 6
        self.obstacle6 = self.canvas_widget.create_image(pixels * 2, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 7
        self.obstacle7 = self.canvas_widget.create_image(pixels * 3, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 8
        self.obstacle8 = self.canvas_widget.create_image(pixels * 4, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 9
        self.obstacle9 = self.canvas_widget.create_image(pixels * 5, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 10
        self.obstacle10 = self.canvas_widget.create_image(pixels * 7, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 11
        self.obstacle11 = self.canvas_widget.create_image(pixels * 8, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 12
        self.obstacle12 = self.canvas_widget.create_image(pixels * 9, pixels * 9, anchor='nw', image=self.obstacle1_object)
        # Obstacle 13
        self.obstacle13 = self.canvas_widget.create_image(pixels * 9, pixels * 8, anchor='nw', image=self.obstacle1_object)
        # Obstacle 14
        self.obstacle14 = self.canvas_widget.create_image(pixels * 9, pixels * 7, anchor='nw', image=self.obstacle1_object)
        # Obstacle 15
        self.obstacle15 = self.canvas_widget.create_image(pixels * 9, pixels * 6, anchor='nw', image=self.obstacle1_object)
        # Obstacle 16
        self.obstacle16 = self.canvas_widget.create_image(pixels * 9, pixels * 1, anchor='nw', image=self.obstacle1_object)
        # Obstacle 17
        self.obstacle17 = self.canvas_widget.create_image(pixels * 9, pixels * 3, anchor='nw', image=self.obstacle1_object)
        # Obstacle 18
        self.obstacle18 = self.canvas_widget.create_image(pixels * 5, pixels * 7, anchor='nw', image=self.obstacle1_object)
        # Obstacle 19
        self.obstacle19 = self.canvas_widget.create_image(pixels * 6, pixels * 7, anchor='nw', image=self.obstacle1_object)
        # Obstacle 20
        self.obstacle20 = self.canvas_widget.create_image(pixels * 7, pixels * 7, anchor='nw', image=self.obstacle1_object)
        # Obstacle 21
        self.obstacle21 = self.canvas_widget.create_image(pixels * 8, pixels * 7, anchor='nw', image=self.obstacle1_object)

        # Obstacle 22
        self.obstacle22 = self.canvas_widget.create_image(pixels * 4, pixels * 6, anchor='nw', image=self.obstacle2_object)
        # Obstacle 23
        self.obstacle23 = self.canvas_widget.create_image(pixels * 5, pixels * 6, anchor='nw', image=self.obstacle2_object)
        # Obstacle 24
        self.obstacle24 = self.canvas_widget.create_image(pixels * 6, pixels * 6, anchor='nw', image=self.obstacle2_object)
        # Obstacle 25
        self.obstacle25 = self.canvas_widget.create_image(pixels * 7, pixels * 6, anchor='nw', image=self.obstacle2_object)
        # Obstacle 26
        self.obstacle26 = self.canvas_widget.create_image(pixels * 8, pixels * 6, anchor='nw', image=self.obstacle2_object)

        # Obstacle 27
        self.obstacle27 = self.canvas_widget.create_image(pixels, pixels * 7, anchor='nw', image=self.obstacle3_object)
        # Obstacle 28
        self.obstacle28 = self.canvas_widget.create_image(pixels * 4, pixels * 1, anchor='nw', image=self.obstacle3_object)
        # Obstacle 29
        self.obstacle29 = self.canvas_widget.create_image(pixels * 4, pixels * 3, anchor='nw', image=self.obstacle3_object)
        # Obstacle 30
        self.obstacle30 = self.canvas_widget.create_image(pixels * 6, pixels * 3, anchor='nw', image=self.obstacle3_object)
        # Obstacle 31
        self.obstacle31 = self.canvas_widget.create_image(pixels * 8, pixels * 2, anchor='nw', image=self.obstacle3_object)
        # Obstacle 32
        self.obstacle32 = self.canvas_widget.create_image(pixels * 8, pixels * 4, anchor='nw', image=self.obstacle3_object)

        # Obstacle 33
        self.obstacle33 = self.canvas_widget.create_image(pixels * 3, pixels * 1, anchor='nw', image=self.obstacle4_object)
        # Obstacle 34
        self.obstacle34 = self.canvas_widget.create_image(pixels * 3, pixels * 3, anchor='nw', image=self.obstacle4_object)
        # Obstacle 35
        self.obstacle35 = self.canvas_widget.create_image(pixels * 3, pixels * 5, anchor='nw', image=self.obstacle4_object)
        # Obstacle 36
        self.obstacle36 = self.canvas_widget.create_image(pixels * 5, pixels * 1, anchor='nw', image=self.obstacle4_object)
        # Obstacle 37
        self.obstacle37 = self.canvas_widget.create_image(pixels * 7, pixels * 4, anchor='nw', image=self.obstacle4_object)

        # Obstacle 38
        dyn_obj_loc = random.choice(cat_avail_space) # (a, b)
        cat1_pos[dyn_obj_loc] += 1
        dy1 = dyn_obj_loc[0] # a
        dx1 = dyn_obj_loc[1] # b
        self.obstacle38 = self.canvas_widget.create_image(pixels * dy1, pixels * dx1, anchor='nw', image=self.obstacle6_object)

        # Obstacle 39
        dyn_obj_loc = random.choice(cat_avail_space)
        cat2_pos[dyn_obj_loc] += 1
        dy2 = dyn_obj_loc[0]
        dx2 = dyn_obj_loc[1]
        self.obstacle39 = self.canvas_widget.create_image(pixels * dy2, pixels * dx2, anchor='nw', image=self.obstacle7_object)

        # Final Point
        # img_flag = Image.open("images/cheeze.png")
        # self.flag_object = ImageTk.PhotoImage(img_flag)
        self.flag = self.canvas_widget.create_image(pixels * 8, pixels * 8, anchor='nw', image=self.obstacle5_object)

        # Uploading the image of Mobile Robot
        img_robot = Image.open("images/rat.png")
        self.robot = ImageTk.PhotoImage(img_robot)

        # Creating an agent with photo of Mobile Robot
        self.agent = self.canvas_widget.create_image(0, 0, anchor='nw', image=self.robot)

        # Packing everything
        self.canvas_widget.pack()

    def createRectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas_widget.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.canvas_widget.create_rectangle(x1, y1, x2, y2, **kwargs)

    # Function for cat movements 1:
    def cat1_move(self):
        global dy1, dx1, cat1_pos, cat_pos

        while flag:
            check1 = []
            time.sleep(0.2)
            if dy1+1 <= env_width-1 and (dy1+1, dx1) in cat_avail_space:
                # if ((dy1+1) * pixels, dx1 * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1+1, dx1))

            if dy1-1 >= 0 and (dy1-1, dx1) in cat_avail_space:
                # if ((dy1-1) * pixels, dx1 * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1-1, dx1))

            if dx1+1 <= env_width-1 and (dy1, dx1+1) in cat_avail_space:
                # if (dy1 * pixels, (dx1+1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1, dx1+1))

            if dx1-1 >= 0 and (dy1, dx1-1) in cat_avail_space:
                # if (dy1 * pixels, (dx1-1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1, dx1-1))

            if dy1-1 >= 0 and dx1-1 >= 0 and (dy1-1, dx1-1) in cat_avail_space:
                # if ((dy1-1) * pixels, (dx1-1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1-1, dx1-1))

            if dy1+1 <= env_width-1 and dx1+1 <= env_width-1 and (dy1+1, dx1+1) in cat_avail_space:
                # if ((dy1+1) * pixels, (dx1+1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1+1, dx1+1))

            if dy1-1 >= 0 and dx1+1 <= env_width-1 and (dy1-1, dx1+1) in cat_avail_space:
                # if ((dy1-1) * pixels, (dx1+1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1-1, dx1+1))

            if dy1+1 <= env_width-1 and dx1-1 >= 0 and (dy1+1, dx1-1) in cat_avail_space:
                # if ((dy1+1) * pixels, (dx1-1) * pixels) != self.canvas_widget.coords(self.agent):
                check1.append((dy1+1, dx1-1))

            if len(check1) == 0:
                dyn_obj_loc = random.choice(cat_avail_space)
                cat1_pos[dyn_obj_loc] += 1
                cat_pos[dyn_obj_loc] += 1
                dy1 = dyn_obj_loc[0]
                dx1 = dyn_obj_loc[1]
            else:
                random.shuffle(check1)
                dyn_obj_mov = random.choice(check1)
                cat1_pos[dyn_obj_mov] += 1
                cat_pos[dyn_obj_mov] += 1
                dy1 = dyn_obj_mov[0]
                dx1 = dyn_obj_mov[1]

                if cat_pos[dyn_obj_mov] == 1:
                    self.createRectangle((pixels * dy1), (pixels * dx1), (pixels * dy1) + 64, (pixels * dx1) + 64, fill='blue', alpha=0.1)
                if cat_pos[dyn_obj_mov] == 6:
                    self.createRectangle((pixels * dy1), (pixels * dx1), (pixels * dy1) + 64, (pixels * dx1) + 64, fill='blue', alpha=0.2)

            self.canvas_widget.moveto(self.obstacle38, pixels * dy1, pixels * dx1)

    # Function for cat movements 2:
    def cat2_move(self):
        global dy2, dx2, cat2_pos, cat_pos

        while flag:
            check2 = []
            time.sleep(0.2)
            if dy2+1 <= env_width-1 and (dy2+1, dx2) in cat_avail_space:
                # if (dy2+1, dx2) != self.canvas_widget.coords(self.agent):
                check2.append((dy2+1, dx2))

            if dy2-1 >= 0 and (dy2-1, dx2) in cat_avail_space:
                # if (dy2-1, dx2) != self.canvas_widget.coords(self.agent):
                check2.append((dy2-1, dx2))

            if dx2+1 <= env_width-1 and (dy2, dx2+1) in cat_avail_space:
                # if (dy2, dx2+1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2, dx2+1))

            if dx2-1 >= 0 and (dy2, dx2-1) in cat_avail_space:
                # if (dy2, dx2-1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2, dx2-1))

            if dy2-1 >= 0 and dx2-1 >= 0 and (dy2-1, dx2-1) in cat_avail_space:
                # if (dy2-1, dx2-1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2-1, dx2-1))

            if dy2+1 <= env_width-1 and dx2+1 <= env_width-1 and (dy2+1, dx2+1) in cat_avail_space:
                # if (dy2+1, dx2+1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2+1, dx2+1))

            if dy2-1 >= 0 and dx2+1 <= env_width-1 and (dy2-1, dx2+1) in cat_avail_space:
                # if (dy2-1, dx2+1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2-1, dx2+1))

            if dy2+1 <= env_width-1 and dx2-1 >= 0 and (dy2+1, dx2-1) in cat_avail_space:
                # if (dy2+1, dx2-1) != self.canvas_widget.coords(self.agent):
                check2.append((dy2+1, dx2-1))

            if len(check2) == 0:
                dyn_obj_loc = random.choice(cat_avail_space)
                cat2_pos[dyn_obj_loc] += 1
                cat_pos[dyn_obj_loc] += 1
                dy2 = dyn_obj_loc[0]
                dx2 = dyn_obj_loc[1]
            else:
                random.shuffle(check2)
                dyn_obj_mov = random.choice(check2)
                cat2_pos[dyn_obj_mov] += 1
                cat_pos[dyn_obj_mov] += 1
                dy2 = dyn_obj_mov[0]
                dx2 = dyn_obj_mov[1]

                if cat_pos[dyn_obj_mov] == 1:
                    self.createRectangle((pixels * dy2), (pixels * dx2), (pixels * dy2) + 64, (pixels * dx2) + 64, fill='blue', alpha=0.1)
                if cat_pos[dyn_obj_mov] == 6:
                    self.createRectangle((pixels * dy2), (pixels * dx2), (pixels * dy2) + 64, (pixels * dx2) + 64, fill='blue', alpha=0.2)

            self.canvas_widget.moveto(self.obstacle39, pixels * dy2, pixels * dx2)

    # Function to reset the environment and start new Episode
    def reset(self):

        self.update()
        #time.sleep(0.1)

        # Updating agent
        self.canvas_widget.delete(self.agent)
        self.agent = self.canvas_widget.create_image(0, 0, anchor='nw', image=self.robot)

        # # Clearing the dictionary and the i
        self.d = {}
        self.i = 0

        # Return observation
        return self.canvas_widget.coords(self.agent)

    # Function to get the next observation and reward by doing next step
    def step(self, action):
        # Current state of the agent
        state = self.canvas_widget.coords(self.agent)
        base_action = np.array([0, 0])

        # Updating next state according to the action
        # Action 'up'
        if action == 0:
            if state[1] >= pixels:
                base_action[1] -= pixels
        # Action 'down'
        elif action == 1:
            if state[1] < (env_height - 1) * pixels:
                base_action[1] += pixels
        # Action right
        elif action == 2:
            if state[0] < (env_width - 1) * pixels:
                base_action[0] += pixels
        # Action left
        elif action == 3:
            if state[0] >= pixels:
                base_action[0] -= pixels

        # Moving the agent according to the action
        # time.sleep(0.01)
        self.canvas_widget.move(self.agent, base_action[0], base_action[1])

        # Writing in the dictionary coordinates of found route
        self.d[self.i] = self.canvas_widget.coords(self.agent)

        # Updating next state
        next_state = self.d[self.i]
        # print(next_state)

        # Updating key for the dictionary
        self.i += 1

        # Calculating the reward for the agent
        if next_state == self.canvas_widget.coords(self.flag):
            reward = 100
            done = True
            next_state = 'goal'

            # Filling the dictionary first time
            if self.c == True:
                for j in range(len(self.d)):
                    self.f[j] = self.d[j]
                self.c = False
                self.longest = len(self.d)
                self.shortest = len(self.d)

            # Checking if the currently found route is shorter
            if len(self.d) < len(self.f):
                # Saving the number of steps for the shortest route
                self.shortest = len(self.d)
                # Clearing the dictionary for the final route
                self.f = {}
                # Reassigning the dictionary
                for j in range(len(self.d)):
                    self.f[j] = self.d[j]

            # Saving the number of steps for the longest route
            if len(self.d) > self.longest:
                self.longest = len(self.d)

        elif next_state in [self.canvas_widget.coords(self.obstacle1),
                            self.canvas_widget.coords(self.obstacle2),
                            self.canvas_widget.coords(self.obstacle3),
                            self.canvas_widget.coords(self.obstacle4),
                            self.canvas_widget.coords(self.obstacle5),
                            self.canvas_widget.coords(self.obstacle6),
                            self.canvas_widget.coords(self.obstacle7),
                            self.canvas_widget.coords(self.obstacle8),
                            self.canvas_widget.coords(self.obstacle9),
                            self.canvas_widget.coords(self.obstacle10),
                            self.canvas_widget.coords(self.obstacle11),
                            self.canvas_widget.coords(self.obstacle12),
                            self.canvas_widget.coords(self.obstacle13),
                            self.canvas_widget.coords(self.obstacle14),
                            self.canvas_widget.coords(self.obstacle15),
                            self.canvas_widget.coords(self.obstacle16),
                            self.canvas_widget.coords(self.obstacle17),
                            self.canvas_widget.coords(self.obstacle18),
                            self.canvas_widget.coords(self.obstacle19),
                            self.canvas_widget.coords(self.obstacle20),
                            self.canvas_widget.coords(self.obstacle21),
                            self.canvas_widget.coords(self.obstacle22),
                            self.canvas_widget.coords(self.obstacle23),
                            self.canvas_widget.coords(self.obstacle24),
                            self.canvas_widget.coords(self.obstacle25),
                            self.canvas_widget.coords(self.obstacle26),
                            self.canvas_widget.coords(self.obstacle27),
                            self.canvas_widget.coords(self.obstacle28),
                            self.canvas_widget.coords(self.obstacle29),
                            self.canvas_widget.coords(self.obstacle30),
                            self.canvas_widget.coords(self.obstacle31),
                            self.canvas_widget.coords(self.obstacle32),
                            self.canvas_widget.coords(self.obstacle33),
                            self.canvas_widget.coords(self.obstacle34),
                            self.canvas_widget.coords(self.obstacle35),
                            self.canvas_widget.coords(self.obstacle36),
                            self.canvas_widget.coords(self.obstacle37)]:
            reward = -10
            done = True
            next_state = 'obstacle'

            # Clearing the dictionary and the i
            self.d = {}
            self.i = 0

        elif next_state in [self.canvas_widget.coords(self.obstacle38)]:
            # if cat_collision[tuple(next_state)] > 2:
            if 1:
                time.sleep(0.2)
                reward = -5
                done = True
                next_state = 'obstacle'

                # Clearing the dictionary and the i
                self.d = {}
                self.i = 0
            else:
                cat_collision[tuple(next_state)] += 1
                reward = -1
                done = False

        elif next_state in [self.canvas_widget.coords(self.obstacle39)]:
            # if cat_collision[tuple(next_state)] > 2:
            if 1:
                time.sleep(0.2)
                reward = -5
                done = True
                next_state = 'obstacle'

                # Clearing the dictionary and the i
                self.d = {}
                self.i = 0
            else:
                cat_collision[tuple(next_state)] += 1
                reward = -1
                done = False

        else:
            a_pos = self.canvas_widget.coords(self.agent)
            c1_pos = self.canvas_widget.coords(self.obstacle38)
            c2_pos = self.canvas_widget.coords(self.obstacle39)
            a_c1 = math.sqrt((a_pos[0] - c1_pos[0])**2 + (a_pos[1] - c1_pos[1])**2)
            a_c2 = math.sqrt((a_pos[0] - c2_pos[0])**2 + (a_pos[1] - c2_pos[1])**2)

            # print(f'a_c1 = {a_c1}')
            # print(f'a_c2 = {a_c2}')

            if a_c1 >= 3 * pixels and a_c2 >= 3 * pixels:
                reward = -1

            elif (a_c1 >= 2 * pixels and a_c2 >= 3 * pixels) or (a_c1 >= 3 * pixels and a_c2 >= 2 * pixels):
                reward = -1.5

            elif a_c1 >= 2 * pixels and a_c2 >= 2 * pixels:
                reward = -2

            elif (a_c1 >= 2 * pixels and a_c2 >= pixels) or (a_c1 >= pixels and a_c2 >= 2 * pixels):
                reward = -2.5

            else:
                reward = -3

            done = False
            # print(f'reward = {reward}\n')

        return next_state, reward, done

    # Function to refresh the environment
    def render(self):
        #time.sleep(0.03)
        self.update()

    # Function to show the found route
    def final(self):
        global flag
        flag = 0
        # Deleting the agent at the end
        self.canvas_widget.delete(self.agent)

        # Showing the number of steps
        print('The shortest route:', self.shortest)
        print('The longest route:', self.longest)

        # Creating initial point
        origin = np.array([32, 32])
        self.initial_point = self.canvas_widget.create_oval(
            origin[0] - 10, origin[1] - 10,
            origin[0] + 10, origin[1] + 10,
            fill='red', outline='red')

        # Filling the route
        for j in range(len(self.f)):
            # Showing the coordinates of the final route
            print(self.f[j])
            self.track = self.canvas_widget.create_oval(
                self.f[j][0] + origin[0] - 10, self.f[j][1] + origin[0] - 10,
                self.f[j][0] + origin[0] + 10, self.f[j][1] + origin[0] + 10,
                fill='red', outline='red')
            # Writing the final route in the global variable a
            a[j] = self.f[j]


# Returning the final dictionary with route coordinates
# Then it will be used in agent_brain.py
def final_states():
    return a


# This we need to debug the environment
# If we want to run and see the environment without running full algorithm
if __name__ == '__main__':
    env = Environment()
    env.mainloop()
