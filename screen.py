import pygame
from pygame.locals import *
import user_inputs

pygame.init()

background = Color(0, 0, 0)
screen = pygame.display.set_mode((600, 600))
screen.fill(background)
connections = set()


def getattrs(iter_, attr):
    return [*map(getattr, iter_, [attr] * len(sprites.all))]


def connect(sender, reciever):
    if sender is not reciever:
        connections.add((sender, reciever))


def rect_of(start, end):
    return pygame.rect.Rect(min(start[0], end[0]), min(start[1], end[1]),
                            abs(start[0] - end[0]), abs(start[1] - end[1]))


class sprites:
    all = []

    def __init__(self, name, rect, color=(255, 255, 255)):
        self.name, self.rect, self.color = name, pygame.rect.Rect(rect), Color(color)
        self.clicked_at, self.prev_rect = (0, 0), self.rect.copy()
        sprites.all.append(self)

    def __getattr__(self, key):
        return getattr(self.rect, key)

    def update(self):
        self.draw()
        self.prev_rect = self.rect.copy()

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

    def move_to(self, pos):
        pos = (pos[0] + self.clicked_at[0], pos[1] + self.clicked_at[1])
        self.rect.update(pos, self.size)
        rects = getattrs(sprites.all, "rect")
        rects.remove(self.rect)
        collide = self.collidelist(rects)
        if collide + 1:
            collide = rects[collide]
            if self.prev_rect.right <= collide.left:
                self.rect.right = collide.left
            elif self.prev_rect.left >= collide.right:
                self.rect.left = collide.right
            elif self.prev_rect.bottom <= collide.top:
                self.rect.bottom = collide.top
            elif self.prev_rect.top >= collide.bottom:
                self.rect.top = collide.bottom


sprites("square1", (200, 200, 50, 50))
sprites("square2", (200, 250, 50, 50))
sprites("square3", (250, 200, 50, 50))
sprites("square4", (250, 250, 50, 50))

while True:
    user_inputs.check()
    if pygame.event.get(QUIT):
        break
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == BUTTON_LEFT:
                user_inputs.event("click")
                for sprite in sprites.all:
                    if sprite.rect.collidepoint(event.pos):
                        user_inputs.event("click_on", sprite, event.pos)
                        break
        elif event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                user_inputs.event("unclick")
        elif event.type == MOUSEMOTION:
            user_inputs.event("move_to", event.pos)
    if user_inputs.do == "connect":
        print(user_inputs.selected)
        connect(*user_inputs.selected)

    screen.fill(background)
    for sender, reciever in connections:
        pygame.draw.line(screen, (255, 255, 255), sender.center, reciever.center)
    if "connecting" in user_inputs.doing:
        pygame.draw.line(screen, (255, 255, 255), user_inputs.selected[0].center, pygame.mouse.get_pos())
    list(map(sprites.update, sprites.all))
    pygame.display.flip()
    sprites.to_update = []
pygame.quit()
