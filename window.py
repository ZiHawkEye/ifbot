class Window():
    def __init__(self,
                 y, x,
                 y_size, x_size,
                 y_cursor, x_cursor,
                 l_margin_size, r_margin_size,
                 nl_routine, nl_countdown,
                 font_style,
                 bf_bg_colours,
                 font,
                 style_height,
                 attributes,
                 line_count):
        self.y = y
        self.x = x
        self.y_size = y_size
        self.x_size = x_size
        self.y_cursor = y_cursor
        self.x_cursor = x_cursor
        self.l_margin_size = l_margin_size
        self.r_margin_size = r_margin_size
        self.nl_routine = nl_routine
        self.nl_countdown = nl_countdown
        self.font_style = font_style
        self.fg_bg_colours = fg_bg_colours
        self.font = font
        self.style_height = style_height
        self.attributes = attributes
        self.line_count = line_count