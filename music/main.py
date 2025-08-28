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
STAFF_TOTAL_LINES = 11  # 5线+4间+上下留白
STAFF_LINE_ROWS = [1, 3, 5, 7, 9]  # 五线谱横线位置
STAFF_LINE_CHAR = "—"
STAFF_GAP_CHAR = " "
POSITION_TO_ROW = {9: 1, 8: 2, 7: 3, 6: 4, 5: 5, 4: 6, 3: 7, 2: 8, 1: 9}

# 自定义配置
CUSTOM_NOTE_WIDTH = 4  # 音符宽度（列数）
CUSTOM_DISPLAY_RANGE = 10  # 传送带前后音符数量
# ===================== 打字机核心配置（关键修复） =====================
TYPEWRITER_TEXT = """
《音乐随想》
—— 同步播放中 ——

每一个跳动的音符，
"""

  # 可修改为任意文本
TYPEWRITER_SPEED = 0.12  # 打字速度（秒/字符），0.12=舒适节奏
TYPEWRITER_COLOR = "\033[36m"  # 青色文本（醒目且不与音符冲突）
TYPEWRITER_ROW_START = 1  # 打字机文本起始行（终端最顶部第1行）

# ===================== 全局变量 =====================
current_note_idx = 0
music_notes = []
is_playing_flag = False
term_width = 80
# 打字机控制变量
is_typing_flag = False
typed_lines = []  # 存储已打印的每一行文本（用于保留）
total_typewriter_lines = TYPEWRITER_TEXT.count('\n')  # 打字机文本总行数

# 固定区域行号（关键调整：打字机在最顶，五线谱在下方）
fixed_lines = {
    'typewriter_end':
    TYPEWRITER_ROW_START + total_typewriter_lines - 1,  # 打字机结束行
    'staff_start':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1,  # 五线谱开始行（与打字机隔1行空白）
    'staff_end':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES - 1,
    'progress':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES,
    'border_bottom':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES + 1
}


# ===================== 修复核心：打字机线程（顶部固定+保留已打文字） =====================
def typewriter_thread():
    global is_typing_flag, typed_lines

    is_typing_flag = True
    typed_lines = [""] * total_typewriter_lines  # 初始化空行列表（对应文本总行数）
    current_line_idx = 0  # 当前正在打印的行索引
    current_char_idx = 0  # 当前行的字符索引
    text_lines = TYPEWRITER_TEXT.split('\n')[1:]  # 分割文本为行（去掉开头空行）

    # 确保文本行数与初始化的typed_lines匹配
    if len(text_lines) < total_typewriter_lines:
        text_lines += [""] * (total_typewriter_lines - len(text_lines))

    while is_typing_flag and current_line_idx < total_typewriter_lines:
        # 若音乐停止，停止打字
        if not is_playing_flag:
            break

        current_line = text_lines[current_line_idx]
        # 逐字符添加到当前行
        if current_char_idx < len(current_line):
            typed_char = current_line[current_char_idx]
            typed_lines[current_line_idx] += typed_char
            current_char_idx += 1
        else:
            # 当前行打完，切换到下一行
            current_line_idx += 1
            current_char_idx = 0

        # 关键：重新打印所有已打行（固定在顶部，保留历史）
        for i in range(len(typed_lines)):
            terminal_row = TYPEWRITER_ROW_START + i
            # 移动光标到当前行开头
            sys.stdout.write(f"\033[{terminal_row};1H")
            # 清空当前行并打印已打文本（带颜色）
            sys.stdout.write(
                f"{TYPEWRITER_COLOR}{typed_lines[i].ljust(term_width)}\033[0m")

        sys.stdout.flush()
        time.sleep(TYPEWRITER_SPEED)

    # 打字完成后，补全未打完的行（避免残缺）
    for i in range(current_line_idx, len(text_lines)):
        terminal_row = TYPEWRITER_ROW_START + i
        sys.stdout.write(f"\033[{terminal_row};1H")
        sys.stdout.write(
            f"{TYPEWRITER_COLOR}{text_lines[i].ljust(term_width)}\033[0m")
    sys.stdout.flush()

    is_typing_flag = False


# ===================== 快速打印代码（保留原功能） =====================
def print_code_character_by_character():
    try:
        script_path = __file__
        with open(script_path, 'r', encoding='utf-8') as f:
            code_content = f.read()

        sys.stdout.write("📝 正在加载程序代码...\n")
        sys.stdout.flush()
        time.sleep(0.5)

        for char in code_content:
            if char == '\n':
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.005)
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.001)

        sys.stdout.write("\n\n✅ 代码加载完成！\n")
        sys.stdout.flush()
        time.sleep(1)

    except Exception as e:
        sys.stdout.write(f"\n⚠️  代码预览功能暂不可用：{str(e)}\n")
        sys.stdout.flush()
        time.sleep(1)


# ===================== 清空终端（跨平台） =====================
def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    sys.stdout.write("\033c")  # 彻底清屏（重置终端）
    sys.stdout.flush()


# ===================== 开始提示（适配打字机位置） =====================
def show_start_prompt():
    clear_terminal()

    prompt_lines = [
        "════════════════════════════════════════════════════════════════",
        "║                                                                ║",
        "║                      ✨ 五线谱播放器即将启动 ✨                   ║",
        "║                                                                ║",
        "║                📝 打字机文本将显示在顶部，永久保留              ║",
        "║                🎵 五线谱在下方同步播放，红色音符为当前播放      ║",
        "║                                                                ║",
        "║                ⚠️  按 Ctrl+C 可随时停止                          ║",
        "║                                                                ║",
        "════════════════════════════════════════════════════════════════"
    ]

    for line in prompt_lines:
        if len(line) <= term_width:
            print(line.center(term_width))
        else:
            print(line[:term_width])

    time.sleep(2.5)  # 延长停留时间，让用户看清提示


# ===================== 音频生成（原功能） =====================
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


# ===================== 播放线程（同步启动打字机） =====================
def audio_play_thread():
    global current_note_idx, is_playing_flag

    # 预处理音频
    total_audio = np.array([], dtype=np.int16)
    note_durations = []
    for note_code, dur_mult in music_notes:
        note_freq = NOTE_FREQS[note_code]
        actual_dur = dur_mult * QUARTER_NOTE_DURATION
        note_audio = generate_audio_note(note_freq, actual_dur)
        total_audio = np.append(total_audio, note_audio)
        note_durations.append(actual_dur)

    # 启动播放和打字机
    is_playing_flag = True
    play_obj = sa.play_buffer(total_audio, 1, 2, SAMPLE_RATE)
    typing_thread = threading.Thread(target=typewriter_thread)
    typing_thread.start()

    # 同步更新当前音符索引
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

    # 播放结束，停止打字机
    play_obj.wait_done()
    is_playing_flag = False
    typing_thread.join()


# ===================== 五线谱可视化（关键：在打字机下方更新，不覆盖） =====================
def staff_visual_thread():
    global current_note_idx, is_playing_flag, term_width

    # 自适应终端宽度
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    # 初始化五线谱固定框架（在打字机下方）
    def init_staff_frame():
        # 打印五线谱顶部边框（与打字机隔1行）
        border_row = fixed_lines['staff_start'] - 1
        sys.stdout.write(f"\033[{border_row};1H")
        sys.stdout.write("=" * term_width)

        # 打印五线谱标题
        title_row = fixed_lines['staff_start']
        sys.stdout.write(f"\033[{title_row};1H")
        sys.stdout.write(
            "🎵 五线谱播放区 | 当前播放：\033[31m红色音符\033[0m | 按Ctrl+C停止".center(
                term_width))

        # 打印五线谱中间边框
        mid_border_row = fixed_lines['staff_start'] + 1
        sys.stdout.write(f"\033[{mid_border_row};1H")
        sys.stdout.write("-" * term_width)

        # 初始化五线谱空白框架
        for i in range(STAFF_TOTAL_LINES):
            staff_row = fixed_lines['staff_start'] + 2 + i
            sys.stdout.write(f"\033[{staff_row};1H")
            if i in STAFF_LINE_ROWS:
                sys.stdout.write(STAFF_LINE_CHAR * term_width)
            else:
                sys.stdout.write(" " * term_width)

        # 初始化进度行
        progress_row = fixed_lines['progress']
        sys.stdout.write(f"\033[{progress_row};1H")
        sys.stdout.write(" " * term_width)

        # 初始化底部边框
        bottom_border_row = fixed_lines['border_bottom']
        sys.stdout.write(f"\033[{bottom_border_row};1H")
        sys.stdout.write("=" * term_width)

        sys.stdout.flush()

    # 先初始化五线谱框架
    init_staff_frame()

    # 动态更新音符和进度（仅操作五线谱区域，不碰打字机区域）
    while is_playing_flag:
        # 1. 清空上一帧音符（仅五线谱区域）
        for i in range(STAFF_TOTAL_LINES):
            staff_row = fixed_lines['staff_start'] + 2 + i
            terminal_row = staff_row
            sys.stdout.write(f"\033[{terminal_row};1H")
            if i in STAFF_LINE_ROWS:
                sys.stdout.write(STAFF_LINE_CHAR * term_width)
            else:
                sys.stdout.write(" " * term_width)

        # 2. 计算音符显示范围
        start_idx = max(0, current_note_idx - CUSTOM_DISPLAY_RANGE)
        end_idx = min(len(music_notes),
                      current_note_idx + CUSTOM_DISPLAY_RANGE + 1)
        center_col = term_width // 2
        base_col = center_col - (current_note_idx -
                                 start_idx) * CUSTOM_NOTE_WIDTH

        # 3. 绘制当前音符
        for note_idx in range(start_idx, end_idx):
            note_code, _ = music_notes[note_idx]
            note_info = NOTE_POSITION_MAP[note_code]
            note_sym = note_info['symbol']
            note_pos = note_info['pos']

            # 映射五线谱行（相对于五线谱框架）
            staff_grid_row = POSITION_TO_ROW.get(note_pos, 5)
            terminal_row = fixed_lines['staff_start'] + 2 + staff_grid_row
            note_start_col = base_col + (note_idx -
                                         start_idx) * CUSTOM_NOTE_WIDTH

            # 确保音符在终端范围内
            if 0 < note_start_col < term_width - CUSTOM_NOTE_WIDTH:
                sys.stdout.write(f"\033[{terminal_row};{note_start_col}H")
                if note_idx == current_note_idx:
                    # 红色高亮当前音符
                    sys.stdout.write(
                        f"\033[31m{note_sym * CUSTOM_NOTE_WIDTH}\033[0m")
                else:
                    sys.stdout.write(note_sym * CUSTOM_NOTE_WIDTH)

        # 4. 更新进度行（不覆盖打字机）
        progress_text = f"播放进度：{current_note_idx + 1}/{len(music_notes)} | 打字机：{'运行中' if is_typing_flag else '已完成'}"
        progress_col = (term_width - len(progress_text)) // 2
        progress_row = fixed_lines['progress']
        sys.stdout.write(f"\033[{progress_row};1H")
        sys.stdout.write(" " * term_width)
        sys.stdout.write(f"\033[{progress_row};{progress_col}H{progress_text}")

        sys.stdout.flush()
        time.sleep(0.05)

    # 播放结束提示
    end_text = "🎶 播放结束！感谢聆听～ | 📝 文本打印完成"
    end_col = (term_width - len(end_text)) // 2
    progress_row = fixed_lines['progress']
    sys.stdout.write(f"\033[{progress_row};1H")
    sys.stdout.write(" " * term_width)
    sys.stdout.write(f"\033[{progress_row};{end_col}H{end_text}")
    sys.stdout.flush()
    time.sleep(4)  # 延长停留时间，方便查看


# ===================== 主控制（原功能） =====================
def start_music_with_staff():
    global current_note_idx, is_playing_flag
    current_note_idx = 0
    is_playing_flag = False

    audio_thread = threading.Thread(target=audio_play_thread)
    visual_thread = threading.Thread(target=staff_visual_thread)

    audio_thread.start()
    time.sleep(0.2)  # 稍等音频启动，确保同步
    visual_thread.start()

    audio_thread.join()
    visual_thread.join()


# ===================== 程序入口 =====================
if __name__ == "__main__":
    try:
        # 步骤1：打印代码（可选，不影响主功能）
        # print_code_character_by_character()

        # 步骤2：读取乐谱
        with open("music/config.txt", "r", encoding="utf-8") as f:
            music_notes = [
                eval(line.strip()) for line in f.readlines()
                if line.strip() and line.strip().startswith("(")
            ]

        # 校验乐谱
        valid_notes = set(NOTE_POSITION_MAP.keys())
        for idx, (note_code, dur) in enumerate(music_notes):
            if note_code not in valid_notes:
                raise ValueError(f"第{idx+1}行：未知音符「{note_code}」")
            if not isinstance(dur, (int, float)) or dur <= 0:
                raise ValueError(f"第{idx+1}行：时长必须为正数")

        # 步骤3：显示开始提示
        show_start_prompt()

        # 步骤4：清空终端并启动
        clear_terminal()
        start_music_with_staff()

    except FileNotFoundError:
        clear_terminal()
        print("❌ 未找到 music/config.txt 文件")
        print("   解决方案：在程序同级目录创建「music」文件夹，放入「config.txt」乐谱")
    except SyntaxError:
        clear_terminal()
        print("❌ config.txt 格式错误！正确示例：('C4', 1)（英文符号）")
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
        print("   建议：重新安装依赖 → pip install numpy simpleaudio")
