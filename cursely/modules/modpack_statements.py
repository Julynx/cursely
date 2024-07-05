"""
Module for modpack statements.
"""

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Union
from zipfile import ZipFile


class ModpackStatement:
    """
    Represents a modpack statement.
    """
    name: str = None
    body: str = None

    def __str__(self) -> str:
        return f"{self.name} {self.body}"

    def run(self):
        """
        Execute the modpack statement.
        """
        raise NotImplementedError("Method run() must be implemented.")

    @staticmethod
    def from_string(modpack_statement_line: str,
                    modpack_file_path: str,
                    app_config: dict) -> "ModpackStatement":
        """
        Parse a modpack statement line.

        Args:
            modpack_statement_line (str): The modpack statement line.
            app_config: Application configuration.

        Returns:
            ModpackStatement: The modpack statement.
        """
        if " " not in modpack_statement_line:
            raise ValueError(
                f"Invalid modpack statement: {modpack_statement_line}")

        # Modpack config statement
        if modpack_statement_line.startswith("config "):

            name = "config"

            body = (modpack_statement_line
                    .strip()
                    .split(" ", maxsplit=1)[-1]
                    .strip())

            return ModpackConfig(name=name,
                                 body=body,
                                 modpack_config_path=body,
                                 modpack_file_path=modpack_file_path,
                                 app_config=app_config)

        # Modpack loader statement
        if modpack_statement_line.startswith("loader "):

            name = "loader"

            body = (modpack_statement_line
                    .strip()
                    .split(" ", maxsplit=1)[-1]
                    .strip())

            loader_version = None
            if "==" in body:
                loader_type, loader_version = body.split("==")
                loader_type = loader_type.lower().strip()
                loader_version = loader_version.strip()
            else:
                loader_type = body

            return ModpackLoader(name=name,
                                 body=body,
                                 loader_type=loader_type,
                                 version=loader_version,
                                 app_config=app_config)

        # Modpack mc version statement
        if modpack_statement_line.startswith("game "):

            name = "game"

            body = (modpack_statement_line
                    .strip()
                    .split(" ", maxsplit=1)[-1]
                    .strip())

            version = None
            if "==" in body:
                version = body.split("==", maxsplit=1)[-1].strip()

            return ModpackMcVersion(name=name,
                                    body=body,
                                    version=version,
                                    app_config=app_config)

        raise ValueError(
            f"Invalid modpack statement: {modpack_statement_line}")


class ModpackConfig(ModpackStatement):
    """
    Represents a modpack config statement.
    """

    def __init__(self, *, name, body, modpack_config_path: str,
                 modpack_file_path: str,
                 app_config: dict):

        self.name = name
        self.body = body
        self.modpack_config_path = modpack_config_path
        modpack_dir = os.path.dirname(modpack_file_path)
        self.modpack_config_path = os.path.join(
            modpack_dir,
            modpack_config_path)
        self.app_config = app_config

    def run(self):

        tmp_dir = "/tmp/cursely"
        if sys.platform == "win32":
            tmp_dir = "C:\\tmp\\cursely"

        # Get the minecraft installation path from app_config["mods_path"]
        mc_install_path = Path(self.app_config["mods_path"]).parent
        if not mc_install_path.is_dir():
            raise ValueError("Invalid 'mods_path'.")

        # Get the modpack config name as the zip file without extension
        modpack_config_name = os.path.basename(self.modpack_config_path)
        modpack_config_name = os.path.splitext(modpack_config_name)[0]

        # Extract the modpack config zip to a temporary folder
        ZipFile(self.modpack_config_path).extractall(tmp_dir)

        # Raise error if the zip does not contain a folder with the same name
        modpack_config_folder = Path(tmp_dir) / Path(modpack_config_name)
        if not modpack_config_folder.is_dir():
            raise ValueError("Invalid modpack config folder structure.\n"
                             "Must be a zipfile <name>.zip"
                             " with a folder <name> inside.")

        # Copy everything from the folder inside the zip to the mc folder
        shutil.copytree(modpack_config_folder,
                        mc_install_path,
                        dirs_exist_ok=True)

        # Remove the temporary folder
        shutil.rmtree(tmp_dir)


class ModpackLoader(ModpackStatement):
    """
    Represents a modpack loader statement.
    """

    @dataclass
    class Fabric:
        """
        Represents a fabric loader.
        """
        name: str = "fabric"

    @dataclass
    class Forge:
        """
        Represents a forge loader.
        """
        name: str = "forge"

    def __init__(self, *, name, body,
                 loader_type: Union[Fabric, Forge, None] = None,
                 version: Union[str, None] = None,
                 app_config: dict = None):
        self.name = name
        self.body = body
        self.loader_type = loader_type
        self.version = version
        self.app_config = app_config

    def run(self):
        if self.loader_type.lower() != self.app_config["loader"].lower():
            raise ValueError(f"Invalid loader type: {self.loader_type}")


class ModpackMcVersion(ModpackStatement):
    """
    Represents a modpack minecraft version statement.
    """

    def __init__(self, *, name, body, version: str = None,
                 app_config: dict = None):
        self.name = name
        self.body = body
        self.version = version
        self.app_config = app_config

    def run(self):
        if self.version != self.app_config["minecraft_version"]:
            raise ValueError(f"Invalid minecraft version: {self.version}")


@dataclass
class StatementRunError:
    """
    Represents a statement run error.
    """

    statement_str: str = "Unknown statement"

    def __str__(self) -> str:
        return str(self.statement_str)

    def __hash__(self) -> int:
        return hash(self.statement_str)

    def __eq__(self, other: "StatementRunError") -> bool:
        return self.statement_str == other.statement_str


StatementRunResult = Union[ModpackStatement, StatementRunError]


def run_modpack_statements(statements: list[ModpackStatement]) \
        -> list[StatementRunResult]:
    """
    Run a list of modpack statements.

    Args:
        statements (list): A list of modpack statements.

    Returns:
        list: A list of statement run results.
    """
    statement_run_results: list[StatementRunResult] = []

    print("Running modpack statements...")

    for statement in statements:
        try:
            statement.run()
            print("*", end="", flush=True)
            statement_run_results.append(statement)
        except Exception:
            print("-", end="", flush=True)
            statement_run_results.append(StatementRunError(statement))

    print()

    return statement_run_results
