import numpy as np
import math
from Tkinter import *
import random
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import skimage
from PIL import Image

def start():
    global coord, pos, c, h_max, v_max, r,empty_ID, data, hexIDs, sol, moves, started, img, xc, yc
    start_button.configure(state=DISABLED)
    canvas.delete(ALL)

    c = int(size_of_puzzle_widget.get())
    xc = x / 2.0
    yc = y / 2.0
    h_max = 1 + 3 / 2 * c
    v_max = math.sqrt(3) / 2 * (1 + 2 * c)
    r = min((x-10) / (2.0 * h_max), (y-10) / (2.0 * v_max))
    coord = np.array([[0, 0]])
    pos = np.array([[xc, yc]])
    empty_ID = 0
    hexIDs = [0]
    data = []
    moves = 0
    img = mpimg.imread('photo.jpg')

    for m in range(-c, c + 1):
        for n in range(-c, c + 1):
            if not ((m > (-n + c)) or (m < (-n - c))):
                if not (m == 0 and n == 0):
                    coord = np.append(coord, [[m, n]], axis=0)
                    z = hexagon(m, n)
                    pos = np.append(pos, [z], axis=0)
                    points = []
                    for k in range(6):
                        x1, y1 = z[0] + r * np.cos(k * np.pi / 3), z[1] + r * np.sin(k * np.pi / 3)
                        points.extend([x1, y1])
                    newHexID = canvas.create_polygon(points, activefill="beige", fill="red", outline="blue", width=4)
                    hexIDs.append(newHexID)
                    canvas.tag_bind(newHexID, '<ButtonPress-1>', click_tile)
                    getImg(z,r)
                    # im = PhotoImage(file="baby_dragon.gif")
                    # canvas.create_image(0,0,image=im)
    sol = list(hexIDs)
    mix_up(0)
    solve_button.configure(state=ACTIVE)
    moves = 0
    started = True

def getImg(z,r):
    cropped_img = img[int(z[1]-math.sqrt(3)/2 *r)-2:int(z[1]+ math.sqrt(3)/2 *r)+2,int(z[0]-r-2):int(z[0]+r+2)]
    print "The shape of the cropped dragon image is: ", cropped_img.shape
    height = cropped_img.shape[0]
    width = cropped_img.shape[1]
    newsize = (height, width)
    target = Image.new('RGBA', newsize, (0, 0, 0, 0))
    target = np.array(target)
    print target
    for row in range(height):
        for column in range(width):
            if not (row < -math.sqrt(3) * column + math.sqrt(3) / 2 * r or row > math.sqrt(3) * column + math.sqrt(
                    3) / 2 * r or row < math.sqrt(3) * column - 3 / 2.0 * math.sqrt(3) * r or row > -math.sqrt(
                3) * column + 5 / 2.0 * math.sqrt(3) * r):
                target[row-1, column-1] = [cropped_img[row, column][0], cropped_img[row, column][1],
                                         cropped_img[row, column][2], 1.]
    print target.shape

def hexagon(m,n):
    global xc,yc,r
    cc = np.array([xc, yc])
    v2 = r*np.array([1 + np.cos(np.pi/3),   np.sin(np.pi/3)])
    v1 = r*np.array([1 + np.cos(np.pi/3),  -np.sin(np.pi/3)])
    z = m*v1 + n*v2 + cc
    return z

def move_tile(hexID):
    global empty_ID, hexIDs, data, moves
    hex_ID = hexIDs.index(hexID)
    diff = coord[hex_ID] - coord[empty_ID]
    if diff.tolist() in valid:
        moves += 1
        if started:
            show_number_of_moves_widget.delete(0, END)
            show_number_of_moves_widget.insert(0, moves)
        data.append(hexID)
        move = pos[empty_ID] - pos[hex_ID]
        canvas.move(hexID, move[0], move[1])
        hexIDs[hex_ID] = 0
        hexIDs[empty_ID] = hexID
        empty_ID = hex_ID
        if check_win():
            root.after(700)
            win()

def solve():
    solve_button.configure(state=DISABLED)
    global data
    k = 0
    while data:
        undo_move = data.pop()
        print "Undoing this move:", undo_move
        root.after(k * 700, move_tile, undo_move)
        k = k + 1

def click_tile(event):
    hexID = (event.widget.find_closest(event.x, event.y))[0]
    move_tile(hexID)

def mix_up(n):
    global moves
    if n <= 10:
        t = random.choice(valid)
        movable_tile = coord[empty_ID] + t
        tmp_list = coord.tolist()
        if movable_tile.tolist() in tmp_list:
            index = tmp_list.index(movable_tile.tolist())
            if index > 0:
                move_tile(hexIDs[index])
                root.after(400, mix_up, n + 1)
            else:
                root.after(0, mix_up, n)
        else:
            root.after(0, mix_up, n)
    else:
        moves = 0

def check_win():
    for i in range(len(hexIDs)):
        if sol[i] != hexIDs[i]:
            return False
    return True

def win():
    solve_button.configure(state=DISABLED)
    status_label.configure(text="Status: YOU WON!")
    start_button.configure(state=ACTIVE)
    canvas.delete(ALL)

root = Tk()
root.title("Hexagon Click and Random Move")

c = 2
x = 500
y = 500
valid = [[-1,0],[-1,1],[0,1],[0,-1],[1,0],[1,-1]]
started = False

info_frame = Frame(root, bg="black")
info_frame.grid(row=0, sticky=EW)

start_button = Button(info_frame, text="START", command=start, height=2)
start_button.grid(row=0, column=0)

solve_button = Button(info_frame, text="SOLVE", command=solve, height=2)
solve_button.grid(row=0, column=1)
solve_button.configure(state=DISABLED)

Label(info_frame, text="Size of puzzle", bg="black", fg="green").grid(row=0, column=2)
size_of_puzzle_widget  = Entry(info_frame, width=5, justify=CENTER)
size_of_puzzle_widget.grid(row=0, column=3)
size_of_puzzle_widget.delete(0,END)
size_of_puzzle_widget.insert(0,"2")

Label(info_frame, text="Number of Moves", bg="black", fg="green").grid(row=0, column=4)
show_number_of_moves_widget  = Entry(info_frame, width=5, justify=CENTER)
show_number_of_moves_widget.grid(row=0, column=5)
show_number_of_moves_widget.delete(0,END)
show_number_of_moves_widget.insert(0,"0")

status_label = Label(info_frame, text="Status: Press the Start button to begin", bg="black", fg="green")
status_label.grid(row=0, column=4)

canvas = Canvas(root, width=x, height=y, bg="beige", highlightthickness=0, bd=0)
canvas.grid(row=1, column=0)

root.mainloop()
