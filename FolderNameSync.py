# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


def FolderNameSync(SOURCE_DIR, DES_DIR): 
    """

    :param SOURCE_DIR: Directory for reference.
    :param DES_DIR:  Directory to modify.
    :return: nothing
    """
    import os

    to_be_renamed = DES_DIR
    reference_dir = SOURCE_DIR

    # Check if the directories exist
    if not os.path.exists(to_be_renamed) or not os.path.exists(reference_dir):
        print("Either directory A or directory B does not exist. Please make sure both exist.")
        exit(1)

    # Iterate/traverse folders in directory_A
    for folder_name_A in os.listdir(to_be_renamed):

        # Read the first 10 characters of the folder's name in directory_A
        prefix_A = folder_name_A[:10]

        # Initialize variable to hold matching folder's name in reference_dir
        folder_name_B = None

        # Find the folder's name in reference_dir with the same first 10 characters
        for candidate_folder_name_B in os.listdir(reference_dir):
            if candidate_folder_name_B.startswith(prefix_A):
                folder_name_B = candidate_folder_name_B
                break

        # If a folder in reference_dir with matching first 10 characters is found
        if folder_name_B:
            # Check if folder_name_A is the same as folder_name_B
            if folder_name_A == folder_name_B:
                print(f"{folder_name_A} is already named correctly. Skipping.")
                continue

            # Prompt for confirmation before renaming
            confirmation = input(f"Do you want to rename {folder_name_A} to {folder_name_B}? (y/n): ")

            if confirmation.lower() == 'y':
                # Rename folder in directory_A to folder_name_B
                original_path_A = os.path.join(to_be_renamed, folder_name_A)
                new_path_A = os.path.join(to_be_renamed, folder_name_B)

                os.rename(original_path_A, new_path_A)
                print(f"Renamed {folder_name_A} to {folder_name_B}.")
            else:
                print(f"Skipped renaming {folder_name_A}.")

        else:
            print(f"No matching folder found in directory B for {folder_name_A}.")
    return 0


if __name__ == '__main__':
    remote_nas = r'YOUR_REMOTE_ADDRESS'  
    local_disk = r'YOUR_LOCAL_ADDRESS'   
    FolderNameSync(local_disk, remote_nas)
