import pyperclip
import keyboard
import re
import time
import logging

# Setup logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Pre-compiled regular expressions for efficiency
TIMING_PATTERN = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
NUMERIC_PATTERN = re.compile(r'^\d+$')
PUNCTUATION_PATTERN = re.compile(r'[.,]')

def format_time(hhmmss):
    """Format time from HH:MM:SS to MM:SS."""
    hh, mm, ss = hhmmss.split(':')
    return f"{mm}:{ss}"

def extract_subtitle_text(subtitle_content):
    """Extract start and end timings along with the first two and last two words of the combined text."""
    lines = subtitle_content.splitlines()
    text_lines = []
    start_timing = ""
    end_timing = ""

    for line in lines:
        if TIMING_PATTERN.match(line):
            if not start_timing:
                start_timing = format_time(line.split(" --> ")[0].split(",")[0])
            end_timing = format_time(line.split(" --> ")[1].split(",")[0])
        elif not NUMERIC_PATTERN.match(line):
            text_lines.append(line)

    text = " ".join(text_lines).lower()
    text = PUNCTUATION_PATTERN.sub('', text)
    words = text.split()
    if len(words) >= 4:
        modified_text = f"{' '.join(words[:2])}... - ...{' '.join(words[-2:])}"
    else:
        modified_text = text

    return start_timing, end_timing, modified_text

def is_subtitle_content(content):
    """Check if the content is likely to be subtitle content."""
    lines = content.splitlines()
    for line in lines:
        if TIMING_PATTERN.match(line):
            return True
    return False

def modify_clipboard():
    try:
        original_text = pyperclip.paste()
        if is_subtitle_content(original_text):
            start_timing, end_timing, modified_text = extract_subtitle_text(original_text)
            pyperclip.copy(f"{start_timing} - {end_timing} ({modified_text})")
    except Exception as e:
        logging.error(f"Error modifying clipboard: {e}")

def on_ctrl_c():
    try:
        time.sleep(0.1)
        modify_clipboard()
    except Exception as e:
        logging.error(f"Error handling Ctrl+C: {e}")

keyboard.add_hotkey('ctrl+c', on_ctrl_c)

print("Script is running... Press Ctrl+C to modify clipboard contents or Ctrl+D to exit.")
try:
    while True:
        keyboard.wait('ctrl+c')
except KeyboardInterrupt:
    print("Script stopped by user")