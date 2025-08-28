import numpy as np
import simpleaudio as sa
import threading
import time
import os
import sys

NOTE_POSITION_MAP = {
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
    'R': {
        'symbol': ' ',
        'pos': 5
    }
}

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

SAMPLE_RATE = 44100
QUARTER_NOTE_DURATION = 0.25
STAFF_TOTAL_LINES = 11
STAFF_LINE_ROWS = [1, 3, 5, 7, 9]
STAFF_LINE_CHAR = "—"
STAFF_GAP_CHAR = " "
POSITION_TO_ROW = {9: 1, 8: 2, 7: 3, 6: 4, 5: 5, 4: 6, 3: 7, 2: 8, 1: 9}

CUSTOM_NOTE_WIDTH = 4
CUSTOM_DISPLAY_RANGE = 10

TYPEWRITER_TEXT = """
七夕快乐，亲爱的大宝！算下来我们已经认识一年多了，这场没有明确开始与时间的恋爱，一路风风雨雨坎坎坷坷，也很是不易。
是大宝一直坚定的爱着我，在每一次emo动摇之时给我安慰，大宝一直没有放弃过我，呜呜呜呜姐姐， 姐姐给我买好看的小裙子，
请我喝奶茶，陪我玩游戏，还当我的专属小瑶，呜呜姐姐真好。（他们一定不知道这个瑶一边玩游戏一边还在挨超♡矮油♡），呜呜大宝，
这一路感谢有你。幸好有你，也只能是你，希望我家大宝永葆青春年华，永远爱我，七夕快乐~
"""
TYPEWRITER_SPEED = 0.12
TYPEWRITER_COLOR = "\033[36m"
TYPEWRITER_ROW_START = 1

current_note_idx = 0
music_notes = []
is_playing_flag = False
term_width = 80
is_typing_flag = False
typed_lines = []
total_typewriter_lines = TYPEWRITER_TEXT.count('\n')

fixed_lines = {
    'typewriter_end':
    TYPEWRITER_ROW_START + total_typewriter_lines - 1,
    'staff_start':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1,
    'staff_end':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES - 1,
    'progress':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES,
    'border_bottom':
    TYPEWRITER_ROW_START + total_typewriter_lines + 1 + STAFF_TOTAL_LINES + 1
}


def typewriter_thread():
    global is_typing_flag, typed_lines

    is_typing_flag = True
    typed_lines = [""] * total_typewriter_lines
    current_line_idx = 0
    current_char_idx = 0
    text_lines = TYPEWRITER_TEXT.split('\n')[1:]

    if len(text_lines) < total_typewriter_lines:
        text_lines += [""] * (total_typewriter_lines - len(text_lines))

    while is_typing_flag and current_line_idx < total_typewriter_lines:
        if not is_playing_flag:
            break

        current_line = text_lines[current_line_idx]
        if current_char_idx < len(current_line):
            typed_char = current_line[current_char_idx]
            typed_lines[current_line_idx] += typed_char
            current_char_idx += 1
        else:
            current_line_idx += 1
            current_char_idx = 0

        for i in range(len(typed_lines)):
            terminal_row = TYPEWRITER_ROW_START + i
            sys.stdout.write(f"\033[{terminal_row};1H")
            sys.stdout.write(
                f"{TYPEWRITER_COLOR}{typed_lines[i].ljust(term_width)}\033[0m")

        sys.stdout.flush()
        time.sleep(TYPEWRITER_SPEED)

    for i in range(current_line_idx, len(text_lines)):
        terminal_row = TYPEWRITER_ROW_START + i
        sys.stdout.write(f"\033[{terminal_row};1H")
        sys.stdout.write(
            f"{TYPEWRITER_COLOR}{text_lines[i].ljust(term_width)}\033[0m")
    sys.stdout.flush()

    is_typing_flag = False


def print_code_character_by_character(script_path):
    try:
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


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    sys.stdout.write("\033c")
    sys.stdout.flush()


def show_start_prompt():
    clear_terminal()

    prompt_lines = [
        "════════════════════════════════════════════════════════════════",
        "║                                                                ║",
        "║                      ✨ 准备运行中 ...    ✨                   ║",
        "║                                                                ║",
        "║                      ⚠️  姐姐 呜呜 ...                         ║",
        "║                                                                ║",
        "════════════════════════════════════════════════════════════════"
    ]

    for line in prompt_lines:
        if len(line) <= term_width:
            print(line.center(term_width))
        else:
            print(line[:term_width])

    time.sleep(2.5)


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
    typing_thread = threading.Thread(target=typewriter_thread)
    typing_thread.start()

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
    typing_thread.join()


def staff_visual_thread():
    global current_note_idx, is_playing_flag, term_width

    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    def init_staff_frame():
        border_row = fixed_lines['staff_start'] - 1
        sys.stdout.write(f"\033[{border_row};1H")
        sys.stdout.write("=" * term_width)

        title_row = fixed_lines['staff_start']
        sys.stdout.write(f"\033[{title_row};1H")
        sys.stdout.write("🎵 嘻嘻嘻 涩姐姐".center(term_width))

        mid_border_row = fixed_lines['staff_start'] + 1
        sys.stdout.write(f"\033[{mid_border_row};1H")
        sys.stdout.write("-" * term_width)

        for i in range(STAFF_TOTAL_LINES):
            staff_row = fixed_lines['staff_start'] + 2 + i
            sys.stdout.write(f"\033[{staff_row};1H")
            if i in STAFF_LINE_ROWS:
                sys.stdout.write(STAFF_LINE_CHAR * term_width)
            else:
                sys.stdout.write(" " * term_width)

        progress_row = fixed_lines['progress']
        sys.stdout.write(f"\033[{progress_row};1H")
        sys.stdout.write(" " * term_width)

        bottom_border_row = fixed_lines['border_bottom']
        sys.stdout.write(f"\033[{bottom_border_row};1H")
        sys.stdout.write("=" * term_width)

        sys.stdout.flush()

    init_staff_frame()

    while is_playing_flag:
        for i in range(STAFF_TOTAL_LINES):
            staff_row = fixed_lines['staff_start'] + 2 + i
            terminal_row = staff_row
            sys.stdout.write(f"\033[{terminal_row};1H")
            if i in STAFF_LINE_ROWS:
                sys.stdout.write(STAFF_LINE_CHAR * term_width)
            else:
                sys.stdout.write(" " * term_width)

        start_idx = max(0, current_note_idx - CUSTOM_DISPLAY_RANGE)
        end_idx = min(len(music_notes),
                      current_note_idx + CUSTOM_DISPLAY_RANGE + 1)
        center_col = term_width // 2
        base_col = center_col - (current_note_idx -
                                 start_idx) * CUSTOM_NOTE_WIDTH

        for note_idx in range(start_idx, end_idx):
            note_code, _ = music_notes[note_idx]
            note_info = NOTE_POSITION_MAP[note_code]
            note_sym = note_info['symbol']
            note_pos = note_info['pos']

            staff_grid_row = POSITION_TO_ROW.get(note_pos, 5)
            terminal_row = fixed_lines['staff_start'] + 2 + staff_grid_row
            note_start_col = base_col + (note_idx -
                                         start_idx) * CUSTOM_NOTE_WIDTH

            if 0 < note_start_col < term_width - CUSTOM_NOTE_WIDTH:
                sys.stdout.write(f"\033[{terminal_row};{note_start_col}H")
                if note_idx == current_note_idx:
                    sys.stdout.write(
                        f"\033[31m{note_sym * CUSTOM_NOTE_WIDTH}\033[0m")
                else:
                    sys.stdout.write(note_sym * CUSTOM_NOTE_WIDTH)

        progress_text = f"播放进度：{current_note_idx + 1}/{len(music_notes)} | 唉，真没想到能走到这一步"
        progress_col = (term_width - len(progress_text)) // 2
        progress_row = fixed_lines['progress']
        sys.stdout.write(f"\033[{progress_row};1H")
        sys.stdout.write(" " * term_width)
        sys.stdout.write(f"\033[{progress_row};{progress_col}H{progress_text}")

        sys.stdout.flush()
        time.sleep(0.05)

    end_text = "🎶 播放结束！七夕快乐～ | "
    end_col = (term_width - len(end_text)) // 2
    progress_row = fixed_lines['progress']
    sys.stdout.write(f"\033[{progress_row};1H")
    sys.stdout.write(" " * term_width)
    sys.stdout.write(f"\033[{progress_row};{end_col}H{end_text}")
    sys.stdout.flush()
    time.sleep(4)


def start_music_with_staff():
    global current_note_idx, is_playing_flag
    current_note_idx = 0
    is_playing_flag = False

    audio_thread = threading.Thread(target=audio_play_thread)
    visual_thread = threading.Thread(target=staff_visual_thread)

    audio_thread.start()
    time.sleep(0.2)
    visual_thread.start()

    audio_thread.join()
    visual_thread.join()


if __name__ == "__main__":
    try:
        # print_code_character_by_character("music/script.py")
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

        show_start_prompt()

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
        sys.stdout.write("\033[?25h")
        print("\n🛑 程序已手动停止")
    except Exception as e:
        clear_terminal()
        print(f"❌ 运行错误：{e}")
        print("   建议：重新安装依赖 → pip install numpy simpleaudio")
