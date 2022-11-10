import pandas as pd
import numpy as np
# from typing import Optional
from dataclasses import dataclass, field

from modules.model import Bar, BarProps


class BaseFunctions:
    def rotationMatrix(self, angle):
        alfa_rad = np.deg2rad(angle)
        return pd.DataFrame([[np.cos(alfa_rad),
                              np.sin(alfa_rad), 0],
                             [-np.sin(alfa_rad),
                              np.cos(alfa_rad), 0], [0, 0, 1]])

    def transmissionMatrix(self, lx, ly):
        return pd.DataFrame([[-1, 0, 0], [0, -1, 0], [-ly, lx, -1]])

    def lss_barStiffnessMatrix_stiff(self, BarProps, Bar):
        # /---------/
        return pd.DataFrame([[BarProps.E * BarProps.A / Bar.len, 0, 0],
                             [0, 12 * BarProps.E * BarProps.I / Bar.len**3,
                              6 * BarProps.E * BarProps.I / Bar.len**2],
                             [0, 6 * BarProps.E * BarProps.I / Bar.len**2,
                              4 * BarProps.E * BarProps.I / Bar.len]])

    def lss_barStiffnessMatrix_hinge_A(self, BarProps, Bar):
        # /\---------/
        return pd.DataFrame([[BarProps.E * BarProps.A / Bar.len, 0, 0],
                             [0, 3 * BarProps.E * BarProps.I / Bar.len**3, 0],
                             [0, 0, 0]])

    def lss_barStiffnessMatrix_hinge_B(self, BarProps, Bar):
        # /---------/\
        return pd.DataFrame([[BarProps.E * BarProps.A / Bar.len, 0, 0],
                             [0, 3 * BarProps.E * BarProps.I / Bar.len**3,
                              3 * BarProps.E * BarProps.I / Bar.len**2],
                             [0, 3 * BarProps.E * BarProps.I / Bar.len**2,
                              3 * BarProps.E * BarProps.I / Bar.len]])

    def gss_barStiffnessMatrix(self, rotationMatrix, lssBarStiffnessMatrix,
                               transmissionMatrix):
        A = rotationMatrix
        k = lssBarStiffnessMatrix
        B = transmissionMatrix

        # shape of final output
        # [kaa, kab],
        # [kba, kbb]

        kaa = A.T.dot(k).dot(A)
        kba = B.dot(kaa)
        kab = kba.T
        kbb = B.dot(kab)

        col1 = pd.concat([kaa, kba])
        col2 = pd.concat([kab, kbb])

        return pd.concat([col1, col2], axis=1)


@dataclass
class BarMatrices(BaseFunctions):
    barProps: BarProps = field(repr=False)
    bar: Bar = field(repr=False)
    rotation: pd.DataFrame = field(init=False)
    transmission: pd.DataFrame = field(init=False)
    lss_stiffness: pd.DataFrame = field(init=False)
    gss_stiffness: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        # define local variables
        angle = self.bar.angle
        barProps = self.barProps
        bar = self.bar
        [lx, ly] = self.bar.l_xy

        # assign to self
        self.rotation = self.rotationMatrix(angle)
        self.transmission = self.transmissionMatrix(lx, ly)

        if bar.hinge_end == False and bar.hinge_start == False:
            self.lss_stiffness = self.lss_barStiffnessMatrix_stiff(
                barProps, bar)

        elif bar.hinge_end == True and bar.hinge_start == False:
            self.lss_stiffness = self.lss_barStiffnessMatrix_hinge_B(
                barProps, bar)

        elif bar.hinge_end == False and bar.hinge_start == True:
            self.lss_stiffness = self.lss_barStiffnessMatrix_hinge_A(
                barProps, bar)

        self.gss_stiffness = self.gss_barStiffnessMatrix(
            self.rotation, self.lss_stiffness, self.transmission)


class LoadMatrix:
    def lss(N, V, M):
        return pd.DataFrame([[N], [V], [M]])

    def gss(localMatrix, A0_transp):
        return A0_transp.dot(localMatrix)

    def super(globalMatrix_1, globalMatrix_2):
        return pd.concat([globalMatrix_1, globalMatrix_2])


def modelMatrix(barMatrices):
    [k1, k2, k3] = barMatrices
    zeros = pd.DataFrame(np.zeros((12, 12)))
    layer1 = zeros.add(k1, fill_value=0)
    layer2 = layer1.add(k2, fill_value=0)
    layer3 = layer2.add(k3, fill_value=0)
    return layer3
