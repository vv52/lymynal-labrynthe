# Lymynal Labrynthe
Eerie precision platformer set in a cursed DOS game. This was mechanically designed as a spiritual successor to the first game I ever created, with some improvements ;)

This game is quite difficult, the present left in the chest in the first area should make many of the levels much more approachable. If you feel that you need some assistance I reccomend taking the chest item, however, the game is 100%able without it and I consider that the "true" experience. That being said, I take the chest item much of the time.

(continued from PyGame project for CS 232 @ HSU - Spring 2021)

## Controls
* ENTER to start game
* ESCAPE to quit
* F to change display mode
* LEFT and RIGHT arrow keys to move
* UP arrow key to jump
* [if chest in level 0 is taken] DOWN arrow key to cancel momentum and slow movement
* S to screenshot during game or results screen (stored in game folder)

To access the special stages, every single coin before the stage where the key appears must be collected or the key will not appear. On stages with corresponding special doors, all coins must be collected before entering door because they disappear while you're gone! The sword only shows up in special stage 2 if you have the ring! If you want to see everything and complete all the content in the canonic way, do not take the chest in the starting area, clear every coin in every stage before doing anything else, and collect every item! The boss is not yet implemented but (outside of not taking the chest) the sword and having every coin are prerequisites to challenging the stage.

## Features
* Physics engine featuring gravity, acceleration, friction, and momentum
* "Forgiving" jump system where player can jump for a few frames after leaving collision state, allowing the player to make jumps just after leaving a platform.
* Hazards that reset the player to the current level's spawn
* Hazards that only trigger if interacted with while falling
* Terrain that slows player and allow for repeated jumping without being on the ground
* Respawn points that change the spawn point for the stage to save player progress in tough stages
* Colectibles that are kept track of from level to level
* Keys that remove hazards to allow progress witin a stage
* Secret key(s) that only spawn if the player has collected every coin until that point
* Secret keys unlock doors in later levels that lead to bonus content
* Spike hazards that can be walked on but are fatal if fallen on
* Moving platforms
* Moving enemies
* Tracking of player stats
* Title screen
* Level names stored in JSON and automatically pushed to window title
* Automatic level progression
* End screen with stats including:
    * total in-game playtime
    * player deaths
    * player collectibles
    * total player jumps
* Sound effects
* Background ambience
* Original music
* Simple animations
* Meticulous level design
* Lots of levels!
* Built in screenshot button
* Formidable challenge
* Secrets!
 
## Dependencies
* pip3 install pygame

## Credits

#### Engine
* I originally followed along partially with this Coder's Legacy tutorial: https://coderslegacy.com/python/pygame-platformer-game-development/
* The "air" / "forgiving jump" system I employ was inspired by an identical mechanic demonstrated in this video: https://www.youtube.com/watch?v=abH2MSBdnWc
* Everything else was of my own design, including the level loading and level format, or was implemented after I tried to follow a bunch of random tutorials and none of them got me where I wanted to be

#### Graphics
* I used free '1-Bit' sprite packs as a base and edited them to fit my needs, sprite packs by VECTORPIXELSTAR on itch.io

#### Audio
* music by me (level 8 and 13 songs)
* title chimes by takecha from freesound.org
* background ambience loop edited but originally by Moulaythami from freesound.org
* coin sound effect by cabled_mess from freesound.org
* death sound effect edited but originally sampled from cabled_mess as well
* jump and next stage sound effects by plasterbrain from freesound.org
* respawn sound effect edited but originally sampled from plasterbrain as well
