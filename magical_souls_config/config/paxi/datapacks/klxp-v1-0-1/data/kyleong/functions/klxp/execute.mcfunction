execute store result score @s kklxp_death run data get entity @s XpLevel 7

execute if score @s kklxp_death > #100 kklxp_death run scoreboard players set @s kklxp_death 100

xp set @s 0 levels

xp set @s 0 points

execute unless score @s kklxp_death matches 0 at @s run function kyleong:klxp/xp