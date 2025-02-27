
class _pygameDrawIface:

    @staticmethod
    def circle(surface, color, pos, radius):
        pass

    @staticmethod
    def rect(surface, bidule):
        pass


class _pygameMathIface:

    def Vector2(self, **args):
        pass


class PygameIface:

    draw = _pygameDrawIface
    math = _pygameMathIface

    KEYDOWN = -1
    KEYUP = 2
    K_LEFT = 3

    @staticmethod
    def Color(rgb):
        pass
