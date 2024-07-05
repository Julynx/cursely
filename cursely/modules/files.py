"""
Contains methods to delete files in a folder.
"""

import os


def delete_files_in_folder(folder):
    """
    Delete all files in a folder.

    Args:
        folder (str): The folder to delete the files from.
    """
    for entry in os.scandir(folder):
        if entry.is_file():
            os.remove(entry.path)
