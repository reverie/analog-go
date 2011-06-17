from math import sqrt
from voronoi import bounded_voronoi, dist, update_diagram
EPSILON = 0.00001

class Stone:
    def __init__(self, player, x, y):
        self.player = player
        self.x = x
        self.y = y
        self.group = None
    def __str__(self):
        return "(%s, %s, %s)" % (self.x, self.y, self.player.number)
    def __repr__(self):
        return "(%s, %s, %s)" % (self.x, self.y, self.player.number)

class Group:
    def __init__(self, stone):
        self.stones = [stone]

    def has_liberties(self, board):
        v = board.voronoi
        group = map(lambda x: (x.x, x.y), self.stones)
        for p in group:
            for vertex in v[p]:
                if dist(p, vertex) >= 1:
                    #print "liberty from %s to %s" % (p, vertex)
                    return True
        return False

    def kill(self, killer, board):
        size = len(self.stones)
        #print "%s killed a group of size %d" % (killer.name, size)
        for s in self.stones:
            board.stones.remove(s)
        self.stones = []
        killer.captured += size

def stone_set_group_set(stone_set):
    group_set = []
    for s in stone_set:
        if s.group not in group_set:
            group_set.append(s.group)
    return group_set

def group_set_merge(group_set):
    base = group_set[0]
    for g in group_set[1:]:
        for s in g.stones:
            s.group = base
            base.stones.append(s)

class Board:
    def __init__(self, length=18, height=18):
        self.length = length
        self.height = height
        self.stones = []
        self.init_voronoi()

    def boundary(self):
        return [(0., 0.), (0., float(self.height)), (float(self.length), float(self.height)), (float(self.length), 0.)]

    def place_stone(self, player, x, y):
        s = Stone(player, x, y)
        self.stones.append(s)
        self.update_voronoi(s)
        s.group = Group(s)
        #print "Placed stone at (%s, %s)" % (x, y)
        something_killed = False
        neighbors = self.get_neighbors(stone=s, distance=2)
        foes = filter(lambda x: x.player != s.player, neighbors)
        #print "Foes:", foes
        if foes != []:
            foe_groups = stone_set_group_set(foes)
            killed_groups = []
            for g in foe_groups:
                if not g.has_liberties(self):
                    killed_groups.append(g)
            for g in killed_groups:
                g.kill(player, self)
                something_killed = True
        neighbors = self.get_neighbors(stone=s, distance=1+EPSILON)
        friends = filter(lambda x: x.player == s.player, neighbors)
        #print "Friends:", friends
        if friends != []:
            friends_groups = stone_set_group_set(friends)
            group_set_merge(friends_groups)
        g = s.group
        if not g.has_liberties(self):
            print "***********ERROR=SUICIDE=ERROR=SUICIDE=ERROR*******"
            something_killed = True
        if something_killed:
            self.redo_voronoi()
        #print "It is in a group of size %s" % len(g.stones)
        #for s in self.stones:
            #print "there is a stone at (%s, %s) owned by %s" % (s.x, s.y, s.player.name)

    def get_neighbors(self, x=None, y=None, stone=None, distance=None):
        if stone != None:
            (x, y) = (stone.x, stone.y)
        if x == None or y == None:
            raise Exception
        return filter(lambda stone: sqrt((stone.y-y)**2+(stone.x-x)**2) < distance, self.stones)

    def init_voronoi(self):
        bound = self.boundary()
        points = []
        self.voronoi = bounded_voronoi(bound, points)

    def update_voronoi(self, stone):
        v = self.voronoi
        new_point = (stone.x, stone.y)
        bound = self.boundary()
        update_diagram(v, new_point, bound)

    def redo_voronoi(self):
        bound = self.boundary()
        points = map(lambda x: (x.x, x.y), self.stones)
        self.voronoi = bounded_voronoi(bound, points)

class Game:
    def __init__(self, players, mode):
        self.board = Board()
        self.players = players
        for i in range(len(self.players)):
            self.players[i].number = i
            self.players[i].game = self
        self.turn = None
        self.passes = None
        self.ongoing = "pre"
        self.mode = mode
    def move_allowed(self, move):
        if self.ongoing != "play":
            return False
        if move == "pass":
            return True
        (x, y) = move
        if x < 0 or y < 0:
            return False
        if x > self.board.length or y > self.board.height:
            return False
        neighborhood = self.board.get_neighbors(x=x, y=y, distance=1)
        if len(neighborhood) != 0:
            return False
        return True
    def start(self):
        self.passes = 0
        self.turn = self.players[0]
        self.ongoing = "play"
        #print ""
        #print "It is %s's move" % (self.turn.name)
        self.start_boss()
    def try_move(self, move):
        if not self.move_allowed(move):
            #print "Illegal move, try again!"
            return False
        if move == "pass":
            self.passes += 1
            print "%s passes" % (self.turn.name)
            self.players = self.players[1:]
            self.players.append(self.turn)
            self.turn = self.players[0]
            if self.passes == len(self.players):
                print "Play is over. Marking dead stones."
                self.ongoing = "mark"
                self.marked = set()
            return True
        else: #placing a stone on the board
            self.passes = 0
            x = move[0]
            y = move[1]
            #print "%s plays at (%s, %s)" % (self.turn.name, x, y)
            self.board.place_stone(self.turn, x, y)
            self.players = self.players[1:]
            self.players.append(self.turn)
            self.turn = self.players[0]
            #print "It is %s's move" % (self.turn.name)
            return True
    def mark_dead_stone(self, stone):
        if self.ongoing != "mark":
            raise Exception
        self.marked.update(stone.group.stones)
        print "Marking dead stone..."
    def unmark_dead_stone(self, stone):
        if self.ongoing != "mark":
            raise Exception
        self.marked.difference_update(stone.group.stones)
        print "Unmarking dead stone..."
    def done_marking(self):
        if self.ongoing != "mark":
            raise Exception
        self.ongoing = "done"
        print "Game over!"
        self.score_territory()
    def score_territory(self):
        for p in self.players:
            p.territory = 4
    def start_boss(self):
        if self.mode == "text":
            while(self.ongoing == "play"):
                p = self.turn
                move = p.get_move()
                self.try_move(move)
        elif self.mode == "video":
            import display
            display.start_play(self)
