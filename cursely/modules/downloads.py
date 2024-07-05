"""
Contains the download_all function and related helper functions
to download mods and URLs.
"""

import os
import shutil
from dataclasses import dataclass
from itertools import repeat
from multiprocessing import Pool
from time import sleep
from typing import Union

import requests

from .config import DOWNLOAD_RETRIES
from .mods import Mod


@dataclass
class DownloadError:
    """
    Represents a download error.
    """

    mod_id: str = None
    name: str = "Unknown mod"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: "DownloadError") -> bool:
        return self.name == other.name


class URL:
    """
    Represents a URL to download.
    """

    def __init__(self, url: str, *, mod_id=None) -> None:
        self.url = url
        self.name = url.split("/")[-1]
        self.mod_id = mod_id

    def __str__(self) -> str:
        text = f"{self.url}"
        if self.mod_id is not None:
            text += f" for mod {self.mod_id}"
        return text

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, other) -> bool:
        return self.url == other.url

    @classmethod
    def from_string(cls, modpack_url_line):
        """
        Construct a URL object from a string.

        Args:
            modpack_url_line (str): The string to parse.

        Returns:
            URL: The URL object.
        """
        url = modpack_url_line.split(" ")[1].strip()
        mod_id = None
        if " for mod " in modpack_url_line:
            mod_id = modpack_url_line.split(" for mod ", maxsplit=1)[-1]
            mod_id = mod_id.strip().split(" ")[0].strip()
        return cls(url, mod_id=mod_id)


Downloadable = Union[Mod, URL]
DownloadResult = Union[Downloadable, DownloadError]


def download_all(downloadables: list[Downloadable],
                 cfg) -> list[DownloadResult]:
    """
    Download mods or URLs.

    Args:
        downloadables (list[Downloadable]): A list of mods or URLs.
        cfg (dict): The config file as a dictionary object.

    Returns:
        list[DownloadResult]: A list of mods or URLs or Nones for
            failed downloads.
    """
    print("Downloading mods...")
    download_results = []

    with Pool() as pool:
        download_results.extend(pool.starmap(_download_wrapper,
                                             zip(downloadables,
                                                 repeat(cfg))))
    print()

    # Clean download results
    hits = [result for result in download_results
            if isinstance(result, Downloadable)]

    errors = [result for result in download_results
              if isinstance(result, DownloadError)
              and result.mod_id not in [hit.mod_id for hit in hits]]

    return hits + errors


def _download_wrapper(downloadable: Downloadable, cfg) -> DownloadResult:
    """
    Wrapper for the mod_download function.

    Args:
        downloadable (Mod or str): The mod to download or a URL.
        cfg (dict): The config file as a dictionary object.
                    Needed for the destination path.
        tries (int): The number of retries if the download fails.

    Returns:
         DownloadResult: The mod or URL if the download was successful,
    """
    def download(downloadable: Downloadable, cfg, tries=DOWNLOAD_RETRIES):
        """
        Download a file from a URL.

        Args:
            downloadable (Downloadable): The object to download.
            cfg (dict): The config file as a dictionary object.
                Needed for the destination path.
            tries (int): The number of retries if the download fails.
                Defaults to .config.DOWNLOAD_RETRIES.

        Returns:
            bool: True if the download was successful, raises otherwise.

        Raises:
            ValueError: If the download fails. Tries "tries" times.
        """
        while tries > 0:

            try:
                with requests.get(downloadable.url,
                                  stream=True, timeout=1) as response:

                    if response.status_code != 200:
                        sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                        tries -= 1
                        continue

                    mod_file = os.path.join(cfg["mods_path"],
                                            downloadable.url.split("/")[-1])

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

    try:
        if not isinstance(downloadable, Downloadable):
            raise ValueError(
                "Parameter \"downloadable\" must be Mod or URL.")

        download(downloadable, cfg)
        print("*", end="", flush=True)
        return downloadable

    except ValueError:
        print("-", end="", flush=True)
        return DownloadError(
            mod_id=str(downloadable.mod_id),
            name=str(downloadable))
