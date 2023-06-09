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

## Downloading and running - Linux & Windows
Open a **Terminal** (Linux) or **Command Prompt** (Windows) and paste the following commands:
```
pip3 install requests numerize prettytable
git clone https://github.com/julynx/cursely
cd cursely
python cursely --help
```

<br>

## Installing to system path - Linux
Open a **Terminal** inside the **cursely folder** and paste the following commands:
```
sudo chmod +x cursely*
sudo cp cursely* /usr/bin
```
You can now run cursely from anywhere with the ```cursely``` command.

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

  # Comment
  $ Shell command
  @ https://manual_mod_download_url
  # [id] [name]
  325471 Inventory Sorting
  429084 Limited Spawners
  551140 Furnace Recycle
  ...
```

Running ```cursely example_modpack.mods``` will:
1) Download and install the listed mods.
2) Download and install their required dependencies.
3) Execute all the commands specified in the file.
4) Print any errors that might have occurred.

<br>

## Uninstalling
To uninstall ```cursely```, simply remove the installation folder and the executables from the system path.

<br>

## Disclaimer
_Modrinth and CurseForge are registered trademarks owned by their respective owners. Any references to these brands within this repository are for descriptive purposes only and do not imply endorsement or affiliation with said trademarks._
