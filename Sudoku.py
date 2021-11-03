# Sudoku.py

# Import pygame, along with other used libraries
import copy
import pygame
import time
from random import shuffle, randint
pygame.font.init()

# Constants
ROWS = 9
COLUMNS = 9
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 600
STATS_Y_COORDINATE = 560
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
THICK = 4
THIN = 1
EASY = 45
MEDIUM = 35
HARD = 25
FPS = 60

# Globals
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
difficulty = EASY


# Grid class represents the entire 9x9 sudoku board.
class Grid:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols

        # Generate random board by starting with blank, use backtracking to solve it
        # with random values, then remove a number of random cells of the solved board
        # according to the desired difficulty.
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        solve(self.board, random=True)
        self.solution = copy.deepcopy(self.board)
        for _ in range(81 - difficulty):
            remove_number(self.board)

        self.width = width
        self.height = height
        # self.gap is the length of a cell in pixels
        self.gap = self.width // self.rows
        # self.cells is a 2-D array of Cell objects
        self.cells = [[Cell(self.board[i][j], i, j, width, height, self.gap) for j in range(cols)] for i in range(rows)]
        # self.selected holds the (row, col) position of a selected cell
        self.selected = None
        # self.currently_filled tracks number of cells currently filled
        self.currently_filled = difficulty

    # Update the board to save current cell values.
    def update_board(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col] = self.cells[row][col].value

    # Sets the selected cell's value if provided a correct answer value.
    # (One unique solution requires >= 17 starting clues.)
    def place(self, val):
        row, col = self.selected
        # place function works only on empty cells
        if self.cells[row][col].value == 0:
            # Set cell to attempted val. Check if val is valid, and
            # board is still solvable. Undo change if val doesn't work.
            self.cells[row][col].set(val)
            self.update_board()
            if valid(self.board, val, row, col) and solve(self.board):
                self.update_board()
                return True
            self.cells[row][col].set(0)
            self.cells[row][col].set_temp(0)
            self.update_board()
        return False

    # Sets the selected cell's temp value so that it may eventually be
    # drawn in gray when drawing process occurs.
    def sketch(self, val):
        row, col = self.selected
        self.cells[row][col].set_temp(val)

    # Draws Grid Lines, and numbers for individual cells
    def draw(self):
        # Draw Grid Lines
        for i in range(self.rows+1):
            # Thick lines to divide the 3x3 sub-grids,
            # regular thin lines to divide each cell
            if i % 3 == 0 and i != 0:
                thickness = THICK
            else:
                thickness = THIN
            # Horizontal
            pygame.draw.line(screen, BLACK, (0, i * self.gap), (self.width, i * self.gap), thickness)
            # Vertical
            pygame.draw.line(screen, BLACK, (i * self.gap, 0), (i * self.gap, self.height), thickness)

        # Draw Cells
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].draw()

    # Selects a single cell so that it may eventually be outlined in red.
    def select(self, row, col):
        # Reset all other cell selections.
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].selected = False
                self.cells[i][j].temp = 0

        # Set chosen cell to be selected, save its row col index into self.selected
        self.cells[row][col].selected = True
        self.selected = (row, col)

    # Sets temp value of selected cell to 0 so that
    # it may eventually cancel an attempted choice
    # and clear it (the gray number) from being displayed.
    def clear(self):
        row, col = self.selected
        if self.cells[row][col].value == 0:
            self.cells[row][col].set_temp(0)

    # Get the board's row col index given the x and y pixel coordinates
    # of a clicked cell.
    def click(self, x, y):
        if x < self.width and y < self.height:
            # To calculate board[row][col] given x and y coordinates,
            # row is y pixel coordinate scaled down by the gap,
            # col is x pixel coordinate scaled down by the gap.
            col = x // self.gap
            row = y // self.gap
            return row, col
        return None

    # Check if sudoku is completed by seeing if all cells are filled.
    def is_finished(self):
        return self.currently_filled == self.rows * self.cols


# Cell class represents a single cell in the 9x9 sudoku board.
class Cell:
    def __init__(self, value, row, col, width, height, gap):
        # self.value stores a correct cell answer, self.temp
        # stores an attempted answer.
        self.value = value
        self.temp = 0
        # Store row col index location of the cell
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        # A selected cell is the one outlined in red that the user clicks on.
        self.selected = False
        self.gap = gap

    # Draw a single cell.
    def draw(self):
        # Set font and size of the value to display in a cell.
        font = pygame.font.SysFont("comicsans", 40)

        # Obtain x and y pixel coordinates from the cell's row col index.
        x = self.col * self.gap
        y = self.row * self.gap

        # Draw the cell value in black if self.value != 0,
        # meaning the cell has its correct answer.
        if self.value != 0:
            text = font.render(str(self.value), True, BLACK)
            screen.blit(text, (x + get_center(self.gap, text.get_width()), y + get_center(self.gap, text.get_height())))

        # Outline cell in red if selected.
        if self.selected:
            pygame.draw.rect(screen, RED, (x, y, self.gap, self.gap), 3)
            # Draw cell value in gray if self.value == 0,
            # meaning a correct answer isn't concluded with this cell yet.
            if self.temp != 0 and self.value == 0:
                text = font.render(str(self.temp), True, GRAY)
                screen.blit(text, (x + get_center(self.gap, text.get_width()), y + get_center(self.gap, text.get_height())))

    # Set the value of a cell.
    def set(self, val):
        self.value = val

    # Set the temp value of a cell.
    def set_temp(self, val):
        self.temp = val


# Checks if a move is valid
def valid(board, num, row, col):
    # Check row
    for j in range(len(board[0])):
        if board[row][j] == num and col != j:
            return False
    # Check column
    for i in range(len(board)):
        if board[i][col] == num and row != i:
            return False
    # Check 3x3 sub-grid
    sub_row = row // 3
    sub_col = col // 3
    for i in range(sub_row * 3, sub_row * 3 + 3):
        for j in range(sub_col * 3, sub_col * 3 + 3):
            if board[i][j] == num and (i, j) != (row, col):
                return False
    return True


# Backtracking algorithm to solve sudoku puzzle.
def solve(board, random=False):
    # Puzzle is solved if there are no more empty cells.
    empty_cell = find_empty_cell(board)
    if not empty_cell:
        return True
    else:
        row, col = empty_cell

    # Setting random randomizes the order in which
    # the algorithm attempts to get a correct answer
    # for a cell. This differs from the else statement,
    # which goes in order from 1 to 9 for a cell.
    if random:
        shuffle(number_list)
        for num in number_list:
            if valid(board, num, row, col):
                board[row][col] = num
                if solve(board, True):
                    return True
                board[row][col] = 0
    else:
        for i in range(1, 10):
            if valid(board, i, row, col):
                board[row][col] = i
                if solve(board, False):
                    return True
                board[row][col] = 0
    # Exhausted all possibilities for a cell, no solution possible at this recursive call.
    return False


# Removes a correct answer from a random row col index of the puzzle.
def remove_number(board):
    # Get random non-empty cell
    row, col = randint(0, 8), randint(0, 8)
    while board[row][col] == 0:
        row, col = randint(0, 8), randint(0, 8)
    board[row][col] = 0


# Returns the row col index of an empty cell, if found.
def find_empty_cell(board):
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 0:
                return row, col
    return None


# Draws all parts of the game screen.
def redraw_window(grid_obj, curr_time, errors, solve_button):
    screen.fill(WHITE)
    # Draw time
    font = pygame.font.SysFont("comicsans", 40)
    draw_text("Time: " + format_time(curr_time), font, BLACK, SCREEN_WIDTH - 180, STATS_Y_COORDINATE)
    # Draw Errors
    draw_text("Errors: " + str(errors), font, RED, 20, STATS_Y_COORDINATE)
    # Draw Solve Button
    pygame.draw.rect(screen, BLACK, solve_button)
    font = pygame.font.SysFont("comicsans", 25)
    draw_text("Solve!", font, RED, SCREEN_WIDTH, STATS_Y_COORDINATE + 5, True)
    # Draw grid and board
    grid_obj.draw()


# Draws text onto the screen. Optional parameters choose to center the text
# onto the middle of a given x and/or y pixel axis.
def draw_text(text, font, color, x, y, centerx = False, centery = False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if centerx and centery:
        text_rect.topleft = (get_center(x, text_obj.get_width()), get_center(y, text_obj.get_height()))
    elif centerx:
        text_rect.topleft = (get_center(x, text_obj.get_width()), y)
    elif centery:
        text_rect.topleft = (x, get_center(y, text_obj.get_height()))
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_obj, text_rect)


# Obtains pixel value to place an object at the center of a given perimeter.
def get_center(boundary_distance, obj_distance):
    return boundary_distance / 2 - obj_distance / 2


# Returns the formatted string to display the game time.
def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60
    curr_time = " " + str(hour) + ":" + str(minute) + ":" + str(sec)
    return curr_time


# Display the main menu.
def main_menu():
    pygame.display.set_caption("Sudoku")
    running = True
    while running:
        clock.tick(FPS)

        screen.fill(WHITE)
        font = pygame.font.SysFont("comicsans", 50)
        draw_text("SUDOKU", font, BLACK, SCREEN_WIDTH, 40, True)
        game_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 120, 250, 60)
        pygame.draw.rect(screen, BLACK, game_button)
        draw_text("Play", font, WHITE, SCREEN_WIDTH, 120 + 15, True)
        instructions_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 220, 250, 60)
        pygame.draw.rect(screen, BLACK, instructions_button)
        draw_text("Instructions", font, WHITE, SCREEN_WIDTH, 220 + 15, True)
        settings_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 320, 250, 60)
        pygame.draw.rect(screen, BLACK, settings_button)
        draw_text("Settings", font, WHITE, SCREEN_WIDTH, 320 + 15, True)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button:
                    click = True

        mx, my = pygame.mouse.get_pos()
        # Enter game screen, instructions screen, or settings
        # screen if their buttons are clicked.
        if game_button.collidepoint(mx, my) and click:
            game()
        if instructions_button.collidepoint(mx, my) and click:
            instructions()
        if settings_button.collidepoint(mx, my) and click:
            settings()

        # Display must be updated at the end of main_menu's while loop
        # to refresh main menu screen when exiting out of a game,
        # instructions, or settings screen.
        pygame.display.update()

    # Program is to be ended, quit pygame.
    pygame.quit()


# Display instructions screen.
def instructions():
    screen.fill(WHITE)
    header_font = pygame.font.SysFont("comicsans", 40)
    text_font = pygame.font.SysFont("comicsans", 25)
    draw_text("Rules:", header_font, BLACK, 10, 15)
    draw_text("A Sudoku game is number-placement puzzle. The objective is", text_font, BLACK, 10, 50)
    draw_text("to fill a 9×9 grid with digits so that each column, each row, and", text_font, BLACK, 10, 70)
    draw_text("each of the nine 3×3 subgrids that compose the grid (also called", text_font, BLACK, 10, 90)
    draw_text("“boxes”, “blocks”, or “regions”) contain all of the digits from 1", text_font, BLACK, 10, 110)
    draw_text("to 9. You can only use each number once in each row, each", text_font, BLACK, 10, 130)
    draw_text("column, and in each of the 3×3 boxes.", text_font, BLACK, 10, 150)

    draw_text("Instructions:", header_font, BLACK, 10, 185)
    draw_text("From the main menu, click play to start a new game. Game", text_font, BLACK, 10, 220)
    draw_text("difficulty can be adjusted by going to Settings from the main", text_font, BLACK, 10, 240)
    draw_text("menu and selecting from various the various difficulty levels.", text_font, BLACK, 10, 260)

    draw_text("To play the game, simply click on a cell of the grid, input a", text_font, BLACK, 10, 295)
    draw_text("number ranging from 1-9 on the keyboard, and press", text_font, BLACK, 10, 315)
    draw_text("enter/return to attempt to enter your answer. Correct answers", text_font, BLACK, 10, 335)
    draw_text("will be saved onto the grid, wrong answers will not be saved and", text_font, BLACK, 10, 355)
    draw_text("will increase the error count on the bottom left corner. To solve ", text_font, BLACK, 10, 375)
    draw_text("the puzzle automatically, press the solve button at the bottom.", text_font, BLACK, 10, 395)

    draw_text("To exit the current screen and enter the previous, click the exit", text_font, BLACK, 10, 430)
    draw_text("button at the top of the window or press the escape key. To exit", text_font, BLACK, 10, 450)
    draw_text("the program, click the exit button or escape key while in the", text_font, BLACK, 10, 470)
    draw_text("main menu.", text_font, BLACK, 10, 490)

    pygame.display.update()
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


# Used when clicking settings button from main menu.
# Used to print the difficulty buttons on the settings screen.
def print_difficulties(easy_button=None, medium_button=None, hard_button=None, custom_button=None,
                       box_color=BLACK, clear=False):
    if clear:
        screen.fill(WHITE)
    font = pygame.font.SysFont("comicsans", 50)
    if easy_button:
        pygame.draw.rect(screen, box_color, easy_button)
        draw_text("Easy", font, WHITE, SCREEN_WIDTH, 120 + 15, True)
    if medium_button:
        pygame.draw.rect(screen, box_color, medium_button)
        draw_text("Medium", font, WHITE, SCREEN_WIDTH, 220 + 15, True)
    if hard_button:
        pygame.draw.rect(screen, box_color, hard_button)
        draw_text("Hard", font, WHITE, SCREEN_WIDTH, 320 + 15, True)
    if custom_button:
        pygame.draw.rect(screen, box_color, custom_button)
        draw_text("Custom", font, WHITE, SCREEN_WIDTH, 420 + 15, True)


# Used when custom button is clicked. Updates text below the button
# and displays the number of starting clues selected.
def update_custom_clues(custom_count):
    white_box = pygame.Rect(get_center(SCREEN_WIDTH, SCREEN_WIDTH), 500, SCREEN_WIDTH, SCREEN_HEIGHT - 500)
    pygame.draw.rect(screen, WHITE, white_box)
    font = pygame.font.SysFont("comicsans", 20)
    draw_text("Use left and right arrow keys to adjust the number of starting clues.", font, BLACK,
              SCREEN_WIDTH, 500, True)
    draw_text("Starting clues = " + str(custom_count), font, BLACK, SCREEN_WIDTH, 520, True)


# Displays the settings screen. Used to set the difficulty of the game.
def settings():
    global difficulty

    easy_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 120, 250, 60)
    medium_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 220, 250, 60)
    hard_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 320, 250, 60)
    custom_button = pygame.Rect(get_center(SCREEN_WIDTH, 250), 420, 250, 60)

    print_difficulties(easy_button, medium_button, hard_button, custom_button, BLACK, True)
    pygame.display.update()

    # Variables for custom kept out of loop so that their values may be updated.
    custom = False
    custom_count = 41
    running = True
    while running:
        clock.tick(FPS)

        mx, my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Left and Right arrow keys controls the adjustment
                # of the starting clues. Works when custom difficulty selected.
                # Minimum number of clues is 0, Maximum is 81.
                if event.key == pygame.K_LEFT:
                    if custom:
                        if custom_count > 0:
                            custom_count -= 1
                            difficulty = custom_count
                            update_custom_clues(custom_count)
                            pygame.display.update()
                if event.key == pygame.K_RIGHT:
                    if custom:
                        if custom_count < 81:
                            custom_count += 1
                            difficulty = custom_count
                            update_custom_clues(custom_count)
                            pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button:
                    click = True

        # Color the selected difficulty box green to indicate choice.
        if easy_button.collidepoint(mx, my) and click:
            custom = False
            print_difficulties(easy_button, medium_button, hard_button, custom_button, BLACK, True)
            print_difficulties(easy_button=easy_button, box_color=GREEN)
            difficulty = EASY
            pygame.display.update()
        if medium_button.collidepoint(mx, my) and click:
            custom = False
            print_difficulties(easy_button, medium_button, hard_button, custom_button, BLACK, True)
            print_difficulties(medium_button=medium_button, box_color=GREEN)
            difficulty = MEDIUM
            pygame.display.update()
        if hard_button.collidepoint(mx, my) and click:
            custom = False
            print_difficulties(easy_button, medium_button, hard_button, custom_button, BLACK, True)
            print_difficulties(hard_button=hard_button, box_color=GREEN)
            difficulty = HARD
            pygame.display.update()
        if custom_button.collidepoint(mx, my) and click:
            custom = True
            print_difficulties(easy_button, medium_button, hard_button, custom_button, BLACK, True)
            print_difficulties(custom_button=custom_button, box_color=GREEN)
            difficulty = custom_count
            update_custom_clues(custom_count)
            pygame.display.update()


# Display the game screen.
def game():
    # Initialize Grid settings. Board will be a square
    # with sides equal to the screen's width in pixels.
    grid_obj = Grid(ROWS, COLUMNS, SCREEN_WIDTH, SCREEN_WIDTH)
    # key saves the user's input value
    key = None
    running = True
    start = time.time()
    errors = 0
    solve_mode = False
    solve_index = 0
    solve_button = pygame.Rect(get_center(SCREEN_WIDTH, 100), STATS_Y_COORDINATE, 100, 28)
    while running:
        clock.tick(FPS)
        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    grid_obj.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = grid_obj.selected
                    if grid_obj.cells[i][j].temp != 0:
                        if grid_obj.place(grid_obj.cells[i][j].temp):
                            grid_obj.currently_filled += 1
                        else:
                            errors += 1
                        key = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if solve_button.collidepoint(mx, my):
                    solve_mode = True

                clicked = grid_obj.click(mx, my)
                if clicked:
                    # Set the clicked cell to be selected.
                    grid_obj.select(clicked[0], clicked[1])
                    key = None

        if solve_mode:
            # When in solve move, automatically obtain next empty cell to be solved.
            i, j = find_empty_cell(grid_obj.board)
            grid_obj.select(i, j)
            # number_list will be iterated through to find the correct key.
            key = number_list[solve_index]

        # Update selected cell's temp value to be user inputted key.
        if grid_obj.selected and key:
            grid_obj.sketch(key)

        if solve_mode:
            i, j = grid_obj.selected
            if grid_obj.cells[i][j].temp != 0:
                if grid_obj.place(grid_obj.cells[i][j].temp):
                    # Correct solve_mode attempt resets solve_index and re-shuffles number_list.
                    grid_obj.currently_filled += 1
                    solve_index = 0
                    shuffle(number_list)
                else:
                    # Current index of number_list doesn't work, attempt next index.
                    solve_index += 1

        # Update game screen.
        redraw_window(grid_obj, play_time, errors, solve_button)
        pygame.display.update()

        # If game is completed, remain at end screen until exit.
        if grid_obj.is_finished():
            running = False
            end_screen = True
            while end_screen:
                for end_event in pygame.event.get():
                    if end_event.type == pygame.QUIT:
                        end_screen = False
                    if end_event.type == pygame.KEYDOWN:
                        if end_event.key == pygame.K_ESCAPE:
                            end_screen = False


# Main function to launch game, goes to main menu.
main_menu()
