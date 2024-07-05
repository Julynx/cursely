# cursely
*Cross-platform mod management for Minecraft.*
<br>
<br>
<br>

<h4 align="center">Get search results from CurseForge and Modrinth.</h4>
<p align="center">
  <img width="600" src="https://i.imgur.com/SrDRMxY.png">
</p>
<br>

<h4 align="center">View mod details, dependencies and download links.</h4>
<p align="center">
  <img width="600" src="https://i.imgur.com/gdgnnyt.png">
</p>
<br>

<h4 align="center">Deploy a modpack with its configuration.</h4>
<p align="center">
  <img width="600" src="https://i.imgur.com/mitqY4c.png">
</p>
<br>

## Installation

To install using poetry, run
```
git clone https://github.com/julynx/cursely
cd cursely/cursely
poetry install
poetry run cursely --help
```

<br>

## Usage
```
cursely [MOD_ID]    Get a brief description of a mod and its download link.
cursely [KEYWORD]   Search for a mod by its name or author.
cursely [MODPACK]   Install all listed mods and their dependencies.
cursely --help      Show this help message.
```

<br>

## Modpacks

A modpack file is a plain text file with the ```.mods``` extension and the following format:
```
example_modpack.mods

  game minecraft == 1.20.1
  loader fabric == 0.15.1
  config example_modpack_config.zip

  #    Mod ID  Comments (optional)  File version (optional)
  mod  325471  Inventory Sorting    == 5455951
  mod  429084  Limited Spawners
  mod  551140  Furnace Recycle

  #         Download URL                      Mod (optional)
  download  https://manual_mod_download_url
  download  https://manual_mod_download_url   for mod 917292

  # ...
```

Running ```cursely example_modpack.mods``` will:
1) Download and install the listed mods.
2) Download and install their required dependencies.
3) Copy the config files from the zip archive to the minecraft installation folder.
4) Print any errors that might have occurred.

<br>

## Resolution files

When installing a modpack, if no resolution file exists, a new one will be
created with the same name and the `.resolved-mods` extension.

If a resolution file already exists, the installer will try to use it
as long as it has the same name as the requested modpack, except for the
extension.

Resolution files contain all the mods and their dependencies, fixed to the
specific versions downloaded by the installer when the build was created.
This enables reproducible builds, providing the option to replicate the exact
same modpack in the future and preventing the incompatibilities that can arise
as mods get updated and their versions change over time.

<br>

## Disclaimer

_Modrinth and CurseForge are registered trademarks owned by their respective owners. Any references to these brands within this repository are for descriptive purposes only and do not imply endorsement or affiliation with said trademarks._
