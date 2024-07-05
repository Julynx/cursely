#!/usr/bin/env python3

"""
Main module for the cursely package.
"""

import os
import sys

import requests

from .modules.config import USAGE_INFO, load_config
from .modules.modpack import install_modpack
from .modules.mods import CurseforgeMod, Mod, ModrinthMod, ModTable
from .modules.search import CurseforgeSearch, ModrinthSearch


def main():
    """
    Main function.
    """

    # Read command line arguments
    try:
        keyword = " ".join(sys.argv[1:]).strip()
    except IndexError:
        keyword = ""

    # Load configuration
    cfg = load_config()

    # Show help message
    if keyword in {"-h", "--help"}:
        print(USAGE_INFO)

    # Build modpack
    elif os.path.isfile(keyword):
        install_modpack(keyword, cfg)

    # Either mod id or search keyword
    elif keyword != "":

        print(f"\nSearching for '{keyword}' "
              f"for {cfg['minecraft_version']} "
              f"{cfg['loader']}...")

        # Attempt to hit the mod and view its details
        try:
            mod = Mod.factory(keyword, cfg=cfg)
            mod_table_str = str(ModTable(mod))

            if isinstance(mod, ModrinthMod):
                print("\nModrinth:")
            elif isinstance(mod, CurseforgeMod):
                print("\nCurseForge:")

            print(f"{mod_table_str}\n")

        # If you can't, then do a fuzzy search
        except ValueError:

            try:
                mods = list(CurseforgeSearch(keyword, cfg))
                print("\nCurseForge:")
                print(f"{ModTable(mods)}")

                mods = list(ModrinthSearch(keyword, cfg))
                print("\nModrinth:")
                print(f"{ModTable(mods)}\n")

            # If the search has no results, print an error message
            except ValueError:
                print("Unable to search for mods.\n")

    else:
        print(USAGE_INFO)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        CLEAR_LINE = "\033[2K"
        print(f"{CLEAR_LINE}\nInterrupted by user.\n")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print("\nUnable to connect to the internet.\n")
        sys.exit(1)
    # except Exception as exc:
    #     print(f"\nERROR: {exc}\n")
    #     sys.exit(2)
