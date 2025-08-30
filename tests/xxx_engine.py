import pyved_engine as pyv


HELP_MSG = 'press ESC to exit, any key to change bg_color...'
CAPTION = 'my first video game, hi mom!'


pyv.init(1, wcaption=CAPTION)
pygame = pyv.pygame
screen = pyv.get_surface()
color_idx = 0
allcolors = ('pink', 'yellow', 'purple')
bg_color = allcolors[0]
print(HELP_MSG)
gameover = False


while not gameover:  # game loop
    for ev in pygame.event.get():
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                gameover = True
            else:
                color_idx = (color_idx + 1) % len(allcolors)
    # update "game logic"
    bg_color = allcolors[color_idx]
    # update the display
    screen.fill(bg_color)
    pyv.flip()
print('done!')
