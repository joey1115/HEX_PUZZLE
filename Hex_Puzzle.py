import numpy as np
import math
from Tkinter import *
import random
import matplotlib.image as mpimg
from PIL import Image
import os
from os import listdir
from os.path import isfile, join


def start():
    global x, y, coord, pos, c, r, empty_ID, data, hexIDs, sol, moves, started, img, xc, yc, canvas1
    global root, img_list, temp1, var
    start_button.configure(state=DISABLED)
    canvas1.delete(ALL)

    filename = var.get()
    img = mpimg.imread(join("images", filename))
    x = img.shape[0]
    y = img.shape[1]
    canvas1.configure(width=y, height=x)
    canvas2.configure(width=y, height=x)
    root.update()
    c = int(size_of_puzzle_widget.get())
    xc = y / 2.0
    yc = x / 2.0
    if c % 2 == 0:
        h_max = (c - 1) * 3 + 1
    else:
        h_max = (c - 2) * 3 + 2 + math.sqrt(3)/2.0
    v_max = math.sqrt(3) / 2 * (1 + 2 * c)
    r = min((y-10) / (2.0 * h_max), (x-10) / (2.0 * v_max))
    coord = np.array([[0, 0]])
    pos = np.array([[xc, yc]])
    empty_ID = 0
    hexIDs = [0]
    data = []
    moves = 0
    img_list = []

    if img.shape[2] == 3:
        temp = Image.fromarray(img, 'RGB')
    else:
        temp = Image.fromarray(img, 'RGBA')
    temp.save("win.gif")
    temp1 = PhotoImage(file="win.gif")
    canvas2.create_image(xc,yc, image=temp1, anchor=CENTER)

    for m in range(-c, c + 1):
        for n in range(-c, c + 1):
            if not ((m > (-n + c)) or (m < (-n - c))):
                if not (m == 0 and n == 0):
                    coord = np.append(coord, [[m, n]], axis=0)
                    z = hexagon(m, n)
                    pos = np.append(pos, [z], axis=0)
                    getImg(z)
                    photo = PhotoImage(file="1.gif")
                    img_list.append(photo)
                    newHexID = canvas1.create_image(z[0], z[1], image=img_list[-1], anchor=CENTER)
                    hexIDs.append(newHexID)
                    canvas1.tag_bind(newHexID, '<ButtonPress-1>', click_tile)
                    root.update()
    sol = list(hexIDs)
    status_label.configure(text="Status: Mixing Up")
    mix_up(0)
    root.after(4000, status_label.configure, {"text": "Status: Move now"})
    moves = 0
    started = True
    solve_button.configure(state=ACTIVE)


def getImg(z):
    global r
    cropped_img = img[int(z[1]-math.sqrt(3)/2 * r):int(z[1] + math.sqrt(3)/2 * r), int(z[0]-r):int(z[0]+r)]
    height = cropped_img.shape[0]
    width = cropped_img.shape[1]
    newsize = (width, height)
    target = Image.new('RGBA', newsize, (255, 255, 255, 0))
    target = np.array(target)
    for row in range(height):
        for column in range(width):
            if not (row <= int(-math.sqrt(3) * column + math.sqrt(3) / 2.0 * r) or row >= int(math.sqrt(3) * column +
                    math.sqrt(3) / 2 * r) or row <= int(math.sqrt(3) * column - 3 / 2.0 * math.sqrt(3) * r) or row >=
                    int(-math.sqrt(3) * column + 5 / 2.0 * math.sqrt(3) * r)):
                target[row, column] = [cropped_img[row, column][0], cropped_img[row, column][1],
                                       cropped_img[row, column][2], 255]
    temp = Image.fromarray(target, 'RGBA')
    alpha = temp.split()[3]
    temp = temp.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
    temp.paste(255, mask)
    temp.save("1.gif", "GIF", transparency=255)


def hexagon(m, n):
    global xc, yc, r
    cc = np.array([xc, yc])
    v2 = r*np.array([1 + np.cos(np.pi/3),   np.sin(np.pi/3)])
    v1 = r*np.array([1 + np.cos(np.pi/3),  -np.sin(np.pi/3)])
    z = m*v1 + n*v2 + cc
    return z


def move_tile(hexID):
    global empty_ID, hexIDs, data, moves, coord
    hex_ID = hexIDs.index(hexID)
    diff = coord[hex_ID] - coord[empty_ID]
    if diff.tolist() in valid:
        moves += 1
        if started:
            show_number_of_moves_widget.delete(0, END)
            show_number_of_moves_widget.insert(0, moves)
        data.append(hexID)
        move = pos[empty_ID] - pos[hex_ID]
        canvas1.move(hexID, move[0], move[1])
        hexIDs[hex_ID] = 0
        hexIDs[empty_ID] = hexID
        empty_ID = hex_ID
        if check_win():
            root.after(700)
            win()


def solve():
    status_label.configure(text="Status: Solving")
    solve_button.configure(state=DISABLED)
    global data
    k = 0
    while data:
        undo_move = data.pop()
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
    global root, canvas1, temp1
    solve_button.configure(state=DISABLED)
    status_label.configure(text="Status: YOU WON!")
    start_button.configure(state=ACTIVE)
    root.after(700, canvas1.delete, ALL)
    root.after(700, canvas1.create_image, xc, yc, {"image": temp1, "anchor": CENTER})
    root.after(4000, status_label.configure, {"text": "Status: Press the Start button"})
    root.update()

root = Tk()
root.title("Hexagon Click and Random Move")

info_frame = Frame(root, bg="black")
info_frame.grid(row=0, column=0, sticky=EW)

frame = Frame(root, bg="black")
frame.grid(row=0, column=1, sticky=EW)

if not os.path.exists("images"):
    os.makedirs("images")

images = [f for f in listdir("images") if isfile(join("images", f))]
var = StringVar(root)
var.set(images[0])
drop = OptionMenu(frame, var, *images)
drop.grid(row=0, column=2, sticky=EW)

Label(frame, text="Choose picture:", bg="black", fg="green").grid(row=0, column=1)

start_button = Button(info_frame, text="START", command=start, height=2)
start_button.grid(row=0, column=0)

solve_button = Button(frame, text="SOLVE", command=solve, height=2)
solve_button.grid(row=0, column=0)
solve_button.configure(state=DISABLED)

Label(info_frame, text="Size of puzzle", bg="black", fg="green").grid(row=0, column=1)
size_of_puzzle_widget = Entry(info_frame, width=5, justify=CENTER)
size_of_puzzle_widget.grid(row=0, column=2)
size_of_puzzle_widget.delete(0, END)
size_of_puzzle_widget.insert(0, "2")

Label(info_frame, text="Number of Moves", bg="black", fg="green").grid(row=0, column=3)
show_number_of_moves_widget = Entry(info_frame, width=5, justify=CENTER)
show_number_of_moves_widget.grid(row=0, column=4)
show_number_of_moves_widget.delete(0, END)
show_number_of_moves_widget.insert(0, "0")

status_label = Label(frame, text="Status: Press the Start button", bg="black", fg="green")
status_label.grid(row=0, column=3)

c = 2
valid = [[-1, 0], [-1, 1], [0, 1], [0, -1], [1, 0], [1, -1]]
started = False

canvas1 = Canvas(root, width=500, height=500, bg="beige", highlightthickness=0, bd=0)
canvas1.grid(row=1, column=0)

canvas2 = Canvas(root, width=500, height=500, bg="beige", highlightthickness=0, bd=0)
canvas2.grid(row=1, column=1)

root.mainloop()
