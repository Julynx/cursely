"""
Configuration module for cursely.
"""

import json
import os
import sys
from time import sleep

import requests

DOWNLOAD_RETRIES = 3
HOME = os.path.expanduser("~")
CONFIG_FOLDER = os.path.join(HOME, ".config", "cursely")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "config.json")

USAGE_INFO = f"""
Usage:
    cursely [MOD_ID]    Get a brief description of a mod and its download link.
    cursely [KEYWORD]   Search for a mod by its name or author.
    cursely [MODPACK]   Install all listed mods and their dependencies.
    cursely --help      Show this help message.

Your configuration (minecraft version, loader, mods path, etc.) is usually
stored in '{CONFIG_PATH}'. If you ever need to modify it,
simply delete the file and run cursely again or edit the file directly.

If you are running cursely for the first time, you do not need to manually
create a configuration file. It will ask you to provide the necessary
information and create the file for you.
"""


SHELL_PATH = "/bin/sh"
SHELL_ARGS = "-c"
DEF_MODS_PATH = os.path.join(HOME, ".minecraft", "mods")
if sys.platform == "win32":
    SHELL_PATH = "cmd"
    SHELL_ARGS = "/c"
    DEF_MODS_PATH = os.path.join(HOME, "AppData", "Roaming",
                                 ".minecraft", "mods")


def load_config():
    """
    Load the config file.
    Uses the global variables CONFIG_FOLDER, CONFIG_PATH and DEF_MODS_PATH.

    Returns:
        dict: The config file as a dictionary object.
    """
    def validate_config():
        """
        Validate the config file.
        Uses the global variable CONFIG_PATH.

        Returns:
            dict: The config file as a dictionary object.
                  {API_KEY: "...",
                   mods_path: "...",
                   minecraft_version: "...",
                   loader: "..."}

        Raises:
            ValueError: If the config file is corrupted or missing.
        """
        # Presence of the config file
        try:
            with open(CONFIG_PATH, "r", encoding='utf-8') as file:
                cfg = json.load(file)
        except OSError as os_error:
            raise ValueError("Config file is corrupted or missing.") \
                from os_error

        # Presence of the keys
        for field in ["API_KEY", "mods_path", "minecraft_version", "loader"]:
            if field in cfg:
                continue
            raise ValueError(f"{field} not found in config file.")

        # Validity of the values: API_KEY
        tries = DOWNLOAD_RETRIES

        while True:

            if tries <= 0:
                raise ValueError("Invalid API_KEY.\n       "
                                 "If you just created your "
                                 "account, please wait a few minutes and "
                                 "try again.")

            end_point = 'https://api.curseforge.com/v1/games/432'
            headers = {"Accept": "application/json",
                       "x-api-key": cfg["API_KEY"]}

            try:
                response = requests.get(end_point, headers=headers, timeout=3)
                if response.status_code == 200:
                    break
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1
                continue

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1
                continue

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1
                continue

        # Mods path
        if not os.path.isdir(cfg["mods_path"].strip()):
            raise ValueError("Invalid mods_path.")

        # Loader
        if cfg["loader"].strip() not in ["Fabric", "Forge"]:
            raise ValueError("Invalid loader. Valid values: Fabric, Forge.")

        return cfg

    try:
        cfg = validate_config()
        return cfg

    except ValueError as exc:
        print(f"\nERROR: {exc}")
        api_link = "https://console.curseforge.com/?#/signup"
        print("\nOops, your config file is missing or invalid!")
        print("I'll help you fix it...\n")
        print(f"Visit {api_link} to get an API key.\n")
        field_0 = input("    What is your API key?: ")
        field_1 = input(f"    Where is your mods folder? ({DEF_MODS_PATH}): ")
        field_2 = input("    What is your Minecraft version?: ")
        field_3 = input("    Are you using Forge or Fabric?: ").capitalize()
        print("\nSaving and testing configuration...\n")

        # If path is empty, write default. Expand user path.
        if field_1.strip() == "":
            field_1 = DEF_MODS_PATH
        field_1 = os.path.expanduser(field_1)

        # Build configuration dictionary
        cfg = {"API_KEY": field_0,
               "mods_path": field_1,
               "minecraft_version": field_2,
               "loader": field_3}

        # Dump configuration to file, making the folder if it doesn't exist
        os.makedirs(CONFIG_FOLDER, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding='utf-8') as file:
            json.dump(cfg, file, indent=4)

        return load_config()
