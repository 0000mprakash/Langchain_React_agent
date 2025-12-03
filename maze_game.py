import random
import threading
import time

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.create_maze(0, 0)
        self.grid[height - 1][width - 1] = 'E'  # Exit point

    def create_maze(self, x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 1:
                self.grid[y + dy // 2][x + dx // 2] = 0
                self.grid[ny][nx] = 0
                self.create_maze(nx, ny)

    def print_maze(self, player_position):
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == player_position:
                    print('P', end=' ')  # Player
                elif self.grid[y][x] == 1:
                    print('#', end=' ')  # Wall
                else:
                    print(self.grid[y][x], end=' ')  # Path or Exit
            print()

class Player:
    def __init__(self, maze):
        self.maze = maze
        self.position = (0, 0)
        self.last_direction = None
        self.running = True

    def move(self, direction):
        x, y = self.position
        if direction == 'w' and y > 0 and self.maze.grid[y - 1][x] in (0, 'E'):
            self.position = (x, y - 1)
        elif direction == 's' and y < self.maze.height - 1 and self.maze.grid[y + 1][x] in (0, 'E'):
            self.position = (x, y + 1)
        elif direction == 'a' and x > 0 and self.maze.grid[y][x - 1] in (0, 'E'):
            self.position = (x - 1, y)
        elif direction == 'd' and x < self.maze.width - 1 and self.maze.grid[y][x + 1] in (0, 'E'):
            self.position = (x + 1, y)
        self.last_direction = direction

    def run(self):
        while self.running:
            if self.last_direction:
                self.move(self.last_direction)
                if self.maze.grid[self.position[1]][self.position[0]] == 'E':
                    self.running = False
                    print('WIN')
            time.sleep(0.1)

def main():
    width, height = 10, 10
    maze = Maze(width, height)
    player = Player(maze)
    
    thread = threading.Thread(target=player.run)
    thread.start()

    while player.running:
        maze.print_maze(player.position)
        move = input('Move (w/a/s/d): ')
        player.move(move)

if __name__ == '__main__':
    main()