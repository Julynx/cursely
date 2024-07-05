"""
Contains methods to search for mods on Curseforge and Modrinth.
"""

from time import sleep

import requests

from .config import DOWNLOAD_RETRIES
from .mods import ModrinthMod


class CurseforgeSearch():
    """
    Search for mods on Curseforge.
    """

    BASE_URL = "https://api.curseforge.com/v1"

    def __init__(self, keyword, cfg) -> None:
        self.keyword = keyword
        self.cfg = cfg
        self.results = []
        self._search()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.results)

    def _make_request(self, url_path, params=None, tries=DOWNLOAD_RETRIES):
        """
        Make a request to the curseforge API.

        Args:
            url_path (str): The url path to the resource.
            tries (int): The number of tries left.

        Returns:
            dict: The response as a json object.

        Raises:
            ValueError: If the request fails.
        """
        while tries > 0:

            end_point = f"{self.BASE_URL}{url_path}"
            headers = {"Accept": "application/json",
                       "x-api-key": self.cfg["API_KEY"]}

            try:
                response = requests.get(end_point,
                                        params=params,
                                        headers=headers,
                                        timeout=1)
                return response.json()["data"]

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

        raise ValueError("Too many failed requests.")

    def _search(self):

        if self.results != []:
            return self.results

        url_path = "/mods/search"
        params = {'gameId': 432,
                  'searchFilter': self.keyword,
                  'gameVersion': self.cfg['minecraft_version'],
                  'modLoaderType': self.cfg['loader']}

        try:
            request = self._make_request(url_path, params=params)
        except ValueError:
            request = []

        mods = []
        for mod_info in request:
            mod = ModrinthMod(mod_info["id"], self.cfg)
            mod._name = mod_info["name"]
            mod._downloads = mod_info["downloadCount"]
            mod._last_updated = mod_info["dateModified"][:10]
            mods.append(mod)

        self.results = iter(mods)
        return self.results


class ModrinthSearch():
    """
    Class to search for mods on Modrinth.
    """

    BASE_URL = "https://api.modrinth.com/v2"

    def __init__(self, keyword, cfg) -> None:
        self.keyword = keyword
        self.cfg = cfg
        self.results = []
        self._search()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.results)

    def _make_request(self, url_path, params=None, tries=DOWNLOAD_RETRIES):
        """
        Make a request to the curseforge API.

        Args:
            url_path (str): The url path to the resource.
            tries (int): The number of tries left.

        Returns:
            dict: The response as a json object.

        Raises:
            ValueError: If the request fails.
        """
        while tries > 0:

            end_point = f"{self.BASE_URL}{url_path}"
            headers = {"Accept": "application/json",
                       "x-api-key": self.cfg["API_KEY"]}

            try:
                response = requests.get(end_point,
                                        params=params,
                                        headers=headers,
                                        timeout=1)
                return response.json()["hits"]

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

        raise ValueError("Too many failed requests.")

    def _search(self):

        if self.results != []:
            return self.results

        facets = [[f"versions:{self.cfg['minecraft_version']}"],
                  [f"categories:{self.cfg['loader'].lower()}"]]
        facets = repr(facets).replace(" ", "").replace("'", "\"")
        url_path = f"/search?query={self.keyword}&facets={facets}"

        try:
            request = self._make_request(url_path)
        except ValueError:
            request = []

        mods = []
        for mod_info in request:
            mod = ModrinthMod(mod_info["project_id"], self.cfg)
            mod._name = mod_info["title"]
            mod._downloads = mod_info["downloads"]
            mod._last_updated = mod_info["date_modified"][:10]
            mods.append(mod)

        self.results = iter(mods)
        return self.results
