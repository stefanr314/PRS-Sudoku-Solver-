import copy
# from concurrent.futures import ProcessPoolExecutor
# from multiprocessing import Pool, Manager
import sudokutools
from multiprocessing import Pool, cpu_count
import time
import timeit
from functools import partial

broj_pokusaja = 0
# start_vreme = time.time()


def find_all_empty(board, size=3):
    empty_cells = []
    for i in range(size**2):
        for j in range(size**2):
            if board[i][j] == 0:
                empty_cells.append((i, j))

    return empty_cells


def allowed_values(board, row, col, size=3):
    """
    Metoda za izvačenje liste dozovoljenih vrijednosti, koje ispunjavaju uslove sudoku slagalice, za navedeno polje
    Args:
        board (list[list[int]]): Reprezentacija ploce dimenzija _size_x_size_ predstavljene kao lista listi
        od int vrijednosti.
        row (int): Indeks reda polja za koje se traže dozvoljene vrijednosti.
        col (int): Indeks kolone polja za koje se traže dozvoljene vrijednosti.
        size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3.

    Returns:
        list: Lista dozvoljenih vrijednosti polja.
    """
    number_list = list()

    for number in range(1, size**2+1):

        found = False
        # Check if all row elements include this number
        for j in range(size**2):
            if board[row][j] == number:
                found = True
                break
        # Check if all column elements include this number
        if found:
            continue
        else:
            for i in range(size**2):
                if board[i][col] == number:
                    found = True
                    break

        # Check if the number is already included in the block
        if found:
            continue
        else:
            row_block_start = size * (row // size)
            col_block_start = size * (col // size)

            row_block_end = row_block_start + size
            col_block_end = col_block_start + size
            for i in range(row_block_start, row_block_end):
                for j in range(col_block_start, col_block_end):
                    if board[i][j] == number:
                        found = True
                        break
        if not found:
            number_list.append(number)
    return number_list


def cache_valid_values(board, size=3):
    """
    Metoda za određivanje keša koji čuva dozvoljenje vrijednosti za svako prazno polje na tabeli.
    Args:
       board (list[list[int]]): Reprezentacija ploce dimenzija _size_x_size_ predstavljene kao lista listi
       od int vrijednosti.
       size (int): Veličina sudoku slagalice; podrazumijevana vrijednost je 3.

    Returns:
        dict: Keš dozvoljenih vrijednosti za svako polje ploče, na način da za ključ, koji predstavlja indeks
        pozicije, se čuva lista dozvoljenih vrijednosti na toj lokaciji.
    """
    cache = dict()
    for i in range(size**2):
        for j in range(size**2):
            if board[i][j] == 0:
                cache[(i, j)] = allowed_values(board, i, j, size)
    return cache


# def check_number(args):
#     board, pos, num, cache = args
#     if valid(board, pos, num):
#         board[pos[0]][pos[1]] = num
#         if solve_with_cache(board, cache):
#             return True
#         board[pos[0]][pos[1]] = 0
#     return False

def generate_possible_boards(board, size=3):
    possible_boards = []
    empty_cells = find_all_empty(board, size)  # Pronađite sve prazne ćelije na tabli

    for cell in empty_cells:
        for num in range(1, size**2+1):  # Probajte svaki broj od 1 do 9
            if sudokutools.valid(board, cell, num, size):  # Proverite da li je broj validan za tu ćeliju
                new_board = copy.deepcopy(board)
                new_board[cell[0]][cell[1]] = num  # Postavite broj u ćeliju
                possible_boards.append(new_board)
                if len(possible_boards) >= cpu_count():  # Ograničite broj generisanih tabli na broj procesora
                    return possible_boards

    return possible_boards


def parallel_solver(board, cache, size=3):
    possible_boards = generate_possible_boards(board, size)
    partial_parallel_solve = partial(parallel_solve_return, cache=cache)
    with Pool(processes=cpu_count()) as pool:  # Koristi maksimalan broj procesa
        results = pool.map(partial_parallel_solve, possible_boards)

    for success, solved_board in results:
        if success:
            print("Rješenje je pronađeno!")
            sudokutools.print_board(solved_board, size)
            # board = copy.deepcopy(solved_board)
            return solved_board

    return None


def parallel_solve_return(board, cache, size=3):
    if solve_with_cache(board, cache, size):
        return True, board
    else:
        return False, None


def solve_with_cache(board, cache, size=3):
    global broj_pokusaja
    # global start_vreme
    # start_vreme = time.time()

    blank = sudokutools.find_empty(board, size)
    if not blank:
        return True
    else:
        row, col = blank

    # cache = orded_valid_values(board, cache, size)
    for value in cache[(row, col)]:
        if sudokutools.valid(board, blank, value, size):
            board[row][col] = value
            broj_pokusaja += 1

            if solve_with_cache(board, cache, size):
                return True

            board[row][col] = 0
    return False


def orded_valid_values(board, cache, size=3):
    cache_priority = dict()
    count_appearance_row = [dict() for i in range(size**2)]
    count_appearance_col = [dict() for i in range(size**2)]
    count_appearance_block = [dict() for i in range(size**2)]

    for row in range(size**2):
        temp_list = list()

        # Iterate through the columns of a row and count appearance of numbers
        # within the cache
        for col in range(size**2):
            if (row, col) in cache.keys():
                for value in cache[(row, col)]:
                    temp_list.append(value)
        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_row[row][number] = temp_list.count(number)

    for col in range(size**2):
        temp_list = list()

        # Iterate through the rows of a column and count appearance of numbers
        # within the cache
        for row in range(size**2):
            if (row, col) in cache.keys():
                for value in cache[(row, col)]:
                    temp_list.append(value)
        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_col[col][number] = temp_list.count(number)

    # Iterate through the 9 different blocks of the board and count
    # appearance of numbers within the cache
    row_block_start = 0
    col_block_start = 0
    block_number = 0
    while True:
        row_block_end = row_block_start + size
        col_block_end = col_block_start + size
        temp_list = list()

        for row in range(row_block_start, row_block_end):
            for col in range(col_block_start, col_block_end):
                if (row, col) in cache.keys():
                    for value in cache[(row, col)]:
                        temp_list.append(value)

        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_block[block_number][number] = temp_list.count(number)

        if row_block_start == size**2-size and col_block_start == size**2-size:
            # jer size**2 - size predstavlja posljedni blok
            break
        elif col_block_start == size**2-size:
            row_block_start += size
            col_block_start = 0
        else:
            col_block_start += size
        block_number += 1

    for row in range(size**2):
        for col in range(size**2):
            temp_list = list()
            block_number = (row // size) * size + col // size
            if (row, col) in cache.keys():
                for value in cache[(row, col)]:
                    freq = count_appearance_row[row][value] + count_appearance_col[col][value] + \
                           count_appearance_block[block_number][value]
                    temp_list.append(freq)
                cache_priority[(row, col)] = temp_list

    values_found = True
    while values_found:
        old_board = copy.deepcopy(board)
        for row in range(size**2):
            for col in range(size**2):
                temp_list = list()
                block_number = (row // size) * size + col // size
                if (row, col) in cache.keys():
                    for value in cache[(row, col)]:
                        if count_appearance_row[row][value] == 1 or count_appearance_col[col][value] == 1 or \
                                count_appearance_block[block_number][value] == 1:
                            board[row][col] = value
                            # return True
        values_found = any(old != new for oldRow, newRow in zip(old_board, board) for old, new in zip(oldRow, newRow))

    for row in range(size**2):
        for col in range(size**2):
            if (row, col) in cache.keys():
                cache[(row, col)] = [i for _, i in sorted(zip(cache_priority[(row, col)], cache[(row, col)]))]
    return cache


if __name__ == "__main__":
    board = sudokutools.generate_board(3)
    start_time = time.time()
    sudokutools.print_board(board, 3)
    cache = cache_valid_values(board, 3)
    cache = orded_valid_values(board, cache, 3)
    solve_with_cache(board, cache, 3)
    sudokutools.print_board(board, 3)
    print(broj_pokusaja)
    print(f"Vrijeme izvršavanja: {(time.time() - start_time) * 1000} ms.")
    # regulartime = timeit.timeit('solve_with_cache(board, cache, 4)', globals=globals(), number=50)
    # parallel_time = timeit.timeit('parallel_solver(board, cache, 4)', globals=globals(), number=50)
    # start_time = time.time()
    # solved_board = parallel_solver(board, cache, 4)
    # if solved_board:
    #     board = solved_board
    # end_time = time.time()
    # # print(board)
    # sudokutools.print_board(board, 4)
    # print("Time taken to solve: {}".format(end_time - start_time))
    # print(f"Regualar backtracking for 50 times: {regulartime}")
    # print(f"Parallel backtracking for 50 times: {parallel_time}")
