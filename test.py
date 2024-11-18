import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots()
ax.set_xlim(0, 2)
ax.set_ylim(-1, 1)
line, = ax.plot([], [], lw=2)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    x = np.linspace(0, 2, 1000)
    y = np.sin(2 * np.pi * (x - 0.01 * frame))
    line.set_data(x, y)
    return line,

ani = animation.FuncAnimation(fig, update, frames=100, init_func=init, blit=True)
plt.show()
