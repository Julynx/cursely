summon minecraft:experience_orb ~ ~ ~ {Tags:["kyleong_klxp"]}

execute store result entity @e[limit=1,sort=nearest,type=minecraft:experience_orb,tag=kyleong_klxp] Value int 1 run scoreboard players get @s kklxp_death

scoreboard players reset @s kklxp_death

tag @e[limit=1,sort=nearest,type=minecraft:experience_orb,tag=kyleong_klxp] remove kyleong_klxp