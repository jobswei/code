import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from tqdm import tqdm
import matplotlib
# Ensure minus sign is displayed correctly
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties

print(matplotlib.matplotlib_fname())
# download the font files and save in this fold
font_path = "/data/zyw/.usr/miniconda3/envs/soft/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf"

font_files = font_manager.findSystemFonts(fontpaths=font_path)

for file in font_files:
    font_manager.fontManager.addfont(file)
for font_name in sorted(font_manager.get_font_names()):
    print(font_name)
# matplotlib.rc("font", family='gongfansuannaibudingti')

myfont = FontProperties(
    fname=
    "src/ttf/SuanNaiBuDing.ttf"
)


def f(a):
    x = np.linspace(-2, 2, 200)
    y = np.abs(x)**(2 / 3) + np.e / 3 * (np.pi - np.abs(x)**2)**0.5 * np.sin(
        a * np.pi * np.abs(x))
    return x, y


# Initialize the figure
fig, ax = plt.subplots()
x = np.linspace(-2, 2, 100)
line, = ax.plot([], [], 'r', lw=2)
ax.set_xlim(-2, 2)
ax.set_ylim(-1.5, 3)
ax.set_title("f(x) = x^(2/3) + e/3 * (pi - x^2)^0.5 * sin(a * pi * x)")
ax.set_xlabel("x")
ax.set_ylabel("f(x)")
# Add Chinese text at (0, 2.5)
ax.text(
    0,
    2.5,
    "苏小奶",
    fontsize=20,
    ha='center',
    va='center',
    color='#FF1493',  # Deep pink color
    fontname=myfont.get_name())

ax.grid()


# Update function for animation
def update(a):
    x, y = f(a)
    line.set_data(x, y)
    ax.set_title(
        f"f(x) = x^(2/3) + e/3 * (pi - x^2)^0.5 * sin({a:.1f} * pi * x)")
    return line,


# Create animation
a_values = np.arange(0, 15, 0.05)

# Wrap the frames with tqdm for progress bar
with tqdm(total=len(a_values), desc="Rendering frames") as pbar:

    def update_with_progress(a):
        result = update(a)
        pbar.update(1)
        return result

    ani = FuncAnimation(fig, update_with_progress, frames=a_values, blit=True)

# Save as MP4
ani.save("/data/zyw/workshop/attempt/animation.mp4", writer="ffmpeg", fps=30)
