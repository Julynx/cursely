"""
Contains classes for mods from curseforge.com and modrinth.com.
"""

import os
import sys
from time import sleep
from typing import Union

from numerize.numerize import numerize
import requests
from prettytable import SINGLE_BORDER, PrettyTable

from .config import DOWNLOAD_RETRIES


class Mod:
    """
    A class to represent a mod.

    Must contain the following attributes:
    [mod_id, version_id]

    Must contain the following properties:
    [name, mod, downloads, last_updated, file, dependencies, website,
    summary, url]
    """

    mod_id: Union[int, str] = None
    version_id: str = None

    @property
    def name(self):
        """
        Get the name of a mod.

        Returns:
            str: The name of the mod.
        """
        raise NotImplementedError

    @property
    def mod(self):
        """
        Get the mod data as a json object.

        Returns:
            dict: The mod as a json object.
        """
        raise NotImplementedError

    @property
    def downloads(self):
        """
        Get the number of downloads of a mod.

        Returns:
            int: The number of downloads.
        """
        raise NotImplementedError

    @property
    def last_updated(self):
        """
        Get the last updated date of a mod.

        Returns:
            str: The last updated date.
        """
        raise NotImplementedError

    @property
    def file(self):
        """
        Get the latest file of a mod.

        Returns:
            dict: The file of the mod as a json object.
        """
        raise NotImplementedError

    @property
    def dependencies(self):
        """
        Get the dependencies of a mod.

        Returns:
            set: The dependencies as a set of Mod objects.
        """
        raise NotImplementedError

    @property
    def website(self):
        """
        Get the website of a mod.

        Returns:
            str: The website of the mod.
        """
        raise NotImplementedError

    @property
    def summary(self):
        """
        Get the summary of a mod.

        Returns:
            str: The summary of the mod.
        """
        raise NotImplementedError

    @property
    def url(self):
        """
        Get the download URL of a mod.

        Returns:
            str: The download URL of the mod.
        """
        raise NotImplementedError

    @staticmethod
    def factory(mod_id, *, cfg, version_id=None):
        """
        Factory function for Mod objects.

        Args:
            mod_id (int or str): The ID of the mod or the URL to the mod.
            version_id (str): The version of the mod.
            cfg (dict): The config file as a dictionary object.

        Returns:
            Mod (CurseforgeMod or ModrinthMod): The mod object.
        """
        try:
            int(mod_id)
            return CurseforgeMod(mod_id, cfg, version_id=version_id)
        except (ValueError, TypeError):
            return ModrinthMod(mod_id, cfg, version_id=version_id)

    @classmethod
    def from_string(cls, modpack_mod_line: str, *, cfg) -> "Mod":
        """
        Parse a modpack mod line.

        Args:
            modpack_mod_line (str): The modpack mod line.
                Must have the format "mod <mod_id> <mod_name> == <version>"

        Returns:
            Mod: The mod object.
        """
        mod_id = modpack_mod_line.strip().split(" ")[1].strip()
        try:
            version_id = modpack_mod_line.split("==", maxsplit=1)[1].strip()
        except IndexError:
            version_id = None

        return cls.factory(mod_id, cfg=cfg, version_id=version_id)


class CurseforgeMod(Mod):
    """
    A class to represent a mod from curseforge.com.
    """
    BASE_URL = "https://api.curseforge.com/v1"

    def __init__(self, mod_id, cfg, *, version_id=None):
        """
        Initialize a CurseforgeMod object.

        Args:
            mod_id (int): The ID of the mod.
            version_id (str): The fileId of the mod.
                Last code in the file URL when opened in a browser.
                https://docs.curseforge.com/#get-mod-file
            cfg (dict): The target config for the mod (fileId).
                {"API_KEY": Your curseforge API key as a string,
                 "minecraft_version": The target minecraft version,
                 "loader": The target loader. ('Fabric' or 'Forge')
                 ...}
        """
        if id is None or cfg is None:
            raise ValueError("id and cfg must not be None.")

        self.mod_id = mod_id
        self.version_id = version_id
        self.cfg = cfg
        self._name = None
        self._mod = None
        self._downloads = None
        self._last_updated = None
        self._file = None
        self._dependencies = None
        self._website = None
        self._summary = None
        self._url = None

    def __eq__(self, __value: object) -> bool:
        """
        Check if two CurseforgeMod objects are equal.

        Args:
            __value (object): The object to compare to.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if isinstance(__value, CurseforgeMod):
            return self.mod_id == __value.mod_id
        return False

    def __repr__(self) -> str:
        """
        String representation of a CurseforgeMod.

        Returns:
            str: The mod name if it is able to get it, else the mod id.
        """
        try:
            return str(self.name)
        except ValueError:
            return str(self.mod_id)

    def __hash__(self) -> int:
        """
        Get the hash of a CurseforgeMod object.

        Returns:
            int: The id of the mod.
        """
        return hash(self.mod_id)

    def _make_request(self, url_path, tries=DOWNLOAD_RETRIES):
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
                response = requests.get(end_point, headers=headers, timeout=1)
                return response.json()["data"]

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

        raise ValueError("Too many failed requests.")

    @property
    def name(self):
        """
        Get the name of a mod.

        Returns:
            str: The name of the mod.

        Raises:
            ValueError: If the name lookup fails.
        """
        if self._name is not None:
            return self._name

        self._name = self.mod["name"]
        return self._name

    @property
    def mod(self):
        """
        Get the mod object.

        Returns:
            dict: The mod as a json object.

        Raises:
            ValueError: If the connection fails.
        """
        if self._mod is not None:
            return self._mod

        url_path = f"/mods/{self.mod_id}"
        self._mod = self._make_request(url_path)
        return self._mod

    @property
    def downloads(self):
        """
        Get the number of downloads of a mod.

        Returns:
            int: The number of downloads.

        Raises:
            ValueError: If the connection fails.
        """
        if self._downloads is not None:
            return self._downloads

        self._downloads = self.mod["downloadCount"]
        return self._downloads

    @property
    def last_updated(self):
        """
        Get the last update of a mod.

        Returns:
            str: The last update.

        Raises:
            ValueError: If the connection fails.
        """
        if self._last_updated is not None:
            return self._last_updated

        date = self.mod["dateModified"][:10]

        self._last_updated = date
        return self._last_updated

    @property
    def file(self):
        """
        Get the latest file of a mod that is compatible with the given config.

        Returns:
            dict: The file of the mod as a json object.

        Raises:
            ValueError: If the connection fails or if no compatible file
            is found.
        """

        def files(mod_id, index=0):
            """
            Get a list of files for a mod. Paginated with page size 50.

            Args:
                index (int): The index of the first file to be returned.

            returns:
                A list of files.

            Raises:
                ValueError: If the request fails.
            """
            url_path = f"/mods/{mod_id}/files?index={index}&pageSize=50"
            response = self._make_request(url_path)
            return response

        def get_file_with_version(mod_id, version):
            """
            Get the file with a specific version.

            Args:
                mod_id (int): The mod ID.
                version (str): The version of the file.

            Returns:
                dict: The file as a json object.

            Raises:
                ValueError: If the file is not found.
            """
            # GET /v1/mods/{modId}/files/{fileId}
            url_path = f"/mods/{mod_id}/files/{version}"
            response = self._make_request(url_path)
            return response

        if self._file is not None:
            return self._file

        compatible_config = {self.cfg["minecraft_version"],
                             self.cfg["loader"]}

        # If no version is specified, get the latest compatible file
        if self.version_id is None:
            max_results = 5000
            page_size = 50
            for i in range(0, max_results, page_size):
                try:
                    response = files(self.mod_id, index=i)
                    if not response:
                        break
                except ValueError:
                    break

                for file in response:
                    if compatible_config <= set(file["gameVersions"]):
                        self.version_id = file["id"]
                        self._file = file
                        return self._file

            raise ValueError("No compatible file found.")

        # pylint: disable=R1720
        else:
            try:
                self._file = get_file_with_version(
                    self.mod_id, self.version_id)
                return self._file
            except ValueError as value_error:
                raise ValueError("No compatible file found.") \
                    from value_error

    @property
    def dependencies(self):
        """
        Get all dependencies of a mod.

        Args:
            mod_id (int): The mod ID.
            cfg (dict): The config dictionary.

        Returns:
            A set of mod IDs.

        Raises:
            IndexError: If the file has no modId or relationType.
            ValueError: If the mod has no dependencies.
        """
        if self._dependencies is not None:
            return self._dependencies

        dependencies = {CurseforgeMod(dependency["modId"], self.cfg)
                        for dependency
                        in self.file["dependencies"]
                        if dependency["modId"] is not None
                        and dependency["relationType"] == 3}

        self._dependencies = dependencies
        return self._dependencies

    @property
    def website(self):
        if self._website is not None:
            return self._website

        self._website = self.mod["links"]["websiteUrl"]
        return self._website

    @property
    def summary(self):
        if self._summary is not None:
            return self._summary

        self._summary = self.mod["summary"]
        return self._summary.strip()

    @property
    def url(self):
        """
        Get the download URL of a mod.

        Returns:
            str: The download URL of the mod.

        Raises:
            ValueError: If the download URL is unavailable or
            the request fails.
        """
        if self._url is not None:
            return self._url

        download_url = self.file["downloadUrl"]
        if download_url:
            download_url = download_url.replace(" ", "%20")
            self._url = download_url
            return self._url

        raise ValueError("Unavailable through API")


class ModrinthMod(Mod):
    """
    A class representing a mod from modrinth.com.
    """
    BASE_URL = "https://api.modrinth.com/v2"
    USER_AGENT = "Cursely/testing2 (github.com/julynx/cursely)"

    def __init__(self, mod_id, cfg, *, version_id=None):
        """
        Initialize a ModrinthMod object.

        Args:
            id (int): The ID of the mod.
            version_id (str): The Version ID of the mod.
                Click on a version -> Metadata -> Copy Version ID
                https://docs.modrinth.com/#tag/versions
            cfg (dict): The target config for the mod.
                {"API_KEY": Your curseforge API key as a string,
                 "minecraft_version": The target minecraft version,
                 "loader": The target loader. ('Fabric' or 'Forge')
                ...}
        """
        if mod_id is None or cfg is None:
            raise ValueError("id and cfg must not be None.")

        self.mod_id = mod_id
        self.version_id = version_id
        self.cfg = cfg
        self._name = None
        self._mod = None
        self._downloads = None
        self._last_updated = None
        self._latest_version = None
        self._version = None
        self._file = None
        self._dependencies = None
        self._website = None
        self._summary = None
        self._url = None

    def __eq__(self, __value: object) -> bool:
        """
        Check if two ModrinthMod objects are equal.

        Args:
            __value (object): The object to compare to.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if isinstance(__value, ModrinthMod):
            return self.mod_id == __value.mod_id
        return False

    def __repr__(self) -> str:
        """
        String representation of a ModrinthMod.

        Returns:
            str: The mod name if it is able to get it, else the mod id.
        """
        try:
            return str(self.name)
        except ValueError:
            return str(self.mod_id)

    def __hash__(self) -> int:
        """
        Get the hash of a ModrinthMod object.

        Returns:
            int: The id of the mod.
        """
        return hash(self.mod_id)

    def _make_request(self, url_path, tries=DOWNLOAD_RETRIES):
        """
        Make a request to the modrinth API.

        Args:
            url_path (str): The url path to the endpoint.
            tries (int): The number of tries left.

        Returns:
            dict: The response as a json object.

        Raises:
            ValueError: If the request fails.
        """
        while tries > 0:

            end_point = f"{self.BASE_URL}{url_path}"
            headers = {"Accept": "application/json",
                       "User-Agent": self.USER_AGENT}

            try:
                response = requests.get(end_point, headers=headers, timeout=1)
                return response.json()

            except requests.RequestException:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

            except Exception:
                sleep((DOWNLOAD_RETRIES + 1 - tries) / 2)
                tries -= 1

        raise ValueError("Too many failed requests.")

    @property
    def name(self):
        """
        Get the name of a mod.

        Returns:
            str: The name of the mod.

        Raises:
            ValueError: If the name lookup fails.
        """
        if self._name is not None:
            return self._name

        self._name = self.mod["title"]
        return self._name

    @property
    def mod(self):
        """
        Get the mod object.

        Returns:
            dict: The mod as a json object.

        Raises:
            ValueError: If the connection fails.
        """
        if self._mod is not None:
            return self._mod

        url_path = f"/project/{self.mod_id}"
        self._mod = self._make_request(url_path)
        return self._mod

    @property
    def downloads(self):
        """
        Get the number of downloads of a mod.

        Returns:
            int: The number of downloads.

        Raises:
            ValueError: If the connection fails.
        """
        if self._downloads is not None:
            return self._downloads

        self._downloads = self.mod["downloads"]
        return self._downloads

    @property
    def last_updated(self):
        """
        Get the last updated date of a mod.

        Returns:
            str: The last updated date.

        Raises:
            ValueError: If the connection fails.
        """
        if self._last_updated is not None:
            return self._last_updated

        date = self.mod["updated"][:10]

        self._last_updated = date
        return self._last_updated

    @property
    def latest_version(self):
        """
        Get the latest version of a mod compatible with the target config.

        Returns:
            dict: The latest version as a json object.

        Raises:
            ValueError: If no compatible version is found.
        """
        if self._latest_version is not None:
            return self._latest_version

        minecraft_version = self.cfg["minecraft_version"]
        mod_loader = self.cfg["loader"].lower()

        url_path = f"/project/{self.mod_id}/version"
        versions = self._make_request(url_path)

        try:
            version = next(version
                           for version in versions
                           if minecraft_version in version["game_versions"]
                           and mod_loader in version["loaders"])
        except StopIteration as stop_iteration:
            raise ValueError("No compatible version found.") \
                from stop_iteration

        self._latest_version = version
        return self._latest_version

    @property
    def version(self):
        """
        Get the exact version of a mod.

        Returns:
            str: The exact version of the mod.
        """
        if self._version is not None:
            return self._version

        minecraft_version = self.cfg["minecraft_version"]
        mod_loader = self.cfg["loader"].lower()

        if self.version_id is not None:
            url = f"/version/{self.version_id}"
            version = self._make_request(url)

            if minecraft_version not in version["game_versions"] or \
               mod_loader not in version["loaders"]:
                raise ValueError("Incompatible version.")
        else:
            version = self.latest_version
            self.version_id = version["id"]

        self._version = version
        return self._version

    @property
    def file(self):
        """
        Get the latest file of a mod compatible with the target config.

        Returns:
            dict: The latest file as a json object.

        Raises:
            ValueError: If no compatible file is found.
        """
        if self._file is not None:
            return self._file

        try:
            version_file = next(file
                                for file
                                in self.version["files"]
                                if file["primary"])

        except StopIteration as stop_iteration:
            raise ValueError("No compatible file found.") \
                from stop_iteration

        self._file = version_file
        return self._file

    @property
    def dependencies(self):
        """
        Get the dependencies of a mod.

        Returns:
            set: The dependencies as a set of ModrinthMod objects.
        """
        if self._dependencies is not None:
            return self._dependencies

        self._dependencies = {ModrinthMod(dependency["project_id"], self.cfg)
                              for dependency
                              in self.latest_version["dependencies"]
                              if dependency["project_id"] is not None
                              and dependency["dependency_type"] == "required"}

        return self._dependencies

    @property
    def website(self):
        if self._website is not None:
            return self._website

        self._website = f"https://modrinth.com/mod/{self.mod['slug']}"
        return self._website

    @property
    def summary(self):
        if self._summary is not None:
            return self._summary

        self._summary = self.mod["description"]
        return self._summary.strip()

    @property
    def url(self):
        """
        Get the download url of a mod.

        Returns:
            str: The download url.

        Raises:
            ValueError: If the download url lookup fails.
        """
        if self._url is not None:
            return self._url

        download_url = self.file["url"]
        if not download_url:
            raise ValueError("Unavailable through API")

        self._url = download_url
        return self._url


class ModTable:
    """
    A class to represent a table of mods.
    """

    def __init__(self, mods):

        if not isinstance(mods, list):
            mods = [mods]

        self.mods = mods
        self._names_column_width = None
        try:
            self._term_width = os.get_terminal_size().columns
        except OSError:
            self._term_width = 80
        self._table = PrettyTable(align="l")

        if sys.platform == "win32":
            self._term_width -= 1

        self._table.set_style(SINGLE_BORDER)

    def __repr__(self):

        error_window = PrettyTable(align="c")
        error_window.header = False
        error_window.set_style(SINGLE_BORDER)

        if len(self.mods) <= 0:
            text = "No mods found.".center(self._term_width - 4)
            error_window.add_row([text])
            string = str(error_window)
        elif len(self.mods) == 1:
            string = str(self.details_view)
        else:
            string = str(self.list_view)

        if self._table_too_wide():
            text = "Window too small!".center(self._term_width - 4)
            error_window.clear_rows()
            error_window.add_row([text])
            string = str(error_window)

        return string

    def _fix_length(self, text, *, length=32):
        """
        Fix the length of a string.

        Args:
            text (str): The string to fix.
            length (int): The length to fix the string to.

        Returns:
            The fixed string.

        Raises:
            IndexError: If the length is less than 3.
        """
        # Remove all emojis from the text
        text = str(text).encode('ascii', 'ignore').decode('ascii').strip()
        output = text[:length - 3] + "..." if len(text) > length else text
        return output.ljust(length)

    def _table_too_wide(self):
        if self._term_width < 45:
            return True

        max_line_length = max(len(line)
                              for line
                              in str(self._table).split("\n"))

        return max_line_length > self._term_width

    @property
    def names_column_width(self):
        """
        Get the width of the names column.
        """
        if self._names_column_width is not None:
            return self._names_column_width

        self._names_column_width = self._term_width - 40
        return self._names_column_width

    @property
    def list_view(self):
        """
        Get the list view of the mods.
        """
        self._table.field_names = ["Id", "Name", "Downloads", "Updated"]

        for mod in sorted(self.mods, key=lambda x: x.downloads, reverse=True):

            mod_id = mod.mod_id
            name = mod.name
            downloads = numerize(mod.downloads)
            last_updated = mod.last_updated[:10]

            row = [self._fix_length(mod_id, length=8),
                   self._fix_length(name, length=self.names_column_width),
                   self._fix_length(downloads, length=9),
                   self._fix_length(last_updated, length=10)]
            self._table.add_row(row)

        return self._table

    @property
    def details_view(self):
        """
        Get the details view of a mod.
        """
        # Mod fields
        mod = self.mods[0]
        mod_id = self._fix_length(mod.mod_id, length=8)
        name = self._fix_length(mod.name, length=self.names_column_width)
        downloads = self._fix_length(numerize(mod.downloads), length=9)
        last_updated = self._fix_length(mod.last_updated, length=10)

        # Title row
        title = f"{mod_id} | {name} | {downloads} | {last_updated}"
        self._table.field_names = [title]

        # Mod details
        website = mod.website
        summary = self._fix_length(mod.summary, length=self._term_width - 4)
        try:
            download_link = mod.url
        except ValueError:
            download_link = "Not available."

        # Add dependencies
        self._table.add_rows([[website], [summary], [""],
                              ["Download:"], [download_link]])

        try:
            mod_dependencies = mod.dependencies
        except ValueError:
            mod_dependencies = []

        if len(mod_dependencies) != 0:
            self._table.add_rows([[""], ["Required dependencies:"]])

        for dependency in mod_dependencies:
            mod_id = self._fix_length(dependency.mod_id, length=8)
            try:
                url = dependency.url
            except ValueError:
                url = "Not available."
            self._table.add_row([f"{mod_id} | {url}"])

        return self._table
