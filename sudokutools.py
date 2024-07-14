#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint, shuffle
import time


def print_board(board, size=3):
    """
   Metoda za prikaz sudoku slagalica sa blagim formatom.

    Args:
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3.
        board (list[list[int]]): Reprezentacija ploce dimenzija size x size predstavljene kao lista listi
         od int vrijednosti.

    Returns:
        None.
    """

    board_string = ""
    for i in range(size**2):
        for j in range(size**2):
            board_string += str(board[i][j]) + " "
            if (j + 1) % size == 0 and j != 0 and j + 1 != size**2:
                board_string += "| "

            if j == size**2-1:
                board_string += "\n"

            if j == size**2-1 and (i + 1) % size == 0 and i + 1 != size**2:
                board_string += "- - - - - - - - - - - \n"
    print(board_string)


def find_empty(board, size=3):
    """
    Metoda za pronalazak praznog polja na sudoku ploci.

    Args:
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3.
        board (list[list[int]]):  Reprezentacija ploce dimenzija size x size predstavljene kao lista listi
         od int vrijednosti.

    Returns:
        tuple[int, int]|None: Poziciju prve prazne ćelije u obliku tuple od indeksa reda i kolone,
        ili None ako nema praznih celija.
    """

    for i in range(size**2):
        for j in range(size**2):
            if board[i][j] == 0:
                return (i, j)
    return None


def valid(board, pos, num, size=3):
    """
   Metoda koja provjerava da li je broj num dozvoljen u ćeliji sa pozicijom pos.

    Args:
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3.
        board (list[list[int]]): Reprezentacija ploce dimenzija size x size predstavljene kao lista listi
         od int vrijednosti.
        pos (tuple[int, int]): Pozicija ćelije koja se provjerava u obliku tuple od indeksa reda i kolone.
        num (int): Broj koji se provjerava.

    Returns:
        bool: True ako je broj dozvoljen u ćeliji, False u suprotnom.
    """

    # provjeravanje po koloni
    for i in range(size**2):
        if board[i][pos[1]] == num:
            return False

    # provjeravanje po redu
    for j in range(size**2):
        if board[pos[0]][j] == num:
            return False

    # provjeravanje po bloku
    start_i = pos[0] - pos[0] % size
    start_j = pos[1] - pos[1] % size
    for i in range(size):
        for j in range(size):
            if board[start_i + i][start_j + j] == num:
                return False
    return True


def solve(board, size=3):
    """
    Rješavanje sudoku slagalice primjenom backtracking algoritma

    Args:
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3
        board (list[list[int]]):  Reprezentacija ploce dimenzija size x size predstavljene kao lista listi
         od int vrijednosti.

    Returns:
        bool: True ako slagalica ima rješenje, False u suprotnom.
    """

    # print(size)
    empty = find_empty(board, size)
    # print(empty[0], empty[1])
    if not empty:
        return True     # ako nema praznih polja sudoku slagalica je riješena

    # opseg u ovom formatu jer range ne obuhvata gornju granicu opsega
    for nums in range(1, size**2 + 1):

        if valid(board, empty, nums, size):
            board[empty[0]][empty[1]] = nums

            if solve(board, size):  # rekurzivni korak
                return True
            board[empty[0]][empty[1]] = 0  # broj je pogrešan pa se vraća na vrijednost 0 (0 predstavlja empty)
    return False


def generate_board(size=3, difficulty=0):
    """
    Metoda za generisanje proizvoljnih sudoku slagalica sa različitim brojem praznih polja.

    Args:
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3

    Returns:
        list[list[int]]: Sudoku slagalicu dimenzija size x size.
    """

    board = [[0 for i in range(size**2)] for j in range(size**2)]

    # Fill the diagonal boxes
    for i in range(0, size**2, size):
        nums = list(range(1, size**2+1))
        shuffle(nums)
        for row in range(size):
            for col in range(size):
                board[i + row][i + col] = nums.pop()

    # Fill the remaining cells with backtracking
    def fill_cells(board, row, col):
        """
        Fills the remaining cells of the sudoku board with backtracking.

        Args:
            board (list[list[int]]): A 9x9 sudoku board represented as a list of lists of integers.
            row (int): The current row index to fill.
            col (int): The current column index to fill.

        Returns:
            bool: True if the remaining cells are successfully filled, False otherwise.
        """

        if row == size**2:
            return True
        if col == size**2:
            return fill_cells(board, row + 1, 0)

        if board[row][col] != 0:
            return fill_cells(board, row, col + 1)

        for num in range(1, size**2+1):
            if valid(board, (row, col), num, size):
                board[row][col] = num

                if fill_cells(board, row, col + 1):
                    return True

        board[row][col] = 0
        return False

    fill_cells(board, 0, 0)

    # Remove a greater number of cells to create a puzzle with fewer initial numbers
    difficulty_dict3 = {0: (16, 31),  # easy
                        1: (31, 46),  # medium
                        2: (46, 61)}  # hard

    difficulty_dict4 = {0: (35, 60),  # easy
                        1: (60, 85),  # medium
                        2: (85, 110),  # hard
                        3: (110, 130)}  # expert
    distinct_rows_cols = set()
    # print((randint(difficulty_dict3[difficulty][0], difficulty_dict3[difficulty][1])))
    # print(difficulty_dict4[difficulty][0])
    while len(distinct_rows_cols) < ((randint(difficulty_dict4[difficulty][0],difficulty_dict4[difficulty][1]))
    if size == 4 else ((randint(difficulty_dict3[difficulty][0],difficulty_dict3[difficulty][1])) if size == 3
    else ())):
        row, col = randint(0, size ** 2 - 1), randint(0, size ** 2 - 1)
        if (row, col) not in distinct_rows_cols:
            board[row][col] = 0

        distinct_rows_cols.add((row, col))

    return board


if __name__ == "__main__":
    start_time = time.time()
    board = generate_board(4)
    print_board(board, 4)
    solve(board, 4)
    end_time = time.time()
    print_board(board, 4)
    print("Time: {} seconds".format(end_time - start_time))
