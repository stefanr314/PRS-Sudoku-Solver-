#!/usr/bin/python
# -*- coding: utf-8 -*-
# from sudokutools import valid, solve, find_empty, generate_board
import sudokutools
import optimized_backtracking as ob
from copy import deepcopy
from sys import exit
import pygame
import time
import random

pygame.init()


class Board:
    def __init__(self, window, size=3):
        """
        Initializes a Board object.

        Args:
            window: The Pygame window object.
        """
        # Generate a new Sudoku board and create a solved version of it.
        self.size = size
        self.board = sudokutools.generate_board(self.size)
        sudokutools.print_board(self.board, self.size)
        self.solvedBoard = deepcopy(self.board)
        self.cache = ob.cache_valid_values(self.board, self.size)
        # self.ordered_cache = ob.orded_valid_values(self.board, self.cache)  # kada bismo ovo uradili vec bi nam upisao
        # vrijednosti bez vizuelizacije
        self.ordered_cache = deepcopy(self.cache)
        # sudokutools.print_board(self.board)
        stari_broj = ob.broj_pokusaja
        ob.solve_with_cache(self.solvedBoard, self.ordered_cache, self.size)
        print(ob.broj_pokusaja - stari_broj)
        # sudokutools.print_board(self.solvedBoard)

        # Create a 2D list of Tile objects to represent the Sudoku board.
        self.window = window

        self.size_board = lambda s: 540 if s == 3 else (720 if s == 4 else 0)  # lambda fija za izracuvanje ukupnih
        # dinamicke dimenzija ploce za prikaz
        self.size_tile = lambda s: 60 if s == 3 else (45 if s == 4 else 0)
        # dinamicke dimenzija polja za prikaz

        self.tiles = [
            [Tile(self.board[i][j], window, i * self.size_tile(self.size), j * self.size_tile(self.size), self.size)
             for j in range(self.size**2)]
            for i in range(self.size**2)
        ]

    def draw_board(self):
        """
        Draws the Sudoku board on the Pygame window.
        """
        for i in range(self.size**2):
            for j in range(self.size**2):
                # Draw vertical lines every three columns.
                if j % self.size == 0 and j != 0:
                    pygame.draw.line(
                        self.window,
                        (0, 0, 0),
                        (j // self.size * 180, 0),  # proprati brojeve moras paziti velicinu tile da onda ide
                        # size puta to
                        (j // self.size * 180, self.size_board(self.size)),
                        4,
                    )
                # Draw horizontal lines every three rows.
                if i % self.size == 0 and i != 0:
                    pygame.draw.line(
                        self.window,
                        (0, 0, 0),
                        (0, i // self.size * 180),  # u oba slucaja je 180 jer je 3*60, a i 4*45 je isto 180
                        (self.size_board(self.size), i // self.size * 180),
                        # poziv preko lambda fije radi isto sto i uslov u liniji 57
                        4,
                    )
                # Draw the Tile object on the board.
                self.tiles[i][j].draw((0, 0, 0), 1)

                # Display the Tile value if it is not 0 (empty).
                if self.tiles[i][j].value != 0:
                    self.tiles[i][j].display(
                        self.tiles[i][j].value, ((17 if self.size == 4 else (21 if self.size == 3 else 0))
                                                 + j * self.size_tile(self.size),
                                                 (16 if self.size == 3 else (14 if self.size == 4 else 0))
                                                 + i * self.size_tile(self.size)), (0, 0, 0)
                    )
        # Draw a horizontal line at the bottom of the board.
        pygame.draw.line(
            self.window,
            (0, 0, 0),
            (0, (i + 1) // self.size * 180),
            (self.size_board(self.size), (i + 1) // self.size * 180),
            4,
        )

    def deselect(self, tile):
        """
        Deselects all tiles except the given tile.

        Args:
            tile (Tile): The tile that should remain selected.

        Returns:
            None
        """
        for i in range(self.size**2):
            for j in range(self.size**2):
                if self.tiles[i][j] != tile:
                    self.tiles[i][j].selected = False

    def redraw(self, keys, wrong, time):
        """
        Redraws the Sudoku board on the game window, highlighting selected, correct, and incorrect tiles, displaying the
        current wrong count and time, and rendering the current keys (potential values) for each tile.

        Args:
            keys (dict): A dictionary containing tuples of (x, y) coordinates as keys and potential values as values.
            wrong (int): The current wrong count.
            time (int): The current time elapsed.

        Returns:
            None
        """
        self.window.fill((255, 255, 255))  # fill the window with white
        self.draw_board()  # draw the Sudoku board
        # Zašto ovim redoslijedom - najjače je što i treba ovako; interesantnoooooo
        for i in range(self.size**2):
            for j in range(self.size**2):
                if self.tiles[j][i].selected:
                    # highlight selected tiles in green
                    self.tiles[j][i].draw((50, 205, 50), 4)
                elif self.tiles[i][j].correct:
                    # highlight correct tiles in dark green
                    self.tiles[j][i].draw((34, 139, 34), 4)
                elif self.tiles[i][j].incorrect:
                    # highlight incorrect tiles in red
                    self.tiles[j][i].draw((255, 0, 0), 4)
                elif self.tiles[i][j].inserted:
                    self.tiles[j][i].draw((255, 140, 100), 4)

        # ???????????????????????????????????????????????????????????????????

        if len(keys) != 0:
            for value in keys:
                # display the potential values for each tile
                self.tiles[value[0]][value[1]].display(
                    keys[value],
                    (21 + value[0] * self.size_tile(self.size), 16 + value[1] * self.size_tile(self.size)),
                    (128, 128, 128),
                )

        if wrong > 0:
            # display the current wrong count as an "X" icon and a number
            font = pygame.font.SysFont("Bauhaus 93", 30)
            text = font.render("X", True, (255, 0, 0))
            self.window.blit(text, (10, self.size_board(self.size) + 6))

            font = pygame.font.SysFont("Bahnschrift", 40)
            text = font.render(str(wrong), True, (0, 0, 0))
            self.window.blit(text, (32, self.size_board(self.size) + 2))

        # display the current time elapsed as a number
        font = pygame.font.SysFont("Bahnschrift", 40)
        text = font.render(str(time), True, (0, 0, 0))
        self.window.blit(text, (self.size_board(self.size) - 152, self.size_board(self.size) + 2))
        pygame.display.flip()  # update the game window

    def fill_some(self):
        """
        Metoda za popunjave polja koja imaju samo jednu dozvoljenu kombinaciju.
        Returns:
            None
        """
        board_old = deepcopy(self.board)
        self.ordered_cache = ob.orded_valid_values(self.board, self.cache, self.size)
        # sudokutools.print_board(board_old, self.size)
        # sudokutools.print_board(self.board, self.size)
        difference_board = {}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()  # exit the game if the user clicks the close button

        for i in range(self.size**2):
            for j in range(self.size**2):
                if not board_old[i][j] == self.board[i][j]:
                    difference_board[(i, j)] = self.board[i][j]
                    # print(self.board[i][j])

        for key, value in difference_board.items():
            # print(key, value)
            self.tiles[key[0]][key[1]].value = value
            self.tiles[key[0]][key[1]].inserted = True
            pygame.time.delay(63)
            self.redraw({}, 0, 0)

        # values_found = True
        # while values_found:
        #     self.cache = ob.cache_valid_values(self.board)
        #     values_found, self.ordered_cache = ob.orded_valid_values(self.board, self.cache)
        #     # self.fill_some()

    def visualSolve(self, wrong, time):
        """
        Recursively solves the Sudoku board visually, highlighting correct and incorrect tiles as it fills them in.

        Args:
            wrong (int): The current wrong count.
            time (int): The current time elapsed.

        Returns:
            bool: True if the board is successfully solved, False otherwise.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()  # exit the game if the user clicks the close button

        # ------------ URADITI DA POSTEPENO PRIKAŽE ------------------

        # self.redraw(
        #     {}, wrong, time
        # )
        # ------------------------------------------------------------
        # empty = ob.find_empty(self.board)
        # self.fill_some()
        empty = sudokutools.find_empty(self.board, self.size)
        if not empty:
            return True  # the board is solved if there are no empty tiles left

        for nums in range(self.size**2):
            if sudokutools.valid(self.board, (empty[0], empty[1]), nums + 1, self.size):
                # fill in the current empty tile with a valid number
                self.board[empty[0]][empty[1]] = nums + 1
                self.tiles[empty[0]][empty[1]].value = nums + 1
                self.tiles[empty[0]][empty[1]].correct = True
                pygame.time.delay(63)  # delay to slow down the solving animation
                self.redraw(
                    {}, wrong, time
                )  # redraw the game window with the updated board

                if self.visualSolve(wrong, time):
                    return True  # recursively solve the rest of the board if the current move is valid

                # if the current move is not valid, reset the tile and highlight it as incorrect
                self.board[empty[0]][empty[1]] = 0
                self.tiles[empty[0]][empty[1]].value = 0
                self.tiles[empty[0]][empty[1]].incorrect = True
                self.tiles[empty[0]][empty[1]].correct = False
                pygame.time.delay(63)  # delay to slow down the solving animation
                self.redraw(
                    {}, wrong, time
                )  # redraw the game window with the updated board

    def hint(self, keys):
        """
        Provides a hint by filling in a random empty tile with the correct number.

        Args:
            keys (dict): A dictionary containing tuples of (x, y) coordinates as keys and potential values as values.

        Returns:
            bool: True if a hint is successfully provided, False if the board is already solved.
        """
        while True:
            i = random.randint(0, self.size**2-1)
            j = random.randint(0, self.size**2-1)
            if self.board[i][j] == 0:
                if (j, i) in keys:
                    del keys[(j, i)]
                # fill in the selected empty tile with the correct number
                self.board[i][j] = self.solvedBoard[i][j]
                self.tiles[i][j].value = self.solvedBoard[i][j]
                return True
            elif self.board == self.solvedBoard:
                return False  # the board is already solved, so no hint can be provided.


class Tile:
    def __init__(
        self,
        value,
        window,
        x1,
        y1,
        size=3
    ):
        """
        Inicijalizacija objekta tipa Tile.

        Args:
            value (int): Vrijednost koja se prikazuju u središtu ćelije.
            window (pygame.Surface): Površina na kojoj se crta ćelija.
            x1 (int): x-coordinate gornjeg-lijevog ćoška ćelije.
            y1 (int): y-kooridnata gornjeg-lijevog ćoška ćelije.
            size (int): Velicina sudoku ploče.

        Attributes:
            value (int): Vrijednost koja se prikazuju u središtu ćelije.
            window (pygame.Surface): Površina na kojoj se crta ćelija.
            rect (pygame.Rect): Pravougaona oblast ćelije.
            selected (bool): Ćelija pritisnuta.
            correct (bool): Vrijednost ćelije ispravna.
            incorrect (bool): Vrijednost ćelije neispravna.
        """

        self.value = value
        self.window = window
        self.size = size
        self.rect = pygame.Rect(x1, y1, 60 if self.size == 3 else (45 if self.size == 4 else 0),
                                60 if self.size == 3 else (45 if self.size == 4 else 0))
        self.selected = False
        self.correct = False
        self.incorrect = False
        self.inserted = False

    def draw(self, color, thickness):
        """
        Metoda za crtanje ćelija na ploči sa obojenim okvirom ćelije.

        Args:
            color (tuple[int, int, int]): RGB vrijednost boje okvira ćelije.
            thickness (int): Debljina okvira.

        Returns:
            None.
        """

        pygame.draw.rect(self.window, color, self.rect, thickness)

    def display(
        self,
        value,
        position,
        color,
    ):
        """
        Metoda za prikaz vrijednosti polja u sredini celije. U slucaju 16x16 slagalica i dvocifrenih brojeva 10-16,
        prikazuju se odgovarajuci ekvivalenti u vidu karaktera.

        Args:
            value (int): Vrijednost koja se prikazuje.
            position (tuple[int, int]): (x, y) koordinate centra ćelije.
            color (tuple[int, int, int]): Boja u RGB formatu za prikaz vrijednosti polja.

        Returns:
            None.
        """

        double_digit_numbers = [10, 11, 12, 13, 14, 15, 16]
        value_to_letter = {
            10: "A",
            11: "B",
            12: "C",
            13: "D",
            14: "E",
            15: "F",
            16: "G"
        }
        font = pygame.font.SysFont("lato", 45 if self.size == 3 else (30 if self.size == 4 else 0))
        if value not in double_digit_numbers:
            text = font.render(str(value), True, color)
        else:
            text = font.render(str(value_to_letter.get(value, "Na")), True, color)
        self.window.blit(text, position)

    def clicked(self, mousePos):
        """
        Metoda koja provjerava da li je polje kliknuto preko miša.

        Args:
            mousePos (tuple[int, int]): (x, y) koordinate miša.

        Returns:
            bool: True ako je polje pritisnuto, False u suprotnom.
        """

        if self.rect.collidepoint(mousePos):
            self.selected = True
        return self.selected


class Button:
    def __init__(self, x, y, width, height, color, text=''):
        """
        Klasa za inicijalizaciju Button objekata.
        Args:
            x: x-koordinata gornjeg lijevog ćoška dugmeta.
            y: y-koordinata gornjeg lijevog ćoška dugmeta.
            width: Širina dugmeta.
            height: Visina dugmeta.
            color: Boja dugmeta.
            text: Tekst unutar okvira dugmeta.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text

    def draw(self, screen):
        # Crtanje dugmeta
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            font = pygame.font.SysFont("Bahnschrift", 20)
            text_surface = font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def draw_rect_with_border(self, screen, border_color, border_thickness, text_color):
        # Crtanje okvira
        pygame.draw.rect(screen, border_color, self.rect)
        # Crtanje popune unutar okvira
        inner_rect = self.rect.inflate(-border_thickness * 2, -border_thickness * 2)
        pygame.draw.rect(screen, self.color, inner_rect)
        if self.text:
            font = pygame.font.SysFont("Bahnschrift", 20)
            text_surface = font.render(self.text,True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def main_display(size=3):
    # Set up the pygame window
    screen = pygame.display.set_mode((550, 590))
    if size == 4:
        screen = pygame.display.set_mode((720, 760))

    screen.fill((255, 255, 255))
    pygame.display.set_caption("Sudoku Solver")
    icon = pygame.image.load("assets/thumbnail.png")
    pygame.display.set_icon(icon)

    # Display "Generating Random Grid" text while generating a random grid
    font = pygame.font.SysFont("Bahnschrift", 40)
    text = font.render("Generating", True, (0, 0, 0))
    screen.blit(text, (175, 245))

    font = pygame.font.SysFont("Bahnschrift", 40)
    text = font.render("Random Grid", True, (0, 0, 0))
    screen.blit(text, (156, 290))
    pygame.display.flip()
    pygame.time.delay(1000)
    # Initialize variables
    wrong = 0
    board = Board(screen, size)
    selected = (-1, -1)
    keyDict = {}
    solved = False
    # start_time = pygame.time.get_ticks()
    start_time = time.time()
    # dio za setovanje spacebar event-a
    # spacebar_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)

    # pygame.event.post(spacebar_event)
    # Loop until the sudoku is solved
    while not solved:
        # Get elapsed time and format it to display in the window
        elapsed = time.time() - start_time
        passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        # Check if the sudoku is solved
        if board.board == board.solvedBoard:
            solved = True

        # Handle events
        for event in pygame.event.get():
            elapsed = time.time() - start_time
            passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                # Check if a Tile is clicked
                mousePos = pygame.mouse.get_pos()
                for i in range(size**2):
                    for j in range(size**2):
                        if board.tiles[i][j].clicked(mousePos):
                            selected = (i, j)
                            # print(selected[0], selected[1])
                            board.deselect(board.tiles[i][j])
            elif event.type == pygame.KEYDOWN:
                # Handle key presses
                if board.board[selected[1]][selected[0]] == 0 and selected != (-1, -1):
                    if event.key == pygame.K_1:
                        keyDict[selected] = 1

                    if event.key == pygame.K_2:
                        keyDict[selected] = 2

                    if event.key == pygame.K_3:
                        keyDict[selected] = 3

                    if event.key == pygame.K_4:
                        keyDict[selected] = 4

                    if event.key == pygame.K_5:
                        keyDict[selected] = 5

                    if event.key == pygame.K_6:
                        keyDict[selected] = 6

                    if event.key == pygame.K_7:
                        keyDict[selected] = 7

                    if event.key == pygame.K_8:
                        keyDict[selected] = 8

                    if event.key == pygame.K_9:
                        keyDict[selected] = 9

                    if event.key == pygame.K_a:
                        if size == 4:
                            keyDict[selected] = 10

                    if event.key == pygame.K_b:
                        if size == 4:
                            keyDict[selected] = 11

                    if event.key == pygame.K_c:
                        if size == 4:
                            keyDict[selected] = 12

                    if event.key == pygame.K_d:
                        if size == 4:
                            keyDict[selected] = 13

                    if event.key == pygame.K_e:
                        if size == 4:
                            keyDict[selected] = 14

                    if event.key == pygame.K_f:
                        if size == 4:
                            keyDict[selected] = 15

                    if event.key == pygame.K_g:
                        if size == 4:
                            keyDict[selected] = 16
                    elif (
                        event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE
                    ):
                        if selected in keyDict:
                            board.tiles[selected[1]][selected[0]].value = 0
                            del keyDict[selected]
                    elif event.key == pygame.K_RETURN:
                        if selected in keyDict:
                            if (
                                keyDict[selected]
                                != board.solvedBoard[selected[1]][selected[0]]
                            ):
                                wrong += 1
                                board.tiles[selected[1]][selected[0]].value = 0
                                del keyDict[selected]
                            else:
                                board.tiles[selected[1]][selected[0]].value = keyDict[
                                    selected
                                ]
                                board.board[selected[1]][selected[0]] = keyDict[selected]
                                del keyDict[selected]

                                # break
                            #
                            # board.tiles[selected[1]][selected[0]].value = keyDict[
                            #     selected
                            # ]
                            # board.board[selected[1]][selected[0]] = keyDict[selected]
                            # del keyDict[selected]

                # Handle hint key
                if event.key == pygame.K_h:
                    board.hint(keyDict)

                # Handle space key
                if event.key == pygame.K_SPACE:
                    board.fill_some()
                    # Deselect all tiles and clear keyDict
                    for i in range(size**2):
                        for j in range(size**2):
                            board.tiles[i][j].selected = False
                    keyDict = {}

                    # Solve the sudoku visually and reset all tile correctness
                    elapsed = time.time() - start_time
                    passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                    board.visualSolve(wrong, passedTime)
                    for i in range(size**2):
                        for j in range(size**2):
                            board.tiles[i][j].correct = False
                            board.tiles[i][j].incorrect = False

                    # Set solved to True after solving the sudoku:
                    solved = True
                    # end_time = pygame.time.get_ticks()
                    # print(f"Vreme odziva: {end_time - start_time} milisekundi")

        board.redraw(keyDict, wrong, passedTime)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


def welcome_display():
    background_image = pygame.image.load('assets/PRSblur.jpg')
    screen = pygame.display.set_mode((800, 650))
    # screen.fill((255, 255, 255))
    screen.blit(background_image, (0, 0))
    pygame.display.set_caption("Sudoku Solver")
    icon = pygame.image.load("assets/thumbnail.png")
    pygame.display.set_icon(icon)

    # # Display "Generating Random Grid" text while generating a random grid
    # font = pygame.font.SysFont("Bahnschrift", 40)
    # text = font.render("Sudoku Solver", True, (0, 0, 0))
    # screen.blit(text, (130, 50))

    button_9x9 = Button(130, 150, 550, 75, (144, 238, 144), '9x9 Sudoku')
    button_16x16 = Button(130, 250, 550, 75, (45, 106, 79), '16x16 Sudoku')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if button_9x9.is_clicked(event):
                main_display()
                screen = pygame.display.set_mode((800, 600))

            elif button_16x16.is_clicked(event):
                main_display(4)
                screen = pygame.display.set_mode((800, 600))

        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        font = pygame.font.SysFont("Bahnschrift", 85)
        text = font.render("Sudoku Solver", True, (0, 0, 0))
        screen.blit(text, (130, 50))
        button_9x9.draw_rect_with_border(screen, (0, 0, 0), 2, (0, 0, 0))
        button_16x16.draw_rect_with_border(screen, (0, 0, 0), 2, (255, 255, 255))
        pygame.display.flip()


# main_display()
welcome_display()
pygame.quit()
