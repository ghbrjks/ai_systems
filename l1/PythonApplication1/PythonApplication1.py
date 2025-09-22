import pygame
import sys
import os

N = 5
solution_count = 0

chessboard = [[0 for _ in range(N)] for _ in range(N)]

knight_moves = [(2, -1), (2, 1), (1, 2), (-1, 2),
                (-2, 1), (-2, -1), (1, -2), (-1, -2)]

FPS = 60
pygame.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
cellW = size[0] // N
cellH = size[1] // N
font = pygame.font.SysFont("Arial", 30)

# создание папки для решений
if not os.path.exists("solutions"):
    os.makedirs("solutions")

# рисование доски
def draw_board():
    screen.fill(WHITE)
    pygame.event.get()
    for i in range(N):
        for j in range(N):
            rect = pygame.Rect(i * cellW, j * cellH, cellW, cellH)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if chessboard[i][j] != 0:
                text = font.render(str(chessboard[i][j]), True, BLACK)
                text_pos = text.get_rect(center=rect.center)
                screen.blit(text, text_pos)

# проеверка возможен ли ход
def valid_move(x, y):
    return (0 <= x < N and 0 <= y < N and chessboard[x][y] == 0)

# рассчет количества ходов по эвристике Варнсдорфа
def count_moves(x, y):
    cnt = 0
    for dx, dy in knight_moves:
        nx, ny = x + dx, y + dy
        if valid_move(nx, ny):
            cnt += 1
    return cnt

# метод перебора
def brute_force(x: int, y: int, step: int):
    global solution_count

    # рисование доски
    chessboard[x][y] = step
    draw_board()
    pygame.display.update()
    clock.tick(FPS)

    # условие правильного решения
    if step == N * N:
        solution_count += 1
        pygame.image.save(screen, f"solutions/solution_{solution_count}.png")
        print(f"Найдено решение #{solution_count}")
        # откат
        chessboard[x][y] = 0
        return

    # эвристика Варнсдорфа
    moves = []
    for dx, dy in knight_moves:
        nx, ny = x + dx, y + dy
        if valid_move(nx, ny):
            moves.append((count_moves(nx, ny), nx, ny))

    moves.sort(key=lambda m: m[0])

    for _, nx, ny in moves:
        brute_force(nx, ny, step + 1)

    # откат
    chessboard[x][y] = 0
    draw_board()
    pygame.display.update()
    clock.tick(FPS)

# запуск поиска
brute_force(0, 0, 1)

print(f"Всего решений найдено: {solution_count}")

running = True
while running:
    clock.tick(FPS)
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
draw_board()