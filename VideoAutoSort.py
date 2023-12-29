# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 21:53:27 2023

@author: Raph
"""

import os
import shutil
import hashlib


def compute_md5(file_path):
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for buf in iter(lambda: f.read(4096), b""):
            hasher.update(buf)
    return hasher.hexdigest()


# # Example usage:
# destination_dir = "./test_dir"
# ensure_directory_structure(destination_dir, "2023", "10", "24")


def get_corresponding_file(file_path):
    """Return the corresponding XML for an MP4 and vice versa."""
    dirname, basename = os.path.split(file_path)
    ext = basename[-3:]
    base = basename[:-4]  # Excluding the extension

    if ext.upper() == 'MP4':
        return os.path.join(dirname, f"{base}M01.XML")
    elif ext.upper() == 'XML':
        return os.path.join(dirname, base[:-4] + ".MP4")
    else:
        return None


def VideoAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX):
    """Automatically sort videos and their corresponding XML files into folders based on their creation date."""

    # Exceptions ================================================
    if MODE != 'COPY' and MODE != 'MOVE':
        print("MODE incorrect. Exiting.")
        raise ValueError("MODE must be either 'COPY' or 'MOVE'.")
    if not os.path.exists(DESTINATION_DIR):
        print("Destination directory does not exist. Exiting.")
        return

    print("**************\n"
          f"Your source directory is \n{SOURCE_DIR}\n"
          f"Your destination is \n{DESTINATION_DIR}\n"
          f"**************\n")

    # all_files = glob(os.path.join(SOURCE_DIR, "*.MP4")) + glob(os.path.join(SOURCE_DIR, "*.XML"))

    SUPPORTED_EXTENSIONS = ['.MOV', '.MP4', '.m4v']

    from ImageAutoSort import tree_files
    # Get all files' list =========================================================================================
    all_files = tree_files(SOURCE_DIR, SUPPORTED_EXTENSIONS)

    # check if directory exists

    if not all_files:
        print("No files found in your source directory. Exiting.")
        return

    processed_files = set()
    exact_files = []
    conflict_files = []
    potential_conflicts = []

    for file in all_files:
        if file in processed_files:
            continue
        # 需要解决文件名不是编码好的情况 =========================================================================================
        basename = os.path.basename(file)
        # [year, month, day] = afunction(basename)
        year = basename[:4]
        month = basename[4:6]
        day = basename[6:8]

        from ImageAutoSort import ensure_directory_structure
        dest_folder = ensure_directory_structure(DESTINATION_DIR, year, month, day,
                                                 FOLDER_SUFFIX if MODE == "COPY" else None)
        dest_file = os.path.join(dest_folder, basename)

        # Todo: Use prefix and filesize to decide conflict =============================================================
        if os.path.exists(dest_file):
            print(f"Found conflict for {basename}... Skip it.")
            potential_conflicts.append((file, dest_file))
            continue

        if MODE == 'COPY':
            print(f"Copying {os.path.basename(file)} from\n{os.path.dirname(file)} to\n{dest_folder}")
            shutil.copy2(file, dest_folder)
        elif MODE == 'MOVE':
            print(f"Moving {os.path.basename(file)} from\n{os.path.dirname(file)} to\n{dest_folder}")
            shutil.move(file, dest_folder)

        processed_files.add(file)

        # Check and copy/move the corresponding file if it exists
        partner_file = get_corresponding_file(file)
        if partner_file and os.path.exists(partner_file):
            if MODE == 'COPY':
                shutil.copy2(partner_file, dest_folder)
            elif MODE == 'MOVE':
                shutil.move(partner_file, dest_folder)
            processed_files.add(partner_file)
    # print(processed_files)
    # Processing conflicts =========================================================================================
    file_can_be_deleted = processed_files
    conflict_files2delete = set()
    for src_file, dest_file in potential_conflicts:
        print(f"Checking conflict for {os.path.basename(src_file)}...")
        src_md5 = compute_md5(src_file)
        des_md5 = compute_md5(dest_file)
        if src_md5 == des_md5:
            exact_files.append(src_file)
            conflict_files2delete.add(src_file)
        else:
            conflict_files.append(src_file)

    if MODE == 'COPY':
        if not conflict_files:
            while True:
                delete_prompt = input(  # Exactly same files in your destination.
                    "\n"
                    "No conflicts. Do you want to delete the files from the "
                    "source directory? (yes/no): ").strip().lower()
                if delete_prompt == 'yes' or delete_prompt == 'no':
                    break

            if delete_prompt == 'yes':
                files2delete = file_can_be_deleted | conflict_files2delete
                for file in files2delete:
                    print(f"Deleting {file}...\n")
                    os.remove(file)
        else:
            # Print file list of conflicts ================================================
            print("\nFiles with naming conflicts (but different content):")
            for conflict_file in conflict_files:
                print(os.path.basename(conflict_file))

            # Prompt user for overwrite
            choice = input(
                "Do you want to overwrite these conflict files in the destination? (yes/no): ").strip().lower()
            if choice == 'yes':
                for conflict_file in conflict_files:
                    from ImageAutoSort import ensure_directory_structure
                    dest_folder = ensure_directory_structure(destination_dir=DESTINATION_DIR,
                                                             year=os.path.basename(conflict_file)[:4],
                                                             month=os.path.basename(conflict_file)[4:6],
                                                             day=os.path.basename(conflict_file)[6:8],
                                                             suffix='RfilingAutoGen')
                    # print(dest_folder)
                    shutil.copy2(conflict_file, dest_folder)
            print("\nIn this case, we will not actively request the deletion of your files.")

    elif MODE == 'MOVE' and conflict_files:
        print("\nFiles with naming conflicts (but different content):")
        for conflict_file in conflict_files:
            print(os.path.basename(conflict_file))
        choice = input("Do you want to overwrite these conflict files in the destination? (yes/no): ").strip().lower()
        if choice == 'yes':
            for conflict_file in conflict_files:
                from ImageAutoSort import ensure_directory_structure
                dest_folder = ensure_directory_structure(DESTINATION_DIR, os.path.basename(conflict_file)[:4],
                                                         os.path.basename(conflict_file)[4:6],
                                                         os.path.basename(conflict_file)[6:8],
                                                         'RfilingAutoGen')
                shutil.move(conflict_file, dest_folder)

    print("\nProcess completed!")


if __name__ == '__main__':
    SOURCE_DIR = r"D:\PRIVATE\M4ROOT\CLIP"  # Your camera's Video folder
    DESTINATION_DIR = r"YOUR_DESTINATION\ILCE\CameraRoll\Video"
    MODE = 'COPY'
    FOLDER_SUFFIX = r'RfilingAutoGen'

    VideoAutoSort(SOURCE_DIR, DESTINATION_DIR, MODE, FOLDER_SUFFIX)
