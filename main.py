from math import floor
import time


class inven:
    def __init__(self, items=None):
        if items is None:
            items = {}
        if type(items) is list:
            self.items = {}
            for item in items:
                if item not in self.items:
                    self.items[item] = 0
                self.items[item] += 1
        else:
            self.items = {key: items[key] for key in items if items[key]}

    def __str__(self):
        return str(self.items)

    def __bool__(self):
        return bool(self.items)

    def __iter__(self):
        return iter(self.items)

    def list(self):
        return sum([[i] * int(self[i]) for i in self], [])

    def __getitem__(self, key):
        return self.items[key] if key in self.items else 0

    def __setitem__(self, key, value):
        if value:
            self.items[key] = value
        elif key in self:
            del self.items[key]

    def __call__(self, value):
        self.items = inven(value).items
        return self

    def __add__(self, other):
        other = inven(other)
        return inven({key: self[key] + other[key] for key in {*self, *other}})

    def __sub__(self, other):
        new = inven()
        other = inven(other)
        for key in {*self, *other}:
            new[key] = max(self[key] - other[key], 0)
            other[key] -= self[key] - new[key]
        new["all"] = max(new["all"] - other.sum, 0)
        return new

    def __mul__(self, other):
        return inven({key: int(self[key] * floor(other)) for key in self})

    def __truediv__(self, other):
        i = min(self[i] // other[i] for i in other)
        new = self - (other * i)
        while new > other:
            new -= other
            i += 1
        return i + (other.trim(new).sum / other.sum)

    def __floordiv__(self, other):
        return floor(self / other)

    def __iadd__(self, other):
        return self(self + other)

    def __isub__(self, other):
        return self(self - other)

    def __imul__(self, other):
        return self(self * other)

    def __eq__(self, other):
        return min(map(lambda key: self[key] == other[key], {*self, *other}))

    def __gt__(self, other):
        return other.trim(self) == other

    def keys(self):
        return self.items.keys()

    def values(self):
        return self.items.values()

    @property
    def sum(self):
        return sum(self.values())

    def pop(self, out):
        out = out.trim(self)
        self -= out
        return out

    def trim(self, other):
        match = inven({key: min(self[key], other[key]) for key in {*self, *other}})
        return inven((self - match).list()[:int(other["all"] - match["all"])]) + match


def process(txt):
    if "#" in txt:
        txt = txt[:txt.index("#")]
    txt = txt.strip()
    recipe = {"name": "", "type": "basic", "rate": 0, "def_speed": 0, "ins": {}, "outs": {}}
    if txt:
        if "=" not in txt:
            txt = txt.replace(" ", "").split(":")
            txt[1] = txt[1].split(",")
            recipe["name"], recipe["type"], recipe["rate"] = "consume_" + txt[0], "consumer", float(txt[1][0])
            recipe["def_speed"], recipe["ins"][txt[0]] = float(txt[1][1 if "," in txt[1] else 0]), recipe["rate"]
        else:
            txt = txt.split("=")
            recipe["name"] = txt[0].strip()
            txt = txt[1].split(":") if ":" in txt[1] else ["", txt[1]]
            txt[1] = txt[1].split(",")
            recipe["rate"], recipe["def_speed"] = float(txt[1][0]), float(txt[1][1 if "," in txt[1] else 0])
            txt = txt[0].strip()
            txt = txt.split(">") if ">" in txt else [txt, recipe["name"]]
            if txt[0]:
                recipe["type"] = "constructor"
                for arg in txt[0].split("+"):
                    arg = arg.strip().split(" ")
                    recipe["ins"][arg[-1]] = float(arg[0]) if len(arg) > 1 else 1
            else:
                recipe["type"] = "extractor"
            if recipe["name"] not in txt[1]:
                if txt[1][-1] not in "0123456789":
                    txt[1] += " +"
                txt[1] += " " + recipe["name"]
            for arg in txt[1].split("+"):
                arg = arg.strip().split(" ")
                recipe["outs"][arg[-1]] = float(arg[0]) if len(arg) > 1 else 1
            recipe["ins"], recipe["outs"] = inven(recipe["ins"]), inven(recipe["outs"])
        return recipe


file = open("recipes")
recipes = {recipe["name"]: recipe for recipe in map(process, file.readlines()) if recipe}
file.close()


def make_property(getter):
    @property
    def prop_get(self):
        if getter.__name__ not in self._props:
            self._props[getter.__name__] = getter(self)
        return self._props[getter.__name__]

    @prop_get.deleter
    def prop(self):
        try:
            del self._props[getter.__name__]
        except KeyError:
            pass

    return prop


class builds:
    all = {}
    levels = None

    def __init__(self, name, inventory=None, *outs, **flags):
        if inventory is None:
            inventory = {}
        self.name, self.inven, self.out_names = name, inven(inventory), outs
        self.in_names, self.stored, self.will_get = set(), inven(), inven()
        self.flags = {"inputs": 1, "outputs": 1, "sender": "stored", "receiver": "will_get",
                      "delete": (), "preserve": (), **flags}
        self._props, self.delete = {}, {"can_get", "can_send", *set(self.flags["delete"])} - set(self.flags["preserve"])
        self.sender = getattr(self, self.flags["sender"])
        self.receiver = getattr(self, self.flags["receiver"])
        builds.all[self.name] = self

    def __repr__(self):
        return self.name

    @classmethod
    def connect(cls, sender, receiver):
        del sender.outs, receiver.ins
        sender.out_names.add(receiver)
        map(delattr, cls.all.values(), ["level"] * len(cls.all))
        cls.levels = None

    @classmethod
    def reset_all(cls):
        for build in cls.all.values():
            build.reset()
            for out in build.outs:
                out.in_names.add(build.name)
        if cls.levels is None:
            cls.levels = [[] for i in range(max(map(lambda x: x.level, cls.all.values())) + 1)]
            for build in cls.all.values():
                cls.levels[build.level].append(build)

    @make_property
    def ins(self):
        return [*map(lambda x: builds.all[x], self.in_names)]

    @make_property
    def outs(self):
        return [*map(lambda x: builds.all[x], self.out_names)]

    @make_property
    def can_get(self):
        return self.inven - self.stored

    @make_property
    def can_send(self):
        return self.sender.trim(sum([out.can_get for out in self.outs], inven()))

    @make_property
    def level(self):
        return max(map(lambda x: x.level, self.ins)) + 1 if self.ins else 0

    def get(self, items):
        self.receiver += self.can_get.pop(items)

    def send(self):
        for out in self.outs:
            out.get(self.sender.pop(self.can_send.trim(out.can_get)))

    def reset(self):
        self.stored += self.receiver.pop(self.receiver).trim(self.inven)
        for prop in self.delete:
            delattr(self, prop)


class passer(builds):
    def __init__(self, name, *outs, inventory=0, **flags):
        super().__init__(name, {"all": inventory}, *outs, receiver="sender", **flags)

    def __str__(self): return self.name

    @make_property
    def can_get(self):
        return self.inven - self.stored + sum([out.can_get for out in self.outs], inven())


class storage(passer):
    def __init__(self, name, inventory, *outs, **flags): super().__init__(name, inventory=inventory, *outs, **flags)

    def __str__(self): return " ".join([self.name, "(", str(self.stored), ":", str(self.stored.sum), "/", str(
        self.inven.sum), ")"])


class actors(builds):
    all = []

    def __init__(self, name, recipe, *outs, speed=None, **flags):
        self.recipe, self.rate, self._speeds = recipe, recipe["rate"], recipe["def_speed"] if speed is None else speed
        if type(self._speeds) is not list:
            self._speeds = [self._speeds]
        self.outven, self.prod, self.progress = inven(self.recipe["outs"]), inven(), 0
        super().__init__(name, self.recipe["ins"], *outs, sender="prod", receiver="stored", delete={"can_act"}, **flags)
        actors.all.append(self)

    @make_property
    def can_act(self):
        can_act = [int(self.progress)]
        if self.outven:
            can_act.append((sum([out.can_get for out in self.outs], inven()) - self.prod) / self.outven)
        can_act = min(can_act)
        return can_act

    @make_property
    def can_get(self):
        return (self.inven * self.can_act) - self.stored

    def send(self):
        self.act()
        super().send()

    def act(self):
        amount = [self.can_act]
        if self.inven:
            amount.append(self.stored / self.inven)
        amount = floor(max(min(amount), 0))
        self.stored -= self.inven * amount
        self.prod += self.outven * amount
        self.progress -= amount

    def reset(self):
        self.progress = min(self.progress, 1)
        self.progress += self.speed
        super().reset()

    @make_property
    def speed(self):
        return sum(self.speeds)

    @property
    def speeds(self):
        return self._speeds

    @speeds.setter
    def speeds(self, value):
        self._speeds = [value]
        del self.speed


class extractor(actors):
    __init__ = actors.__init__

    def __str__(self): return " ".join([self.name, "(", str(self.prod), "/", str(self.outven), ")"])


class constructor(actors):
    __init__ = actors.__init__

    def __str__(self):
        return " ".join([self.name, "(", str(self.stored), "/", str(self.inven), ">", str(self.prod), "/", str(
            self.outven), ")"])


class consumer(actors):
    __init__ = actors.__init__

    def __str__(self): return " ".join([self.name, "(", str(self.stored), "/", str(self.inven), ")"])


def recipe_build(name, recipe, *outs, **kwargs):
    recipe = recipes[recipe]
    return globals()[recipe["type"]](name, recipe, *outs, **kwargs)


recipe_build("iron_miner", "iron_ore", "iron_ore_splitter", speed=[120, 135, 90])
passer("iron_ore_splitter", "iron_smelter", "steel_foundry")
recipe_build("coal_miner", "coal", "steel_foundry", speed=[135, 90])
recipe_build("limestone_miner", "limestone", "concrete_crafter", speed=90)
recipe_build("iron_smelter", "iron_ingots", "iron_splitter", speed=120)
passer("iron_splitter", "rod_crafter", "plate_crafter")
recipe_build("steel_foundry", "steel_ingots", "steel_splitter", speed=[45, 30])
passer("steel_splitter", "steel_beam_crafter", "steel_tube_crafter")
recipe_build("copper_miner", "copper_ore", "copper_smelter")
recipe_build("copper_smelter", "copper_ingots", "copper_sheet_crafter")

recipe_build("plate_crafter", "iron_plates", "reinforced_plate_crafter", speed=90)
recipe_build("rod_crafter", "iron_rods", "rod_splitter", speed=60)
passer("rod_splitter", "steel_tube_crafter", "screw_crafter")
recipe_build("screw_crafter", "screws", "reinforced_plate_crafter", speed=60)
recipe_build("reinforced_plate_crafter", "reinforced_iron_plates", "merger", speed=30)

recipe_build("steel_beam_crafter", "steel_beams", "encased_steel_beam_crafter")
recipe_build("concrete_crafter", "concrete", "encased_steel_beam_crafter", speed=30)
recipe_build("encased_steel_beam_crafter", "encased_steel_beams", "merger", speed=30)

recipe_build("copper_sheet_crafter", "copper_sheets", "pipe_crafter")
recipe_build("steel_tube_crafter", "steel_tubes", "pipe_crafter", "screw_crafter", speed=30)
recipe_build("pipe_crafter", "pipes", "merger", speed=30)

passer("merger", "storage")
storage_build = storage("storage", 9999)

start = time.time()

while True:
    builds.reset_all()
    print(storage_build, time.time() - start, sep="\n")
    if input():
        break
    start = time.time()
    for level in builds.levels:
        for build in level:
            build.send()
