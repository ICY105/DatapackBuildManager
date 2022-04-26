# DatapackBuildManager
A simple build system for managing dependencies of Minecraft Datapacks written in Python, sort of like a make file for datapacks. It currently automates:
* Downloading dependencies from a URL (local files are also supported)
* Cleaning datapack of dangleing files
* Copying dependencies into datapack, merging files where pratical
* Integrating function tags
* Upgrading versioned libraries build version (doesn't cover all edge cases, you will need to check what does and does not get updated)

As with any tool that could potentially destroy your project, please take backups (I mean, you are using git, right?)

Usage:
```
Setup your dependencies.json file (see example in repo)

Run this from command line for basic operation:
    python build-datapack.py <datapack>

For advanced operation, add -h to see flags:
    python build-datapack.py -h
```

# Known Libraries
These are datapack libraries that work with DatapackBuildManager. If you know of a library that should be on this list, please contact me.

'Versioned' libraries are formatted such that if an end-user is using multiple datapacks implementing that library, they will not conflict. In most cases unversioned libraries won't cause problems, but can cause conflicts. 'Static' libraries are unversioned, but are intended to never change so they can't cause conlicts.

Library | Author | Description | Versioned | Note
--------|--------|-------------|-----------|-----
[AESTD](https://github.com/Aeldrion/AESTD) | Aeldrion | A 'common library' of useful entity tags, block tags, item tags, entity tags, predicates, and other useful stuff | No |
[Block Utils](https://github.com/ICY105/BlockUtils) | ICY105 | Adds various utilities for interacting with blocks. Currently limited to detecting redstone power. | Yes |
[ChunkScan](https://github.com/ICY105/ChunkScan) | ICY105 | Adds a post-gen chunk scaning system. Supports any dimension (including custom), custom worldheights, and is compatible with other worldgen systems, both normal and postgen. | Yes |
[ChunkScan.Ores](https://github.com/ICY105/ChunkScan.Ores) | ICY105 | Adds a custom ore generation system built on ChunkScan. Supports any dimension (including custom) and biome filtering. | Yes | Requires ChunkScan
[Datapack Energy](https://github.com/ICY105/DatapackEnergy) | ICY105 | Adds a robust and optimized energy transfer system for Tech datapacks adding machines. | Yes |
[Get Shape Util](https://github.com/asd988/getshape_util) | asd988 | Provides a system for getting the shape of most blocks. | No |
[Iris](https://github.com/Aeldrion/Iris) | Aeldrion | An extremely precise system for determing what block a player is looking at. | No |
[Lantern Load](https://github.com/LanternMC/load) | LanternMC | A common system for controlling load order. This is the basis of most libraries, and all versioned libraries. | Static | Usually you do not need to add this explicitly, any datapack depending on LanternLoad will implement it themselves.
[Loottable Autosmelt](https://github.com/ICY105/LoottableAutosmelt) | ICY105 | Adds loot-table based tool abilities like autosmelt and void. | No | Extensive loot table modifications can cause incompatibilies between libraries.
[LTOS](https://github.com/gibbsly/ltos) | gibbsly | A utility to reliably determine who broke a block and what was broken. | No | Extensive loot table modifications can cause incompatibilies between libraries. Not properly versioned.
[NBT Crafting API](https://github.com/BigPapi13/NBT-Crafting-API) | BigPapi13 | Implements a system to access the NBT of items in the vanilla crafting table. Only works on unstackable items, and cannot affect output. | No |
[Player Action](https://github.com/ICY105/PlayerAction) | ICY105 | Provides hooks for various player actions, including click detection. | Yes |
[Player DB](https://github.com/rx-modules/PlayerDB) | rx | Implements an efficient system for storing and retrieving per-player data in storage. | Yes |
[QCB](https://github.com/Ellivers/QCB) | Ellivers | Adds a common cross-datapack soloution to remove barrel opening sounds from custom blocks without using /stopsound. | Static |
[Random](https://github.com/Aeldrion/Minecraft-Random) | Aeldrion | Provides a variety of random number generators. | No |
[Ray Collision Detector](https://github.com/K-bai/Minecraft-Ray-Collision-Detector) | K-bai | A precise ray-marching system to locate blocks. | No |
[Score Based Damage](https://github.com/ErrorCraft/Score-Based-Damage) | ErrorCraft | Adds a system for damaging players using attributes | No |
[Smithed Actionbar](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds a cross-datpack soloution for requesting use of the actionbar, instead of monopolizing its use. | Yes | The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files.
[Smithed Crafter](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds a cross-datapack barrel-based custom crafting table for NBT recipes. | Yes The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files. 
[Smithed Custom-Block](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds utilities relating to handleing custom blocks, such as placing custom blocks. | Yes | The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files.
[Smithed Damage](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds an API for damaging entities, including players through attribute manipulation. Includes calculations for armor and enchantments. | Yes | The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files.
[Smithed Item](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds and API for adding custom durability to items. | Yes | The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files.
[Smithed Prevent Aggression](https://github.com/Smithed-MC/Libraries) | MC Smithed | Adds a cross-datpack soloution for preventing hostile mobs from attacking technical entites like wandering traders. | Yes | The repo is uncompiled- you will need a compiled link, or you will need to download, build, and direct DBM to local files.
[String Parsing](https://github.com/5uso/String-Parser) | 5uso | Adds a system for for parsing strings into character arrays. | No |
[WASD Arithmetic](https://github.com/MulverineX/wasd_arithmetic/tree/generated) | MulverineX | Adds detection of local direction input (wasd) using maths. | No |
