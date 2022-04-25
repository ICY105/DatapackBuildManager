# DatapackBuildManager
A simple build system for managing dependencies of Minecraft Datapacks. Automates downloading dependency datapacks, cleaning & copying into a datapack, and merging files where possible.

As with any tool that could potentially destroy your project, please take backups (I mean, you are using git, right?)

Usage:
```
Setup your dependencies.json file (see example in repo)

Run this from command line for basic operation:
    python build-datapack.py <datapack>

For advanced operation, add -h to see flags:
    python build-datapack.py -h
```
