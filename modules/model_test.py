from dataclasses import dataclass, field
import math
import numpy as np

# -------------- MODEL OBJECTS -------------------


@dataclass
class DOF:
    # [x, y, fi]
    STIFF = [0, 0, 0]
    HINGE = [0, 0, 1]
    FREE_HINGE_X = [1, 0, 1]
    FREE_HINGE_Y = [0, 1, 1]
    FREE = [1, 1, 1]


@dataclass
class Point:
    """
    x: X coordinate
    y: Y coordinate
    name: name of a point. Only for representation
    codeNumbers: array of three numbers used to position point in a stiffness matrix.
    """
    x: int
    y: int
    name: str
    codeNumbers: list
    dof: list


@dataclass
class BarProps:
    material: str
    crossSection: dict

    A: int = field(init=False)
    E: int = field(init=False)
    I: int = field(init=False)

    def __post_init__(self) -> None:
        self.A = crossSectionArea(self.crossSection)
        self.E = elasticModulus(self.material)
        self.I = momentOfInertia(self.crossSection)


@dataclass
class Bar:
    point_a: Point
    point_b: Point
    name: str

    @property
    def len(self):
        return calculateDistance(self.point_a, self.point_b)

    @property
    def angle(self):
        return angle(self.point_a, self.point_b)

    @property
    def l_xy(self):
        return l_xy(self.point_a, self.point_b)

    @property
    def codeNumbers(self):
        return self.point_a.codeNumbers.__add__(self.point_b.codeNumbers)


@dataclass
class Load:
    bar: Bar
    Q: int = 0
    F: int = 0
    F_position: int = 0.5
# -------------- FUNCTIONS -------------------


def l_xy(A, B):
    point_1 = [A.x, A.y]
    point_2 = [B.x, B.y]

    # Bar vector
    vector = np.array(point_2) - np.array(point_1)
    l_xy = np.array(point_1) - np.array(point_2)

    if vector[0] != 0:
        return l_xy*-1
    if vector[0] == 0:
        return l_xy


def crossSectionArea(crossSection):
    return crossSection['width'] * crossSection['height'] * 10**-6


def momentOfInertia(crossSection):
    return 1 / 12 * crossSection['width'] * \
        (crossSection['height']**3) * 10 ** -12


def elasticModulus(material):
    if material == "C16/20":
        E = 2.9 * (10**7)
    if material == "C20/25":
        E = 3.0 * (10**7)
    if material == "C25/30":
        E = 3.1 * (10**7)
    if material == "C30/37":
        E = 3.3 * (10**7)
    if material == "C35/45":
        E = 3.4 * (10**7)
    return E


def calculateDistance(A, B):
    point_1 = [A.x, A.y]
    point_2 = [B.x, B.y]
    return math.sqrt((abs(point_1[1]) - abs(point_1[0]))**2 + (abs(point_2[1]) - abs(point_2[0]))**2)


def angle(A, B):
    point_1 = [A.x, A.y]
    point_2 = [B.x, B.y]

    # Bar vector
    vector = np.array(point_2) - np.array(point_1)
    # GSS vector
    i_vector = np.array([1, 0])

    vector_magnitude = math.sqrt(vector[0]**2+vector[1]**2)
    i_vector_magnitude = math.sqrt(i_vector[0]**2+i_vector[1]**2)

    alfa = np.degrees(np.arccos(
        (vector.dot(i_vector)) /
        (vector_magnitude * i_vector_magnitude)
    ))

    if vector[1] > 0:
        return alfa*-1
    else:
        return alfa
