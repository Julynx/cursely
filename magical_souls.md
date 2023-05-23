## Graphics and performance

# 455508 Iris Shaders
# 394468 Sodium
# 360438 Lithium
372124 Phosphor
# 448233 Entity culling
459857 FerriteCore
433518 LazyDFU
256717 Clumps
627566 Memory leak fix

## Sounds and special effects

393442 Lamb Dynamic Lights
254284 AmbientSounds 5
478890 ExtraSounds
513689 Smooth Swapping
543661 Stylish Effects

## Convenience

859712 PickupWidely (Fabric)
310111 Roughly Enough Items Fabric/Forge
421377 HT's TreeChop
263420 Xaero's Minimap
317780 Xaero's World Map
530816 No telemetry
# 308702 Mod Menu
# XXXXXX No LAN cheating
# XXXXXX Shifty Hotbar
547689 TrashSlot
401978 Disable Custom Worlds Advice
243190 Shoulder Surfing Reloaded
435044 Better Third Person
515415 Stacker
325471 Inventory Sorting
429084 Limited Spawners
551140 Furnace Recycle
447359 Passive Shield
390913 Fixed anvil repair cost
523801 Anvil restoration
452834 Right Click Harvest
458048 Diagonal Fences
445838 Animal Feeding Trough
397434 Polymorph
411557 ToolTipFix
676136 Model gap fix
623806 Auto HUD

## World gen and structures

513688 Terralith
# 636540 Structory
# 783522 Structory: Towers
615351 Better Villages - Fabric
530309 Awesome Dungeon - Fabric
391366 Repurposed Structures
# 637201 Immersive structures
585782 Additional Structures
656977 MVS - Moog's Voyager Structures
656079 Red’s More Structures
698309 Explorify – Dungeons & Structures
626761 Towns and Towers
569737 Philip's Ruins
410902 Fabric Waystones
521673 Bountiful

## Extras

535291 MCA Reborn
443694 Enchanced Celestials
412082 Supplementaries
559148 Enchanted Vertical Slabs
296676 Culinary Construct

## YUNG's mods

817666 YUNG's Better Nether Fortresses
631403 YUNG's Better Witch Huts
590988 YUNG's Bridges
689252 YUNG's Better Ocean Monuments
590993 YUNG's Extras
631020 YUNG's Better Desert Temples
373591 YUNG's Better Mineshafts
525586 YUNG's Better Dungeons
480684 YUNG's Better Strongholds
418881 Paxi

## Combat mechanics

639842 Better Combat

## Armor and weapons

659887 Simply Swords
407311 MC Dungeons Weapons
426206 MC Dungeons Armors
442332 MC Story Mode Armors
580681 Immersive Armors
734325 Wizards
811662 Spellblades and such
517833 Arcanus: Legacy
632066 Marium's Soulslike Weaponry
663567 Mythic Upgrades

## Accessories

401236 Artifacts
828331 Gliders

## Mobs and/or mob alterations

392015 Eldritch Mobs
514468 The Graveyard
551364 Friends and Foes
371033 Rotten Creatures
561625 Creeper Overhaul
465336 Terrarian Slimes
438365 Bosses of Mass Destruction
390991 Adventurez

## Manual dependencies

459496 Indium    (Required by Supplementaries)

## Custom commands - Mods

# Structory             (Curseforge API miss)
$ wget -P ~/.minecraft/mods/ 'https://mediafilez.forgecdn.net/files/4441/631/Structory_1.19.3_v1.3.1a.jar'

# Structory Towers      (Curseforge API miss)
$ wget -P ~/.minecraft/mods/ 'https://mediafilez.forgecdn.net/files/4441/351/Structory_Towers_1.19.3_v1.0.2.jar'

# Entity culling        (Curseforge API miss)
$ wget -P ~/.minecraft/mods/ 'https://mediafilez.forgecdn.net/files/4404/950/entityculling-fabric-1.6.1-mc1.19.2.jar'

# Immersive structures  (Curseforge API miss)
$ wget -P ~/.minecraft/mods/ 'https://mediafilez.forgecdn.net/files/4497/514/%5bUniversal%5dImmersive+Structures-2.0.7a.jar'

# No LAN cheating       (Modrinth)
$ wget -P ~/.minecraft/mods/ 'https://cdn-raw.modrinth.com/data/i5JxLPkx/versions/1.5.0%2B1.19-pre1/no-lan-cheating-1.5.0%2B1.19-pre1.jar'

# Sodium                (Modrinth)
$ wget -P ~/.minecraft/mods/ 'https://cdn-raw.modrinth.com/data/AANobbMI/versions/rAfhHfow/sodium-fabric-mc1.19.2-0.4.4%2Bbuild.18.jar'

# Lithium               (Modrinth)
$ wget -P ~/.minecraft/mods/ 'https://cdn-raw.modrinth.com/data/gvQqBUqZ/versions/m6sVgAi6/lithium-fabric-mc1.19.2-0.11.1.jar'

# Iris                  (Modrinth)
$ wget -P ~/.minecraft/mods/ 'https://cdn-raw.modrinth.com/data/YL57xq9U/versions/7MJ26Y79/iris-mc1.19.2-1.6.2.jar'

# ModMenu               (Modrinth)
$ wget -P ~/.minecraft/mods/ 'https://cdn-raw.modrinth.com/data/mOgUt4GM/versions/V4hnfgRO/modmenu-4.1.2.jar'

# Shifty Hotbar         (Listed as 1.19)
$ wget -P ~/.minecraft/mods/ 'https://mediafilez.forgecdn.net/files/3836/816/shifty-hotbar-mc1.19-1.1.jar'

## Custom commands - Configs

$ rm -rf /tmp/cursely.zip /tmp/cursely 
$ wget https://github.com/Julynx/cursely/raw/main/magical_souls_config.zip -O /tmp/cursely.zip
$ mkdir /tmp/cursely
$ unzip -o /tmp/cursely.zip -d /tmp/cursely
$ cp -r /tmp/cursely/magical_souls_config/* ~/.minecraft
