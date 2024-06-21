## Rfiling：相机照片视频自动化整理的脚本

### 概述
**无论是通过 FTP 无线传输还是用 SD 卡，每次拍完照片和视频后，你都得要把他们传输到电脑或 NAS，然后逐个分类，有够麻烦。Rfiling应运而生！** Rfiling 是我做的一组 Python 脚本，可以帮你自动做相机的拷卡和整理工作。Rfiling 支援照片(JPG, HEIC, RAW+JPG)和视频(MP4, Sony的MP4和它配套的XML），会提取元数据，能够自动处理文件冲突。你可以试试看！

Rfiling主要由三个函数组成：
- `MediaRenamer`：通过读取视频元数据来重命名视频文件的脚本，可以帮你把Color Primaries/Transfer characteristics 写在文件名上。
- `VideoAutoSort`：根据创建日期帮助你复制和整理视频，支持自动处理文件冲突。
- `ImageAutoSort`：功能与 VideoAutoSort 相同，但处理的是图像文件。

### 要求
- Python 环境
- 需要的库：`os`、`shutil`、`time`、`exifread`、`xml`、`pymediainfo`
  - 建议使用 `exifread` 的版本 2.3.1。我发现最新版本（3.0.0）处理HEIF有一些问题。

### 安装
1. 从 GitHub 仓库克隆或下载脚本。
2. 确保系统已安装 Python。用Pycharm Comunity 版本就很好。
3. 根据需要安装缺失的库。

### 使用方法
1. **设置源和目标目录及参数**：定义源和目标目录的路径。这些路径应为绝对路径。详细信息请参见脚本中的 `__main__` 函数。

2. **运行脚本**：写一个Python script 调用函数。可以参考 [PlayGround.py](PlayGround.py) 文件。这样每次就可以一键拷卡了！

```python
from VideoAutoSort import VideoAutoSort
from MediaRenamer import MediaRenamer

SOURCE_DIR = r"D:\PRIVATE\M4ROOT\CLIP" # Your camera's Video folder

DESTINATION_DIR = r"DESTINATION_DIR"
MODE = 'COPY'
FOLDER_SUFFIX = r'RfilingAutoGen'

VideoAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX)

TARGET_DIR = r"TARGET_DIR"

MediaRenamer(TARGET_DIR)
```


### “Video/ImageAutoSort” 的功能
- **支持的文件格式**：
  - **ImageAutoSort**：由 ExifRead 支持的图像文件，包括 ARW（索尼相机的原始图像格式），会自动处理与ARW配套的 JPG 。
  - **VideoAutoSort**：索尼相机拍摄的视频文件（在 ILCE A7C 上测试）。它会自动解析文件名中的视频创建日期并将视频复制到按照日期命名的目标文件夹。
- **冲突处理**：在整理过程中检测并处理文件冲突。还提供在复制后删除源文件的选项（还在做），确保没有数据丢失。
- **元数据提取**：从图像 EXIF 数据中提取日期信息进行整理。
- **自动文件夹命名**: 目录格式是 `\2024\06\2024-06-13-Rfiling` 这样子，其中`Rfiling`是 `suffix`，可以自己在函数里面设定。你可以随便改后缀，比如改成`2024-06-13 去鸟特乐支玩`，`*AutoSort`会自动识别日期，每次都放到`2024-06-13 去鸟特乐支玩`里面（而不是新建一个`2024-06-13-Rfiling`）.
  
### “MediaRenamer” 的功能
- **重命名视频文件**：重命名索尼相机拍摄的视频文件（在 ILCE A7C 上测试）。它会自动解析与视频文件同名的索尼 XML 文件，并在视频文件名后加上 XML 文件中的颜色、分辨率和帧率信息。如果 XML 文件不存在，它会尝试使用 MediaInfo 进行解析并重命名。举个例子：

```
20230813_C1573.MP4 
将被重命名为 -> 
20230813_C1573-1080p120-rec2100-hlg_rec2020.MP4
```
这样子就可以让你一眼看出来你拍的是什么帧率，Color Space 和Transfer characteristics 了。

### 未来改进
- **移动模式**: 自动删除已经处理过了的照片/视频文件。目前的实现还不完善，有一些edge case 没有处理
- **演示模式**：列出文件及其操作而不实际执行。
- **撤销功能和视觉反馈**：计划中。
- **错误处理**：可以添加更健全的错误处理和日志记录。
- **拖放功能**：可以添加一个 GUI，以允许拖放整理功能。不过我不太会做，有朋友推荐方法实现的吗？

### 联系和支持
如有问题、建议或贡献，的话可以创建Issues。欢迎你的反馈和贡献！

### 请我喝杯咖啡
如果你喜欢这个项目，请考虑[请我喝杯咖啡](https://www.buymeacoffee.com/zhizhiyang)。感谢你的支持！


## Rfiling: Camera Photo Video Auto - User Guide

### Overview
Rfiling is a set of Python script designed to automate the sorting of images from a source directory to a destination directory. **Whether using FTP or an SD card, every time you finish taking photos and videos, you need to find a way to transfer them from temporary media to your computer or NAS, and then categorize them one by one. This process is repetitive and cumbersome. Thefore, I write these scripts  to solve the problem described above.** This set supports both copying and moving images, and handles file conflicts and metadata extraction. It consists of:
- `MediaRenamer`: a script to rename video files with their metadata
- `VideoAutoSort`: a script to help you copy and sort videos with thier creation date with duplication detection.
- `ImageAutoSort`: same feature as VideoAutoSort, but dealing with images.

### Requirements
- Python environment
- Required libraries: `os`, `shutil`, `time`, `exifread`, `xml`, `pymediainfo`.
  - The version of `exifread` is better to be 2.3.1, which is the version used in development. We encontered bugs while using the latest version (3.0.0) in development.

### Installation
1. Clone or download the scripts from the GitHub repository.
2. Ensure Python is installed on your system.
3. Install any missing libraries as needed.

### Usage
1. **Set Source and Destination Directories and parameter:** Define the paths for your source and destination directories. These paths should be absolute paths. Check out the `__main__` function in the script for more details.
   

2. **Run the Script:** Execute the script with the defined parameters. 


### Features of "Video/ImageAutoSort"
- **Supported File Formats:** 
   - **ImageAutoSort**: Image file supported by ExifRead, including ARW (raw image format of Sony cameras). 
   - **VideoAutoSort**: Video files captured by sony camera (tested on ILCE A7C). It will automatically parse the video creation date from the file name and copy the video to the destination folder.
- **Conflict Handling:** Detects and handles file conflicts during the sorting process. Also provides an option to delete source files after copying, ensuring no data loss.
- **Metadata Extraction:** Extracts date information from image EXIF data for sorting.


### Features of "MediaRenamer"
- **Rename Video Files:** Rename video files captured by sony camera (tested on ILCE A7C). It will automatically parse sony's XML file with the same name as the video file and suffixing the video file with the Color/Resolution/framerate information in the XML file. If XML does not exist, it will try to use MediaInfo to parse and then rename. For example:

```
20230813_C1573.MP4 
Will be renamed to -> 
20230813_C1573-1080p120-rec2100-hlg_rec2020.MP4
```


### Limitations and Future Improvements
- **Demo Mode:** Lists files and their operations without performing them.
- **Undo Feature and Visual Feedback:** Planned but not yet implemented.
- **Error Handling:** More robust error handling and logging can be added.
- **Drag-and-Drop:** A GUI can be added to allow drag-and-drop sorting functionality.

### Contact and Support
For issues, suggestions, or contributions, please visit the GitHub repository or contact the maintainer. Your feedback and contributions are welcome! 

### Buy me a coffee
If you like this project, please consider [buying me a coffee](https://www.buymeacoffee.com/zhizhiyang). Thank you for your support!
