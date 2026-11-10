

import tkinter as tk

WIDTH = 610
HEIGHT = 400



class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y, speed):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        if coords[0] <= 0 or coords[2] >= WIDTH:    
            self.direction[0] *= -1
        if coords[1] <= 0:                          
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5


        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                p = game_object.get_position()
                self.direction[1] = -1
                if x < (p[0] + p[2]) / 2:
                    self.direction[0] = -1
                else:
                    self.direction[0] = 1
                return

        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            coords = game_objects[0].get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1



class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='white')
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
     
        if coords[0] + offset < 0:
            offset = -coords[0]
        if coords[2] + offset > WIDTH:
            offset = WIDTH - coords[2]
        super().move(offset, 0)
        if self.ball is not None:      
            self.ball.move(offset, 0)

    def move_to(self, x):              
        coords = self.get_position()
        center = (coords[0] + coords[2]) / 2
        self.move(x - center)



class Brick(GameObject):
    COLORS = {1: '#cccccc', 2: '#888888', 3: '#555555'}  

    def __init__(self, canvas, x, y, hits):
        self.width = 70
        self.height = 20
        self.hits = hits
        self.points = hits * 10          
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=Brick.COLORS[hits], outline='black', tags='brick')
        super().__init__(canvas, item)

    def hit(self):
        """Returns True when the brick is destroyed."""
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return True
        self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
        return False


class BonusBrick(Brick):
    """NEW: a bright white brick, only 1 hit but gives 50 points (inheritance)."""
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 1)
        self.points = 50
        self.canvas.itemconfig(self.item, fill='white')



class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0,
                                width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))
        self.canvas.bind('<Motion>', self.mouse_move)
        self.canvas.bind('<space>', lambda _: self.start_game())
        self.canvas.bind('<r>', lambda _: self.restart())

        self.new_game()

    def new_game(self):
        self.canvas.delete('all')
        self.lives = 3
        self.score = 0
        self.level = 1
        self.items = {}
        self.ball = None
        self.playing = False
        self.finished = False

        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle
        self.hud = self.draw_text(300, 20, '', 14)
        self.build_bricks()
        self.setup_game()

    def restart(self):
        if self.finished:           
            self.new_game()

 
    def build_bricks(self):
        rows = self.level + 2          
        for row in range(rows):
            for col in range(8):
                x = 38 + col * 76
                y = 60 + row * 24
                if col == 3 and row == rows - 1:
                    brick = BonusBrick(self.canvas, x, y)
                elif row == 0:
                    brick = Brick(self.canvas, x, y, min(self.level + 1, 3))
                else:
                    brick = Brick(self.canvas, x, y, 1)
                self.items[brick.item] = brick

    def setup_game(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 335, 5 + self.level)   
        self.paddle.set_ball(self.ball)
        self.playing = False
        self.update_hud()
        self.text = self.draw_text(300, 200, 'Press SPACE to start', 28)

    def draw_text(self, x, y, text, size=40):
        font = ('Arial', size, 'bold')
        return self.canvas.create_text(x, y, text=text, font=font, fill='white')

    def update_hud(self):
        text = 'Score: %d     Level: %d     Lives: %d' % (self.score,self.level,self.lives)
        self.canvas.itemconfig(self.hud, text=text)

   
    def mouse_move(self, event):
        if not self.finished:
            self.paddle.move_to(event.x)

    def start_game(self):
        if self.playing or self.finished:
            return
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.playing = True
        self.game_loop()

  
    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.next_level()
        elif self.ball.get_position()[3] >= self.height:
            self.lose_life()
        else:
            self.ball.update()
            self.after(20, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick):
                if obj.hit():
                    self.score += obj.points
        self.update_hud()

    def next_level(self):
        self.level += 1
        if self.level > 3:
            self.finished = True
            self.playing = False
            self.ball.delete()
            self.draw_text(300, 200, 'You Win!')
            self.draw_text(300, 250, 'Press R to play again', 16)
        else:
            self.build_bricks()
            self.setup_game()

    def lose_life(self):
        self.lives -= 1
        if self.lives == 0:
            self.finished = True
            self.playing = False
            self.update_hud()
            self.draw_text(300, 200, 'Game Over!')
            self.draw_text(300, 250, 'Press R to restart', 16)
        else:
            self.setup_game()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker - 042')
    game = Game(root)
    game.mainloop()