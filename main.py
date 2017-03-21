#! /usr/bin/env python2
# -*- coding: latin-1 -*-
from __future__ import print_function
import os
import string

BASEPATH = os.path.dirname(__file__)

# Constantes del juego
OUTPUT = 7, 3  # Salida
DIR, X, Y, SIZE = 0, 1, 2, 3  # Posiciones de datos en tupla de coche
BLOCK_W, BLOCK_H = 5, 3  # Tamaño del bloque
WIN = COLLISION = True
TARGET = 'A'

# Caracteres para dibujar cuadros
COE = u'\u2500'  #
CNS = u'\u2502'  #
CES = u'\u250C'  #
CSO = u'\u2510'  #
CNE = u'\u2514'  #
CON = u'\u2518'  #
COES = u'\u252C'  #
CNES = u'\u251C'  #
CONS = u'\u2524'  #
CONE = u'\u2534'  #
CSOM = u'\u2593'  #


def read_levels():
    # Lectura del fichero de niveles
    filepath = os.path.join(BASEPATH, 'niveles.txt')
    if not os.path.exists(filepath):
        raise IOError('File %s does not exists.')

    fich = open(filepath, 'r')
    nlevels = int(fich.readline())
    levels = []
    for _ in range(nlevels):
        nCars = int(fich.readline())
        cars = {}
        for __, letter in zip(range(nCars), string.ascii_uppercase):
            o, x, y, s = list(fich.readline().rstrip())
            cars[letter] = o, int(x), int(y), int(s)
        levels.append(cars)
    fich.close()
    return levels


def read_records():
    # Lectura del fichero de records
    filepath = os.path.join(BASEPATH, 'records.txt')
    if not os.path.exists(filepath):
        return {}

    fich = open(filepath, 'r')
    nlevels = int(fich.readline())
    records = {}
    for _ in range(nlevels):
        level, record = map(int, fich.readline().split(' '))
        records[level] = record
    fich.close()
    return records


def save_records(records):
    # Salvado de records obtenidos en el juego actual
    filepath = os.path.join(BASEPATH, 'records.txt')
    fich = open(filepath, 'w')
    fich.write(str(len(records)) + '\n')
    for level, record in sorted(records.items()):
        fich.write('%d %i\n' % (level, record))
    fich.close()


def select_level(levels, records):
    # Verificación de selección correcta de nivel
    choosen = None
    # Cálculo de último nivel con record
    if records:
        max_level = min(len(levels), max([l for l in range(len(levels)) if l in records]) + 1)
    else:
        choosen = 1
    # Validación de entrada
    while choosen is None:
        try:
            choosen = raw_input('Elija nivel (%d-%d): ' % (1, max_level))
            choosen = int(choosen)
        except ValueError, e:
            print('Error: la entrada no es un entero.')
            choosen = None
        else:
            if not (0 < choosen <= max_level):
                choosen = None
                print('Error: el nivel elegido no existe.')
    return choosen, levels[choosen - 1]


def get_dimensions(cars):
    # Obtención de dimensiones que se ajusten a los coches del nivel
    cells = reduce(lambda x, y: list(set(x) | set(y)), map(car_range, cars.values()))
    x, y = 0, 1  # Posición de coordenadas en la tupla (x, y)
    w = max(map(lambda c: c[x], cells))
    h = max(map(lambda c: c[y], cells))
    return w + 2, h + 2  # Añadimos bordes


def print_record(level, records):
    record = records.get(level, 0)
    print('NIVEL %d - RECORD %d movimiento' % (level, record) + 's' if not record == 1 else '')


def get_horizontal_pintable(name, car):
    # Construcción de la representación de coche horizontal
    _, x, y, s = car
    # Bordes izquierdo y derecho del coche
    cells = {(x, y): [CES + COE * (BLOCK_W - 1)] +
                     [CNS + ' ' * (BLOCK_W - 1)] * ((BLOCK_H - 3) // 2) +
                     [CNS + ' %s  ' % name] +
                     [CNS + ' ' * (BLOCK_W - 1)] * ((BLOCK_H - 3) // 2) +
                     [CNE + COE * (BLOCK_W - 1)],
             (x + s - 1, y): [COE * (BLOCK_W - 1) + CSO] +
                             [' ' * (BLOCK_W - 1) + CNS] * ((BLOCK_H - 3) // 2) +
                             ['  %s ' % name.lower() + CNS] +
                             [' ' * (BLOCK_W - 1) + CNS] * ((BLOCK_H - 3) // 2) +
                             [COE * (BLOCK_W - 1) + CON]}
    # Casillas intermedias
    for xs in range(1, s - 1):
        cells[x + xs, y] = [COE * BLOCK_W] + \
                           [u' ' * BLOCK_W] * (BLOCK_H - 2) + \
                           [COE * BLOCK_W]
    return cells


def get_vertical_pintable(name, car):
    # Construcción de la representación de coche vertical
    _, x, y, s = car
    # Bordes superior e inferior derecho del coche
    cells = {(x, y): [CES + COE * (BLOCK_W - 2) + CSO] +
                     [CNS + ' ' * (BLOCK_W - 2) + CNS] * ((BLOCK_H - 3) // 2) +
                     [CNS + ' %s ' % name + CNS] +
                     [CNS + ' ' * (BLOCK_W - 2) + CNS] * ((BLOCK_H - 3) // 2) +
                     [CNS + ' ' * (BLOCK_W - 2) + CNS],
             (x, y + s - 1): [CNS + ' ' * (BLOCK_W - 2) + CNS] +
                             [CNS + ' ' * (BLOCK_W - 2) + CNS] * ((BLOCK_H - 3) // 2) +
                             [CNS + ' %s ' % name.lower() + CNS] +
                             [CNS + ' ' * (BLOCK_W - 2) + CNS] * ((BLOCK_H - 3) // 2) +
                             [CNE + COE * (BLOCK_W - 2) + CON]}
    # Casillas intermedias
    for ys in range(1, s - 1):
        cells[x, y + ys] = [CNS + ' ' * (BLOCK_W - 2) + CNS] * BLOCK_H
    return cells


def get_cars_printable(cars):
    # Proxy para obtener representación de un coche
    cells = {}
    getprintable = {'H': get_horizontal_pintable, 'V': get_vertical_pintable}
    for name, car in cars.items():
        cells.update(getprintable[car[DIR]](name, car))
    return cells


def get_output_printable(height, output):
    # Representación de la salida del nivel
    if not (0 < output[X] < height - 1):  # Orientación horizontal
        return {output: [CSOM * BLOCK_W]}
    else:  # Orientación vertical
        return {output: [CSOM] * BLOCK_H}


def update_win_cell(cells, height, output):
    # Representación especial de la casilla de salida al ganar el juego
    x, y = 0, 1
    if not (0 < output[y] < height - 1):
        cells[output][0] = CSOM * BLOCK_W
        cells[output].append([CONE + (COE * (BLOCK_W - 1))])
    else:
        cells[output][0] = CSOM + cells[output][0][1:] + CONS
        for i in range(1, BLOCK_H):
            cells[output][i] = CSOM + cells[output][i][1:] + CNS


def print_table(width, height, cars, win=False):
    # Impresión por pantalla de estado actual del tablero

    # Esquinas del tablero
    cells = {(0, 0): CES, (width - 1, 0): CSO, (0, height - 1): CNE, (width - 1, height - 1): CON}

    # Bordes superior e inferior
    for j in range(1, width - 1):
        cells[j, 0] = [COES + (COE * (BLOCK_W - 1))]
        cells[j, height - 1] = [CONE + (COE * (BLOCK_W - 1))]

    # Bordes izquierdo y derecho
    for i in range(1, height - 1):
        cells[0, i] = [CNES] + [CNS] * (BLOCK_H - 1)
        cells[width - 1, i] = [CONS] + [CNS] * (BLOCK_H - 1)

    # Inclusión de la salida en el tablero
    cells.update(get_output_printable(height, OUTPUT))

    # Inclusión de los coches en el tablero
    cells.update(get_cars_printable(cars))

    if win:  # Inclusión de la casilla de salida en caso de ganar
        update_win_cell(cells, height, OUTPUT)

    # Bucle de impresión del tablero
    for y in range(height):  # Recorrido por filas
        block_size = 1 if not y or y == height - 1 else BLOCK_H
        for i in range(block_size):  # Impresión por cada línea del bloque
            line = ''
            for x in range(width):  # Recorrido por columnas
                cell = cells.get((x, y), None)
                try:
                    line += cell[i] if cell else ' ' * BLOCK_W
                except:
                    raise IndexError('Not %d at "%s"' % (i, cell))
            print(line)


def ask_movement(cars):
    # Validación de entrada de los movimientos en el turno
    movements = ''
    while not movements:
        movements = raw_input('Movimientos = ')
        if any([x not in cars.keys() for x in movements.upper()]):
            print('Movimiento no vÃ¡lido')
            movements = ''
    return movements


def move_forwards(car):
    # Movimiento hacia adelante del coche
    if car[DIR] == 'H':
        return car[X] + 1, car[Y]
    else:
        return car[X], car[Y] + 1


def move_backwards(car):
    # Movimiento hacia atrás del coche
    if car[DIR] == 'H':
        return car[X] - 1, car[Y]
    else:
        return car[X], car[Y] - 1


def car_range(car):
    # Lista de las coordenadas de bloque ocupadas por un coche
    if car[DIR] == 'H':
        return [(j, car[Y]) for j in range(car[X], car[X] + car[SIZE])]
    else:
        return [(car[X], i) for i in range(car[Y], car[Y] + car[SIZE])]


def check_win(car):
    # Verificación de la coordenadas de salida entre las casillas de un coche
    return OUTPUT in car_range(car)


def check_collision(carid, car, cars, width, height):
    # Verificación de colisión con los bordes del tablero
    if not all([0 < x < width - 1 and 0 < y < height - 1 for x, y in car_range(car)]):
        return True

    # Verificación de intersección entre las casillas de dos coches
    if any([any([(x, y) in car_range(c) for k, c in cars.items() if k != carid]) for x, y in car_range(car)]):
        return True

    return False


def make_movements(width, height, cars, movements):
    # Ejecución de los movimientos dados
    for i, move in enumerate(movements):
        carid = move.upper()
        car = cars[carid]
        # Cálculo de nuevas coordenadas del coche
        if move.isupper():
            x, y = move_backwards(car)
        else:
            x, y = move_forwards(car)
        car = car[DIR], x, y, car[SIZE]
        if carid == TARGET:
            if check_win(car):  # Verificación de coche objetivo fuera del tablero
                cars.update({carid: car})
                return i + 1, None, WIN
        # Verificación de colisión con las nuevas coordenadas
        if not check_collision(carid, car, cars, width, height):
            cars.update({carid: car})
        else:
            return i, move, None
    return i + 1, None, None


def play(cars):
    # Función principal del juego
    win = None
    count = 0
    width, height = get_dimensions(cars)  # Cálculo de tamaño del tablero
    print_table(width, height, cars)
    # Inicio del bucle del juego
    movements = ask_movement(cars)
    moves, collision, win = make_movements(width, height, cars, movements)
    count += moves
    while not win:
        if collision:
            print('Movimiento %s imposible por bloqueo' % collision)
        print_table(width, height, cars)
        movements = ask_movement(cars)
        moves, collision, win = make_movements(width
                                               , height, cars, movements)
        count += moves

    # Impresión final del juego
    print_table(width, height, cars, win)
    return count


def ask_play_again():
    return raw_input('Desea pasar al siguiente nivel? [S/N]_').lower() == 's'


def main():
    # Función principal del programa
    levels = read_levels()
    records = read_records()
    level, cars = select_level(levels, records)  # Selección de nivel
    while level is not None:
        print_record(level, records)  # Impresión de record actual
        movements = play(cars)  # Juego
        print('ENHORABUENA, HA COMPLETADO EL NIVEL!')
        print('Movimientos: %d' % movements, end=' ')
        # Verificación de nuevo record
        last_record = records.get(level, None)
        if not last_record or movements > last_record:
            records[level] = movements
            save_records(records)
            print('(NUEVO RECORD!)')
        else:
            print()
        if ask_play_again():  # Consulta sobre paso al siguiente nivel
            level += 1
            cars = levels[level - 1]
        else:
            level = None
    save_records(records)


if __name__ == '__main__':
    main()
