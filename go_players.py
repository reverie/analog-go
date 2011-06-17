class TextPlayer:
    def __init__(self, name):
        self.name = name
        self.captured = 0
        self.game = None
        self.number = None
    def get_move(self):
        move = raw_input()
        try:
            move = map(float, move.split(','))
        except:
            move = "pass"
        return move

class GraphicsPlayer:
    def __init__(self, name, display):
        self.name = name
        self.captured = 0
        self.territory = 0
        self.game = None
        self.number = None
        self.display = display
