
from VideoAutoSort import VideoAutoSort
from MediaRenamer import MediaRenamer

SOURCE_DIR = r"D:\PRIVATE\M4ROOT\CLIP" # Your camera's Video folder

DESTINATION_DIR = r"DESTINATION_DIR"
MODE = 'COPY'
FOLDER_SUFFIX = r'RfilingAutoGen'

VideoAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX)

TARGET_DIR = r"TARGET_DIR"

MediaRenamer(TARGET_DIR)