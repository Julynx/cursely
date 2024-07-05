"""
Contains functions to install a modpack from a modpack file.
"""

import os
from dataclasses import dataclass

from ordered_set_37 import OrderedSet

from .config import CONFIG_PATH
from .dependencies import calculate_dependencies
from .downloads import URL, DownloadResult, download_all, DownloadError
from .files import delete_files_in_folder
from .lockfile import LockFile, associated_lock_file_path
from .modpack_statements import (ModpackStatement, StatementRunError,
                                 run_modpack_statements)
from .mods import Mod


def install_modpack(modpack_file_path: str, cfg):
    """
    Install a modpack from a modpack file.

    Args:
        modpack_file (str): Path to the modpack file.
        cfg (dict): The config file as a dictionary object.
    """
    using_lock_file = False

    # Search if there is an associated lock file
    lock_file_path = associated_lock_file_path(modpack_file_path)
    if os.path.isfile(lock_file_path):
        modpack_file_path = lock_file_path
        using_lock_file = True
        print()
        print("Using existing resolution file:")
        print(f"{modpack_file_path}")
        print("Delete it to build from scratch.")
    else:
        print()
        print("[!] No resolution file found. Building from scratch.")

    # Process modpack file
    modpack = Modpack.from_file(modpack_file_path, cfg)
    downloads = modpack.mods | modpack.urls

    # Calculate dependencies
    if not using_lock_file:
        print()
        try:
            downloads |= {dep for dep in calculate_dependencies(modpack.mods)
                          if dep not in downloads}
        except ValueError:
            print()
            print(f"[x] Build FAILED for {cfg['minecraft_version']}"
                  f" {cfg['loader']}!")
            print()
            print("Review your configuration and modpack files and try again.")
            print(f"Config file: {CONFIG_PATH}")
            print(f"Modpack file: {modpack_file_path}")
            print()
            return

    # Delete files in mods folder
    print()
    print("Ready to build")
    print(f"{modpack_file_path}")
    print(f"over Minecraft {cfg['minecraft_version']} on {cfg['loader']}.")
    print("")
    print("[!] This will erase your mods folder!")
    print("")
    print("Press ENTER to continue, CTRL+C to cancel:")

    try:
        input()
        delete_files_in_folder(cfg["mods_path"])
    except KeyboardInterrupt:
        print("\nBuild cancelled.\n")
        return

    # Run modpack statements
    if modpack.statements:
        statement_run_results = run_modpack_statements(modpack.statements)
        errors = [result for result in statement_run_results
                  if isinstance(result, StatementRunError)]

        print()
        if errors:
            print("[!] The following statements failed:")
            for error in errors:
                print(f"    - {error}")
            print()

    # Download mods, dependencies and URLs
    download_results: list[DownloadResult] = download_all(downloads, cfg)
    errors = [result for result in download_results
              if isinstance(result, DownloadError)]

    print()
    if errors:
        print("[!] The following downloads failed:")
        for error in errors:
            print(f"    - {error}")
        print()

    # Generate and save lock file
    if not using_lock_file:

        print("Saving resolved versions...")

        lock_file = LockFile.from_results(
            statement_run_results, download_results)
        lock_file_path = associated_lock_file_path(modpack_file_path)
        lock_file.to_disk(lock_file_path)

        print()
        print("Resolved versions saved to resolution file:")
        print(f"{lock_file_path}")
        print()

    # Build finished
    print("Build finished.\n")


@dataclass
class Modpack:
    """
    Represents a modpack file.
    """
    statements: OrderedSet[ModpackStatement] = None
    mods: set[Mod] = None
    urls: set[URL] = None

    def __str__(self) -> str:
        text = ""
        text += "".join(f"{statement}\n" for statement in self.statements)
        text += "".join(f"mod {mod.mod_id}\n" for mod in self.mods)
        text += "".join(f"download {url.url[0:16]}...{url.url[-40:]}\n"
                        for url in self.urls)
        return text

    @classmethod
    def from_file(cls, modpack_file_path: str, cfg):
        """
        Load a modpack file.

        Args:
            modpack_file_path (str): Path to the modpack file.
            cfg (dict): The config file as a dictionary object.

        Returns:
            ModpackFile: The modpack file.
        """
        file_lines = []
        with open(modpack_file_path, "r", encoding='utf-8') as file:
            file_lines = file.readlines()

        return cls(
            statements=OrderedSet([
                ModpackStatement.from_string(
                    modpack_statement_line=line.strip(),
                    modpack_file_path=modpack_file_path,
                    app_config=cfg)
                for line in file_lines
                if line.lstrip().startswith(("game ", "loader ", "config "))]),

            mods={
                Mod.from_string(modpack_mod_line=line.strip(), cfg=cfg)
                for line in file_lines
                if line.lstrip().startswith("mod ")},

            urls={
                URL.from_string(modpack_url_line=line.strip())
                for line in file_lines
                if line.lstrip().startswith("download ")})
