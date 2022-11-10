from dataclasses import dataclass, field
from modules.model import Bar


class BaseFunctions:
    def loadPosition(self, barLength, load):
        a_distance = barLength - barLength * load.F_position
        b_distance = barLength - a_distance
        return a_distance, b_distance

    def bendingMoment_F_stiff(self, load, distance):
        # /---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        Ma = -load.F * a_distance * b_distance**2 / barLength**2
        Mb = load.F * a_distance**2 * b_distance / barLength**2
        return Ma, Mb

    def bendingMoment_Q_stiff(self, load, distance):
        # /---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        Ma = -load.Q * barLength**2 / 12
        Mb = load.Q * barLength**2 / 12
        return Ma, Mb

    def shearForce_F_stiff(self, load, distance):
        # /---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        Va = -load.F * b_distance**2 / \
            barLength**3 * (barLength + 2 * a_distance)
        Vb = -load.F * a_distance**2 / \
            barLength**3 * (barLength + 2 * b_distance)
        return Va, Vb

    def shearForce_Q_stiff(self, load, distance):
        # /---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        Vb = -load.Q * barLength / 2
        Va = -load.Q * barLength / 2
        return Va, Vb

    def bendingMoment_F_hinge(self, load, distance):
        # /\---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        M = 3 * load.F * barLength / 16
        return M

    def bendingMoment_Q_hinge(self, load, distance):
        # /\---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        M = load.Q * barLength**2 / 8
        return M

    def shearForce_F_hinge(self, load, distance):
        # /\---------/

        Va = -load.F * 5 / 16
        Vb = -load.F * 11 / 16
        return Va, Vb

    def shearForce_Q_hinge(self, load, distance):
        # /\---------/
        [a_distance, b_distance] = distance
        barLength = a_distance + b_distance

        Va = -load.Q * barLength * 3 / 8
        Vb = -load.Q * barLength * 5 / 8
        return Va, Vb


@dataclass
class Load:
    bar: Bar = field(repr=False)
    Q: int = 0
    F: int = 0
    F_position: int = 0.5


@dataclass
class InternalForces_primary(BaseFunctions):
    load: Load
    bar: Bar = field(repr=False)

    Ma: int = field(init=False, default_factory=lambda: 0)
    Mb: int = field(init=False, default_factory=lambda: 0)

    Va: int = field(init=False, default_factory=lambda: 0)
    Vb: int = field(init=False, default_factory=lambda: 0)

    def __post_init__(self) -> None:
        # define local variables
        barLength = self.bar.len
        load = self.load
        distance = self.loadPosition(barLength, load)

        if self.bar.hinge_start == False and self.bar.hinge_end == False:
            # assign to self
            if self.load.F != 0:
                [self.Ma, self.Mb] = self.bendingMoment_F_stiff(load, distance)
                [self.Va, self.Vb] = self.shearForce_F_stiff(load, distance)
            if self.load.Q != 0:
                [self.Ma, self.Mb] = self.bendingMoment_Q_stiff(load, distance)
                [self.Va, self.Vb] = self.shearForce_Q_stiff(load, distance)

        elif self.bar.hinge_start == True and self.bar.hinge_end == False:
            # assign to self
            if self.load.F != 0:
                self.Ma = 0
                self.Mb = self.bendingMoment_F_hinge(load, distance)
                [self.Va, self.Vb] = self.shearForce_F_hinge(load, distance)
            if self.load.Q != 0:
                self.Ma = 0
                self.Mb = self.bendingMoment_Q_hinge(load, distance)
                [self.Va, self.Vb] = self.shearForce_Q_hinge(load, distance)

        elif self.bar.hinge_start == False and self.bar.hinge_end == True:
            # assign to self
            if self.load.F != 0:
                self.Ma = self.bendingMoment_F_hinge(load, distance)
                self.Mb = 0
                [self.Vb, self.Va] = self.shearForce_F_hinge(load, distance)
            if self.load.Q != 0:
                self.Ma = self.bendingMoment_Q_hinge(load, distance)
                self.Mb = 0
                [self.Vb, self.Va] = self.shearForce_Q_hinge(load, distance)
