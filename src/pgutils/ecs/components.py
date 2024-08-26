from pygame.surface import Surface
from dataclasses import dataclass

@dataclass
class Transform:
    x: float
    y: float
    rotX: float
    rotY: float

@dataclass
class Render:
    sprite: Surface
