# Game Installation and Running Instructions

To install and run the game, use the following Makefile commands:

```bash
make
make run
```

Milestone 3
Russell Welch: 100 Pts

Implemented Player Movement and Physics (25 Pts):
-   Created player class with velocity, gravity, and jump mechanics.
-   Implemented horizontal and vertical movement based on input.
-   Implemented collision detection with the environment.
-   Implemented ground check and platform drop-through mechanics.

Implemented Player Animation (15 Pts):
-   Loaded and managed multiple animation sequences (idle, run, jump).
-   Implemented animation frame switching based on player state.
-   Handled sprite flipping for correct facing direction.

Implemented Player Interaction (15 Pts):
-   Implemented collision detection with interactable objects.
-   Implemented feedback system for interactions.

Developed Core Game Systems (20 Pts):
-   Created Game class to manage game state and scenes.
-   Created SceneManager to handle scene transitions.
-   Created EventSystem for communication between game components.

Developed Game Scenes (15 Pts):
-   Created GameplayScene to manage game logic and rendering.
-   Created PrologueScene to manage the game's introductory sequence.
-   Created PauseScene to manage the pause menu.

Developed UI Elements (10 Pts):
-   Created GameHUD to display resources and room information.
-   Implemented resource bars with animations.

