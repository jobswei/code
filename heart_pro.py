import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from tqdm import tqdm
import matplotlib
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from matplotlib.patheffects import withStroke
import matplotlib.cm as cm

# 字体配置（请确认路径正确）
try:
    myfont = FontProperties(
        fname=
        "src/ttf/SuanNaiBuDing.ttf"
    )
except:
    myfont = FontProperties()
    print("⚠️ 字体加载失败，将使用默认字体")


# 心形曲线生成函数（添加彩虹渐变）
def f(a):
    x = np.linspace(-2, 2, 500)
    y = np.abs(x)**(2 / 3) + np.e / 3 * (np.pi - np.abs(x)**2)**0.5 * np.sin(
        a * np.pi * np.abs(x))
    colors = cm.rainbow(np.linspace(0, 1, len(x)))
    return x, y, colors


# 初始化画布
fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, facecolor='black')
ax.set_xlim(-2, 2)
ax.set_ylim(-1.5, 3.5)

# 浪漫文字配置
love_text = ax.text(0,
                    3.0,
                    "❤ 苏小奶 ❤",
                    fontsize=35,
                    ha='center',
                    color='#FF69B4',
                    fontproperties=myfont,
                    path_effects=[withStroke(linewidth=3, foreground="white")])

# 初始化星空背景
n_stars = 150
stars = ax.scatter(np.random.uniform(-2, 2, n_stars),
                   np.random.uniform(-1.5, 4.5, n_stars),
                   c='white',
                   s=np.random.rand(n_stars) * 8,
                   alpha=0.6)

# 初始化心形曲线（使用散点实现渐变）
scat = ax.scatter([], [], s=40, alpha=0.9, edgecolors='none')


def update(a):
    x, y, colors = f(a)

    # 更新心形曲线
    scat.set_offsets(np.column_stack([x, y]))
    scat.set_color(colors)

    # 更新星空
    stars.set_offsets(np.random.uniform(-2, 2, size=(n_stars, 2)))
    stars.set_sizes(np.random.rand(n_stars) * 10)

    # 文字心跳效果
    love_text.set_fontsize(35 + 3 * np.sin(a * 2))

    return scat, stars, love_text


# 创建动画
a_values = np.arange(0, 20, 0.15)

# 使用tqdm显示渲染进度
with tqdm(total=len(a_values) * 2, desc="✨ 双格式渲染") as pbar:
    # 先创建动画对象
    ani = FuncAnimation(fig,
                        lambda a: (update(a), pbar.update(1))[0],
                        frames=a_values,
                        blit=True)

    # 保存GIF（透明背景）
    ani.save("/data/zyw/workshop/attempt/love_heart.gif",
             writer=PillowWriter(fps=24),
             savefig_kwargs={'transparent': True},
             progress_callback=lambda i, n: pbar.update(0))

    # 保存MP4（更高画质）
    ani.save(
        "/data/zyw/workshop/attempt/love_heart.mp4",
        writer=FFMpegWriter(fps=24,
                            metadata={
                                'title': 'Math Love',
                                'artist': 'DeepSeek'
                            },
                            extra_args=['-crf', '18']),  # 控制画质（0-51，越小越好）
        dpi=100,
        progress_callback=lambda i, n: pbar.update(0))

print(
    "✅ 双格式生成完成！\nGIF路径：/data/zyw/workshop/attempt/love_heart.gif\nMP4路径：/data/zyw/workshop/attempt/love_heart.mp4"
)
