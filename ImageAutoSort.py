# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 21:53:27 2023

@author: Raph
"""

import os
import shutil
import hashlib
import exifread


def compute_md5(file_path):
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for buf in iter(lambda: f.read(4096), b""):
            hasher.update(buf)
    return hasher.hexdigest()


def ensure_directory_structure(destination_dir, year, month, day, suffix):
    """Create the directory structure if it doesn't exist. Return the final directory path."""
    year_folder = os.path.join(destination_dir, year)
    month_folder = os.path.join(year_folder, month.zfill(2))

    # First, make sure year and month folders exist before attempting to list contents
    for folder in [year_folder, month_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    date_prefix = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    existing_day_folders = [d for d in os.listdir(month_folder) if d.startswith(date_prefix)]

    if existing_day_folders:
        day_folder = os.path.join(month_folder, existing_day_folders[0])
    else:
        day_folder = os.path.join(month_folder, f"{date_prefix}-{suffix}")

    # Only need to check for day_folder here, as year_folder and month_folder were already checked above
    if not os.path.exists(day_folder):
        os.makedirs(day_folder)

    return day_folder


def do_xmp_file(xmp_files, file, des_folder, MODE):
    # Check for an associated .xmp file ========================================================================
    # need file, des_folder
    xmp_file = os.path.splitext(file)[0] + '.xmp'
    # print(xmp_file)
    if os.path.exists(xmp_file):
        # Copy the .xmp file to the same destination as the image file
        des_xmp_file = os.path.join(des_folder, os.path.basename(xmp_file))
        if os.path.exists(des_xmp_file):
            print("We found a xmp file at the destination. We will preserve the xml at the destination.\n"
                  "We won't delete the one at the source directory.")
        else:
            if MODE == 'COPY':
                print(f"Copying associated .xmp file {os.path.basename(xmp_file)} to\n{des_folder}")
                shutil.copy2(xmp_file, des_xmp_file)  # Do copy
                xmp_files.add(xmp_file)
            if MODE == 'MOVE':
                print(f"Moving associated .xmp file {os.path.basename(xmp_file)} to\n{des_folder}")
                shutil.move(xmp_file, des_xmp_file)  # Do copy
                xmp_files.add(xmp_file)
    return xmp_files


def get_date_from_exif(file_path):
    """
    Extract the date from the Exif data of an image file using exifread.
    Returns a tuple of (year, month, day) or None if Exif data is not found or DateTimeOriginal tag is missing.
    """
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                year, month, day = date_str.split(":")[0], date_str.split(":")[1], date_str.split(":")[2].split()[0]
                return year, month, day
    except Exception as e:
        print(f"Error reading Exif data from {file_path}: {e}")
    return None


def should_ignore_folder(folder_path):
    import os
    """Check if the folder should be ignored based on its name or its content."""
    if "@Recycle" in folder_path:
        return True
    if ".nomedia" in os.listdir(folder_path):
        return True
    return False


def tree_files(SOURCE_DIR, SUPPORTED_EXTENSIONS):
    """
    GEt all files within a specific extensions.
    :param SOURCE_DIR: the directory to explore
    :param SUPPORTED_EXTENSIONS: the extension to take
    :return:
    """
    import os
    # Dealing with exception =========================================================================================
    SUPPORTED_EXTENSIONS = [ext.lower() for ext in SUPPORTED_EXTENSIONS]
    all_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        # from ImageAutoSort import should_ignore_folder
        if should_ignore_folder(root):
            print(f"{root} is ignored.\n")
            continue
        for file in files:
            if file.lower().endswith(tuple(SUPPORTED_EXTENSIONS)):
                file_full_dir = os.path.join(root, file)
                print(f"{file_full_dir} added.\n")
                all_files.append(file_full_dir)
    return all_files


def ImageAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX):
    """
    Automatically sorts images based on some criteria.

    Args:
        SOURCE_DIR (str): The directory from which images will be sorted.
        DESTINATION_DIR (str): The directory to which sorted images will be moved or copied.
        MODE (str): The operation mode - 'COPY' or 'MOVE'.
        FOLDER_SUFFIX: The suffix of the deepest folder.

    Returns:
        None

    Raises:
        ValueError: If MODE is not 'COPY' or 'MOVE'.
    """

    # Configuration =========================================================================================
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.arw', '.dng', '.heic']

    # todo: Check if it is in demo mode: which just list the files and their operations (copy or conflict),
    #  but not do it.
    demo_mode = True

    # todo: 1-Click to undo the last operation.
    # todo: Show the picture which is being sorted.

    if MODE != 'COPY' and MODE != 'MOVE':
        print("MODE incorrect. Existing. ")
        raise ValueError("MODE must be either 'COPY' or 'MOVE'.")
        # from sys import exit
        # exit(1)

    print("**************\n"
          f"Source: \n{SOURCE_DIR}\n"
          f"Destination: \n{DESTINATION_DIR}\n"
          f"**************\n")
    # all_files = []
    # for root, dirs, files in os.walk(SOURCE_DIR):
    #     if should_ignore_folder(root):
    #         continue
    #     for file in files:
    #         if file.lower().endswith(tuple(SUPPORTED_IMAGE_EXTENSIONS)):
    #             all_files.append(os.path.join(root, file))
    all_files = tree_files(SOURCE_DIR, SUPPORTED_IMAGE_EXTENSIONS)

    copied_files = set()
    moved_files = set()
    conflict_files2delete = set()
    xmp_files = set()
    exact_files = []
    conflict_files = []
    potential_conflicts = []
    dir_potential_conflicts = {}  #dict

    for file in all_files:
        if file in copied_files:
            continue
        import time
        start = time.time()
        date_from_exif = get_date_from_exif(file)
        end = time.time()
        print(f"Time spent on EXIF extraction: {end - start:.2f}s")

        if date_from_exif:
            year, month, day = date_from_exif
        else:
            print(f"Failed to extract date from Exif for {file}. Skipping.")
            continue

        des_folder = ensure_directory_structure(DESTINATION_DIR, year, month, day, FOLDER_SUFFIX)
        des_file = os.path.join(des_folder, os.path.basename(file))

        if os.path.exists(des_file):
            print(f"Found conflict for {os.path.basename(file)}... Skip it.")
            potential_conflicts.append((file, des_file))
            dir_potential_conflicts[os.path.basename(file)] = des_file

            # Check for an associated .xmp file ========================================================================
            do_xmp_file(xmp_files, file, des_folder, MODE)
        else:
            if MODE == 'COPY':
                print(f"Copying {os.path.basename(file)} from\n{os.path.dirname(file)} to\n{des_folder}")
                start = time.time()
                shutil.copy2(file, des_folder)  # Do copy
                copied_files.add(file)
                end = time.time()
                print(f"Time spent on copy: {end - start:.2f}s")
            elif MODE == 'MOVE':
                print(f"Moving {os.path.basename(file)} from\n{os.path.dirname(file)} to\n{des_folder}")
                start = time.time()
                shutil.move(file, des_folder)  # Do move
                moved_files.add(file)
                end = time.time()
                print(f"Time spent on copy: {end - start:.2f}s")
            else:
                print("MODE incorrect.")
            # Check for an associated .xmp file ========================================================================
            do_xmp_file(xmp_files, file, des_folder, MODE)

    # Processing conflicts =========================================================================================
    file_can_be_deleted = copied_files | xmp_files
    for src_file, des_file in potential_conflicts:
        print(f"Checking conflict for {os.path.basename(src_file)}...")
        src_md5 = compute_md5(src_file)
        des_md5 = compute_md5(des_file)
        if src_md5 == des_md5:
            exact_files.append(src_file)
            conflict_files2delete.add(src_file)
        else:
            conflict_files.append(src_file)
    if not conflict_files:
        delete_prompt = 'no'  # default.
        if not exact_files:
            if not copied_files:
                pass  # Nothing to delete
            else:
                delete_prompt = input(
                    "\nDo you want to delete the files from the source directory? (yes/no): ").strip().lower()
        else:  # within the scope!
            delete_prompt = input(
                "\nExactly same files in your destination. No conflicts. Do you want to delete the files from the "
                "source directory? (yes/no): ").strip().lower()

        if delete_prompt == 'yes':
            files2delete = file_can_be_deleted | conflict_files2delete
            for file in files2delete:
                # Turn this into a function ============================================================================
                try:
                    print(f"Deleting {file}...\n")
                    os.remove(file)
                except PermissionError as e:
                    if 'WinError 32' in str(e):
                        print(f"Couldn't delete file {file} because it's being used by another process.")
                    else:
                        print(f"Permission error for file {file}: {e}")
            # for file in copied_files:
            #     try:
            #         os.remove(file)
            #     except PermissionError as e:
            #         if 'WinError 32' in str(e):
            #             print(f"Couldn't delete file {file} because it's being used by another process.")
            #         else:
            #             print(f"Permission error for file {file}: {e}")
            # for file in conflict_files2delete:
            #     try:
            #         os.remove(file)
            #     except PermissionError as e:
            #         if 'WinError 32' in str(e):
            #             print(f"Couldn't delete file {file} because it's being used by another process.")
            #         else:
            #             print(f"Permission error for file {file}: {e}")

    # If conflicts happen =========================================================================================
    else:
        print("\nFiles with naming conflicts (but different content):")
        for conflict_file in conflict_files:
            print(os.path.basename(conflict_file))
        choice = input("Do you want to overwrite these conflict files in the destination? (yes/no): ").strip().lower()
        if choice == 'yes':
            for conflict_file in conflict_files:
                des_folder = dir_potential_conflicts[os.path.basename(conflict_file)]
                shutil.copy2(conflict_file, des_folder)
        print("\nIn this case, we won't proactively delete your files.")

    print("\nProcess completed!")


class FileSorting:
    def __init__(self, SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX):
        self.SOURCE_DIR = SOURCE_DIR
        self.DESTINATION_DIR = DESTINATION_DIR
        self.MODE = MODE
        self.FOLDER_SUFFIX = FOLDER_SUFFIX

    def ImageAutoSort(self):
        ImageAutoSort(self.SOURCE_DIR, self.DESTINATION_DIR, self.MODE, self.FOLDER_SUFFIX)

if __name__ == '__main__':
    # ver = "Raphael's Image auto-sorting script. "
    # print(ver)

    SOURCE_DIR = r"SOURCE_DIR"
    DESTINATION_DIR = r"DESTINATION_DIR"
    MODE = 'COPY'  # 'COPY' or 'MOVE', MOVE is not an atomic activity, so it is not recommended.
    ImageAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, 'RfilingAutoGen')


    # # Future development: use class to collect all methods (like namesync or video sorting)
    # SortDemoFolder = FileSorting(SOURCE_DIR=r"SOURCE_DIR",
    #                              DESTINATION_DIR=r"DESTINATION_DIR",
    #                              MODE='COPY',
    #                              FOLDER_SUFFIX='RfilingAutoGen')