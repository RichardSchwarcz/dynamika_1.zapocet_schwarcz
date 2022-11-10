from matplotlib import pyplot as plt
from matplotlib.patches import Circle


def plotSchema(points: list) -> None:
    x = []
    y = []

    fig = plt.figure()
    fig.suptitle('schema', fontsize=14, fontweight='bold')
    ax = fig.add_subplot()

    for point in points:
        x.append(point.x)
        y.append(point.y)

        if point.dof == [0, 0, 0]:
            ax.annotate(".", xy=(point.x, point.y), bbox={})
        if point.dof == [0, 0, 1]:
            ax.annotate(".", xy=(point.x, point.y), arrowprops={})
        if point.dof == [0, 1, 1]:
            ax.annotate(".", xy=(point.x, point.y), arrowprops={})

        ax.text(point.x+0.1, point.y+0.1, point.name,
                bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 3}, fontweight='bold')

    plt.plot(x, y, 'o-', color='gray')


def highlightNotZero(x):
    if -1*10**-3 < x < 1*10**-3:
        # gray
        color = "#f2f2f2"
    elif x > 1*10**-3:
        # green
        color = "#E1FFD5"
    elif x < 1*10**-3:
        # red
        color = "#FFDCD5"
    return f"background: {color}"
