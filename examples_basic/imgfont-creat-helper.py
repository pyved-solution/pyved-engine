"""
this file can help to convert TTF-based fonts to image-based fonts,
can be handy for various projects when attempting to port the game
so it runs nicely in the web context
"""
import pyved_engine as pyv


pyv.init(pyv.RETRO_MODE)

screen = pyv.get_surface()
width, height = screen.get_size()
FT_PATH = 'mixed_assets/alphbeta.ttf'
pyg_font = pyv.new_font_obj(FT_PATH, 12)

block = pyv.gui.TextBlock(
    pyg_font, 'no text', (255, 0, 0)  # pick either pyg_font or custom_ft
)
block.text_align = 0  # here, 0 means: left aligned text

block.rect.center = (width // 2, height // 2)  # center the text block relatively to the screen
print('*~*~*\npress and hold the space bar ; press ENTER to change alignment')
can_exit = False

GL_BG_COLOR = (0, 0, 0)
block.debug = 0

# sert a afficher tous les car. sans exception!
INIT_TXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZa\nabcdefghijklmnopqrstuvwxyz.\n"
INIT_TXT += ".-,:+\'!?0\n0123456789()/_=\\[]*\"<>;@$%{}'\n"
block.text = INIT_TXT
mod = False

while not can_exit:
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            can_exit = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_RETURN:
                block.text_align = (block.text_align + 1) % 2  # switch text align
            elif ev.key == pyv.evsys0.K_ESCAPE:
                can_exit = True

    if pyv.evsys0.pressed_keys()[pyv.evsys0.K_SPACE]:
        if block.text == INIT_TXT:
            block.text = 'Coucou cest un test et cest\nnimporte quoi ce que l\'on tape ici'
            mod = True
    else:
        if mod:
            block.text = INIT_TXT
            mod = False
    screen.fill(GL_BG_COLOR)
    block.draw(screen)
    pyv.flip()

pyv.quit()
