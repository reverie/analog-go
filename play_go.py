import analog_go
import go_players

MODE = "video"

p1 = go_players.TextPlayer('andrew')
p2 = go_players.TextPlayer('keenan')
players = [p1, p2]
game = analog_go.Game(players, MODE)
game.start()
