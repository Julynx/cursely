"""
Contains methods to install a modpack config zip to a Minecraft installation.
"""

import shutil
import sys


def install_modpack_config(modpack_config_path: str,
                           mc_installation_path: str):
    """
    Install a modpack config to a Minecraft installation.

    Args:
        modpack_config_path (str): The path to the modpack config.
        mc_installation_path (str): The path to the Minecraft installation.
    """
    tmp_dir = "/tmp/cursely"
    if sys.platform == "win32":
        tmp_dir = "C:\\tmp\\cursely"

    shutil.unpack_archive(modpack_config_path, tmp_dir)
    shutil.copytree(tmp_dir, mc_installation_path, dirs_exist_ok=True)
    shutil.rmtree(tmp_dir)
