# Stellar Haven

> **CPSC 4160 — 2D Game Engine Construction**  
> Clemson University, Fall 2024 (Senior Year)  
> Created by Russell Welch  
> [GitHub](https://github.com/russellocean) • [LinkedIn](https://linkedin.com/in/russelldoescode)

---

## Table of Contents

- [Stellar Haven](#stellar-haven)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Game Story \& Description](#game-story--description)
  - [Key Features](#key-features)
  - [Gameplay Video](#gameplay-video)
  - [Paid Asset Packs](#paid-asset-packs)
  - [How to Run](#how-to-run)
  - [License \& Credits](#license--credits)
    - [Code License](#code-license)
    - [Artwork \& Assets](#artwork--assets)
    - [Special Thanks](#special-thanks)

---

## Introduction

**Stellar Haven** is a 2D space-settlement and crew-management simulation, developed entirely in **Python** using **Pygame**. This project was created for the **CPSC 4160 "2-D Game Engine Construction"** course at Clemson University during the Fall 2024 semester, in my senior year.

The game was **built from scratch in Pygame with no external libraries**, featuring handcrafted systems for tile-grid management, AI behavior, building mechanics, resource management, and more. It demonstrates the core principles of building a small game engine and showcases efficient code organization, extensible systems, and custom game logic tailored to a space-themed simulation experience.

---

## Game Story & Description

In **Stellar Haven**, you play as the **Overseer** of a remote trading outpost located at the edge of known space. Your outpost offers shelter, trade, and opportunity for wayward travelers, explorers, and pioneers venturing into the cosmos in search of resources and new homes.

Throughout the game, you'll:

- **Construct** and **expand** your outpost with facilities like housing units, canteens, research labs, and engine bays.
- **Manage** critical resources including power, oxygen, and credits.
- **Respond** to random events and new settlers seeking refuge or resources.
- **Assign** crew members on missions (which play out off-screen) to gather supplies and bolster the outpost.
- **Balance** the well-being of your settlers, ensuring their safety from threats and hazards in deep space.

By effectively managing resources and growing your colony, you'll transform a modest outpost into a thriving hub on the frontier of space.

---

## Key Features

1. **Robust Tile Grid System**  
   A custom grid system underpins the entire world, handling tile-based collisions, interactions, and rendering.

2. **Tilemap Generator Tool**  
   A stand-alone tool that allows you to select tiles from a master image and export them with their settings to configuration files. This enables quick iteration on tile designs and easy integration into the main game.

3. **Asset Manager**  
   A unified system to load sprites, tiles, and animations from external config files, ensuring all assets remain organized and easily swappable.

4. **Dynamic Grid Renderer**  
   Implements contextual rendering logic so tiles automatically adapt to their surroundings (e.g., corners of walls use corner tiles, floor trims render along bottom edges, etc.).

5. **Robust Player Controller**  
   Includes advanced platforming capabilities such as one-way platforms (Mario-style), so the player can jump through them from below but also drop down if they press down.

6. **AI System**  
   Each AI character is assigned a randomized name, job, and set of voice lines. They dynamically react to in-game events such as resource shortages or system malfunctions.

7. **Building System**  
   Players can create and customize various ship rooms. This system automatically updates the collision map and spawns AI occupants to bring these rooms to life.

8. **Resource Management**  
   Balances power, oxygen, and credits, forcing the player to make strategic decisions about expansions, repairs, and crew assignments.

9. **Layer Rendering System**  
   The game scene is drawn in multiple layers (background, game layer, system layer, UI, debug layer), maintaining clarity and visual hierarchy.

10. **Dialog System**  
    NPCs and crew members deliver story beats and context-sensitive lines to the player, enriching the narrative and gameplay experience.

---

## Gameplay Video

A gameplay showcase video is included in the repository:

---

## Paid Asset Packs

This project uses two paid asset packs from [itch.io](https://itch.io):

1. **Player & AI Character Sprites**  
   [Warped Space Marine by Ansimuz](https://ansimuz.itch.io/warped-space-marine)  
   _Required location: `assets/characters/`_

2. **Spaceship Tileset**  
   [Spaceship Tileset Pack by Mucho Pixels](https://muchopixels.itch.io/spaceship-tileset-pack)  
   _Required location: `assets/tilemaps/`_

Since these are _paid_ assets, they **are not included** in this repository. If you wish to run the game with the original art, you will need to:

1. Purchase these asset packs separately
2. Create the required directories:
   ```bash
   mkdir -p assets/characters
   mkdir -p assets/tilemaps
   ```
3. Place the assets in their respective directories as specified above

Alternatively, you can substitute your own placeholder assets, as the project supports loading assets through its config-based Asset Manager.

---

## How to Run

1. **Install Dependencies**

   ```bash
   make setup
   ```

   This will:

   - Create a virtual environment
   - Install required packages from `requirements.txt`
   - Set up Python 3.9+ and Pygame

2. **Clone or Download** the repository

3. **Acquire or Provide Assets**

   - Place the purchased or placeholder assets in the `assets/` directory, following the folder structure referenced in the config files.

4. **Launch the Game**

   ```bash
   make run
   ```

5. **Optional: Launch Tilemap Helper**  
   For development/modding, you can use the tilemap helper tool:

   ```bash
   make tilemap-helper
   ```

6. **Cleanup**  
   To clean up generated files and virtual environment:
   ```bash
   make clean
   ```

---

## License & Credits

### Code License

This project is released under the MIT License. Please see LICENSE for details.

### Artwork & Assets

Original code and placeholder art are free to use under the same license. Paid assets from Ansimuz and Mucho Pixels are not included and must be purchased separately or replaced with user-owned artwork.

### Special Thanks

- Professor Matias Volonte for guidance and support throughout CPSC 4160.
