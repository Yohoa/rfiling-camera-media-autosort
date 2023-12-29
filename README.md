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
- **Demo Mode:**W Lists files and their operations without performing them.
- **Undo Feature and Visual Feedback:** Planned but not yet implemented.
- **Error Handling:** More robust error handling and logging can be added.
- **Drag-and-Drop:** A GUI can be added to allow drag-and-drop sorting functionality.

### Contact and Support
For issues, suggestions, or contributions, please visit the GitHub repository or contact the maintainer. Your feedback and contributions are welcome! 

### Buy me a coffee
If you like this project, please consider [buying me a coffee](https://www.buymeacoffee.com/zhizhiyang). Thank you for your support!
