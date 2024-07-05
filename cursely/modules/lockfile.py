"""
Contains classes and methods to work with lock files.
"""

from dataclasses import dataclass

from ordered_set_37 import OrderedSet

from .downloads import DownloadError, DownloadResult, URL
from .modpack_statements import (ModpackStatement, StatementRunError,
                                 StatementRunResult)
from .mods import Mod


@dataclass
class LockFile:
    """
    Represents a lock file.
    """
    resolved_statements: OrderedSet[ModpackStatement] = None
    failed_statements: OrderedSet[StatementRunError] = None

    resolved_mods: set[Mod] = None
    resolved_urls: set[URL] = None
    failed_downloads: set[DownloadError] = None

    @classmethod
    def from_results(cls, statement_run_results: list[StatementRunResult],
                     download_results: list[DownloadResult]) -> "LockFile":
        """
        Generate a lock file from the results of a modpack build.

        Args:
            statement_run_results (list[StatementRunResult]): A list of
                statements or errors.
            download_results (list[DownloadResult]): A list of mods or URLs or
                errors.

            Returns:
                LockFile: The lock file.
        """
        lock_file = LockFile()
        lock_file.resolved_statements = OrderedSet()
        lock_file.failed_statements = OrderedSet()
        lock_file.resolved_mods = set()
        lock_file.resolved_urls = set()
        lock_file.failed_downloads = set()

        for item in statement_run_results:

            if isinstance(item, StatementRunError):
                lock_file.failed_statements.add(item)

            elif isinstance(item, ModpackStatement):
                lock_file.resolved_statements.add(item)

        for item in download_results:

            if isinstance(item, DownloadError):
                lock_file.failed_downloads.add(item)

            elif isinstance(item, Mod):
                lock_file.resolved_mods.add(item)

            elif isinstance(item, URL):
                lock_file.resolved_urls.add(item)

        return lock_file

    def to_disk(self, lock_file_path: str):
        """
        Save a lock file to a file.

        Args:
            lock_file (LockFile): The lock file.
            lock_file_path (str): The path to the lock file.
        """
        with open(lock_file_path, "w", encoding='utf-8') as file:

            if self.resolved_statements:
                for statement in self.resolved_statements:
                    file.write(f"{statement}\n")
                    print("*", end="", flush=True)
                file.write("\n")

            if self.resolved_mods:
                for mod in self.resolved_mods:
                    file.write(
                        f"mod {mod.mod_id} {mod.name} == {mod.version_id}\n")
                    print("*", end="", flush=True)
                file.write("\n")

            if self.resolved_urls:
                for url in self.resolved_urls:
                    file.write(f"download {url}\n")
                    print("*", end="", flush=True)
                file.write("\n")

            if self.failed_statements:
                file.write("# Failed statements:\n")
                for statement in self.failed_statements:
                    file.write(f"# - {statement}\n")
                    print("*", end="", flush=True)
                file.write("\n")

            if self.failed_downloads:
                file.write("# Failed downloads:\n")
                for error in self.failed_downloads:
                    file.write(f"# - {error}\n")
                    print("*", end="", flush=True)
                file.write("\n")

            if any((self.resolved_statements, self.resolved_mods,
                    self.resolved_urls, self.failed_statements,
                    self.failed_downloads)):
                print()


def associated_lock_file_path(modpack_file_path: str):
    """
    Get the path to the associated lock file.

    Args:
        modpack_file_path (str): The path to the modpack file.

    Returns:
        str: The path to the associated lock file.
    """
    return modpack_file_path.replace(".mods", ".resolved-mods")
