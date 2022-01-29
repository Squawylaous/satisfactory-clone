import time
doing, do = [""], ""
clicked, clicked_at, selected, start_time = None, (0, 0), [], 0


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
        clicked_at = (args[1])
        clicked.clicked_at = (clicked.left - args[1][0], clicked.top - args[1][1])
    elif name == "move_to":
        if doing[-1] == "clicked" and (
                time.time() - start_time > 0.25 or abs(args[0][0] - clicked_at[0]) + abs(args[0][1] - clicked_at[1]) > 15):
            doing[-1], start_time = "dragging", None
        elif clicked:
            clicked.move_to(args[0])
    elif name == "unclick":
        if doing[-1] == "clicked":
            clicked.move_to(clicked_at)
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
