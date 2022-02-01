import time
from pygame import Vector2 as vector
doing, do = [""], ""
clicked, clicked_at, selected, start_time = None, vector(), [], 0


def check():
    global do, selected
    if do:
        do, selected = "", []


def event(name, *args):
    global doing, do, clicked, clicked_at, selected, start_time
    if name == "click":
        doing[-1], clicked = "click_scan", None
    elif name == "click_on":
        doing[-1], clicked, start_time = "clicked", args[0], time.time()
        clicked_at = vector(args[1])
        clicked.clicked_at = vector(clicked.topleft) - clicked_at
    elif name == "move_to":
        if doing[-1] == "clicked" and (
                time.time() - start_time > 0.1 or vector(args[0]).distance_squared_to(clicked_at) > 15 ** 2):
            doing[-1], start_time = "dragging", None
        elif clicked:
            clicked.move_to(vector(args[0]))
    elif name == "unclick":
        if doing[-1] == "clicked":
            clicked.stop_move(clicked_at)
            selected.append(clicked)
            if len(doing) > 1:
                doing = doing[:-1]
                if doing[-1] == "connecting":
                    do = "connect"
                    doing = [""]
            else:
                doing[-1] = "connecting"
                doing.append("")
        else:
            doing = [""]
            selected = []
        clicked = None
