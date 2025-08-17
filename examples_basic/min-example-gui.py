from pyved_engine.sublayer_implem import PygameWrapper
import pyved_engine
# Step 4: (usage) Injecting the dependency explicitly:
engine_depc = PygameWrapper()
pyv = pyved_engine.EngineRouter(
    engine_depc
)
pyv.bootstrap_e()

pyv.init(pyv.LOW_RES_MODE)


screen = pyv.get_surface()
width, height = screen.get_size()

INIT_TXT = 'hello user this\nis\nsome\ndope\ntext'
ALT_TXT = 'i\nunderstand that\nyou watch the console'
USING_IMGBASED_FT = True

pyv.preload_assets(
    {'asset_list': ['niobe_font.png', ], 'sound_list': [], 'data_files': []}, prefix_asset_folder='mixed_assets/', prefix_sound_folder='./'
)

if USING_IMGBASED_FT:
    ft_obj = pyv.gui.ImgBasedFont(
        (15, 130, 243),  # we specify: the color that should be viewed as transparent
        img=pyv.vars.images['niobe_font']
    )  # special font format
else:
    FT_PATH = 'mixed_assets/alphbeta.ttf'
    ft_obj = pyv.new_font_obj(FT_PATH, 16)


block = pyv.gui.TextBlock(ft_obj, INIT_TXT, (0, 0, 0))
block.rect.center = (width // 2, height // 2)  # lets center the text block
print('*~*~*\npress and hold the space bar ; press ENTER to change alignment')
ended = False

while not ended:
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            ended = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_RETURN:
                block.text_align = (block.text_align + 1) % 2  # switch text align
            elif ev.key == pyv.evsys0.K_SPACE:
                block.text = ALT_TXT
            elif ev.key == pyv.evsys0.K_ESCAPE:
                ended = True
        elif ev.type == pyv.evsys0.KEYUP:
            if not pyv.evsys0.key.get_pressed()[pyv.evsys0.K_SPACE]:
                block.text = INIT_TXT
    screen.fill('white')
    block.draw(screen)
    pyv.flip()
pyv.quit()
