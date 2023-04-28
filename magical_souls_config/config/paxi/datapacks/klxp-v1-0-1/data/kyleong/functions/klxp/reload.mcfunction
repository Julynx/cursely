scoreboard objectives add kklxp_death deathCount

scoreboard players set #100 kklxp_death 100

tellraw @a {"text":"------------------------------------","color":"green","bold":true}

tellraw @a {"text":"'KeepInventory lose xp' Data pack activated","color":"green","hoverEvent":{"action":"show_text","contents":[{"text":"To: planetminecraft.com","color":"gold"}]},"clickEvent":{"action":"open_url","value":"https://www.planetminecraft.com/data-pack/qptp"}}

tellraw @a {"text":" "}
tellraw @a {"text":"[v1.0.1] Datapack made by Kyleong","color":"green","hoverEvent":{"action":"show_text","contents":[{"text":"To: youtube.com","color":"gold"}]},"clickEvent":{"action":"open_url","value":"https://www.youtube.com/channel/UCGclCRGdWUjJdVcHLZfdaOg"}}

tellraw @a {"text":" "}
tellraw @a {"text":"[Click Me] Credits","color":"gold","underlined":true,"clickEvent":{"action":"run_command","value":"/function kyleong:klxp/credits"}}

tellraw @a {"text":"------------------------------------","color":"green","bold":true}