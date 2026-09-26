"""Longitudinal motor cross-section rendering shared by the UI and reports."""

import math

import numpy as np

from .grain import PerforatedGrain
from .grains import (
    BottomHemisphericalGrain,
    EndBurningGrain,
    TopHemisphericalGrain,
)


PROPELLANT_COLOR = "#BFBFBF"
PORT_COLOR = "#202020"
CONTOUR_COLOR = "#2F75B5"
OUTLINE_COLOR = "#505050"


def _equivalent_port_radius(grain, regression):
    area = grain.getPortArea(regression)
    if area is None or area <= 0:
        return 0
    return math.sqrt(area / math.pi)


def grain_profile(grain, regression, samples=160):
    """Return local x, outer radius, and void radius for an axial grain cut."""
    length = grain.getProperty("length")
    radius = grain.getProperty("diameter") / 2
    regression = max(float(regression), 0)

    if grain.getWebLeft(regression) <= 0:
        return np.array([]), np.array([]), np.array([])

    if isinstance(grain, TopHemisphericalGrain):
        x = np.linspace(0, length, samples)
        outer = np.sqrt(np.maximum(radius**2 - (x - length) ** 2, 0))
        cavityRadius = grain.getProperty("portDiameter") / 2 + regression
        inner = np.sqrt(
            np.maximum(cavityRadius**2 - (x - length) ** 2, 0)
        )
        inner[x < length - cavityRadius] = 0
        return x, outer, np.minimum(inner, outer)

    if isinstance(grain, BottomHemisphericalGrain):
        cavityRadius = grain.getProperty("portDiameter") / 2 + regression
        outletRadius = grain.getProperty("outletDiameter") / 2 + regression
        propellantLength = math.sqrt(
            max(radius**2 - outletRadius**2, 0)
        )
        x = np.linspace(0, min(length, propellantLength), samples)
        outer = np.sqrt(np.maximum(radius**2 - x**2, 0))
        sphericalVoid = np.sqrt(
            np.maximum(cavityRadius**2 - x**2, 0)
        )
        sphericalVoid[x > cavityRadius] = 0
        inner = np.maximum(sphericalVoid, outletRadius)
        return x, outer, np.minimum(inner, outer)

    if isinstance(grain, EndBurningGrain):
        start, end = grain.getEndPositions(regression)
        if end <= start:
            return np.array([]), np.array([]), np.array([])
        x = np.array([start, end])
        outer = np.full(2, radius)
        return x, outer, np.zeros(2)

    if isinstance(grain, PerforatedGrain):
        start, end = grain.getEndPositions(regression)
        if end <= start:
            return np.array([]), np.array([]), np.array([])
        x = np.array([start, end])
        outer = np.full(2, radius)
        inner = np.full(2, min(_equivalent_port_radius(grain, regression), radius))
        return x, outer, inner

    x = np.array([0, length])
    return x, np.full(2, radius), np.zeros(2)


def draw_motor_cross_section(
    axis,
    motor,
    regressions=None,
    contour_fractions=None,
    show_labels=True,
):
    """Draw all grains in physical order as one coherent axial cross-section."""
    if regressions is None:
        regressions = [0] * len(motor.grains)
    if len(regressions) != len(motor.grains):
        raise ValueError("One regression value is required for each grain")

    axis.clear()
    offset = 0
    maximumRadius = max(
        grain.getProperty("diameter") / 2 for grain in motor.grains
    )

    for index, (grain, regression) in enumerate(
        zip(motor.grains, regressions)
    ):
        length = grain.getProperty("length")
        radius = grain.getProperty("diameter") / 2
        axis.plot(
            [offset, offset + length, offset + length, offset, offset],
            [radius, radius, -radius, -radius, radius],
            color=OUTLINE_COLOR,
            linewidth=0.7,
            linestyle=":",
        )

        x, outer, inner = grain_profile(grain, regression)
        if x.size:
            globalX = x + offset
            axis.fill_between(
                globalX,
                inner,
                outer,
                color=PROPELLANT_COLOR,
                linewidth=0,
            )
            axis.fill_between(
                globalX,
                -outer,
                -inner,
                color=PROPELLANT_COLOR,
                linewidth=0,
            )
            axis.plot(globalX, outer, color=OUTLINE_COLOR, linewidth=1)
            axis.plot(globalX, -outer, color=OUTLINE_COLOR, linewidth=1)
            axis.plot(globalX, inner, color=PORT_COLOR, linewidth=1)
            axis.plot(globalX, -inner, color=PORT_COLOR, linewidth=1)

        if contour_fractions is not None and len(contour_fractions):
            wall = grain.getWebLeft(0)
            for fraction in contour_fractions:
                contourRegression = wall * fraction
                contourX, _, contourInner = grain_profile(
                    grain, contourRegression
                )
                if contourX.size:
                    contourOuter = grain_profile(
                        grain, contourRegression
                    )[1]
                    axis.plot(
                        contourX + offset,
                        contourInner,
                        color=CONTOUR_COLOR,
                        linewidth=0.6,
                        alpha=0.8,
                    )
                    if isinstance(grain, EndBurningGrain):
                        axis.plot(
                            [contourX[-1] + offset] * 2,
                            [-contourOuter[-1], contourOuter[-1]],
                            color=CONTOUR_COLOR,
                            linewidth=0.6,
                            alpha=0.8,
                        )
                    elif isinstance(grain, PerforatedGrain):
                        for endIndex in (0, -1):
                            axis.plot(
                                [contourX[endIndex] + offset] * 2,
                                [
                                    contourInner[endIndex],
                                    contourOuter[endIndex],
                                ],
                                color=CONTOUR_COLOR,
                                linewidth=0.6,
                                alpha=0.8,
                            )
                            axis.plot(
                                [contourX[endIndex] + offset] * 2,
                                [
                                    -contourOuter[endIndex],
                                    -contourInner[endIndex],
                                ],
                                color=CONTOUR_COLOR,
                                linewidth=0.6,
                                alpha=0.8,
                            )
                    axis.plot(
                        contourX + offset,
                        -contourInner,
                        color=CONTOUR_COLOR,
                        linewidth=0.6,
                        alpha=0.8,
                    )

        if show_labels:
            axis.text(
                offset + length / 2,
                maximumRadius * 1.18,
                f"{index + 1}\n{grain.geomName}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        offset += length

    axis.axhline(0, color=PORT_COLOR, linewidth=0.45, alpha=0.5)
    margin = max(offset * 0.02, maximumRadius * 0.1)
    axis.set_xlim(-margin, offset + margin)
    axis.set_ylim(-maximumRadius * 1.35, maximumRadius * 1.45)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("Axial position / Posição axial (m)")
    axis.set_ylabel("Radius / Raio (m)")
    axis.grid(False)
    return axis
