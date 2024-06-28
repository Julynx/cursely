import os
import shutil
import subprocess
import sys
from itertools import chain, repeat
from multiprocessing import Pool
from time import sleep

import requests

from .config import CONFIG_PATH, DOWNLOAD_RETRIES, SHELL_ARGS, SHELL_PATH
from .mods import CurseforgeMod, Mod, ModrinthMod


def build_modpack(modpack_file, cfg):
    """
    Build a modpack from a modpack file.

    Args:
        modpack_file (str): Path to the modpack file.
        cfg (dict): The config file as a dictionary object.
    """

    def process_file(modpack_file, cfg):
        """
        Process a modpack file.

        Args:
            modpack_file (str): Path to the modpack file.
            cfg (dict): The config file as a dictionary object.

        Returns:
            dict: A dictionary containing the information from the file:
                  {mods: {Mod(id=12123), ...},
                   urls: {str, ...},
                   windows_cmds: [str, ...],
                   linux_cmds: [str, ...]
                   generic_cmds: [str, ...]}
        """
        file_lines = []
        with open(modpack_file, "r") as file:
            file_lines = file.readlines()

        return {
            "mods": {
                Mod(line.strip().split(" ", maxsplit=1)[0],
                    cfg,
                    version=version_from_modpack_line(line))
                for line
                in file_lines
                if line.strip()                          # Skip empty
                and not line.lstrip().startswith("#")    # Skip comments
                and not line.lstrip().startswith("$")    # Skip commands
                and not line.lstrip().startswith("@")},  # Skip URLs

            "urls": {
                line[len("@"):].strip()
                for line
                in file_lines
                if line.startswith("@")},

            "windows_cmds": [
                line[len("$ %WIN32%"):].strip()
                for line
                in file_lines
                if line.lstrip().startswith("$ %WIN32%")],

            "linux_cmds": [
                line[len("$ %LINUX%"):].strip()
                for line
                in file_lines
                if line.lstrip().startswith("$ %LINUX%")],

            "generic_cmds": [
                line[len("$"):].strip()
                for line
                in file_lines
                if line.lstrip().startswith("$")
                and not line.lstrip().startswith("$ %LINUX%")
                and not line.lstrip().startswith("$ %WIN32%")]}

    def version_from_modpack_line(modpack_line):
        """
        Get the version from a modpack line.

        Args:
            modpack_line (str): A line from the modpack file.

        Returns:
            str: The version of the mod.
        """
        try:
            return modpack_line.split("==", maxsplit=1)[1].strip()
        except IndexError:
            return None

    def delete_files_in_folder(folder):
        """
        Delete all files in a folder.

        Args:
            folder (str): The folder to delete the files from.
        """
        for entry in os.scandir(folder):
            if entry.is_file():
                os.remove(entry.path)

    def calculate_dependencies(mods):
        """
        Calculate the dependencies of a list of mods.

        Args:
            mods (list): A list of mods.

        Returns:
            set: The dependencies of the mods.
                 Will catch any errors and print error messages.
        """
        print("Calculating dependencies...")
        dependencies = []

        with Pool() as pool:
            dependencies.extend(pool.map(mod_dependencies_wrapper, mods))

        print()

        dependencies = set(chain.from_iterable(dependencies))

        if -1 in dependencies:
            raise ValueError("Failed to get dependencies.")

        return dependencies

    def download_mods_or_urls(mods_or_urls, cfg):
        """
        Download mods or URLs.

        Args:
            mods_or_urls (list): A list of mods or URLs.
            cfg (dict): The config file as a dictionary object.

        Returns:
            list: A list of the downloaded mods.
        """
        print("Downloading mods...")
        mods = []

        with Pool() as pool:
            mods.extend(pool.starmap(mod_download_wrapper,
                                     zip(mods_or_urls,
                                         repeat(cfg))))
        print()

        return mods

    def run_commands(modpack):
        """
        Run the commands in the modpack file.
        Commands may be generic, Windows or Linux specific.

        Args:
            modpack (dict): The modpack file as a dictionary object.
        """
        print("Running custom commands...")

        commands_to_run = modpack["generic_cmds"]
        if sys.platform == "linux":
            commands_to_run += modpack["linux_cmds"]
        elif sys.platform == "win32":
            commands_to_run += modpack["windows_cmds"]

        for command in commands_to_run:
            print("*", end="", flush=True)
            process = subprocess.run([SHELL_PATH, SHELL_ARGS, command],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            if process.returncode != 0:
                print(f"\n{command}")
                print(f"- Command exited with code: {process.returncode}")

        print()

    # Process modpack file
    modpack = process_file(modpack_file, cfg)

    # Calculate dependencies
    print()
    try:
        dependencies = calculate_dependencies(modpack["mods"])
    except ValueError:
        print()
        print(f"Build FAILED for {cfg['minecraft_version']} {cfg['loader']}!")
        print("Review your configuration and modpack files and try again.")
        print(f"Configs file: {CONFIG_PATH}")
        print(f"Modpack file: {modpack_file}\n")
        return

    # Delete files in mods folder
    print(f"\nReady to build {modpack_file}\n"
          f"over Minecraft {cfg['minecraft_version']} "
          f"on {cfg['loader']}.\n")
    print("┌────────────────────────────────────────────┐")
    print("│ Warning! This will erase your mods folder! │")
    print("│ Press ENTER to continue, CTRL+C to cancel. │")
    print("└────────────────────────────────────────────┘")
    try:
        input()
        delete_files_in_folder(cfg["mods_path"])
    except KeyboardInterrupt:
        print("\nBuild cancelled.\n")
        return

    # Download mods, dependencies and URLs
    downloads = modpack["mods"] | dependencies | modpack["urls"]
    download_mods_or_urls(downloads, cfg)

    # Run commands (TODO)
    print()
    if any(modpack[k] for k in ["windows_cmds", "linux_cmds", "generic_cmds"]):
        run_commands(modpack)

    print()


def mod_download_wrapper(mod_or_url, cfg):
    """
    Wrapper for the mod_download function.

    Args:
        mod_or_url (Mod or str): The mod to download or a URL.
        cfg (dict): The config file as a dictionary object.
                    Needed for the destination path.
        tries (int): The number of retries if the download fails.

    Returns:
        int: The ID of the mod if the download suceeded, -1 otherwise.
             If the parameter is a string, the ID returned in case of
             success is 0.
    """
    def download_from_url(url, cfg, tries=DOWNLOAD_RETRIES):
        """
        Download a file from a URL.

        Args:
            url (str): The URL of the file.
            cfg (dict): The config file as a dictionary object.
                        Needed for the destination path.

        Returns:
            bool: True if the download was successful, raises otherwise.

        Raises:
            ValueError: If the download fails. Tries DOWNLOAD_RETRIES times.
        """
        while tries > 0:

            try:
                with requests.get(url, stream=True, timeout=1) as response:

                    if response.status_code != 200:
                        sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                        tries -= 1
                        continue

                    mod_file = os.path.join(cfg["mods_path"],
                                            url.split("/")[-1])

                    with open(mod_file, "wb") as file:
                        shutil.copyfileobj(response.raw, file)

                    return True

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1
                continue

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1
                continue

        raise ValueError("Too many failed downloads.")

    mod_id = None
    name = None

    try:
        # If the variable is a Mod
        if isinstance(mod_or_url, (CurseforgeMod, ModrinthMod)):
            mod_id = mod_or_url.mod_id          # Save the ID of the Mod
            name = repr(mod_or_url)             # Save the name of the Mod
            mod_or_url = mod_or_url.url

        # If the variable is a string (URL)
        elif isinstance(mod_or_url, str):
            mod_id = 0                          # Save the ID of the URL (0)
            name = mod_or_url.split("/")[-1]    # Save the name of the URL

        # Unsupported variable type
        else:
            raise ValueError("Parameter must be Mod or string (mod_or_url).")

        download_from_url(mod_or_url, cfg)
        print("*", end="", flush=True)
        return mod_id

    except ValueError:
        print(f"\n- Unable to download '{name}'.", flush=True)
        return -1


def mod_dependencies_wrapper(mod):
    """
    Wrapper for the mod_dependencies function.

    Args:
        mod (Mod): The mod to get the dependencies for.

    Returns:
        set: The dependencies of the mod. {-1} in case of error.
    """
    try:
        dependencies = mod.dependencies
        print("*", end="", flush=True)
        return dependencies
    except ValueError:
        print(f"\n- Unable to get dependencies for '{mod}'.", flush=True)
        return {-1}
