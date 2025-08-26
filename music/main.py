import numpy as np
import simpleaudio as sa
import threading
import time
import os
import sys

# ===================== 核心配置：音符→五线谱位置映射（单个字符） =====================
NOTE_POSITION_MAP = {
    # 低音区（3组）
    'C3': {
        'symbol': '♩',
        'pos': 1
    },
    'C#3': {
        'symbol': '♯',
        'pos': 1
    },
    'D3': {
        'symbol': '♩',
        'pos': 2
    },
    'D#3': {
        'symbol': '♯',
        'pos': 2
    },
    'E3': {
        'symbol': '♩',
        'pos': 3
    },
    'F3': {
        'symbol': '♩',
        'pos': 4
    },
    'F#3': {
        'symbol': '♯',
        'pos': 4
    },
    'G3': {
        'symbol': '♩',
        'pos': 5
    },
    'G#3': {
        'symbol': '♯',
        'pos': 5
    },
    'A3': {
        'symbol': '♩',
        'pos': 5
    },
    'A#3': {
        'symbol': '♯',
        'pos': 5
    },
    'B3': {
        'symbol': '♩',
        'pos': 6
    },
    # 中音区（4组）
    'C4': {
        'symbol': '♪',
        'pos': 5
    },
    'C#4': {
        'symbol': '♭',
        'pos': 5
    },
    'D4': {
        'symbol': '♪',
        'pos': 6
    },
    'D#4': {
        'symbol': '♭',
        'pos': 6
    },
    'E4': {
        'symbol': '♪',
        'pos': 7
    },
    'F4': {
        'symbol': '♪',
        'pos': 8
    },
    'F#4': {
        'symbol': '♭',
        'pos': 8
    },
    'G4': {
        'symbol': '♪',
        'pos': 7
    },
    'G#4': {
        'symbol': '♭',
        'pos': 7
    },
    'A4': {
        'symbol': '♪',
        'pos': 8
    },
    'A#4': {
        'symbol': '♭',
        'pos': 8
    },
    'B4': {
        'symbol': '♪',
        'pos': 9
    },
    # 高音区（5组）
    'C5': {
        'symbol': '♫',
        'pos': 7
    },
    'C#5': {
        'symbol': '♮',
        'pos': 7
    },
    'D5': {
        'symbol': '♫',
        'pos': 8
    },
    'D#5': {
        'symbol': '♮',
        'pos': 8
    },
    'E5': {
        'symbol': '♫',
        'pos': 9
    },
    'F5': {
        'symbol': '♫',
        'pos': 9
    },
    'F#5': {
        'symbol': '♮',
        'pos': 9
    },
    'G5': {
        'symbol': '♫',
        'pos': 9
    },
    # 休止符
    'R': {
        'symbol': ' ',
        'pos': 5
    }
}

# 音符频率映射
NOTE_FREQS = {
    'C3': 130.81,
    'C#3': 138.59,
    'D3': 146.83,
    'D#3': 155.56,
    'E3': 164.81,
    'F3': 174.61,
    'F#3': 185.00,
    'G3': 196.00,
    'G#3': 207.65,
    'A3': 220.00,
    'A#3': 233.08,
    'B3': 246.94,
    'C4': 261.63,
    'C#4': 277.18,
    'D4': 293.66,
    'D#4': 311.13,
    'E4': 329.63,
    'F4': 349.23,
    'F#4': 369.99,
    'G4': 392.00,
    'G#4': 415.30,
    'A4': 440.00,
    'A#4': 466.16,
    'B4': 493.88,
    'C5': 523.25,
    'C#5': 554.37,
    'D5': 587.33,
    'D#5': 622.25,
    'E5': 659.25,
    'F5': 698.46,
    'F#5': 739.99,
    'G5': 783.99,
    'R': 0.0
}

# 基础参数
SAMPLE_RATE = 44100
QUARTER_NOTE_DURATION = 0.25
STAFF_TOTAL_LINES = 11  # 修复：原5行无法显示5条横线，恢复11行（5线+4间+上下留白）
STAFF_LINE_ROWS = [1, 3, 5, 7, 9]  # 五线谱横线位置（0=最上，10=最下）
STAFF_LINE_CHAR = "—"
STAFF_GAP_CHAR = " "
POSITION_TO_ROW = {
    9: 1,
    8: 2,
    7: 3,
    6: 4,
    5: 5,
    4: 6,
    3: 7,
    2: 8,
    1: 9
}  # 音高→五线谱行映射

# 自定义配置
CUSTOM_NOTE_WIDTH = 4  # 音符宽度（列数）
CUSTOM_DISPLAY_RANGE = 10  # 传送带前后音符数量

# ===================== 全局变量 =====================
current_note_idx = 0
music_notes = []
is_playing_flag = False
term_width = 80
# 固定区域行号记录（用于后续局部刷新定位）
fixed_lines = {
    'border_top': 0,
    'title': 1,
    'border_mid': 2,
    'staff_start': 3,  # 五线谱开始行
    'staff_end': 3 + STAFF_TOTAL_LINES - 1,  # 五线谱结束行
    'progress': 3 + STAFF_TOTAL_LINES,  # 进度行
    'border_bottom': 3 + STAFF_TOTAL_LINES + 1  # 底部边框行
}


# ===================== 新增功能1：快速逐个字符打印当前代码 =====================
def print_code_character_by_character():
    """以极快速度逐个字符打印当前脚本代码"""
    try:
        # 获取当前脚本路径
        script_path = __file__
        # 读取脚本内容（utf-8编码，避免中文乱码）
        with open(script_path, 'r', encoding='utf-8') as f:
            code_content = f.read()

        # 逐个字符打印，延迟极小（0.001秒）
        sys.stdout.write("📝 正在加载程序代码...\n")
        sys.stdout.flush()
        time.sleep(0.5)

        for char in code_content:
            # 特殊处理：换行时稍作延迟，保持格式可读性
            if char == '\n':
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.005)
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.001)  # 核心：控制打印速度，0.001秒/字符

        # 代码打印完成提示
        sys.stdout.write("\n\n✅ 代码加载完成！\n")
        sys.stdout.flush()
        time.sleep(1)  # 停留1秒让用户看清

    except Exception as e:
        # 代码读取失败时跳过该环节，不影响主功能
        sys.stdout.write(f"\n⚠️  代码预览功能暂不可用：{str(e)}\n")
        sys.stdout.flush()
        time.sleep(1)


# ===================== 新增功能2：清空终端（跨平台兼容） =====================
def clear_terminal():
    """清空终端，兼容Windows/Linux/macOS"""
    if os.name == 'nt':  # Windows系统
        os.system('cls')
    else:  # Linux/macOS系统
        os.system('clear')
    # 额外用ANSI码确保清屏彻底
    sys.stdout.write("\033c")
    sys.stdout.flush()


# ===================== 新增功能3：大字体显示“开始运行”（ASCII艺术修饰） =====================
def show_start_prompt():
    """用大字体+装饰显示开始运行提示"""
    # 清屏后显示
    clear_terminal()

    # 装饰性大字体提示（用符号环绕，视觉上放大）
    prompt_lines = [
        "════════════════════════════════════════════════════════════════",
        "║                                                                ║",
        "║                      ✨ 开始运行五线谱播放器 ✨                   ║",
        "║                                                                ║",
        "║                      🎶 正在初始化音频引擎...                  ║",
        "║                                                                ║",
        "║                ⚠️  提示：按 Ctrl+C 可随时停止播放                ║",
        "║                                                                ║",
        "════════════════════════════════════════════════════════════════"
    ]

    # 居中显示（适配不同终端宽度）
    for line in prompt_lines:
        if len(line) <= term_width:
            # 终端宽度足够，直接居中
            print(line.center(term_width))
        else:
            # 终端宽度不足，截取显示
            print(line[:term_width])

    # 停留2秒，让用户看清提示
    time.sleep(2)


# ===================== 音频生成 =====================
def generate_audio_note(freq, dur):
    sample_count = int(SAMPLE_RATE * dur)
    time_axis = np.linspace(0, dur, sample_count, False)

    if freq > 0:
        base_wave = 0.7 * np.sin(freq * time_axis * 2 * np.pi)
        harmonic2 = 0.2 * np.sin(2 * freq * time_axis * 2 * np.pi)
        harmonic3 = 0.1 * np.sin(3 * freq * time_axis * 2 * np.pi)
        audio_wave = base_wave + harmonic2 + harmonic3
    else:
        audio_wave = np.zeros(sample_count)

    audio_wave *= 32767 / np.max(np.abs(audio_wave))
    return audio_wave.astype(np.int16)


# ===================== 播放线程 =====================
def audio_play_thread():
    global current_note_idx, is_playing_flag

    total_audio = np.array([], dtype=np.int16)
    note_durations = []

    for note_code, dur_mult in music_notes:
        note_freq = NOTE_FREQS[note_code]
        actual_dur = dur_mult * QUARTER_NOTE_DURATION
        note_audio = generate_audio_note(note_freq, actual_dur)
        total_audio = np.append(total_audio, note_audio)
        note_durations.append(actual_dur)

    is_playing_flag = True
    play_obj = sa.play_buffer(total_audio, 1, 2, SAMPLE_RATE)

    play_start_time = time.time()
    while is_playing_flag:
        elapsed_time = time.time() - play_start_time
        accum_dur = 0

        for idx, dur in enumerate(note_durations):
            accum_dur += dur
            if elapsed_time < accum_dur:
                current_note_idx = idx
                break

        if elapsed_time >= sum(note_durations):
            break
        time.sleep(0.01)

    play_obj.wait_done()
    is_playing_flag = False


# ===================== 五线谱可视化（局部刷新核心优化） =====================
def staff_visual_thread():
    global current_note_idx, is_playing_flag, term_width

    # 1. 自适应终端宽度
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    # 2. 打印固定框架（仅打印一次，后续不重复）
    def print_fixed_frame():
        # 顶部边框
        print("=" * term_width)
        # 标题
        print("🎵 五线谱音乐播放器 | 当前播放：红色音符 | 按Ctrl+C停止".center(term_width))
        # 中间边框
        print("-" * term_width)
        # 五线谱框架（含固定横线）
        for row in range(STAFF_TOTAL_LINES):
            if row in STAFF_LINE_ROWS:
                # 五线谱横线
                print(STAFF_LINE_CHAR * term_width)
            else:
                # 五线谱间隙（空白）
                print(" " * term_width)
        # 进度行（初始空白）
        print(" " * term_width)
        # 底部边框
        print("=" * term_width)

    print_fixed_frame()

    # 3. 局部刷新音符和进度（核心：仅更新变化区域）
    while is_playing_flag:
        # --------------------------
        # 第一步：清空上一帧音符（仅操作五线谱区域）
        # --------------------------
        for staff_row in range(STAFF_TOTAL_LINES):
            terminal_row = fixed_lines['staff_start'] + staff_row
            sys.stdout.write(f"\033[{terminal_row};1H")
            if staff_row in STAFF_LINE_ROWS:
                sys.stdout.write(STAFF_LINE_CHAR * term_width)
            else:
                sys.stdout.write(" " * term_width)

        # --------------------------
        # 第二步：计算当前要显示的音符信息
        # --------------------------
        start_idx = max(0, current_note_idx - CUSTOM_DISPLAY_RANGE)
        end_idx = min(len(music_notes),
                      current_note_idx + CUSTOM_DISPLAY_RANGE + 1)
        center_col = term_width // 2
        base_col = center_col - (current_note_idx -
                                 start_idx) * CUSTOM_NOTE_WIDTH

        # --------------------------
        # 第三步：绘制当前帧音符
        # --------------------------
        for note_idx in range(start_idx, end_idx):
            note_code, _ = music_notes[note_idx]
            note_info = NOTE_POSITION_MAP[note_code]
            note_sym = note_info['symbol']
            note_pos = note_info['pos']

            staff_row = POSITION_TO_ROW.get(note_pos, 5)
            terminal_row = fixed_lines['staff_start'] + staff_row
            note_start_col = base_col + (note_idx -
                                         start_idx) * CUSTOM_NOTE_WIDTH

            if 0 < note_start_col < term_width - CUSTOM_NOTE_WIDTH:
                sys.stdout.write(f"\033[{terminal_row};{note_start_col}H")
                if note_idx == current_note_idx:
                    # 红色单个字符重复填充宽度
                    sys.stdout.write(
                        f"\033[31m{note_sym * CUSTOM_NOTE_WIDTH}\033[0m")
                else:
                    sys.stdout.write(note_sym * CUSTOM_NOTE_WIDTH)

        # --------------------------
        # 第四步：更新进度行
        # --------------------------
        progress_text = f"进度：{current_note_idx + 1}/{len(music_notes)} | 音符宽度：{CUSTOM_NOTE_WIDTH}列"
        progress_col = (term_width - len(progress_text)) // 2
        sys.stdout.write(f"\033[{fixed_lines['progress']};1H")
        sys.stdout.write(" " * term_width)
        sys.stdout.write(
            f"\033[{fixed_lines['progress']};{progress_col}H{progress_text}")

        # --------------------------
        # 第五步：刷新缓冲区
        # --------------------------
        sys.stdout.flush()
        time.sleep(0.05)

    # 4. 播放结束提示
    end_text = "🎶 播放结束！感谢聆听～"
    end_col = (term_width - len(end_text)) // 2
    sys.stdout.write(f"\033[{fixed_lines['progress']};1H")
    sys.stdout.write(" " * term_width)
    sys.stdout.write(f"\033[{fixed_lines['progress']};{end_col}H{end_text}")
    sys.stdout.flush()
    time.sleep(3)  # 播放结束后停留3秒


# ===================== 主控制 =====================
def start_music_with_staff():
    global current_note_idx, is_playing_flag
    current_note_idx = 0
    is_playing_flag = False

    audio_thread = threading.Thread(target=audio_play_thread)
    visual_thread = threading.Thread(target=staff_visual_thread)

    audio_thread.start()
    time.sleep(0.1)
    visual_thread.start()

    audio_thread.join()
    visual_thread.join()


# ===================== 程序入口（整合新增功能） =====================
if __name__ == "__main__":
    try:
        # 步骤1：快速逐个字符打印代码
        print_code_character_by_character()

        # 步骤2：读取并校验乐谱
        with open("music/config.txt", "r", encoding="utf-8") as f:
            music_notes = [
                eval(line.strip()) for line in f.readlines()
                if line.strip() and line.strip().startswith("(")
            ]

        valid_notes = set(NOTE_POSITION_MAP.keys())
        for idx, (note_code, dur) in enumerate(music_notes):
            if note_code not in valid_notes:
                raise ValueError(f"第{idx+1}行：未知音符「{note_code}」")
            if not isinstance(dur, (int, float)) or dur <= 0:
                raise ValueError(f"第{idx+1}行：时长必须为正数")

        # 步骤3：显示大字体开始提示
        show_start_prompt()

        # 步骤4：清空终端，启动播放
        clear_terminal()
        start_music_with_staff()

    except FileNotFoundError:
        clear_terminal()
        print("❌ 未找到 music/config.txt 文件")
        print("   请在程序同级目录创建「music」文件夹，并放入「config.txt」乐谱")
    except SyntaxError:
        clear_terminal()
        print("❌ config.txt 格式错误！正确示例：('C4', 1)")
        print("   注意：使用英文括号、引号、逗号，无多余空格")
    except ValueError as e:
        clear_terminal()
        print(f"❌ 乐谱错误：{e}")
    except KeyboardInterrupt:
        clear_terminal()
        sys.stdout.write("\033[?25h")  # 恢复光标
        print("\n🛑 程序已手动停止")
    except Exception as e:
        clear_terminal()
        print(f"❌ 运行错误：{e}")
        print("   请尝试重新安装依赖：pip install numpy simpleaudio")
