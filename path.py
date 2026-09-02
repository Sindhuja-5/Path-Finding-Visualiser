import asyncio
import heapq
import random
import pygame


# ============================================================
# CONFIGURATION
# ============================================================

GRID_WIDTH = 700
PANEL_WIDTH = 600
WINDOW_WIDTH = GRID_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = 700

MIN_ROWS = 5
MAX_ROWS = 50
START_ROWS = 25

GRID_PADDING = 25


# ============================================================
# COLORS
# ============================================================

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


# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):
    """Use a common font with a safe fallback."""
    return pygame.font.SysFont(
        "comicsans",
        size,
        bold=bold,
    )


# ============================================================
# GRID METRICS
# ============================================================

def get_grid_metrics(rows, width):
    """
    Calculate grid cell size and centered offset.

    The grid is kept inside the main 800x800 area with
    padding on all four sides.
    """

    available_width = width - (2 * GRID_PADDING)

    gap = max(
        1,
        available_width // rows,
    )

    grid_size = gap * rows

    offset = (width - grid_size) // 2

    return gap, offset


# ============================================================
# NODE
# ============================================================

class Node:
    def __init__(
        self,
        row,
        col,
        width,
        total_rows,
        offset,
    ):
        self.row = row
        self.col = col

        self.x = offset + col * width
        self.y = offset + row * width

        self.width = width
        self.total_rows = total_rows

        self.color = WHITE
        self.neighbors = []

        self.dec_animation = False
        self.weight = False

    def get_pos(self):
        return self.row, self.col

    def is_visited(self):
        return self.color in (
            VISIT1,
            VISIT2,
            VISIT3,
        )

    def is_open(self):
        return self.color in (
            OPEN,
            OPEN1,
        )

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
        self.neighbors = []
        self.dec_animation = False

    def make_visit(self):
        self.color = (
            VISIT3
            if self.is_weight()
            else VISIT2
        )

    def make_open(self):
        self.color = (
            OPEN1
            if self.is_weight()
            else OPEN
        )

    def make_barrier(self):
        if not self.is_start() and not self.is_end():
            self.color = BLACK
            self.weight = False

    def make_weight(self):
        if (
            not self.is_start()
            and not self.is_end()
            and not self.is_barrier()
        ):
            self.color = BROWN
            self.weight = True

    def make_end(self):
        self.color = END
        self.weight = False

    def make_start(self):
        self.color = START
        self.weight = False

    def make_path(self):
        if not self.is_start():
            self.color = (
                PATH3
                if self.is_weight()
                else PATH1
            )

    def looking_at(self):
        if not self.is_start() and not self.is_end():
            self.color = LOOK

    def draw(self, win):
        pygame.draw.rect(
            win,
            self.color,
            (
                self.x,
                self.y,
                self.width,
                self.width,
            ),
        )

    def update_neighbors(self, grid, diag=False):
        self.neighbors = []

        r = self.row
        c = self.col
        rows = self.total_rows

        # Down
        if (
            r < rows - 1
            and not grid[r + 1][c].is_barrier()
        ):
            self.neighbors.append(
                grid[r + 1][c]
            )

        # Up
        if (
            r > 0
            and not grid[r - 1][c].is_barrier()
        ):
            self.neighbors.append(
                grid[r - 1][c]
            )

        # Right
        if (
            c < rows - 1
            and not grid[r][c + 1].is_barrier()
        ):
            self.neighbors.append(
                grid[r][c + 1]
            )

        # Left
        if (
            c > 0
            and not grid[r][c - 1].is_barrier()
        ):
            self.neighbors.append(
                grid[r][c - 1]
            )

        # Optional diagonal movement
        if diag:
            diagonal_positions = (
                (r + 1, c + 1),
                (r - 1, c + 1),
                (r - 1, c - 1),
                (r + 1, c - 1),
            )

            for nr, nc in diagonal_positions:
                if (
                    0 <= nr < rows
                    and 0 <= nc < rows
                    and not grid[nr][nc].is_barrier()
                ):
                    self.neighbors.append(
                        grid[nr][nc]
                    )

    def __lt__(self, other):
        return False


# ============================================================
# BUTTON
# ============================================================

class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
    ):
        self.color = BUTTON_COLOR
        self.x = int(x)
        self.y = int(y)
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        self.text = text

    def _get_text_font(self):
        # Automatically shrink long labels so they never overflow.
        max_width = max(
            10,
            self.width - 18,
        )

        size = min(
            24,
            max(13, self.height - 10),
        )

        while size > 11:
            font = get_font(size)
            text = font.render(
                self.text,
                True,
                BLACK,
            )

            if (
                text.get_width() <= max_width
                and text.get_height()
                <= self.height - 6
            ):
                return font, text

            size -= 1

        font = get_font(11)

        return (
            font,
            font.render(
                self.text,
                True,
                BLACK,
            ),
        )

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(
                win,
                outline,
                (
                    self.x - 2,
                    self.y - 2,
                    self.width + 4,
                    self.height + 4,
                ),
                0,
                border_radius=self.height // 2 + 2,
            )

        pygame.draw.rect(
            win,
            self.color,
            (
                self.x,
                self.y,
                self.width,
                self.height,
            ),
            0,
            border_radius=self.height // 2,
        )

        if self.text:
            font, text = self._get_text_font()

            text_rect = text.get_rect(
                center=(
                    self.x + self.width // 2,
                    self.y + self.height // 2,
                )
            )

            win.blit(
                text,
                text_rect,
            )

    def is_hover(self, pos):
        return (
            self.x <= pos[0]
            <= self.x + self.width
            and self.y <= pos[1]
            <= self.y + self.height
        )


# ============================================================
# OUTPUT / INFORMATION PANEL
# ============================================================

class Screen:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
    ):
        self.color = SCREEN_COLOR

        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

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

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(
                win,
                outline,
                (
                    self.x - 2,
                    self.y - 2,
                    self.width + 4,
                    self.height + 4,
                ),
                0,
                border_radius=8,
            )

        pygame.draw.rect(
            win,
            self.color,
            (
                self.x,
                self.y,
                self.width,
                self.height,
            ),
            0,
            border_radius=8,
        )

        # Header / label
        if self.label1:
            font = get_font(
                16,
                bold=True,
            )

            label = font.render(
                self.label1,
                True,
                BLACK,
            )

            win.blit(
                label,
                (
                    self.x + 12,
                    self.y + 10,
                ),
            )

        # Three lines of content
        lines = [
            self.text1,
            self.text2,
            self.text3,
        ]

        start_y = self.y + 44

        for index, value in enumerate(lines):
            if not value:
                continue

            font_size = (
                18
                if self.width >= 400
                else 16
            )

            font = get_font(font_size)

            text = font.render(
                value,
                True,
                BLACK,
            )

            # Scale down if a result line is too long.
            while (
                text.get_width()
                > self.width - 24
                and font_size > 11
            ):
                font_size -= 1

                font = get_font(font_size)

                text = font.render(
                    value,
                    True,
                    BLACK,
                )

            rect = text.get_rect(
                center=(
                    self.x + self.width // 2,
                    start_y + index * 34,
                )
            )

            win.blit(
                text,
                rect,
            )

    def is_hover(self, pos):
        return (
            self.x <= pos[0]
            <= self.x + self.width
            and self.y <= pos[1]
            <= self.y + self.height
        )


# ============================================================
# HEURISTIC
# ============================================================

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


# ============================================================
# ANIMATIONS
# ============================================================

def visit_animation(visited):
    for node in visited[:]:
        if (
            node.color == VISIT1
            or node.color == VISIT3
        ):
            visited.remove(node)
            continue

        r, g, b = node.color

        if g < 255:
            g += 1

        node.color = (
            r,
            g,
            b,
        )


def path_animation(path):
    for node in path:
        if node.is_start():
            continue

        r, g, b = node.color

        if node.dec_animation:
            g -= 1

            if g <= PATH1[1]:
                node.dec_animation = False

        else:
            g += 1

            if g >= PATH2[1]:
                node.dec_animation = True

        node.color = (
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b)),
        )


# ============================================================
# PATH RECONSTRUCTION
# ============================================================

def reconstruct_path(
    came_from,
    start,
    current,
):
    path = []
    cost = 0

    while current in came_from:
        current = came_from[current]

        if current != start:
            path.insert(0, current)

            # Cost is based on the node entered.
            cost += (
                5
                if current.is_weight()
                else 1
            )

    return path, cost


# ============================================================
# EVENT PROCESSING
# ============================================================

def process_quit_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    return True


# ============================================================
# COMMON SEARCH SETUP
# ============================================================

def prepare_search(grid):
    for row in grid:
        for node in row:
            node.neighbors = []
            node.dec_animation = False

            # Preserve start/end/barrier/weight states.
            if (
                node.is_start()
                or node.is_end()
                or node.is_barrier()
                or node.is_weight()
            ):
                continue

            node.color = WHITE

    for row in grid:
        for node in row:
            node.update_neighbors(grid)

    return


# ============================================================
# A* ALGORITHM
# ============================================================

async def A_star(
    draw,
    grid,
    start,
    end,
    output,
    win,
    width,
):
    count = 0
    visited = []

    open_heap = []

    heapq.heappush(
        open_heap,
        (
            h(
                start.get_pos(),
                end.get_pos(),
            ),
            count,
            start,
        ),
    )

    came_from = {}

    g_score = {
        node: float("inf")
        for row in grid
        for node in row
    }

    g_score[start] = 0

    open_set_hash = {start}

    while open_heap:
        if not process_quit_events():
            return visited, False

        _, _, current = heapq.heappop(
            open_heap
        )

        if current not in open_set_hash:
            continue

        open_set_hash.remove(current)

        if current == end:
            path, cost = reconstruct_path(
                came_from,
                start,
                end,
            )

            for node in path:
                node.make_path()

            start.make_start()

            output.set_text1(
                f"Path Length: {cost}"
            )

            output.set_text2(
                f"#Visited nodes: {len(visited)}"
            )

            if len(visited):
                output.set_text3(
                    f"Efficiency: "
                    f"{round(cost / len(visited), 3)}"
                )
            else:
                output.set_text3(
                    "Efficiency: N/A"
                )

            return visited, path

        if current != start:
            visited.append(current)
            current.make_visit()

        for neighbor in current.neighbors:
            move_cost = (
                5
                if neighbor.is_weight()
                else 1
            )

            tentative_g = (
                g_score[current]
                + move_cost
            )

            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                count += 1

                f_score = (
                    tentative_g
                    + h(
                        neighbor.get_pos(),
                        end.get_pos(),
                    )
                )

                heapq.heappush(
                    open_heap,
                    (
                        f_score,
                        count,
                        neighbor,
                    ),
                )

                open_set_hash.add(neighbor)

                if neighbor != end:
                    neighbor.make_open()

        visit_animation(visited)

        for row in grid:
            for node in row:
                node.draw(win)

        draw_grid(
            win,
            len(grid),
            width,
        )

        pygame.display.update()

        # Required so the browser remains responsive when using Pygbag.
        await asyncio.sleep(0)

    return visited, False


# ============================================================
# DIJKSTRA ALGORITHM
# ============================================================

async def Dijkstra(
    draw,
    grid,
    start,
    end,
    output,
    win,
    width,
):
    """
    Dijkstra's shortest-path algorithm.

    Unlike A*, Dijkstra does not use a heuristic.
    It always expands the currently known lowest-cost node.
    """

    count = 0
    visited = []

    open_heap = []

    heapq.heappush(
        open_heap,
        (
            0,
            count,
            start,
        ),
    )

    came_from = {}

    distance = {
        node: float("inf")
        for row in grid
        for node in row
    }

    distance[start] = 0

    open_set_hash = {start}

    while open_heap:
        if not process_quit_events():
            return visited, False

        current_distance, _, current = (
            heapq.heappop(open_heap)
        )

        if current not in open_set_hash:
            continue

        open_set_hash.remove(current)

        # Ignore stale heap entries.
        if current_distance > distance[current]:
            continue

        if current == end:
            path, cost = reconstruct_path(
                came_from,
                start,
                end,
            )

            for node in path:
                node.make_path()

            start.make_start()

            output.set_text1(
                f"Path Length: {cost}"
            )

            output.set_text2(
                f"#Visited nodes: {len(visited)}"
            )

            if len(visited):
                output.set_text3(
                    f"Efficiency: "
                    f"{round(cost / len(visited), 3)}"
                )
            else:
                output.set_text3(
                    "Efficiency: N/A"
                )

            return visited, path

        if current != start:
            visited.append(current)
            current.make_visit()

        for neighbor in current.neighbors:
            move_cost = (
                5
                if neighbor.is_weight()
                else 1
            )

            new_distance = (
                distance[current]
                + move_cost
            )

            if new_distance < distance[neighbor]:
                came_from[neighbor] = current
                distance[neighbor] = new_distance

                count += 1

                heapq.heappush(
                    open_heap,
                    (
                        new_distance,
                        count,
                        neighbor,
                    ),
                )

                open_set_hash.add(neighbor)

                if neighbor != end:
                    neighbor.make_open()

        visit_animation(visited)

        for row in grid:
            for node in row:
                node.draw(win)

        draw_grid(
            win,
            len(grid),
            width,
        )

        pygame.display.update()

        await asyncio.sleep(0)

    return visited, False


# ============================================================
# MAZE HELPERS
# ============================================================

def make_black(grid, win):
    for row in grid:
        for node in row:
            node.make_barrier()
            node.draw(win)

    pygame.display.update()

def get_wall_gaps(start, end):
    length = end - start

    if length <= 8:
        num_gaps = 5
    elif length <= 15:
        num_gaps = 6
    else:
        num_gaps = 4

    num_gaps = min(
        num_gaps,
        length,
    )

    return set(
        random.sample(
            range(start, end),
            num_gaps,
        )
    )

async def recursive_maze(
    draw,
    grid,
    left,
    right,
    top,
    bottom,
    win,
    width,
):
    """
    Recursive Division maze generation.

    The region uses [left, right) x [top, bottom)
    coordinates.
    """

    if (
        right - left < 2
        or bottom - top < 2
    ):
        return

    # Choose orientation based on the shape of the region.
    if right - left != bottom - top:
        vertical = (
            right - left
            > bottom - top
        )
    else:
        vertical = random.choice(
            [True, False]
        )

    if vertical:

        possible_walls = list(
            range(
                left + 1,
                right - 1,
            )
        )

        if not possible_walls:
            return

        wall_x = random.choice(
            possible_walls
        )

        gap_y = get_wall_gaps(
            top,
            bottom,
        )

        # Build the entire vertical wall first.
        for y in range(top, bottom):

            if y in gap_y:
                continue

            node = grid[y][wall_x]

            if (
                not node.is_start()
                and not node.is_end()
            ):
                node.make_barrier()

        # Draw only once after the complete wall is created.
        for row in grid:
            for n in row:
                n.draw(win)

        draw_grid(
            win,
            len(grid),
            width,
        )

        pygame.display.update()

        await asyncio.sleep(0)

    else:

        possible_walls = list(
            range(
                top + 1,
                bottom - 1,
            )
        )

        if not possible_walls:
            return

        wall_y = random.choice(
            possible_walls
        )

        gap_x = get_wall_gaps(
            left,
            right,
        )

        # Build the entire horizontal wall first.
        for x in range(left, right):

            if x in gap_x:
                continue

            node = grid[wall_y][x]

            if (
                not node.is_start()
                and not node.is_end()
            ):
                node.make_barrier()

        # Draw only once after the complete wall is created.
        for row in grid:
            for n in row:
                n.draw(win)

        draw_grid(
            win,
            len(grid),
            width,
        )

        pygame.display.update()

        await asyncio.sleep(0)

    # Recursively divide the two resulting regions.
    if vertical:

        await recursive_maze(
            draw,
            grid,
            left,
            wall_x,
            top,
            bottom,
            win,
            width,
        )

        await recursive_maze(
            draw,
            grid,
            wall_x + 1,
            right,
            top,
            bottom,
            win,
            width,
        )

    else:

        await recursive_maze(
            draw,
            grid,
            left,
            right,
            top,
            wall_y,
            win,
            width,
        )

        await recursive_maze(
            draw,
            grid,
            left,
            right,
            wall_y + 1,
            bottom,
            win,
            width,
        )


async def recursive_div(
    draw,
    width,
    grid,
    start,
    end,
    left,
    right,
    top,
    bottom,
    win,
):
    """
    Create an outer border and then recursively divide
    the interior.
    """

    rows = len(grid)

    # Outer border.
    for i in range(rows):
        grid[0][i].make_barrier()
        grid[rows - 1][i].make_barrier()
        grid[i][0].make_barrier()
        grid[i][rows - 1].make_barrier()

    # Keep the maze visually updated while creating the border.
    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(
        win,
        rows,
        width,
    )

    pygame.display.update()

    await asyncio.sleep(0)

    await recursive_maze(
        draw,
        grid,
        left + 1,
        right - 1,
        top + 1,
        bottom - 1,
        win,
        width,
    )


# ============================================================
# GRID
# ============================================================

def make_grid(rows, width):
    grid = []

    gap, offset = get_grid_metrics(
        rows,
        width,
    )

    for row in range(rows):
        grid.append([])

        for col in range(rows):
            grid[row].append(
                Node(
                    row,
                    col,
                    gap,
                    rows,
                    offset,
                )
            )

    return grid


# ============================================================
# DRAW GRID
# ============================================================

def draw_grid(win, rows, width):
    gap, offset = get_grid_metrics(
        rows,
        width,
    )

    grid_size = gap * rows

    for i in range(rows + 1):
        pygame.draw.line(
            win,
            GREY,
            (
                offset,
                offset + i * gap,
            ),
            (
                offset + grid_size,
                offset + i * gap,
            ),
        )

    for i in range(rows + 1):
        pygame.draw.line(
            win,
            GREY,
            (
                offset + i * gap,
                offset,
            ),
            (
                offset + i * gap,
                offset + grid_size,
            ),
        )


# ============================================================
# CLICK POSITION
# ============================================================

def get_clicked_pos(pos, rows, width):
    gap, offset = get_grid_metrics(
        rows,
        width,
    )

    x, y = pos

    row = (
        y - offset
    ) // gap

    col = (
        x - offset
    ) // gap

    return row, col


# ============================================================
# UI HELPERS
# ============================================================

def draw_section_title(
    win,
    text,
    x,
    y,
):
    font = get_font(
        22,
        bold=True,
    )

    rendered = font.render(
        text,
        True,
        WHITE,
    )

    rect = rendered.get_rect(
        center=(x, y)
    )

    win.blit(
        rendered,
        rect,
    )

def draw_legend(win, x, y, width):
    item_font = get_font(14)

    legend_items = [
        ("Start", START),
        ("End", END),
        ("Barrier", BLACK),
        ("Weighted", BROWN),
        ("Visited", VISIT2),
        ("Visited Weighted", VISIT3),
        ("Open", OPEN),
        ("Open Weighted", OPEN1),
        ("Path", PATH1),
        ("Weighted Path", PATH3),
    ]

   # Split into three columns
    col1_items = legend_items[:4]
    col2_items = legend_items[4:7]
    col3_items = legend_items[7:]

    item_height = 25
    box_size = 16

    start_y = y + 4

    # Column positions
    col1_x = x + 10
    col2_x = x + width // 3 + 5
    col3_x = x + (2 * width) // 3 + 5

    for index, (label, color) in enumerate(col1_items):
        item_y = start_y + index * item_height
        pygame.draw.rect(win, color, (col1_x, item_y, box_size, box_size))
        pygame.draw.rect(win, WHITE, (col1_x, item_y, box_size, box_size), 1)
        text = item_font.render(label, True, WHITE)
        win.blit(text, (col1_x + 22, item_y - 1))

    for index, (label, color) in enumerate(col2_items):
        item_y = start_y + index * item_height
        pygame.draw.rect(win, color, (col2_x, item_y, box_size, box_size))
        pygame.draw.rect(win, WHITE, (col2_x, item_y, box_size, box_size), 1)
        text = item_font.render(label, True, WHITE)
        win.blit(text, (col2_x + 22, item_y - 1))

    for index, (label, color) in enumerate(col3_items):
        item_y = start_y + index * item_height
        pygame.draw.rect(win, color, (col3_x, item_y, box_size, box_size))
        pygame.draw.rect(win, WHITE, (col3_x, item_y, box_size, box_size), 1)
        text = item_font.render(label, True, WHITE)
        win.blit(text, (col3_x + 22, item_y - 1))

def make_ui_buttons(
    width,
    panel_width,
    height,
):
    panel_x = width

    # Small side margin so controls remain fully visible.
    margin_x = 10

    usable_width = (
        panel_width
        - (2 * margin_x)
    )

    button_height = 42
    small_gap = 10

    # Same width as A* and Dijkstra.
    standard_button_width = 180

    # ---------------- Options ----------------
    # Maze-related controls are kept together.

    options_y = 55

    # Build Maze
    maze_button = Button(
        panel_x + margin_x,
        options_y + 32,
        standard_button_width,
        button_height,
        "Build Maze",
    )

    control_width = 45

    rows_display_width = standard_button_width

    rows_y = (
        options_y
        + 32
        + button_height
        + 12
    )

    options = [

        # 0 - Decrease rows
        Button(
            panel_x + margin_x,
            rows_y,
            control_width,
            button_height,
            "-",
        ),

        # 1 - Rows display
        Button(
            panel_x
            + margin_x
            + control_width
            + small_gap,
            rows_y,
            rows_display_width,
            button_height,
            f"Rows: {START_ROWS}",
        ),

        # 2 - Increase rows
        Button(
            panel_x
            + margin_x
            + control_width
            + small_gap
            + rows_display_width
            + small_gap,
            rows_y,
            control_width,
            button_height,
            "+",
        ),

        # 3 - Weight
        Button(
            panel_x + margin_x,
            rows_y
            + button_height
            + 12,
            standard_button_width,
            button_height,
            "Weight",
        ),

        # 4 - Clear
        Button(
            panel_x + margin_x,
            rows_y
            + (button_height + 12) * 2,
            standard_button_width,
            button_height,
            "Clear",
        ),
    ]

    # ---------------- Algorithms ----------------

    algorithm_y = (
        options[4].y
        + options[4].height
        + 38
    )

    algorithm_gap = 10
    algorithm_width = 180

    algorithms = [

        Button(
            panel_x + margin_x,
            algorithm_y + 32,
            algorithm_width,
            button_height,
            "A*",
        ),

        Button(
            panel_x
            + margin_x
            + algorithm_width
            + algorithm_gap,
            algorithm_y + 32,
            algorithm_width,
            button_height,
            "Dijkstra",
        ),
    ]

    # ---------------- Output ----------------

    output_y = height - 155
    output_height = 135

    output = Screen(
        panel_x + margin_x,
        output_y,
        usable_width,
        output_height,
        "Choose an Algorithm",
    )

    return (
        maze_button,
        algorithms,
        options,
        output,
    )


# ============================================================
# DRAW EVERYTHING
# ============================================================

def draw(
    win,
    grid,
    rows,
    width,
    maze_button,
    algorithms,
    options,
    output,
    weight_mode
):
    win.fill(BG_COLOR)

    # ---------------- Grid ----------------

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(
        win,
        rows,
        width,
    )

    # ---------------- Side Panel ----------------

    panel_x = width
    panel_width = (
        win.get_width()
        - width
    )

    # ---------------- Options ----------------

    options_title_y = (
        maze_button.y - 18
    )

    draw_section_title(
        win,
        "Options",
        panel_x + panel_width // 2,
        options_title_y,
    )

    maze_button.draw(
        win,
        BLACK,
    )

    for index, option in enumerate(options):

        if index == 3 and weight_mode:
            option.color = BROWN
        else:
            option.color = BUTTON_COLOR

        option.draw(
            win,
            BLACK,
        )

    # ---------------- Algorithms ----------------

    algorithm_title_y = (
        algorithms[0].y - 18
    )

    draw_section_title(
        win,
        "Algorithms",
        panel_x + panel_width // 2,
        algorithm_title_y,
    )

    for algorithm in algorithms:
        algorithm.draw(
            win,
            BLACK,
        )

    # ---------------- Legend ----------------

    legend_y = algorithms[0].y + 75

    draw_legend(
        win,
        panel_x,
        legend_y,
        panel_width,
    )

    # ---------------- Results ----------------

    output.draw(
        win,
        BLACK,
    )

    pygame.display.update()


# ============================================================
# STATE RESET
# ============================================================

def reset_search_state():
    return None, None, [], [], False


def clear_grid(grid):
    for row in grid:
        for node in row:
            node.reset()


# ============================================================
# MAIN APPLICATION
# ============================================================

async def main(win, width):
    rows = START_ROWS

    grid = make_grid(
        rows,
        width,
    )

    (
        maze_button,
        algorithms,
        options,
        output,
    ) = make_ui_buttons(
        width,
        win.get_width() - width,
        win.get_height(),
    )

    output.set_label1(
        f"Number of rows: {rows}"
    )

    output.set_text1(
        "1. Build Maze"
    )

    output.set_text2(
        "2. Pick starting node"
    )

    output.set_text3(
        "3. Pick ending node"
    )

    start = None
    end = None

    visited = []
    path = []
    weighted = []

    weight_mode = False

    running = True
    started = False

    while running:

        if not process_quit_events():
            break

        # ---------------- Animations ----------------

        if visited:
            visit_animation(visited)

        if path:
            path_animation(path)

        # ---------------- Draw ----------------

        draw(
            win,
            grid,
            rows,
            width,
            maze_button,
            algorithms,
            options,
            output,
            weight_mode
        )

        # ---------------- Events ----------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                continue

            # Do not accept grid/menu clicks while an algorithm is running.
            if started:
                continue

            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = event.pos

            # ====================================================
            # LEFT CLICK
            # ====================================================

            if event.button == 1:

                # ---------------- Grid ----------------

                if (
                    0 <= pos[0] < width
                    and 0 <= pos[1] < width
                ):

                    row, col = get_clicked_pos(
                        pos,
                        rows,
                        width,
                    )

                    if (
                        0 <= row < rows
                        and 0 <= col < rows
                    ):

                        node = grid[row][col]

                        if node in visited:
                            visited.remove(node)

                        if node in path:
                            path.remove(node)

                        # ---------------- Weight Mode ----------------

                        if weight_mode:

                            if (
                                node != start
                                and node != end
                                and not node.is_barrier()
                            ):

                                if node.is_weight():
                                    node.weight = False
                                    node.color = WHITE

                                    if node in weighted:
                                        weighted.remove(node)

                                else:
                                    node.make_weight()

                                    if node not in weighted:
                                        weighted.append(node)

                        # ---------------- Normal Mode ----------------

                        else:

                            # Pick start
                            if (
                                start is None
                                and node != end
                            ):
                                start = node
                                start.make_start()

                            # Pick end
                            elif (
                                end is None
                                and node != start
                            ):
                                end = node
                                end.make_end()

                            # Make barrier
                            elif (
                                node != start
                                and node != end
                            ):
                                node.make_barrier()

                # ---------------- Build Maze ----------------

                elif maze_button.is_hover(pos):

                    started = True
                    weight_mode = False

                    start = None
                    end = None

                    visited = []
                    path = []
                    weighted = []

                    clear_grid(grid)

                    output.set_text1(
                        "Generating maze..."
                    )

                    output.set_text2("")
                    output.set_text3("")

                    output.draw(
                        win,
                        BLACK,
                    )

                    pygame.display.update()

                    await recursive_div(
                        lambda: draw(
                            win,
                            grid,
                            rows,
                            width,
                            maze_button,
                            algorithms,
                            options,
                            output,
                            weight_mode
                        ),
                        width,
                        grid,
                        start,
                        end,
                        0,
                        rows,
                        0,
                        rows,
                        win,
                    )

                    output.set_label1(
                        f"Number of rows: {rows}"
                    )

                    output.set_text1(
                        "1. Build Maze"
                    )

                    output.set_text2(
                        "2. Pick starting node"
                    )

                    output.set_text3(
                        "3. Pick ending node"
                    )

                    started = False

                # ---------------- A* ----------------

                elif algorithms[0].is_hover(pos):

                    if start and end:

                        started = True

                        prepare_search(grid)

                        visited = []
                        path = []

                        output.set_text1(
                            "Running A*..."
                        )

                        output.set_text2("")
                        output.set_text3("")

                        draw(
                            win,
                            grid,
                            rows,
                            width,
                            maze_button,
                            algorithms,
                            options,
                            output,
                            weight_mode
                        )

                        visited, path = await A_star(
                            lambda: draw(
                                win,
                                grid,
                                rows,
                                width,
                                maze_button,
                                algorithms,
                                options,
                                output,
                                weight_mode
                            ),
                            grid,
                            start,
                            end,
                            output,
                            win,
                            width,
                        )

                        if not path:
                            output.set_text1(
                                "Path not available"
                            )

                        started = False

                    else:

                        output.set_text1(
                            "Select a start and end node first"
                        )

                # ---------------- Dijkstra ----------------

                elif algorithms[1].is_hover(pos):

                    if start and end:

                        started = True

                        prepare_search(grid)

                        visited = []
                        path = []

                        output.set_text1(
                            "Running Dijkstra..."
                        )

                        output.set_text2("")
                        output.set_text3("")

                        draw(
                            win,
                            grid,
                            rows,
                            width,
                            maze_button,
                            algorithms,
                            options,
                            output,
                            weight_mode
                        )

                        visited, path = await Dijkstra(
                            lambda: draw(
                                win,
                                grid,
                                rows,
                                width,
                                maze_button,
                                algorithms,
                                options,
                                output,
                                weight_mode
                            ),
                            grid,
                            start,
                            end,
                            output,
                            win,
                            width,
                        )

                        if not path:
                            output.set_text1(
                                "Path not available"
                            )

                        started = False

                    else:

                        output.set_text1(
                            "Select a start and end node first"
                        )

                # ---------------- Weight Mode ----------------

                elif options[3].is_hover(pos):

                    weight_mode = not weight_mode

                    if weight_mode:
                        output.set_text1(
                            "Weight mode enabled"
                        )
                        output.set_text2(
                            "Click cells to add weights"
                        )
                        output.set_text3(
                            "Click Weight again to exit"
                        )
                    else:
                        output.set_text1(
                            "Weight mode disabled"
                        )
                        output.set_text2("")
                        output.set_text3("")

                # ---------------- Clear ----------------

                elif options[4].is_hover(pos):

                    start = None
                    end = None

                    visited = []
                    path = []
                    weighted = []

                    weight_mode = False

                    clear_grid(grid)

                    output.set_label1(
                        f"Number of rows: {rows}"
                    )

                    output.set_text1(
                        "1. Build Maze"
                    )

                    output.set_text2(
                        "2. Pick starting node"
                    )

                    output.set_text3(
                        "3. Pick ending node"
                    )

                # ---------------- Decrease rows ----------------

                elif options[0].is_hover(pos):

                    if rows > MIN_ROWS:

                        rows -= 1

                        start = None
                        end = None

                        weight_mode = False

                        visited = []
                        path = []
                        weighted = []

                        grid = make_grid(
                            rows,
                            width,
                        )

                    output.set_label1(
                        f"Number of rows: {rows}"
                    )

                    output.set_text1(
                        "1. Build Maze"
                    )

                    output.set_text2(
                        "2. Pick starting node"
                    )

                    output.set_text3(
                        "3. Pick ending node"
                    )

                    options[1].text = (
                        f"Rows: {rows}"
                    )

                # ---------------- Increase rows ----------------

                elif options[2].is_hover(pos):

                    if rows < MAX_ROWS:

                        rows += 1

                        start = None
                        end = None

                        weight_mode = False

                        visited = []
                        path = []
                        weighted = []

                        grid = make_grid(
                            rows,
                            width,
                        )

                    output.set_label1(
                        f"Number of rows: {rows}"
                    )

                    output.set_text1(
                        "1. Build Maze"
                    )

                    output.set_text2(
                        "2. Pick starting node"
                    )

                    output.set_text3(
                        "3. Pick ending node"
                    )

                    options[1].text = (
                        f"Rows: {rows}"
                    )

        # Required for browser/Pygbag responsiveness.
        await asyncio.sleep(0)

    pygame.quit()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

async def run():
    pygame.init()

    win = pygame.display.set_mode(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )
    )

    pygame.display.set_caption(
        "Path Finding Visualiser"
    )

    await main(
        win,
        GRID_WIDTH,
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(run())
