"""
Just a demo to showcase how one would program the popular "Breakout" game using pyved.

Remark:
that examples uses the non-atomic game loop, ensuring its compatibility with web ctx.
Using c=pyv.get_game_ctrl() then c.loop()
is very handy but it becomes tricky when sharing games online
"""
import math
from pyved_engine.abstraction.PygameWrapper import PygameWrapper
import pyved_engine
# Step 4: (usage) Injecting the dependency explicitly:
engine_depc = PygameWrapper()
pyv = pyved_engine.EngineRouter(
    engine_depc
)
pyv.bootstrap_e()


# --------------------------------
# CONSTANTS
# (Define some colors)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
WALL_X, WALL_Y = 4, 80
# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
# misc
SCR_WIDTH = 960

# --------------------------------
# GLOBAL VARIABLES
clock = screen = None
player_lost = False
blocks = None
player = None
allsprites = font = balls = background = ball = None


class Block(pyv.Sprite):
    """This class represents each block that will get knocked out by the ball
    It derives from the "Sprite" class"""

    def __init__(self, color, x, y):
        """ Constructor. Pass in the color of the block,
            and its x and y position. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create the image of the block of appropriate size
        # The width and height are sent as a list for the first parameter.
        self.image = pyv.surface_create([BLOCK_W, BLOCK_H])

        # Fill the image with the appropriate color
        self.image.fill(color)

        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()

        # Move the top left of the rectangle to x,y.
        # This is where our block will appear..
        self.rect.x = x
        self.rect.y = y


class Ball(pyv.Sprite):
    """ This class represents the ball
        It derives from the "Sprite" class"""

    # Speed in pixels per cycle
    speed = 10.0

    # Floating point representation of where the ball is
    x, y = BALL_INIT_POS

    # Direction of ball (in degrees)
    direction = 200

    width, height = BALL_SIZE, BALL_SIZE

    # Constructor. Pass in the color of the block, and its x and y position
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create the image of the ball
        self.image = pyv.surface_create([self.width, self.height])

        # Color the ball
        self.image.fill(WHITE)

        # Get a rectangle object that shows where our image is
        self.rect = self.image.get_rect()

        # Get attributes for the height/width of the screen
        self.screenwidth, self.screenheight = pyv.get_surface().get_size()

    def bounce(self, diff):
        """ This function will bounce the ball
            off a horizontal surface (not a vertical one) """

        self.direction = (180 - self.direction) % 360
        self.direction -= diff

    def update(self):
        """ Update the position of the ball. """
        # Sine and Cosine work in degrees, so we have to convert them
        direction_radians = math.radians(self.direction)

        # Change the position (x and y) according to the speed and direction
        self.x += self.speed * math.sin(direction_radians)
        self.y -= self.speed * math.cos(direction_radians)

        # Move the image to where our x and y are
        self.rect.x = self.x
        self.rect.y = self.y

        # Do we bounce off the top of the screen?
        if self.y <= 0:
            self.bounce(0)
            self.y = 1

        # Do we bounce off the left of the screen?
        if self.x <= 0:
            self.direction = (360 - self.direction) % 360
            self.x = 1

        # Do we bounce of the right side of the screen?
        if self.x > self.screenwidth - self.width:
            self.direction = (360 - self.direction) % 360
            self.x = self.screenwidth - self.width - 1

        # Did we fall off the bottom edge of the screen?
        if self.y > self.screenheight:
            return True
        return False


class Player(pyv.Sprite):
    """ This class represents the bar at the bottom that the
    player controls. """

    def __init__(self):
        """ Constructor for Player. """
        # Call the parent's constructor
        super().__init__()

        self.width = 75
        self.height = 15
        self.image = pyv.surface_create([self.width, self.height])
        self.image.fill(WHITE)

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.screenwidth, self.screenheight = pyv.get_surface().get_size()

        self.rect.x = 0
        self.rect.y = self.screenheight - self.height

    def update(self):
        """ Update the player position. """
        # Get where the mouse is
        pos = pyv.get_mouse_coords()
        # Set the left side of the player bar to the mouse position
        self.rect.x = pos[0]
        # Make sure we don't push the player paddle
        # off the right side of the screen
        if self.rect.x > self.screenwidth - self.width:
            self.rect.x = self.screenwidth - self.width


def init(vmst=None):
    global player_lost, screen, clock, blocks, player, allsprites, font, balls, background, ball
    pyv.init(1, wcaption='Breakout', maxfps=25)  # name the game-> window caption
    screen = pyv.get_surface()

    # This is a font we use to draw text on the screen (size 36)
    font = pyv.new_font_obj(None, 36)

    # Create a surface we can draw on
    background = pyv.surface_create(screen.get_size())

    # Create sprite lists
    blocks = pyv.SpriteGroup()
    balls = pyv.SpriteGroup()
    allsprites = pyv.SpriteGroup()

    # Create the player paddle object
    player = Player()
    allsprites.add(player)

    # Create the ball
    ball = Ball()
    allsprites.add(ball)
    balls.add(ball)

    # The top of the block (y position)
    top = WALL_Y

    # --- Create blocks
    # Five rows of blocks
    for row in range(5):
        # 32 columns of blocks
        column = 0
        while WALL_X+(column+1)*(BLOCK_W+BLOCK_SPACING) < SCR_WIDTH:
            # Create a block (color,x,y)
            x = WALL_X + column * (BLOCK_W + BLOCK_SPACING)
            y = top
            custom_color = 150, (x * 0.27) % 256, (y * 1.22) % 256
            block = Block(custom_color, x, y)
            blocks.add(block)
            allsprites.add(block)
            column += 1
            # print(column, ':', block.rect.left, '<->', block.rect.right)

        # Move the top of the next row down
        top += BLOCK_H + BLOCK_SPACING

    # Clock to limit speed
    clock = pyv.create_clock()


def update(time_info=None):
    global player_lost, clock, blocks, player, allsprites, font, ball

    # Main program loop
    # Process the events in the game
    for event in pyv.event_get():
        if event.type == pyv.EngineEvTypes.Quit:
            pyv.vars.gameover = True

    # Update the ball and player position as long
    # as the game is not over.
    if not player_lost:
        # Update the player and ball positions
        player.update()
        player_lost = ball.update()

    # See if the ball hits the player paddle
    if pyv.sprite_collision(player, balls, False):
        # The 'diff' lets you try to bounce the ball left or right
        # depending where on the paddle you hit it
        diff = (player.rect.x + player.width / 2) - (ball.rect.x + ball.width / 2)

        # Set the ball's y position in case
        # we hit the ball on the edge of the paddle
        ball.rect.y = screen.get_height() - player.rect.height - ball.rect.height - 1
        ball.bounce(diff)

    # Check for collisions between the ball and the blocks
    deadblocks = pyv.sprite_collision(ball, blocks, True)

    # If we actually hit a block, bounce the ball
    if len(deadblocks) > 0:
        ball.bounce(0)

        # Game ends if all the blocks are gone
        if len(blocks) == 0:
            player_lost = True

    # Clear the screen
    screen.fill(BLACK)

    # If we are done, print game over
    if player_lost:
        text = font.render("Game Over", True, WHITE)
        textpos = text.get_rect(centerx=background.get_width() / 2)
        textpos.top = 300
        screen.blit(text, textpos)

    # Draw Everything
    allsprites.draw(screen)

    # Flip the screen and show what we've drawn
    pyv.flip()


def end_game(vmst=None):
    pyv.close_game()


pyv.run_game(init, update, end_game)
