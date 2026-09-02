# **Path Finding Visualiser**

An interactive path-finding visualiser built with **Python, Pygame, and Pygbag**. Visualise how different path-finding algorithms explore a grid, find the shortest path, and handle barriers and weighted cells.

This project was built to make path-finding algorithms easier to understand by providing a visual representation of how they explore a search space. Instead of only seeing the final shortest path, the visualiser shows the exploration process and allows different algorithms and grid configurations to be tested interactively.

## **🚀 Live Demo**

**[Open the Path Finding Visualiser](https://sindhuja-5.github.io/Path-Finding-Visualiser/)**

The project runs directly in the browser using Pygbag/WebAssembly — no Python installation is required for the live demo.

## **✨ Features**

- Interactive grid-based path finding
- Adjustable maze size from **5 × 5 to 50 × 50** (Default maze size: **25 × 25**)
- Generate random mazes using recursive division
- Add weighted cells
- Clear paths (without resetting the grid)
- Clear the entire grid
- Visualise algorithm exploration step-by-step
- Compare **A\*** and **Dijkstra's Algorithm**
- Runs locally with Python/Pygame
- Runs in the browser through Pygbag

## **🧠 Algorithms**

### A* Search

A* uses the cost of the path travelled so far together with a heuristic estimate of the remaining distance.

It uses:

```text
f(n) = g(n) + h(n)

where:
g(n) = cost from the start node to the current node
h(n) = estimated cost from the current node to the target
f(n) = estimated total cost
```
For this project, A* uses the Manhattan distance as its heuristic.

### **Dijkstra's Algorithm**

Dijkstra's algorithm explores nodes based only on the accumulated cost from the start node.

It guarantees the shortest path when all edge weights are non-negative, but unlike A*, it does not use a heuristic to guide the search toward the target.

## **🎮 How to Use**
1. Choose the maze size
2. Build a maze if you want randomly generated barriers
3. Add weights if you want to visualise weighted path finding
4. Select an algorithm
5. Watch the algorithm explore the grid and find the path

### Grid Controls
Left click — interact with grid cells
Build Maze — generate a random maze
Weight — enable weighted cells
Clear Path — remove the current path while keeping the grid including barriers and weighted cells
Clear Grid — reset the grid
− / + — decrease or increase maze size
A* — run A* search
Dijkstra — run Dijkstra's algorithm

## **🖥️ Run Locally**
Requirements
Python 3.10+
Pygame

### Install Pygame:

pip install pygame

### Clone the repository:

git clone https://github.com/sindhuja-5/Path-Finding-Visualiser.git
cd Path-Finding-Visualiser

### Run the application:

python main.py

The Pygame window should open automatically.

## **🌐 Build for the Web**

The project uses Pygbag to run the Pygame application in the browser.

Install Pygbag:

pip install pygbag

Build the web version:

python -m pygbag --build .

The generated web build can then be deployed using GitHub Pages or another static hosting service.

## **🛠️ Tech Stack**
1. Python
2. Pygame
3. Pygbag
4. WebAssembly
5. GitHub Pages
