!pip install jit

!pip install --upgrade pip

!pip install pygame --pre

!pip install numpy

!pip install cython

import pygame
from queue import PriorityQueue
import time
import numpy as np
import functools
import threading

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (133, 2, 1)
VISIT1 = (0, 255, 230)
VISIT2 = (0, 80, 230)
VISIT3 = (1, 106, 106)
LOOK = (0, 255, 164)
START = (217, 1, 183)
END = RED
GREY = (63, 63, 63)
OPEN = (0, 255, 149)
OPEN1 = (0, 106, 0)
PATH1 = (255, 200, 0)
PATH2 = (255, 254, 0)
PATH3 = (0, 200, 0)
BG_COLOR = (6, 69, 96)
BUTTON_COLOR = (19, 175, 240)
SCREEN_COLOR = (204, 230, 255)
VISITED = []

class Node:
    def __init__(self, row, col, width, total_rows):
        self.last = pygame.time.get_ticks()
        self.cooldown = 300 
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.dec_animation = False
        self.weight = False
        
    def get_pos(self):
        return self.row, self.col
    
    def is_visited(self):
        return self.color == VISIT1
    
    def is_open(self):
        return self.color == OPEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_weight(self):
        return self.weight
    
    def is_start(self):
        return self.color == START
    
    def is_end(self):
        return self.color == END
    
    def is_neutral(self):
        return self.color == WHITE
    
    def is_looked(self):
        return self.color == LOOK
    
    def reset(self):
        self.color = WHITE
        self.weight = False
    
    def make_visit(self):
        if not self.is_weight():
            self.color = VISIT2
        else:
            self.color = VISIT3
        
        
    def make_open(self):
        if not self.is_weight():
            self.color = OPEN
        else:
            self.color = OPEN1
    
    def make_barrier(self):
        if not self.is_start() and not self.is_end():
            self.color = BLACK
            self.weight = False
            
    def make_weight(self):
        if not self.is_start() and not self.is_end():
            self.color = BROWN
            self.weight = True
    
    def make_end(self):
        self.color = END
        self.weight = False
    
    def make_start(self):
        self.color = START
        self.weight = False
        
    def make_path(self):
        if not self.is_weight():
            self.color = PATH1
        else:
            self.color = PATH3
    
    def looking_at(self):
        self.color = LOOK
    
    def draw(self, win):
        try:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        except:
            print(self.color)
            input()
            
    def update_neighbors(self, grid, diag = False):
        r = self.row 
        c = self.col
        if r < self.total_rows-1 and not grid[r+1][c].is_barrier():
            self.neighbors.append(grid[r+1][c])
            
        if r > 0 and not grid[r-1][c].is_barrier():
            self.neighbors.append(grid[r-1][c])
            
        if c < self.total_rows-1 and not grid[r][c+1].is_barrier():
            self.neighbors.append(grid[r][c+1])
            
        if c > 0 and not grid[r][c-1].is_barrier():
            self.neighbors.append(grid[r][c-1])
        
        if diag:
            if r < self.total_rows-1 and c < self.total_rows-1 and not grid[r+1][c+1].is_barrier():
                self.neighbors.append(grid[r+1][c+1])

            if r > 0 and c < self.total_rows-1 and not grid[r-1][c+1].is_barrier():
                self.neighbors.append(grid[r-1][c+1])

            if r > 0 and c > 0 and not grid[r-1][c-1].is_barrier():
                self.neighbors.append(grid[r-1][c-1])

            if r < self.total_rows-1 and c > 0 and not grid[r+1][c-1].is_barrier():
                self.neighbors.append(grid[r+1][c-1])
    
    def __lt__(self, other):
        return False

class button():
    def __init__(self, x, y,width,height, text=''):
        self.color = BUTTON_COLOR
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            pygame.draw.circle(win, outline, (self.x, self.y+self.height//2), self.height//2+2)
            pygame.draw.circle(win, outline, (self.x+self.width, self.y+self.height//2), self.height//2+2)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        pygame.draw.circle(win, self.color, (self.x, self.y+self.height//2), self.height//2)
        pygame.draw.circle(win, self.color, (self.x+self.width, self.y+self.height//2), self.height//2)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 35)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def is_hover(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x-self.height//2 and pos[0] < self.x + self.width+self.height//2:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

class screen():
    def __init__(self, x,y,width,height, text=''):
        self.color = SCREEN_COLOR
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label1 = ""
        self.text1 = text
        self.text2 = ""
        self.text3 = ""
        
    def set_label1(self, label):
        self.label1 = label
    
    def set_text1(self, text):
        self.text1 = text
    def set_text2(self, text):
        self.text2 = text
    def set_text3(self, text):
        self.text3 = text
        
    def get_text1(self):
        return self.text1

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.label1 != '':
            font = pygame.font.SysFont('comicsans', 20)
            label = font.render(self.label1, 1, (0,0,0))
            win.blit(label, (self.x + 10, self.y + 10))
        
        if self.text1 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text1, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2) - 50))
        if self.text2 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text2, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
        if self.text3 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text3, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), 50 + self.y + (self.height/2 - text.get_height()/2)))

    def is_hover(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def visit_animation2(node):
    if node.color == VISIT1:
        return True
    else:
        r, g, b = node.color
        b += 1
        node.color = (r, g, b)
        return False

def visit_animation(visited):
    for node in visited:
        if node.color == VISIT1 or node.color == VISIT3:
            visited.remove(node)
            continue
        r, g, b = node.color
        if g < 255:
            g += 1
        node.color = (r, g, b)

def path_animation(path):
    for node in path:
        if not node.is_start():
            r, g, b = node.color
            if node.dec_animation:
                g -= 1
                if g <= PATH1[1]:
                    node.dec_animation = False
            else:
                g += 1
                if g >= PATH2[1]:
                    node.dec_animation = True
        node.color = (r, g, b)

def reconstruct_path(came_from, start, current, draw, visited,  win, width, grid, is_draw = True):
    path = []
    c = 0
    while current in came_from:
        visit_animation(visited)
        current = came_from[current]
        if current.is_weight():
            c+= 5
        else:
            c+=1
        if current in visited:
            visited.remove(current)
        if current != start:
            path.insert(0, current)
        current.make_path()
        if is_draw:
            for rows in grid:
                for node in rows:
                    node.draw(win)
            draw_grid(win, len(grid), width)
            pygame.display.update()
    return path, c-1

def A_star(draw, grid, start, end, output, win, width):
    count = 0
    vis = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    visited = []
    nebrs = []
    
    open_set_hash = {start}
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            path, inc = reconstruct_path(came_from, start, end, draw, visited, win, width, grid)
            start.make_start()
            output.set_text1(f"Path Length: {inc}")
            output.set_text2(f"#Visited nodes: {vis}")
            if vis != 0:
                output.set_text3(f"Efficiency: {np.round(inc/vis, decimals=3)}")
            return visited, path
        c = 1      
        for neighbor in current.neighbors:
            if not neighbor.is_barrier():
                if neighbor.is_weight():
                    c = 5

                temp_g_score = g_score[current] + c
                temp_f_score = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_f_score
                    if neighbor not in open_set_hash:
                        count+=1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                    if neighbor != end:
                        nebrs.append(neighbor)
                        neighbor.make_open()
        
        if current != start:
            vis+=c
            visited.append(current)
            current.make_visit()
#         t = Thread(target = functionname, [args = (arg1, arg2, ...)]
        visit_animation(visited)
#         nebr_animation(nebrs)
        for rows in grid:
            for node in rows:
                node.draw(win)
        draw_grid(win, len(grid), width)
        pygame.display.update()
            
    return visited, False

def make_black(grid, win):
    for row in grid:
        for node in row:
            node.make_barrier()
            node.draw(win)
    pygame.display.update()

def recursive_maze(draw, width, grid, start, end, left, right, top, bottom, win):
    if right-left >= 1 and bottom-top >=1:
        vertical = True
        test = False
        if right-left >= bottom-top:
            if bottom-top == 1:
                if (bottom < len(grid) and grid[left][bottom].is_barrier()) and (top-1 >= 0 and grid[left][top-1].is_barrier()):
                    vertical = False
            if vertical == True:
                l = left
                r = right
                if left-1>=0 and grid[left-1][top].is_barrier():
                    l = left+1
                if right<50 and grid[right][top].is_barrier():
                    r = right-1
                if l >= r:
                    vertical = False 
            if vertical == True:
                test = True
                rand = np.random.randint(l, r)
                if top<bottom and ((bottom - top <= 3) or (top-1 >= 0 and grid[left][top-1].is_neutral() and bottom < len(grid) and grid[left][bottom].is_neutral())):
                    br = bottom
                if top+1 < bottom-1:
                    br = np.random.randint(top+1, bottom-1)
                elif top+1 == bottom-1:
                    br = top+1
                else:
                    br = bottom
                
        elif right-left <= bottom-top:
            if right-left == 1:
                if (right < len(grid) and grid[right][top].is_barrier()) and (left-1 >= 0 and grid[left-1][top].is_barrier()):
                    return 
            t = top
            b = bottom
            if top-1>= 0 and grid[left][top-1].is_barrier():
                t = top+1
            if bottom < 50 and grid[left][bottom].is_barrier():
                b = bottom-1
            if t >= b:
                return
            test = True
            rand = np.random.randint(t, b)
            if left<right and ((right - left<= 3) or (left-1 >= 0 and grid[left-1][bottom].is_neutral() and right < len(grid) and grid[right][bottom].is_neutral())):
                    br = bottom
            if left+1 < right-1:
                br = np.random.randint(left+1, right-1)
            elif left+1 == right-1:
                br = left+1
            else:
                br = right
            vertical = False
        if test == False:
            return
        prob = 3
        if vertical:
            for y in range(top, br):
                grid[rand][y].make_barrier()
                grid[rand][y].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
                
            if not np.random.randint(prob) and br - top <= 2:
                grid[rand][y+1].make_barrier()
                grid[rand][y+1].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
                
            for y in range(br+1, bottom):
                grid[rand][y].make_barrier()
                grid[rand][y].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
        else:
            for x in range(left, br):
                grid[x][rand].make_barrier()
                grid[x][rand].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
                
            if not np.random.randint(prob) and br - left <= 2:
                grid[x+1][rand].make_barrier()
                grid[x+1][rand].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
                
            for x in range(br+1, right):
                grid[x][rand].make_barrier()
                grid[x][rand].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
        
        if vertical:
            recursive_maze(draw, width, grid, start, end, rand+1, right, top, br, win)
            recursive_maze(draw, width, grid, start, end, left, rand, top, br, win)
            recursive_maze(draw, width, grid, start, end, rand+1, right, br+1, bottom, win)
            recursive_maze(draw, width, grid, start, end, left, rand, br+1, bottom, win)
        else:
            recursive_maze(draw, width, grid, start, end, left, br, top, rand, win)
            recursive_maze(draw, width, grid, start, end, left, br, rand+1, bottom, win)
            recursive_maze(draw, width, grid, start, end, br+1, right, top, rand, win)
            recursive_maze(draw, width, grid, start, end, br+1, right, rand+1, bottom, win)

def recursive_div(draw, width, grid, start, end, left, right, top, bottom, win, break_at = 0):
    for i in range(right):
        grid[0][i].make_barrier()
        grid[bottom-1][right-1-i].make_barrier()
        draw()
    for i in range(bottom-1):
        grid[i][0].make_barrier()
        grid[bottom-1-i][right-1].make_barrier()
        draw()
    recursive_maze(draw, width, grid, start, end, left+1, right-1, top+1, bottom-1, win)

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return np.array(grid)

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (0, i*gap), (rows*gap, i*gap))
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (i*gap, 0), (i*gap, rows*gap))

def get_clicked_pos(pos, rows, width):
    gap = width//rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def draw(win, grid, rows, width, algorithms, mazes, options, output, menu = True):
    win.fill(BG_COLOR)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    if menu:
        n = 17
        delta = 700
        ht = 900
        width = ht
        w = 1600
        font = pygame.font.SysFont('comicsans', 35)
        text = font.render("Algorithms", 1, WHITE)
        top = 0
        end = ht//13
        win.blit(text, (width+delta//6, (end-top)/2.5))
        for algorithm in algorithms:
            algorithm.draw(win, BLACK)
        
        text = font.render("Mazes", 1, WHITE)
        but_height = ht//15
        top += (4*but_height)
        end += (1.9*(3*but_height//2)) + but_height + ht//12
        win.blit(text, (width+delta//6, ((end-top)/2) + top))
        for maze in mazes:
            maze.draw(win, BLACK)
            
        end += (1.3*(3*but_height//2)) + ht//6
        top += (5*but_height//2)
        
        text = font.render("Options", 1, WHITE)
        win.blit(text, (width+delta//6, ((end-top)/2) + top))
        for option in options:
            option.draw(win, BLACK)
        output.draw(win, BLACK)
    pygame.display.update()

def main(win, width):
    ROWS = 50
    w, ht = pygame.display.get_surface().get_size()
    width = ht
    grid = make_grid(ROWS, width)
    delta = w - width
    
    top_start = ht/13
    but_height = ht//15
    but_width = delta//4
    
    algorithms = [
        button(width+delta//5, top_start, but_width-but_height, but_height, "A*"),
    ]
    top_start = top_start + (1.9*(3*but_height//2)) + but_height + ht//12
    but_height = ht//15
    but_width = delta//4+ delta//10
    mazes = [
        button(width+delta//5 +(5*(but_width-80)//4), top_start, but_width-but_height, but_height, 'Recursive Division'),
    ]
    top_start = top_start + (1.3*(3*but_height//2)) + ht//10
    but_height = ht//15
    but_width =  delta//10
    options = [
        button(width+delta//5, top_start, but_width-but_height+20, but_height, "Clear"),
        button(width+delta//5-20 + delta//5 + (4*(but_width+50)//3), top_start, 0, but_height, "-"),
        button(width+delta//5 + delta//5 + (4*(but_width+50)//3)+(4*(but_width-30)//3), top_start,0, but_height, "+"),
    ]
    sc_start = ht-240
    sc_height = 230
    sc_width = delta-delta//4
    output = screen(width+delta//8, sc_start, sc_width, sc_height, "Choose an Algorithm")
    output.set_label1(f"Number of rows: {ROWS}")
    output.set_text1("1. Pick starting node")
    output.set_text2("2. Pick ending node")
    output.set_text3("3. Choose an algorithm")
    
    start = None
    end = None
    
    run = True
    started = False
    visited = []
    weighted = []
    path = False
    while run:
        if len(visited):
            visit_animation(visited)
            
        if path:
            path_animation(path)
            
        draw(win, grid, ROWS, width, algorithms, mazes, options, output)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if started:
                continue
                
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos, ROWS, width)
                if row>= 0 and row<ROWS and col < ROWS and col >= 0:
                    node = grid[row][col]
                    if node in visited:
                        visited.remove(node)
                    if node in weighted:
                        weighted.remove(node)
                    if path:
                        if node in path:
                            path.remove(node)
                    if not start and node != end:
                        if node in visited:
                            visited.remove(node)
                        start = node
                        start.make_start()
                    elif not end and node != start:
                        end = node
                        end.make_end()
                    elif node != end and node != start:
                        node.make_barrier()
                        
                elif algorithms[0].is_hover(pos):
                    output.draw(win, (0, 0, 0))
                    if len(weighted):
                        for node in weighted:
                            node.make_weight()
                    if start and end:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                                if not node.is_neutral() and node != start and node != end and not node.is_barrier() and not node.is_weight():
                                    node.reset()
                        visited = []
                        path = []
                        output.set_text1("......")
                        output.set_text2("")
                        output.set_text3("")
                        output.draw(win, BLACK)
                        pygame.display.update()
                        visited, path = A_star(lambda: draw(win, grid, ROWS, width, algorithms, mazes, options, output), grid, start, end, output, win, width)
                        if not path:
                            output.set_text1("Path not available")
                               
                elif mazes[0].is_hover(pos):
                    output.set_text1("......")
                    output.set_text2("")
                    output.set_text3("")
                    output.draw(win, BLACK)
                    pygame.display.update()
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
#                             if node.is_barrier() or node.is_start() or node.is_end():
                            node.reset()
                    recursive_div(lambda: draw(win, grid, ROWS, width, algorithms, mazes, options, output),width, grid, start, end, 0, ROWS, 0, ROWS, win)
                    output.set_text1("1. Pick starting node")
                    output.set_text2("2. Pick ending node")
                    output.set_text3("3. Choose an algorithm")
                                
                elif options[0].is_hover(pos):
                    output.set_text1("1. Pick starting node")
                    output.set_text2("2. Pick ending node")
                    output.set_text3("3. Choose an algorithm")
                    output.draw(win, BLACK)
                    pygame.display.update()
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                            
                elif options[1].is_hover(pos):
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                    if ROWS>5:
                        ROWS-=1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Number of rows: {ROWS}")
                        
                elif options[2].is_hover(pos):
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                    if ROWS<100:
                        ROWS+=1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Number of rows: {ROWS}")
                        
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos, ROWS, width)
                if row>= 0 and row<ROWS and col < ROWS and col >= 0:
                    node = grid[row][col]
                    if path:
                        if node in path:
                            path.remove(node)
                    if node in visited:
                        visited.remove(node)
                    if node in weighted:
                        weighted.remove(node)
                    node.reset()
                    if node == start:
                        start = None
                    elif node == end:
                        end = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.quit() 

pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH+700, WIDTH))

pygame.display.set_caption("Path Finder")
main(WIN, WIDTH)
