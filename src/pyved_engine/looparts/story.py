"""
this file is mostly "glue code" to hold together the modern gamedev API (actor-based)
 along with legacy parts of the code that are contained within the "polarbear" pyv sub-module
"""
import collections
import glob
import json
import random
import re
# from .. import pe_vars as _vars
# from ..foundation.events import EvListener, EngineEvTypes
from ..actors_pattern import new_actor, peek


# - aliases
# pygame = _hub.pygame  # alias to keep on using pygame, easily
from .. import core

pyv = core.ref_engine()
polarbear = pyv.polarbear

pbear_frects_mod = polarbear.frects
Frect = pbear_frects_mod.Frect
default_border = polarbear.default_border
p_draw_text = polarbear.draw_text
render_text = polarbear.render_text

# - constants
ANCHOR_CENTER = pbear_frects_mod.ANCHOR_CENTER
ANCHOR_UPPERLEFT = pbear_frects_mod.ANCHOR_UPPERLEFT
MENU_ITEM_COLOR = (150, 145, 130)
MENU_SELECT_COLOR = (128, 250, 230)
DEFAULT_FONT_SIZE_CONV_MENU = 24


class Transition:
    def __init__(self, trigger, next_state_label):
        self.trigger = trigger
        self.next_state_label = next_state_label

    def is_triggered(self, info):
        return self.trigger == info

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.trigger, self.next_state_label)


class State:
    def __init__(self, label, message, transitions, image=None, is_initial=False, is_terminal=False):
        self.label = label
        self.message = message
        self.transitions = transitions
        self.image = image
        self._initial = is_initial
        self._terminal = is_terminal

    def process_input(self, info):
        # Processes input to determine the next state
        if self.is_terminal():
            return None
            # raise RuntimeError('Attempting to act while in a terminal state')
        for transition in self.transitions:
            if transition.is_triggered(info):
                return transition.next_state_label

    def is_terminal(self):
        return self._terminal

    def is_initial(self):
        return self._initial


class Automaton:
    def __init__(self, *li_automata):
        """
        :param li_automata: 1+ pair or pairs that have the format: (automaton_name, automaton_data)
        """
        self.states = {}
        self.current_state_label = None

        self.automata_storage = dict()
        for elt in li_automata:
            name, packed_data = elt
            self.automata_storage[name] = packed_data

        self.inner_data = None
        first_automaton_dat = li_automata[0][1]
        self.load_from_json(first_automaton_dat)

    def load_from_json(self, data):
        self.inner_data = data
        #with open(file_path, 'r') as f:
        #    data = json.load(f)
        for state_data in data['states']:
            transitions = [Transition(t['trigger'], t['next_state']) for t in state_data.get('transitions', [])]
            state = State(
                state_data['label'],
                state_data['msg'],
                transitions,
                image=state_data.get('image', None),
                is_initial=state_data.get('initial', False),
                is_terminal=state_data.get('terminal', False)
            )
            self.states[state.label] = state
        self.reset()

    def handle_input(self, info) -> int:
        """
        Advances to the next state based on input

        :param info: text
        :return: 0 (no transition), 1 (simple transition), 2 (transition to another automaton)
        """
        next_state_label = self.get_current_state().process_input(info)
        if next_state_label is None:
            return 0

        if re.match(r'encounter_\w+', next_state_label):
            self.load_from_json(self.automata_storage[next_state_label])
            return 2

        self.current_state_label = next_state_label
        return 1

    def get_current_state(self):
        return self.states[self.current_state_label]

    def reset(self):
        for state in self.states.values():
            if state.is_initial():
                self.current_state_label = state.label
                break
        else:
            raise ValueError("No initial state defined in the JSON file.")

    def display_image(self):
        current_state = self.get_current_state()
        if current_state.image:
            print(f"Image: {current_state.image}")


# - fct qui encapsule tout pour donner une interface plus simple (actor-based)
def new_automaton_viewer(li_automata, fontname=None):
    if not (isinstance(li_automata, list) or isinstance(li_automata, tuple)):
        raise ValueError('Error type, in new_automaton_viewer: expected type for li_automata-> list/tuple')

    # we have to pass args differently...
    ref_automaton = Automaton(
        *[(automaton_name, pyv.data[automaton_name]) for automaton_name in li_automata]
    )
    # declare what actor contains
    data = {
        'ref_viewer': new_conversation_view_actor(ref_automaton, fontname)
    }

    # - behavior
    def on_conv_begins(this, ev):
        peek(this.ref_viewer).active = True

    # evsys4
    # data['wrapped_obj'].turn_on()
    return new_actor('automaton_viewer', locals())


# ---------------------------------------
#  all below comes from old rpgmenu (polarbear)
# ---------------------------------------
class MenuItem(object):
    def __init__(self, msg, value, desc, menu):
        self.value = value
        self.desc = desc
        self.font = menu.font
        self.width = menu.w
        self.justify = -1
        self.menuitem = menu.menuitem
        self.menuselect = menu.menuselect
        self.item_image = None
        self.select_image = None
        self.height = 0

        self._msg = None
        self.cached_antialias_status = None
        self.set_msg(msg)

    @property
    def msg(self):
        return self._msg

    def set_msg(self, msg, antialias_val=True):
        self._msg = msg
        # by default, it uses antialias
        self.item_image = render_text(
            self.font, self._msg, self.width, justify=self.justify, color=self.menuitem, antialias=antialias_val
        )
        self.select_image = render_text(
            self.font, self._msg, self.width, justify=self.justify, color=self.menuselect, antialias=antialias_val
        )
        self.cached_antialias_status = antialias_val
        self.height = self.select_image.get_height()

    # msg = property(_get_msg, _set_msg)

    SORT_LAYER = 0

    def sort_order(self):
        return (self.SORT_LAYER, self._msg)

    def __lt__(self, other):
        """ Comparison of menu items done by sort order, as defined above """
        return self.sort_order() < other.sort_order()

    def __str__(self):
        return self._msg

    def render(self, screen, dest, w_antialias, selected=False):
        if w_antialias != self.cached_antialias_status:
            # need to redraw labels
            self.set_msg(self._msg, antialias_val=w_antialias)

        if selected:
            screen.blit(self.select_image, dest)
        else:
            screen.blit(self.item_image, dest)


# The DescBox is the default MenuDesc. It takes a string stored in the menu
# item and displays it. However, it is not the only menu description possible!
# Any object with a render_desc(menu_item) method will work.
# Also note that the desc associated with each menu item doesn't need to be
# a string- it all depends on the needs of the descobj you're using.

# class DescBox(Frect):
#     # The DescBox inherits from Frect, since that's basically what it is.
#     def __init__(self, menu, dx, dy, w=300, h=100, anchor=ANCHOR_CENTER, border=default_border, justify=-1, font=None,
#                  color=None, **kwargs):
#         self.menu = menu
#         self.border = border
#         self.justify = justify
#         if not anchor:
#             anchor = menu.anchor
#         self.font = font or pygame.font.Font("assets/DejaVuSansCondensed-Bold.ttf", DEFAULT_FONT_SIZE)
#         self.color = color or INFO_GREEN
#         super(DescBox, self).__init__(dx, dy, w, h, anchor, **kwargs)
#
#     def __call__(self, menu_item):
#         mydest = self.get_rect()
#         if self.border:
#             self.border.render(mydest)
#         if menu_item and menu_item.desc:
#             img = render_text(self.font, menu_item.desc, self.w, justify=self.justify, color=self.color)
#             pyv.vars.blit(img, mydest)


class Menu(pyv.EvListener, Frect):  # N.B (tom) it would be better to inherit from EventReceiver +have a Frect attribute

    def __init__(self, dx, dy, font, w=300, h=100, anchor=ANCHOR_CENTER, menuitem=MENU_ITEM_COLOR,
                 menuselect=MENU_SELECT_COLOR, border=default_border, predraw=None, padding=0,
                 item_class=MenuItem, antialias=False):
        # lets use multiple inheritance
        pyv.EvListener.__init__(self)
        Frect.__init__(self, dx, dy, w, h, anchor)

        self.menuitem = menuitem
        self.menuselect = menuselect
        self.border = border
        if font:
            self.font = font
        else:
            self.font = pyv.new_font_obj(None, DEFAULT_FONT_SIZE_CONV_MENU)
        self.antialias_flag = antialias

        self.more_image = self.font.render("+", self.antialias_flag, menuselect)
        self.padding = padding
        self.item_class = item_class

        self.items = []
        self.top_item = 0
        self.selected_item = 0
        self.can_cancel = True
        self.descobj = None
        self.quick_keys = {}

        self._item_rects = collections.OrderedDict()
        self._the_highest_top = 0

        # predraw is a function that
        # redraws/clears the screen before the menu is rendered.
        self.predraw = predraw

        self.screen = pyv.get_surface()

        # -> to the model
        self.no_choice_made = True
        self.choice = False

    def add_item(self, msg, value, desc=None):
        item = self.item_class(msg, value, desc, self)
        self.items.append(item)

    def add_descbox(self, x, y, w=30, h=10, justify=-1, font=None, **kwargs):
        self.descobj = DescBox(self, x, y, w, h, border=self.border, justify=justify, font=font or self.font, **kwargs)

    def arrange(self):
        # Set the position of all on-screen menu items.
        mydest = self.get_rect()
        item_num = self.top_item
        self._item_rects.clear()
        y = mydest.top
        while y < mydest.bottom:
            if item_num < len(self.items):
                itemdest = pyv.new_rect_obj(mydest.x, y, self.w, self.items[item_num].height)
                # Only add this item to the menu if it fits inside the menu or is the first menu item.
                if itemdest.bottom <= mydest.bottom or not self._item_rects:
                    self._item_rects[item_num] = itemdest
                y += self.items[item_num].height + self.padding
            else:
                break
            item_num += 1

        # While we're here, might as well calculate the highest top.
        self._the_highest_top = len(self.items) - 1
        item_num = self._the_highest_top
        y = mydest.bottom
        while y >= mydest.top and item_num >= 0:
            y -= self.items[item_num].height
            if y >= mydest.top:
                self._the_highest_top = item_num
            item_num -= 1
            y -= self.padding

    def render_whole_menu(self, antialias, do_extras=True):
        mydest = self.get_rect()
        if do_extras:
            if self.predraw:
                self.predraw()
            if self.border:
                self.border.render(mydest)

        self.screen.set_clip(mydest)
        self.arrange()
        for item_num, area in list(self._item_rects.items()):
            self.items[item_num].render(
                self.screen, area, antialias, (item_num == self.selected_item) and do_extras
            )
        self.screen.set_clip(None)

        if self.descobj:
            self.descobj(self.get_current_item())

    def get_mouseover_item(self, pos):
        # Return the menu item under this mouse position.
        # self.arrange must have been called previously!
        for item_num, area in list(self._item_rects.items()):
            if area.collidepoint(pos):
                return item_num

    def query(self):
        # TODO refactor this, so it doesnt hook the game loop anymore

        # A return of False means selection was cancelled.
        # pygame.event.clear()
        if not self.items:
            return False
        elif self.selected_item >= len(self.items):
            self.selected_item = 0
        self.no_choice_made = True
        self.choice = False

        # Do an initial arrangement of the menu.
        self.arrange()

    def on_paint(self, ev):
        if ev.type == pyv.EngineEvTypes.Paint:
            self.render()

    # - deprecated
    # def on_quit
    # elif ev.type == pygame.QUIT:
    #     self.no_choice_made = False

    # TODO keyboard management when talking to someone
    # elif ev.type == pygame.KEYDOWN:
    #     # A key was pressed, oh happy day! See what key it was and act
    #     # accordingly.
    #     if ev.key == pygame.K_UP:
    #         self.selected_item -= 1
    #         if self.selected_item < 0:
    #             self.selected_item = len(self.items) - 1
    #         if self.selected_item not in self._item_rects:
    #             self.top_item = min(self.selected_item, self._the_highest_top)
    #     elif ev.key == pygame.K_DOWN:
    #         self.selected_item += 1
    #         if self.selected_item >= len(self.items):
    #             self.selected_item = 0
    #         if self.selected_item not in self._item_rects:
    #             self.top_item = min(self.selected_item, self._the_highest_top)
    #     elif ev.key == pygame.K_SPACE or ev.key == pygame.K_RETURN:
    #         self.pev(MyEvTypes.ConvChoice, value=self.items[self.selected_item].value)
    #         self.no_choice_made = False
    #     elif (ev.key == pygame.K_ESCAPE or ev.key == pygame.K_BACKSPACE) and self.can_cancel:
    #         self.no_choice_made = False
    #     elif ev.key >= 0 and ev.key < 256 and chr(ev.key) in self.quick_keys:
    #         self.pev(MyEvTypes.ConvChoice, value=self.quick_keys[chr(ev.key)])
    #         self.no_choice_made = False
    #     elif ev.key > 255 and ev.key in self.quick_keys:
    #         self.pev(MyEvTypes.ConvChoice, value=self.quick_keys[ev.key])
    #         self.no_choice_made = False

    def on_mousedown(self, ev):
        if ev.button == 1:
            mouse_pos = pyv.get_mouse_coords()
            moi = self.get_mouseover_item(mouse_pos)
            if moi is not None:
                self.set_item_by_position(moi)
        elif ev.button == 4:
            self.top_item = max(self.top_item - 1, 0)
        elif ev.button == 5:
            self.top_item = min(self.top_item + 1, self._the_highest_top)

    def on_mouseup(self, ev):
        #mouse_pos = vscreen.proj_to_vscreen(pyv.get_mouse_pos())
        mouse_pos = pyv.get_mouse_coords()
        if ev.button == 1:
            moi = self.get_mouseover_item(mouse_pos)
            if moi is self.selected_item:
                # avant transition vers automaton
                # self.pev(MyEvTypes.ConvChoice, value=self.items[self.selected_item].value)
                # après:
                self.pev(pyv.EngineEvTypes.ConvStep, value=self.items[self.selected_item].msg)
                pyv.post_ev('conv_step', value=self.items[self.selected_item].msg)
                self.no_choice_made = False
        elif ev.button == 3 and self.can_cancel:
            self.no_choice_made = False

    def on_mousemotion(self, ev):
        mouse_pos = pyv.get_mouse_coords()
        moi = self.get_mouseover_item(mouse_pos)
        if moi is not None:
            self.set_item_by_position(moi)

    def sort(self):
        self.items.sort()

    alpha_key_sequence = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    def add_alpha_keys(self):
        # Adds a quick key for every item currently in the menu.
        key_num = 0
        for item in self.items:
            item.set_msg(self.alpha_key_sequence[key_num] + ') ' + item.msg)
            self.quick_keys[self.alpha_key_sequence[key_num]] = item.value
            key_num += 1
            if key_num >= len(self.alpha_key_sequence):
                break

    def add_files(self, filepat):
        file_list = glob.glob(filepat)

        for f in file_list:
            self.add_item(f, f)
        self.sort()

    def reposition(self):
        self.arrange()
        if self.selected_item < self.top_item:
            self.top_item = self.selected_item
        elif self.selected_item > max(self._item_rects.keys()):
            self.top_item = max(list(self._item_rects.keys()) + [self._the_highest_top])
        self.arrange()

    def has_value(self, v):
        for i in self.items:
            if i.value == v:
                return True

    def set_item_by_value(self, v):
        for n, i in enumerate(self.items):
            if i.value == v:
                self.selected_item = n
        self.reposition()

    def set_item_by_position(self, n):
        if n < len(self.items):
            self.selected_item = n
        self.reposition()

    def set_random_item(self):
        if self.items:
            n = random.randint(0, len(self.items) - 1)
            self.set_item_by_position(n)

    def get_current_item(self):
        if self.selected_item < len(self.items):
            return self.items[self.selected_item]

    def get_current_value(self):
        if self.selected_item < len(self.items):
            return self.items[self.selected_item].value


class PopUpMenu(Menu):
    """Creates a small menu at the current mouse position."""

    def __init__(self, w=200, h=250, predraw=None, border=default_border, **kwargs):
        mouse_pos = pyv.get_mouse_coords()
        x, y = mouse_pos
        x += 8
        y += 8
        sw, sh = pyv.screen.get_size()
        if x + w + 32 > sw:
            x += -w - 32
        if y + h + 32 > sh:
            y += -h - 32
        super().__init__(x, y, w, h, ANCHOR_UPPERLEFT, border=border, predraw=predraw, **kwargs)


class AlertMenu(Menu):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75
    FULL_RECT = Frect(-175, -125, 350, 250)
    TEXT_RECT = Frect(-175, -125, 350, 165)

    def __init__(self, desc):
        super().__init__(-self.WIDTH // 2, self.HEIGHT // 2 - self.MENU_HEIGHT, self.WIDTH, self.MENU_HEIGHT,
                         border=None, predraw=self.pre)
        self.desc = desc

    def pre(self):
        default_border.render(self.FULL_RECT.get_rect())
        p_draw_text(self.font, self.desc, self.TEXT_RECT.get_rect(), justify=0, antialias=self.antialias_flag)


# -------------------------------
#  all below comes from old "dialogue" file (polarbear)
# -------------------------------
class Offer(object):
    # An Offer is a single line spoken by the NPC.
    # "effect" is a callable with no parameters.
    # "replies" is a list of replies.
    def __init__(self, msg, effect=None, replies=()):
        self.msg = msg
        self.effect = effect
        self.replies = list(replies)

    def __str__(self):
        return self.msg

    @classmethod
    def from_json(cls, jdict):
        # We spoke about not needing a json loader yet. But, in terms of hardcoding a conversation, it was just as
        # easy to write this as to hand-code a dialogue tree.
        msg = jdict.get("msg", "Hello there!")
        effect = None
        replies = list()
        for rdict in jdict.get("replies", ()):
            replies.append(Reply.from_json(rdict))
        return cls(msg, effect, replies)

    @classmethod
    def load_json(cls, filename):
        with open(filename) as f:
            jdict = json.load(f)
        return cls.from_json(jdict)


class Reply(object):
    # A Reply is a single line spoken by the PC, leading to a new offer
    def __init__(self, msg, destination=None):
        self.msg = msg
        self.destination = destination

    def __str__(self):
        return self.msg

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.msg, self.destination)

    @classmethod
    def from_json(cls, jdict):
        msg = jdict.get("msg", "And you too!")
        destination = jdict.get("destination")
        if destination:
            destination = Offer.from_json(destination)
        return cls(msg, destination)


# if youre using the kengi/2023-style event sys (that is evsys4)...
# you should be fine with 'ConversationView' !
# Otherwise, you can prefer using this:
CONV_TEXT_AREA = Frect(-75, -100, 300, 100)
CONV_MENU_AREA = Frect(-75, 30, 300, 80)
CONV_PORTRAIT_AREA = Frect(-240, -110, 150, 225)


def new_conversation_view_actor(ref_automaton, font_name):
    """
    nota bene: font_name can be None, if it's the case we should use a default font

    this conversation view only shows what the NPC is saying, not what the player can say
    """

    print('creation new conversation view actor with font_name=', font_name)
    data = {
        'text': None,  # will received the first msg on the 1st update event
        'automaton': ref_automaton,
        'portrait': None,
        'my_menu': None,  # to store possible answers
        'up_to_date': False,
        'antialias': False,
        'font': pyv.new_font_obj(None, DEFAULT_FONT_SIZE_CONV_MENU) if font_name is None else pyv.data[font_name],
        'pre_render': None,
        'ready_to_leave': False,
        'active': False
    }
    img_id = data['automaton'].inner_data['portrait']
    data['portrait'] = pyv.images[img_id] if img_id else None

    # - utils
    def refresh_portrait(this, img_name):
        this.portrait = pyv.images[img_name] if img_name else None

    # --------------
    # - behavior
    def on_conv_step(this, ev):
        if not this.active:
            return
        # ~ iterate over the conversation...
        # print('--trait convCchoice', 'passage-->', ev.value)
        this.up_to_date = False
        automaton_sig = this.automaton.handle_input(ev.value)
        if automaton_sig == 0:
            this.ready_to_leave = True
            pyv.post_ev('conv_finish')
        elif automaton_sig == 2:
            # update portrait if needed
            refresh_portrait(this, this.automaton.inner_data['portrait'])
        # self.curr_offer = ev.value

    def on_update(this, ev):
        if not this.active:
            return
        if not this.up_to_date:
            this.up_to_date = True
            this.text = ref_automaton.get_current_state().message
            this.my_menu = Menu(
                CONV_MENU_AREA.dx, CONV_MENU_AREA.dy, this.font,
                w=CONV_MENU_AREA.w, h=CONV_MENU_AREA.h,
                border=None, predraw=None, antialias=False
            )
            # populate menu
            for rep in this.automaton.get_current_state().transitions:
                rep.apply_to_menu(this.my_menu)
            if this.text and not this.my_menu.items:
                this.my_menu.add_item("[Continue]", None)
            else:
                this.my_menu.sort()
            # this.my_menu.active = True

    def on_draw(this, ev):
        if not this.active or this.ready_to_leave:
            return
        if this.pre_render:
            this.pre_render()
        text_rect = CONV_TEXT_AREA.get_rect()
        default_border.render(text_rect)
        p_draw_text(this.font, this.text, text_rect, antialias=this.antialias)
        default_border.render(CONV_MENU_AREA.get_rect())
        # menu
        if this.my_menu:
            this.my_menu.render_whole_menu(this.antialias)
        if this.portrait:
            ev.screen.blit(this.portrait, CONV_PORTRAIT_AREA.get_rect())

    # will have to forward 3 mouse events...
    def on_mousemotion(this, ev):
        if not this.active:
            return
        if this.my_menu:
            this.my_menu.on_mousemotion(ev)

    def on_mouseup(this, ev):
        if not this.active:
            return
        if this.my_menu:
            this.my_menu.on_mouseup(ev)

    def on_mousedown(this, ev):
        if not this.active:
            return
        if this.my_menu:
            this.my_menu.on_mousedown(ev)

    return new_actor('conversation_view', locals())


# - deprecated!
class deprecConversationView(pyv.EvListener):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.

    def _refresh_portrait(self, x):
        self.portrait = pyv.images[x] if x else None

    def __init__(self, ref_automaton, font_name=None, antialias=False, pre_render=None):
        super().__init__()
        self.text = ''
        self.root_offer = ref_automaton
        self.portrait = None
        self._refresh_portrait(ref_automaton.inner_data['portrait'])

        self.pre_render = pre_render
        self.font = pyv.data[font_name] if font_name else pyv.new_font_obj(None, DEFAULT_FONT_SIZE_CONV_MENU)  # using pre-load via engine

        # cela equivaut à curr_state
        # self.curr_offer = root_offer
        self.dialog_upto_date = False
        self.existing_menu = None
        self.antialias_flag = antialias
        self.screen = pyv.get_surface()
        self.ready_to_leave = False

    def turn_off(self):  # because the conversation view can be closed from "outside" i.e. the main program
        if self.existing_menu:
            self.existing_menu.turn_off()
        super().turn_off()

    def on_update(self, ev):
        # if self.curr_offer is not None:
        if not self.ready_to_leave:
            if self.dialog_upto_date:
                return
            if self.existing_menu:
                self.existing_menu.turn_off()

            self.dialog_upto_date = True
            self.text = self.root_offer.get_current_state().message  # self.curr_offer.msg

            # create a new Menu inst.
            print('new menu instantiated ---')
            mymenu = Menu(
                self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                border=None, predraw=self.render)
            mymenu.turn_on()

            self.existing_menu = mymenu
            # for i in self.curr_offer.replies:
            for rep in self.root_offer.get_current_state().transitions:
                rep.apply_to_menu(mymenu)
            if self.text and not mymenu.items:
                mymenu.add_item("[Continue]", None)
            else:
                mymenu.sort()
            # TODO fix
            # this code was disabled when transitioning to 'Automaton'
            # nextfx = self.curr_offer.effect
            #if nextfx:
            #    nextfx()
        else:
            # auto-close everything
            self.pev(pyv.EngineEvTypes.ConvFinish)
            self.turn_off()

    def on_conv_step(self, ev):
        # ~ iterate over the conversation...
        # print('--trait convCchoice', 'passage-->', ev.value)
        self.dialog_upto_date = False
        automaton_sig = self.root_offer.handle_input(ev.value)
        if automaton_sig == 0:
            self.ready_to_leave = True
        elif automaton_sig == 2:
            # update portrait if needed
            self._refresh_portrait(
                self.root_offer.inner_data['portrait']
            )
        # self.curr_offer = ev.value

    def render(self):
        self.on_paint(None)

    def on_paint(self, ev):
        if self.pre_render:
            self.pre_render()
        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        p_draw_text(self.font, self.text, text_rect, antialias=self.antialias_flag)
        default_border.render(self.MENU_AREA.get_rect())
        if self.portrait:
            self.screen.blit(self.portrait, self.PORTRAIT_AREA.get_rect())
