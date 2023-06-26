# cursely
*Cross-platform mod management for Minecraft.*
<br>
<br>
<br>

<h4 align="center">Browse recently updated mods.</h4>
<p align="center">  
  <img width="600" src="https://i.imgur.com/pN6QVwI.png">
</p>
<br>

<h4 align="center">Search for mods by name and author.</h4>
<p align="center">  
  <img width="600" src="https://i.imgur.com/uxZZ0NC.png">
</p>
<br>

<h4 align="center">View mod details and get dependencies and download links.</h4>
<p align="center">  
  <img width="600" src="https://i.imgur.com/6JqYYNS.png">
</p>
<br>

<h4 align="center">Automatically deploy a modpack and its configs.</h4>
<p align="center">  
  <img width="600" src="https://i.imgur.com/m1HmvEJ.png">
</p>
<br>

## Installation
> To use [cursely](https://github.com/julynx/cursely) you need a [Curseforge API key](https://console.curseforge.com/?#/signup).

The first step is to install the required dependencies:
```
pip3 install requests prettytable numerize
```

Then, clone the repository and install the executable files:
```
git clone https://github.com/julynx/cursely /tmp/cursely
sudo chmod +x /tmp/cursely/cursely*
sudo cp /tmp/cursely/cursely* /usr/bin
```

<br>

## Usage

Cursely will ask for your Minecraft version, loader (Fabric or Forge), and API key when you run it for the first time, and will save those settings to ```.config/cursely/config.json```. From now on, it will only show mods compatible with that configuration.

You can now run the ```cursely``` command followed by any of the arguments listed below:
```
  cursely             Browse popular recently updated mods.
  cursely [MOD_ID]    Get a brief description of a mod and its download link.
  cursely [KEYWORD]   Search for a mod by its name or author.
  cursely [MODPACK]   Install all listed mods and their dependencies.
```

<br>

## Modpacks

A modpack file is a plain text file with the ```.mods``` extension and the following format:
```
example_modpack.mods

  # This line is a comment and will be ignored
  $ This is a bash command that will be executed
  12345 Name of mod with ID=12345
  67890 Name of mod with ID=67890
  ...
```

Running ```cursely example_modpack.mods``` will:
1) Download and install the listed mods.
2) Download and install their required dependencies.
3) Execute all the commands specified in the file.
4) Print any errors that might have occurred.

You can also use the ```cursely_modpack``` command, followed by the name of a modpack file (minus the extension) hosted in this repository to retrieve and deploy it.

For example, ```cursely_modpack magical_souls``` will fetch and install the modpack file ```github.com/julynx/cursely/magical_souls.mods```.

<br>

## Uninstalling
To uninstall [cursely](https://github.com/julynx/cursely), delete the executables and the configuration using the command:
```
sudo rm -rf /usr/bin/cursely* ~/.config/cursely
```

<br>

## Notes
If you are a Windows user, check out the [multiplatform beta](https://github.com/Julynx/cursely/tree/multiplatform_beta) (W.I.P.).
