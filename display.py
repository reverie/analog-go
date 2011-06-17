import sys, pygame, random, time
from analog_go import EPSILON

BOARD_START = (40, 40)
GRID_UNIT_PIXELS = 20
RADIUS = GRID_UNIT_PIXELS/2
ROWS = 19
BOARD_WIDTH = (ROWS-1)*GRID_UNIT_PIXELS
BOARD_RECT = (BOARD_START[0], BOARD_START[1], BOARD_WIDTH+1, BOARD_WIDTH+1)

size = (width, height) = (640, 480)
black = (0, 0, 0)
grid = (20, 20, 20)
white = (200, 200, 200)
red = (200, 0, 0)
green = (0, 200, 0)
grey = (100, 100, 100)
bg = (100, 50, 25)
alpha = (0, 255, 1)

randstate = random.getstate()

stone = pygame.Surface((GRID_UNIT_PIXELS, GRID_UNIT_PIXELS))
stone.fill(alpha)
stone.set_colorkey(alpha)
stonerect = stone.get_rect()
black_stone = stone.copy()
white_stone = stone.copy()
black_dead_stone = stone.copy()
white_dead_stone = stone.copy()
pygame.draw.circle(black_stone, black, (RADIUS, RADIUS), RADIUS)
pygame.draw.circle(white_stone, white, (RADIUS, RADIUS), RADIUS)
pygame.draw.circle(black_dead_stone, grey, (RADIUS, RADIUS), RADIUS)
pygame.draw.circle(white_dead_stone, grey, (RADIUS, RADIUS), RADIUS)
pygame.draw.circle(black_dead_stone, black, (RADIUS, RADIUS), RADIUS, 3)
pygame.draw.circle(white_dead_stone, white, (RADIUS, RADIUS), RADIUS, 3)
pygame.draw.circle(black_dead_stone, alpha, (RADIUS, RADIUS), 4)
pygame.draw.circle(white_dead_stone, alpha, (RADIUS, RADIUS), 4)


pygame.init()
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 30)
screen = pygame.display.set_mode(size)

def pos_rect(row, col):
    start = stonerect.move(BOARD_START)
    moved = start.move(row*GRID_UNIT_PIXELS, col*GRID_UNIT_PIXELS)
    centered = moved.move(-stonerect.width/2, -stonerect.height/2)
    return centered

def draw_board(surface):
    for row in range(ROWS):
        start = (BOARD_START[0], BOARD_START[1]+row*GRID_UNIT_PIXELS)
        end = (BOARD_START[0]+BOARD_WIDTH, BOARD_START[1]+row*GRID_UNIT_PIXELS)
        pygame.draw.line(surface, grid, start, end)
    for col in range(ROWS):
        start = (BOARD_START[0]+col*GRID_UNIT_PIXELS, BOARD_START[1])
        end = (BOARD_START[0]+col*GRID_UNIT_PIXELS, BOARD_START[1]+BOARD_WIDTH)
        pygame.draw.line(surface, grid, start, end)
    pygame.draw.rect(surface, black, BOARD_RECT, 4)
        
def draw_stones(surface, stones, game):
    stone_rects = []
    for s in stones:
        x = s.x
        y = s.y
        color = s.player.number
        stone_position = pos_rect(x, y)
        stone_rects.append((s, stone_position))
        if not color:
            if game.ongoing == "mark" and s in game.marked:
                screen.blit(black_dead_stone,stone_position)
            else:
                screen.blit(black_stone,stone_position)
        else:
            if game.ongoing == "mark" and s in game.marked:
                screen.blit(white_dead_stone,stone_position)
            else:
                screen.blit(white_stone,stone_position)
    return stone_rects

def pixels_to_board(xy):
    (px_x, px_y) = xy
    px_x -= BOARD_START[0]
    px_y -= BOARD_START[1]
    x = float(ROWS-1)*px_x/BOARD_WIDTH
    y = float(ROWS-1)*px_y/BOARD_WIDTH
    return (x, y)

def board_to_pixels(xy):
    (x, y) = xy
    px_x = int(x*BOARD_WIDTH/(ROWS-1))
    px_y = int(y*BOARD_WIDTH/(ROWS-1))
    px_x += BOARD_START[0]
    px_y += BOARD_START[1]
    return (px_x, px_y)

def highlight_stone(stone):
    xy = (stone.x, stone.y)
    p_xy = board_to_pixels(xy)
    pygame.draw.circle(screen, red, p_xy, RADIUS, 1)

def highlight_group(group):
    for s in group.stones:
        highlight_stone(s)

def distance(p1, p2):
    from math import sqrt
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt(dx**2 + dy**2)

def dist_1(start, direction):
    d = distance(start, direction)
    grower = 1+EPSILON/2
    vector = (direction[0]-start[0], direction[1]-start[1])
    vector = (vector[0]*grower, vector[1]*grower)
    unit = (vector[0]/d, vector[1]/d)
    return (start[0]+unit[0], start[1]+unit[1])

def stone_intersect(s0, s1):
    p1 = (s0.x, s0.y)
    p2 = (s1.x, s1.y)
    from voronoi import halfplane, normalize
    (midpoint, slope) = halfplane(p1, p2)[0]
    dist = distance(p1, p2)
    from math import sqrt
    mp_dist = sqrt(1 - (dist/2)**2)+EPSILON/2
    from operator import add, sub, mul
    vector = (1, slope)
    vector = normalize(vector)
    vector = map(mul, vector, [mp_dist]*2)
    choice_1 = map(add, midpoint, vector)
    choice_2 = map(sub, midpoint, vector)
    return (choice_1, choice_2)

def draw_stone_poly(stone, game):
    v = game.board.voronoi
    poly = v[(stone.x, stone.y)]
    pp = map(board_to_pixels, poly)
    pygame.draw.aalines(screen, grey, True, pp, 1)



def start_play(game):
    while game.ongoing == "play":
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(bg)
        draw_board(screen)
        stones = game.board.stones
        stone_rects = draw_stones(screen, stones, game)
        mouse_pos = pygame.mouse.get_pos()
        stone_pos = pixels_to_board(mouse_pos)
        highlight_stone = False
        mouse_on_stone = False
        mouse_stone = None
        for s in stones:
            draw_stone_poly(s, game)
        for (s, r) in stone_rects:
            if not r.collidepoint(mouse_pos[0], mouse_pos[1]):
                continue
            d = distance(r.center, mouse_pos)/RADIUS
            if d > 1:
                continue
            mouse_on_stone = True
            mouse_stone = s
            if d <= 0.3 or (s.player != game.turn):
                highlight_stone = True
                highlight_group(s.group)
                #draw_stone_poly(s, game)
            break
        if mouse_on_stone and not highlight_stone: #figure out new stone_pos
            stone_pos = dist_1((s.x, s.y), stone_pos)
            if not game.move_allowed(stone_pos):
                neighbors = game.board.get_neighbors(x=stone_pos[0], y=stone_pos[1], distance=(1+EPSILON))
                if len(neighbors) == 2:
                    neighbors.remove(mouse_stone)
                    intheway = neighbors[0]
                    choices = stone_intersect(mouse_stone, intheway)
                    d0 = distance(stone_pos, (choices[0][0], choices[0][1]))
                    d1 = distance(stone_pos, (choices[1][0], choices[1][1]))
                    if d0 < 1:
                        stone_pos = choices[0]
                    else:
                        stone_pos = choices[1]

        if not highlight_stone:
            if game.move_allowed(stone_pos):
                pygame.draw.circle(screen, green, board_to_pixels(stone_pos), RADIUS, 1)
                neighbors = game.board.get_neighbors(x=stone_pos[0], y=stone_pos[1], distance=(1+EPSILON))
                neighbors = filter(lambda s: s.player == game.turn, neighbors)
                for n in neighbors:
                    pygame.draw.aaline(screen, grey, board_to_pixels(stone_pos), board_to_pixels((n.x, n.y)))
            else:
                pygame.draw.circle(screen, grey, board_to_pixels(stone_pos), RADIUS, 1)
        player = font.render("Turn: %s" % game.turn.name, True, black)
        screen.blit(player, (420, 400))
        text = font.render("Pass", True, black)
        text_shadow = font.render("Pass", True, green)
        if (420 < mouse_pos[0] < 400+text.get_width()) and \
            (100 < mouse_pos[1] < 100+text.get_height()):
            mouse_on_pass = True
        else:
            mouse_on_pass = False
        if mouse_on_pass:
            screen.blit(text_shadow, (420+1, 100+1))
        screen.blit(text, (420, 100))
        pygame.display.flip()
        if pygame.mouse.get_pressed()[0]:
            if mouse_on_pass:
                game.try_move("pass")
                time.sleep(0.5)
            else:
                move = stone_pos
                game.try_move(move)
    while game.ongoing == "mark":
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        screen.fill(bg)
        draw_board(screen)
        stones = game.board.stones
        stone_rects = draw_stones(screen, stones, game)
        mark_text = font.render("Mark dead", True, black)
        screen.blit(mark_text, (420, 100))
        done_text = font.render("Done", True, green)
        screen.blit(done_text, (421, 401))
        text = font.render("Done", True, black)
        screen.blit(text, (420, 400))
        mouse_pos = pygame.mouse.get_pos()
        stone_pos = pixels_to_board(mouse_pos)
        highlight_stone = False
        mouse_on_stone = False
        mouse_stone = None
        for (s, r) in stone_rects:
            if not r.collidepoint(mouse_pos[0], mouse_pos[1]):
                continue
            d = distance(r.center, mouse_pos)/RADIUS
            if d > 1:
                continue
            mouse_on_stone = True
            mouse_stone = s
            highlight_stone = True
            highlight_group(s.group)
            break
        if mouse_stone:
            if pygame.mouse.get_pressed()[0]:
                game.mark_dead_stone(mouse_stone)
                print "Stone marked!"
            if pygame.mouse.get_pressed()[2]:
                game.unmark_dead_stone(mouse_stone)
                print "Stone unmarked!"
        if (420 < mouse_pos[0] < 400+done_text.get_width()) and \
            (400 < mouse_pos[1] < 400+done_text.get_height()) and \
            pygame.mouse.get_pressed()[0]:
            mouse_on_done = True
        else:
            mouse_on_done = False
        if mouse_on_done:
            game.done_marking()
        pygame.display.flip()

    small_font = pygame.font.Font(pygame.font.get_default_font(), 10)
    for (num, p) in enumerate(game.players):
        scoreline = "%s's score: %s captures + %s territory = %s" % (p.name, p.captured, p.territory, p.captured+p.territory)
        text = small_font.render(scoreline, True, black)
        screen.blit(text, (410, 200+num*30))
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        pygame.display.flip()
