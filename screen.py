import pygame
from pygame.locals import *
from pygame import Vector2 as vector
import user_inputs
import logic

pygame.init()

background = Color(0, 0, 0)
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen_rect = screen.get_rect()
screen.fill(background)
connections = set()


def connect(sender, reciever):
    if sender is not reciever:
        connections.add((sender, reciever))


def getattrs(iter_, attr):
    return [*map(getattr, iter_, [attr] * len(sprites.all))]


class sprites:
    all = {}
    levels = []
    size = 45

    def __init__(self, build):
        self.build, self.name, self.level = build, build.name, None
        self.rect = pygame.rect.Rect(screen_rect.centerx, screen_rect.bottom - 1.5 * sprites.size,
                                     sprites.size, sprites.size)
        self.clicked_at, self.prev_rect = vector(), self.rect.copy()
        sprites.all[self.name] = self

    def __getattr__(self, key):
        return getattr(self.rect, key)

    @classmethod
    def reset_all(cls):
        if logic.builds.levels is None:
            for sprite in cls.all.values():
                sprite.level = None
            cls.levels = None
        logic.builds.reset_all()
        for sprite in cls.all.values():
            for out in sprite.build.outs:
                connect(sprite, cls.all[out.name])
        if cls.levels is None:
            cls.levels = [[] for i in range(len(logic.builds.levels))]
            for sprite in cls.all.values():
                sprite.level = sprite.build.level
                cls.levels[sprite.level].append(sprite)
            for level in cls.levels:
                for i in range(len(level)):
                    level[i].rect.center = (screen_rect.centerx + sprites.size * 1.5 * (2 * i - (len(level) - 1)),
                                            screen_rect.bottom - (level[i].level + 0.5) * 2 * sprites.size)

    def update(self):
        self.draw()
        self.prev_rect = self.rect.copy()

    def draw(self):
        pygame.draw.rect(screen, (128, 128, 128), self.rect)

    def move_to(self, pos):
        pos += self.clicked_at
        self.rect.x = pos.x
        self.rect.clamp_ip(screen_rect)
        rects = getattrs(sprites.all.values(), "rect")
        rects.remove(self.rect)
        for collide in self.collidelistall(rects):
            collide = rects[collide]
            if self.prev_rect.right <= collide.left:
                self.rect.right = collide.left
            if self.prev_rect.left >= collide.right:
                self.rect.left = collide.right
            if self.prev_rect.bottom <= collide.top:
                self.rect.bottom = collide.top
            if self.prev_rect.top >= collide.bottom:
                self.rect.top = collide.bottom

    def stop_move(self, pos):
        pass


sprites(logic.recipe_build("iron_miner", "iron_ore", "iron_ore_splitter", speed=[120, 135, 90]))
sprites(logic.passer("iron_ore_splitter", "iron_smelter", "steel_foundry"))
sprites(logic.recipe_build("coal_miner", "coal", "steel_foundry", speed=[135, 90]))
sprites(logic.recipe_build("limestone_miner", "limestone", "concrete_crafter", speed=90))
sprites(logic.recipe_build("iron_smelter", "iron_ingots", "iron_splitter", speed=120))
sprites(logic.passer("iron_splitter", "rod_crafter", "plate_crafter"))
sprites(logic.recipe_build("steel_foundry", "steel_ingots", "steel_splitter", speed=[45, 30]))
sprites(logic.passer("steel_splitter", "steel_beam_crafter", "steel_tube_crafter"))
sprites(logic.recipe_build("copper_miner", "copper_ore", "copper_smelter"))
sprites(logic.recipe_build("copper_smelter", "copper_ingots", "copper_sheet_crafter"))

sprites(logic.recipe_build("plate_crafter", "iron_plates", "reinforced_plate_crafter", speed=90))
sprites(logic.recipe_build("rod_crafter", "iron_rods", "rod_splitter", speed=60))
sprites(logic.passer("rod_splitter", "steel_tube_crafter", "screw_crafter"))
sprites(logic.recipe_build("screw_crafter", "screws", "reinforced_plate_crafter", speed=60))
sprites(logic.recipe_build("reinforced_plate_crafter", "reinforced_iron_plates", "merger", speed=30))

sprites(logic.recipe_build("steel_beam_crafter", "steel_beams", "encased_steel_beam_crafter"))
sprites(logic.recipe_build("concrete_crafter", "concrete", "encased_steel_beam_crafter", speed=30))
sprites(logic.recipe_build("encased_steel_beam_crafter", "encased_steel_beams", "merger", speed=30))

sprites(logic.recipe_build("copper_sheet_crafter", "copper_sheets", "pipe_crafter"))
sprites(logic.recipe_build("steel_tube_crafter", "steel_tubes", "pipe_crafter", "screw_crafter", speed=30))
sprites(logic.recipe_build("pipe_crafter", "pipes", "merger", speed=30))

sprites(logic.passer("merger", "storage"))
sprites(logic.storage("storage", 9999))

sprites.reset_all()

"""recipe_build("iron_miner", "iron_ore", "iron_smelter", "steel_foundry", speed=[120, 135, 90])
recipe_build("coal_miner", "coal", "steel_foundry", speed=[135, 90])
recipe_build("limestone_miner", "limestone", "concrete_crafter", speed=90)
recipe_build("iron_smelter", "iron_ingots", "rod_crafter", "plate_crafter", speed=120)
recipe_build("steel_foundry", "steel_ingots", "steel_beam_crafter", "steel_tube_crafter", speed=[45, 30])
recipe_build("copper_miner", "copper_ore", "copper_smelter")
recipe_build("copper_smelter", "copper_ingots", "copper_sheet_crafter")

recipe_build("plate_crafter", "iron_plates", "reinforced_plate_crafter", speed=90)
recipe_build("rod_crafter", "iron_rods", "steel_tube_crafter", "screw_crafter", speed=60)
recipe_build("screw_crafter", "screws", "reinforced_plate_crafter", speed=60)
recipe_build("reinforced_plate_crafter", "reinforced_iron_plates", "storage", speed=30)

recipe_build("steel_beam_crafter", "steel_beams", "encased_steel_beam_crafter")
recipe_build("concrete_crafter", "concrete", "encased_steel_beam_crafter", speed=30)
recipe_build("encased_steel_beam_crafter", "encased_steel_beams", "storage", speed=30)

recipe_build("copper_sheet_crafter", "copper_sheets", "pipe_crafter")
recipe_build("steel_tube_crafter", "steel_tubes", "pipe_crafter", "screw_crafter", speed=30)
recipe_build("pipe_crafter", "pipes", "storage", speed=30)

storage_build = storage("storage", 9999)

level_pos = [[]]
from functools import reduce

while True:
    builds.reset_all()
    print(storage_build, sep="\n")
    if input():
        break
    for level in builds.levels:
        for build in level:
            build.send()"""

"""while True:
    for level in builds.levels:
        for i in range(len(level)):
            level[i].level_pos = sum(map(lambda x: x.level_pos, level[i].ins)) / len(level[i].ins) if level[i].ins else i
    all_level_pos = []
    for level in builds.levels:
        gcd = reduce(lambda x, p:x % p if x else p, sorted(map(lambda x:x.level_pos, level)))
        for build in level:
            build.level_pos = int(build.level_pos // gcd)
        level_pos = sorted(map(lambda x:x.level_pos, level))
        level_pos = {i: level_pos.count(i) for i in level_pos}
        all_level_pos.append(level_pos)
        print([*map(lambda x:x.level_pos, level)])
    print(*all_level_pos, sep="\n")"""


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
                for sprite in sprites.all.values():
                    if sprite.rect.collidepoint(event.pos):
                        user_inputs.event("click_on", sprite, event.pos)
                        break
        elif event.type == MOUSEBUTTONUP:
            if event.button == BUTTON_LEFT:
                user_inputs.event("unclick")
        elif event.type == MOUSEMOTION:
            user_inputs.event("move_to", event.pos)
    if user_inputs.do == "connect":
        connect(*user_inputs.selected)

    screen.fill(background)
    for i in range(screen_rect.bottom, -1, -sprites.size * 4):
        pygame.draw.rect(screen, (64, 64, 64), (screen_rect.left, i, screen_rect.w, sprites.size * 2))
    for sender, reciever in connections:
        pygame.draw.line(screen, (255, 255, 255), sender.center, reciever.center)
    if "connecting" in user_inputs.doing:
        pygame.draw.line(screen, (255, 255, 255), user_inputs.selected[0].center, pygame.mouse.get_pos())
    list(map(sprites.update, sprites.all.values()))
    pygame.display.flip()
    sprites.to_update = []
pygame.quit()
