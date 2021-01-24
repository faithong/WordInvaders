"""
pygame-menu
https://github.com/ppizarror/pygame-menu

THEMES
Theme class and predefined themes.

License:
-------------------------------------------------------------------------------
The MIT License (MIT)
Copyright 2017-2021 Pablo Pizarro R. @ppizarror

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-------------------------------------------------------------------------------
"""

__all__ = [

    # Main class
    'Theme',

    # Custom colors
    'THEME_BLUE',
    'THEME_DARK',
    'THEME_DEFAULT',
    'THEME_GREEN',
    'THEME_ORANGE',
    'THEME_SOLARIZED'

]

import pygame_menu.font as _font
import pygame_menu.locals as _locals
import pygame_menu.utils as _utils
import pygame_menu.widgets as _widgets
from pygame_menu.baseimage import BaseImage
from pygame_menu.scrollarea import get_scrollbars_from_position

from pygame_menu._custom_types import ColorType, Tuple, List, Union, VectorType, Dict, Any, \
    Tuple2NumberType, NumberType, PaddingType, Optional, Type

import copy


def _check_menubar_style(style: int) -> bool:
    """
    Check menubar style.

    :param style: Style
    :return: ``True`` if correct
    """
    return style in (_widgets.MENUBAR_STYLE_ADAPTIVE, _widgets.MENUBAR_STYLE_SIMPLE,
                     _widgets.MENUBAR_STYLE_TITLE_ONLY, _widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL,
                     _widgets.MENUBAR_STYLE_NONE, _widgets.MENUBAR_STYLE_UNDERLINE,
                     _widgets.MENUBAR_STYLE_UNDERLINE_TITLE)


class Theme(object):
    """
    Class defining the visual rendering of menus and widgets.

    .. note::

        All colors must be defined with a tuple of 3 or 4 numbers in the formats:

            - (R,G,B)
            - (R,G,B,A)

        Red (R), Green (G) and Blue (B) must be numbers between 0 and 255.
        A means the alpha channel (opacity), if 0 the color is transparent, 100 means opaque.

    .. note::

        Themes only modify visual behaviour of the Menu. For other options
        like rows/columns, enabling or disabling overflow, position, or Menu
        width/height see Menu parameters.

    :param background_color: Menu background color
    :type background_color: tuple, list, :py:class:`pygame_menu.baseimage.BaseImage`
    :param cursor_color: Cursor color (used in some text-gathering widgets like ``TextInput``)
    :type cursor_color: tuple, list
    :param cursor_selection_color: Color of the text selection if the cursor is enabled on certain widgets
    :type cursor_selection_color: tuple, list
    :param cursor_switch_ms: Interval of cursor switch between off and on status
    :type cursor_switch_ms: int, float
    :param focus_background_color: Color of the widget focus, this must be a tuple of 4 elements *(R, G, B, A)*
    :type focus_background_color: tuple, list
    :param fps: Menu max fps (frames per second). If ``0`` there's no limit
    :type fps: int, float
    :param readonly_color: Color of the widget in readonly mode
    :type readonly_color: tuple, list
    :param readonly_selected_color: Color of the selected widget in readonly mode
    :type readonly_selected_color: tuple, list
    :param scrollarea_outer_margin: Outer scroll area margin (px); the tuple is added to computed scroll area width/height, it can add an margin to bottom/right scrolls after widgets. If value less than ``1`` use percentage of width/height. It cannot be a negative value
    :type scrollarea_outer_margin: tuple, list
    :param scrollarea_position: Position of scroll area scrollbars. See :py:mod:`pygame_menu.locals`
    :type scrollarea_position: str
    :param scrollbar_color: Scrollbars color
    :type scrollbar_color: tuple, list
    :param scrollbar_shadow: Indicate if a shadow is drawn on each scrollbar
    :type scrollbar_shadow: bool
    :param scrollbar_shadow_color: Color of the scrollbar shadow
    :type scrollbar_shadow_color: tuple, list
    :param scrollbar_shadow_offset: Offset of the scrollbar shadow
    :type scrollbar_shadow_offset: int, float
    :param scrollbar_shadow_position: Position of the scrollbar shadow. See :py:mod:`pygame_menu.locals`
    :type scrollbar_shadow_position: str
    :param scrollbar_slider_color: Color of the sliders
    :type scrollbar_slider_color: tuple, list
    :param scrollbar_slider_pad: Space between slider and scrollbars borders
    :type scrollbar_slider_pad: int, float
    :param scrollbar_thick: Scrollbar thickness in px
    :type scrollbar_thick: int, float
    :param selection_color: Color of the selected widget; it affects font color and the selection effect
    :type selection_color: tuple, list
    :param surface_clear_color: Surface clear color before applying background function
    :type surface_clear_color: tuple, list
    :param title_background_color: Title background color
    :type title_background_color: tuple, list
    :param title_bar_modify_scrollarea: If ``True`` title bar modifies the scrollbars of the scrollarea depending on the style
    :param title_bar_style: Style of the title, use :py:class:`pygame_menu.widgets.MenuBar` widget styles
    :type title_bar_style: int
    :param title_close_button: Draw a back-box button on header to close the Menu. If user moves through nested submenus this buttons turns to a back-arrow
    :type title_close_button: bool
    :param title_floating: If ``True`` title don't contributes height to the Menu. Thus, scroll uses full menu width/height
    :type title_floating: bool
    :param title_font: Optional title font, if ``None`` theme uses the Menu default font
    :type title_font: str, None
    :param title_font_antialias: Title font renders with antialiasing
    :type title_font_antialias: bool
    :param title_font_color: Title font color. If ``None`` use the widget font color
    :type title_font_color: tuple, list, None
    :param title_font_size: Font size of the title
    :type title_font_size: int
    :param title_offset: Offset *(x-position, y-position)* of title (px)
    :type title_offset: tuple, list
    :param title_shadow: Enable shadow on title
    :type title_shadow: bool
    :param title_shadow_color: Title shadow color
    :type title_shadow_color: tuple, list
    :param title_shadow_offset: Offset of shadow on title
    :type title_shadow_offset: int, float
    :param title_shadow_position: Position of the shadow on title. See :py:mod:`pygame_menu.locals`
    :type title_shadow_position: str
    :param title_updates_pygame_display: If ``True`` the menu title updates See :py:mod:`pygame.display.caption` automatically on draw
    :type title_updates_pygame_display: bool
    :param widget_alignment: Widget default `alignment <https://pygame-menu.readthedocs.io/en/latest/_source/create_menu.html#widgets-alignment>`_. See :py:mod:`pygame_menu.locals`
    :type widget_alignment: str
    :param widget_background_color: Background color of a widget, it can be a color or a BaseImage object. Background fills the entire widget + the padding
    :type widget_background_color: tuple, list, :py:class:`pygame_menu.baseimage.BaseImage`, None
    :param widget_background_inflate: Inflate background in *(x, y)* in px. By default it uses the highlight margin. This parameter is visual only. For modifying widget size use padding instead
    :type widget_background_inflate: tuple, list
    :param widget_border_color: Widget border color
    :type widget_border_color: tuple, list
    :param widget_border_inflate: Widget inflate size in *(x, y)* in px. These values cannot be negative
    :type widget_border_inflate: tuple, list
    :param widget_border_width: Widget border width (px). If ``0`` the border is disabled. Border width don't contributes to the widget width/height, it's visual-only
    :type widget_border_width: int
    :param widget_font: Widget font path or name
    :type widget_font: str
    :param widget_font_antialias: Widget font renders with antialiasing
    :type widget_font_antialias: bool
    :param widget_font_background_color: Widget font background color. If ``None`` the value will be the same as ``background_color`` if it's is a color object and if ``widget_font_background_color_from_menu`` is ``True`` and ``widget_background_color`` is ``None``
    :type widget_font_background_color: tuple, list, None
    :param widget_font_background_color_from_menu: Use Menu background color as font background color. Disabled by default
    :type widget_font_background_color_from_menu: bool
    :param widget_font_color: Color of the font
    :type widget_font_color: tuple, list
    :param widget_font_size: Font size
    :type widget_font_size: int
    :param widget_margin: Horizontal and vertical margin of each element in Menu (px)
    :type widget_margin: tuple, list
    :param widget_padding: Padding of the widget according to CSS rules. It can be a single digit, or a tuple of 2, 3, or 4 elements. Padding modifies widget width/height
    :type widget_padding: int, float, tuple, list
    :param widget_offset: *(x, y)* axis offset of widgets within Menu (px) respect to top-left corner. If value less than ``1`` use percentage of width/height. It cannot be a negative value
    :type widget_offset: tuple, list
    :param widget_selection_effect: Widget selection effect object. This is visual-only, the selection properties does not affect widget height/width
    :type widget_selection_effect: :py:class:`pygame_menu.widgets.core.Selection`
    :param widget_shadow: Indicate if the widget text shadow is enabled
    :type widget_shadow: bool
    :param widget_shadow_color: Color of the widget shadow
    :type widget_shadow_color: tuple, list
    :param widget_shadow_offset: Offset of the widget shadow
    :type widget_shadow_offset: int, float
    :param widget_shadow_position: Position of the widget shadow. See :py:mod:`pygame_menu.locals`
    :type widget_shadow_position: str
    """
    _disable_validation: bool
    background_color: Union[ColorType, 'BaseImage']
    cursor_color: ColorType
    cursor_selection_color: ColorType
    cursor_switch_ms: NumberType
    focus_background_color: ColorType
    fps: NumberType
    readonly_color: ColorType
    readonly_selected_color: ColorType
    scrollarea_outer_margin: Tuple2NumberType
    scrollarea_position: str
    scrollbar_color: ColorType
    scrollbar_shadow: bool
    scrollbar_shadow_color: ColorType
    scrollbar_shadow_offset: NumberType
    scrollbar_shadow_position: str
    scrollbar_slider_color: ColorType
    scrollbar_slider_pad: NumberType
    scrollbar_thick: NumberType
    selection_color: ColorType
    surface_clear_color: ColorType
    title_background_color: ColorType
    title_bar_modify_scrollarea: bool
    title_bar_style: int
    title_close_button: bool
    title_floating: bool
    title_font: str
    title_font_antialias: bool
    title_font_color: ColorType
    title_font_size: int
    title_offset: Tuple2NumberType
    title_shadow: bool
    title_shadow_color: ColorType
    title_shadow_offset: NumberType
    title_shadow_position: str
    title_updates_pygame_display: bool
    widget_alignment: str
    widget_background_color: Optional[Union[ColorType, 'BaseImage']]
    widget_background_inflate: Tuple2NumberType
    widget_border_color: ColorType
    widget_border_inflate: Tuple2NumberType
    widget_border_width: int
    widget_font: str
    widget_font_antialias: str
    widget_font_background_color: Optional[ColorType]
    widget_font_background_color_from_menu: bool
    widget_font_color: ColorType
    widget_font_size: int
    widget_margin: Tuple2NumberType
    widget_offset: Tuple2NumberType
    widget_padding: PaddingType
    widget_selection_effect: 'pygame_menu.widgets.core.Selection'
    widget_shadow: bool
    widget_shadow_color: ColorType
    widget_shadow_offset: NumberType
    widget_shadow_position: str

    def __init__(self, **kwargs) -> None:

        # Menu general
        self.background_color = self._get(kwargs, 'background_color', 'color_image', (220, 220, 220))
        self.focus_background_color = self._get(kwargs, 'focus_background_color', 'color', (0, 0, 0, 180))
        self.fps = self._get(kwargs, 'fps', (int, float), 30)
        self.readonly_color = self._get(kwargs, 'readonly_color', 'color', (120, 120, 120))
        self.readonly_selected_color = self._get(kwargs, 'readonly_selected_color', 'color', (190, 190, 190))
        self.selection_color = self._get(kwargs, 'selection_color', 'color', (255, 255, 255))
        self.surface_clear_color = self._get(kwargs, 'surface_clear_color', 'color', (0, 0, 0))

        # Cursor/Text gathering
        self.cursor_color = self._get(kwargs, 'cursor_color', 'color', (0, 0, 0))
        self.cursor_selection_color = self._get(kwargs, 'cursor_selection_color', 'color', (30, 30, 30, 120))
        self.cursor_switch_ms = self._get(kwargs, 'cursor_switch_ms', (int, float), 1000)

        # Menubar/Title
        self.title_background_color = self._get(kwargs, 'title_background_color', 'color', (70, 70, 70))
        self.title_bar_modify_scrollarea = self._get(kwargs, 'title_bar_modify_scrollarea', bool, True)
        self.title_bar_style = self._get(kwargs, 'title_bar_style', int, _widgets.MENUBAR_STYLE_ADAPTIVE)
        self.title_close_button = self._get(kwargs, 'menubar_close_button', bool, True)
        self.title_floating = self._get(kwargs, 'title_floating', bool, False)
        self.title_font = self._get(kwargs, 'title_font', str, _font.FONT_OPEN_SANS)
        self.title_font_antialias = self._get(kwargs, 'title_font_antialias', bool, True)
        self.title_font_color = self._get(kwargs, 'title_font_color', 'color', (220, 220, 220))
        self.title_font_size = self._get(kwargs, 'title_font_size', int, 40)
        self.title_offset = self._get(kwargs, 'title_offset', 'tuple2', (5, -1))
        self.title_shadow = self._get(kwargs, 'title_shadow', bool, False)
        self.title_shadow_color = self._get(kwargs, 'title_shadow_color', 'color', (0, 0, 0))
        self.title_shadow_offset = self._get(kwargs, 'title_shadow_offset', (int, float), 2)
        self.title_shadow_position = self._get(kwargs, 'title_shadow_position', 'position',
                                               _locals.POSITION_NORTHWEST)
        self.title_updates_pygame_display = self._get(kwargs, 'title_updates_pygame_display', bool, False)

        # ScrollArea
        self.scrollarea_outer_margin = self._get(kwargs, 'scrollarea_outer_margin', 'tuple2', (0, 0))
        self.scrollarea_position = self._get(kwargs, 'scrollarea_position', str, _locals.POSITION_SOUTHEAST)

        # ScrollBar
        self.scrollbar_color = self._get(kwargs, 'scrollbar_color', 'color', (220, 220, 220))
        self.scrollbar_shadow = self._get(kwargs, 'scrollbar_shadow', bool, False)
        self.scrollbar_shadow_color = self._get(kwargs, 'scrollbar_shadow_color', 'color', (0, 0, 0))
        self.scrollbar_shadow_offset = self._get(kwargs, 'scrollbar_shadow_offset', (int, float), 2)
        self.scrollbar_shadow_position = self._get(kwargs, 'scrollbar_shadow_position', 'position',
                                                   _locals.POSITION_NORTHWEST)
        self.scrollbar_slider_color = self._get(kwargs, 'scrollbar_slider_color', 'color', (200, 200, 200))
        self.scrollbar_slider_pad = self._get(kwargs, 'scrollbar_slider_pad', (int, float), 0)
        self.scrollbar_thick = self._get(kwargs, 'scrollbar_thick', (int, float), 20)

        # Generic widget themes
        self.widget_selection_effect = self._get(kwargs, 'widget_selection_effect', _widgets.core.Selection,
                                                 _widgets.HighlightSelection())
        widget_selection_margin = self.widget_selection_effect.get_xy_margin()

        self.widget_alignment = self._get(kwargs, 'widget_alignment', 'alignment', _locals.ALIGN_CENTER)
        self.widget_background_color = self._get(kwargs, 'widget_background_color', 'color_image_none', )
        self.widget_background_inflate = self._get(kwargs, 'background_inflate', 'tuple2', (0, 0))
        self.widget_border_color = self._get(kwargs, 'widget_border_color', 'color', (0, 0, 0))
        self.widget_border_inflate = self._get(kwargs, 'widget_border_inflate', 'tuple2', widget_selection_margin)
        self.widget_border_width = self._get(kwargs, 'widget_border_width', int, 0)
        self.widget_font = self._get(kwargs, 'widget_font', str, _font.FONT_OPEN_SANS)
        self.widget_font_antialias = self._get(kwargs, 'widget_font_antialias', bool, True)
        self.widget_font_background_color = self._get(kwargs, 'widget_font_background_color', 'color_none', )
        self.widget_font_background_color_from_menu = self._get(kwargs, 'widget_font_background_color_from_menu',
                                                                bool, False)
        self.widget_font_color = self._get(kwargs, 'widget_font_color', 'color', (70, 70, 70))
        self.widget_font_size = self._get(kwargs, 'widget_font_size', int, 30)
        self.widget_margin = self._get(kwargs, 'widget_margin', 'tuple2', (0, 10))
        self.widget_padding = self._get(kwargs, 'widget_padding', (int, float, tuple, list), 0)
        self.widget_offset = self._get(kwargs, 'widget_offset', 'tuple2', (0, 0))
        self.widget_shadow = self._get(kwargs, 'widget_shadow', bool, False)
        self.widget_shadow_color = self._get(kwargs, 'widget_shadow_color', 'color', (0, 0, 0))
        self.widget_shadow_offset = self._get(kwargs, 'widget_shadow_offset', (int, float), 2)
        self.widget_shadow_position = self._get(kwargs, 'widget_shadow_position', 'position',
                                                _locals.POSITION_NORTHWEST)

        # Upon this, no more kwargs should exist, raise exception if there's more
        for invalid_keyword in kwargs.keys():
            msg = 'parameter Theme.{} does not exist'.format(invalid_keyword)
            raise ValueError(msg)

        # Test purpose only, if True disables any validation
        self._disable_validation = False

    def validate(self) -> 'Theme':
        """
        Validate the values of the theme. If there's a invalid parameter throws an
        ``AssertionError``.

        This function also converts all lists to tuples. This is done because lists
        are mutable.

        :return: Self reference
        """
        if self._disable_validation:
            return self

        # Boolean asserts
        assert isinstance(self.title_close_button, bool)
        assert isinstance(self.title_bar_modify_scrollarea, bool)
        assert isinstance(self.title_font_antialias, bool)
        assert isinstance(self.title_shadow, bool)
        assert isinstance(self.scrollbar_shadow, bool)
        assert isinstance(self.widget_font_antialias, bool)
        assert isinstance(self.widget_font_background_color_from_menu, bool)
        assert isinstance(self.widget_shadow, bool)

        # Value type checks
        _utils.assert_alignment(self.widget_alignment)
        _utils.assert_position(self.scrollbar_shadow_position)
        _utils.assert_position(self.title_shadow_position)
        _utils.assert_position(self.widget_shadow_position)
        assert _check_menubar_style(self.title_bar_style)
        assert get_scrollbars_from_position(self.scrollarea_position) is not None

        assert isinstance(self.cursor_switch_ms, (int, float))
        assert isinstance(self.fps, (int, float))
        assert isinstance(self.scrollbar_shadow_offset, (int, float))
        assert isinstance(self.scrollbar_slider_pad, (int, float))
        assert isinstance(self.scrollbar_thick, (int, float))
        assert isinstance(self.title_floating, bool)
        assert isinstance(self.title_font, str)
        assert isinstance(self.title_font_size, int)
        assert isinstance(self.title_shadow_offset, (int, float))
        assert isinstance(self.title_updates_pygame_display, bool)
        assert isinstance(self.widget_border_width, int)
        assert isinstance(self.widget_font, str)
        assert isinstance(self.widget_font_size, int)
        assert isinstance(self.widget_padding, (int, float, tuple, list))
        assert isinstance(self.widget_selection_effect, _widgets.core.Selection)
        assert isinstance(self.widget_shadow_offset, (int, float))

        # Format colors, this converts all color lists to tuples automatically
        self.background_color = self._format_opacity(self.background_color)
        self.cursor_color = self._format_opacity(self.cursor_color)
        self.cursor_selection_color = self._format_opacity(self.cursor_selection_color)
        self.focus_background_color = self._format_opacity(self.focus_background_color)
        self.readonly_color = self._format_opacity(self.readonly_color)
        self.readonly_selected_color = self._format_opacity(self.readonly_selected_color)
        self.scrollbar_color = self._format_opacity(self.scrollbar_color)
        self.scrollbar_shadow_color = self._format_opacity(self.scrollbar_shadow_color)
        self.scrollbar_slider_color = self._format_opacity(self.scrollbar_slider_color)
        self.selection_color = self._format_opacity(self.selection_color)
        self.surface_clear_color = self._format_opacity(self.surface_clear_color)
        self.title_background_color = self._format_opacity(self.title_background_color)
        self.widget_border_color = self._format_opacity(self.widget_border_color)
        self.title_font_color = self._format_opacity(self.title_font_color)
        self.title_shadow_color = self._format_opacity(self.title_shadow_color)
        self.widget_background_color = self._format_opacity(self.widget_background_color)
        self.widget_font_background_color = self._format_opacity(self.widget_font_background_color)
        self.widget_font_color = self._format_opacity(self.widget_font_color)

        # List to tuple
        self.scrollarea_outer_margin = self._vec_to_tuple(self.scrollarea_outer_margin, 2)
        self.title_offset = self._vec_to_tuple(self.title_offset, 2)
        self.widget_background_inflate = self._vec_to_tuple(self.widget_background_inflate, 2)
        self.widget_border_inflate = self._vec_to_tuple(self.widget_border_inflate, 2)
        self.widget_margin = self._vec_to_tuple(self.widget_margin, 2)
        if isinstance(self.widget_padding, (tuple, list)):
            self.widget_padding = self._vec_to_tuple(self.widget_padding)
            assert 2 <= len(self.widget_padding) <= 4, 'widget padding tuple length must be 2, 3 or 4'
            for p in self.widget_padding:
                assert p >= 0, 'all padding elements must be equal or greater than zero'
        else:
            assert self.widget_padding >= 0, 'padding cannot be a negative number'
        self.widget_offset = self._vec_to_tuple(self.widget_offset, 2)

        # Check sizes
        assert self.scrollarea_outer_margin[0] >= 0 and self.scrollarea_outer_margin[1] >= 0, \
            'scroll area outer margin must be equal or greater than zero in both axis'
        assert self.widget_offset[0] >= 0 and self.widget_offset[1] >= 0, \
            'widget offset must be equal or greater than zero'
        assert self.widget_border_inflate[0] >= 0 and self.widget_border_inflate[1] >= 0, \
            'widget border inflate must be equal or greater than zero in both axis'

        assert self.cursor_switch_ms > 0, 'cursor switch ms must be greater than zero'
        assert self.fps >= 0, 'fps must be equal or greater than zero'
        assert self.scrollbar_shadow_offset > 0, 'scrollbar shadow offset must be greater than zero'
        assert self.scrollbar_slider_pad >= 0, 'slider pad must be equal or greater than zero'
        assert self.scrollbar_thick > 0, 'scrollbar thickness must be greater than zero'
        assert self.title_font_size > 0, 'title font size must be greater than zero'
        assert self.widget_font_size > 0, 'widget font size must be greater than zero'
        assert self.widget_shadow_offset > 0, 'widget shadow offset must be greater than zero'

        # Configs
        self.widget_selection_effect.set_color(self.selection_color)

        # Color asserts
        assert self.focus_background_color[3] != 0, \
            'focus background color cannot be fully transparent, suggested opacity between 1 and 255'

        return self

    def set_background_color_opacity(self, opacity: float) -> 'Theme':
        """
        Modify the Menu background color with given opacity.

        :param opacity: Opacity value, from ``0`` (transparent) to ``1`` (opaque)
        :return: Self reference
        """
        _utils.assert_color(self.background_color)
        assert isinstance(opacity, float)
        assert 0 <= opacity <= 1, 'opacity must be a number between 0 (transparent) and 1 (opaque)'
        self.background_color = (self.background_color[0], self.background_color[1],
                                 self.background_color[2], int(opacity * 255))
        return self

    @staticmethod
    def _vec_to_tuple(obj: Union[Tuple, List], check_length: int = 0) -> Tuple:
        """
        Return a tuple from a list or tuple object.

        :param obj: Object
        :param check_length: Check length if not zero
        :return: Tuple
        """
        if isinstance(obj, tuple):
            v = obj
        elif isinstance(obj, list):
            v = tuple(obj)
        else:
            raise ValueError('object is not a vector')
        if check_length > 0:
            if len(v) != check_length:
                raise ValueError('object is not a {0}-length vector'.format(check_length))
        return v

    def copy(self) -> 'Theme':
        """
        Creates a deep copy of the object.

        :return: Copied theme
        """
        return copy.deepcopy(self)

    @staticmethod
    def _format_opacity(color: Optional[Union[VectorType, 'BaseImage']]
                        ) -> Optional[Union[ColorType, 'BaseImage']]:
        """
        Adds opacity to a 3 channel color. (R,G,B) -> (R,G,B,A) if the color
        has not an alpha channel. Also updates the opacity to a number between
        0 and 255.

        Color may be an Image, so if this is the case return the same object.

        - If the color is a list, return a tuple.
        - If the color is ``None``, return ``None``.

        :param color: Color object
        :return: Color in the same format
        """
        if isinstance(color, BaseImage):
            return color
        if color is None:
            return color
        if isinstance(color, (tuple, list)):
            _utils.assert_color(color)
            if len(color) == 4:
                if isinstance(color, tuple):
                    return color
                return tuple(color)
            elif len(color) == 3:
                color = color[0], color[1], color[2], 255
        else:
            raise ValueError('invalid color type {0}, only tuple or list are valid'.format(color))
        return color

    # noinspection PyTypeChecker
    @staticmethod
    def _get(params: Dict[str, Any], key: str,
             allowed_types: Optional[Union[Type, str, List[Type], Tuple[Type, ...]]] = None,
             default: Any = None) -> Any:
        """
        Return a value from a dictionary.

        Custom types (str)
            -   alignment           pygame-menu alignment (locals)
            -   callable            Is callable type, same as ``'function'``
            -   color               Check color
            -   color_image         Color or :py:class:`pygame_menu.baseimage.BaseImage`
            -   color_image_none    Color, :py:class:`pygame_menu.baseimage.BaseImage`, or None
            -   color_none          Color or None
            -   image               Value must be ``BaseImage``
            -   none                None only
            -   position            pygame-menu position (locals)}
            -   type                Type-class (bool, str, etc...)
            -   tuple2              Only valid numeric tuples ``(x,y)`` or ``[x,y]``
            -   tuple3              Only valid numeric tuples ``(x,y,z)`` or ``[x,y,z]``

        :param params: Parameters dictionary
        :param key: Key to look for
        :param allowed_types: List of allowed types
        :param default: Default value to return
        :return: The value associated to the key
        """
        value = params.pop(key, default)
        if allowed_types is not None:
            other_types = []  # Contain other types to check from
            if not isinstance(allowed_types, (tuple, list)):
                allowed_types = (allowed_types,)
            for valtype in allowed_types:

                if valtype == 'alignment':
                    _utils.assert_alignment(value)

                elif valtype == callable or valtype == 'function' or valtype == 'callable':
                    assert _utils.is_callable(value), 'value must be callable type'

                elif valtype == 'color':
                    _utils.assert_color(value)

                elif valtype == 'color_image':
                    if isinstance(value, BaseImage):
                        return value
                    _utils.assert_color(value)

                elif valtype == 'color_image_none':
                    if value is None or isinstance(value, BaseImage):
                        return value
                    _utils.assert_color(value)

                elif valtype == 'color_none':
                    if value is None:
                        return value
                    _utils.assert_color(value)

                elif valtype == 'image':
                    assert isinstance(value, BaseImage), 'value must be BaseImage type'

                elif valtype == 'none':
                    assert value is None

                elif valtype == 'position':
                    _utils.assert_position(value)

                elif valtype == 'type':
                    assert isinstance(value, type), 'value is not type-class'

                elif valtype == 'tuple2':
                    _utils.assert_vector(value, 2)

                elif valtype == 'tuple3':
                    _utils.assert_vector(value, 3)

                else:  # Unknown type
                    assert isinstance(valtype, type), \
                        'allowed type "{0}" is not a type-class'.format(valtype)
                    other_types.append(valtype)

            # Check other types
            if len(other_types) > 0:
                others = tuple(other_types)
                msg = 'Theme.{} type shall be in {} types (got {})'.format(key, others, type(value))
                assert isinstance(value, others), msg

        return value


THEME_DEFAULT = Theme()

THEME_DARK = Theme(
    background_color=(40, 41, 35),
    cursor_color=(255, 255, 255),
    cursor_selection_color=(80, 80, 80, 120),
    scrollbar_color=(39, 41, 42),
    scrollbar_slider_color=(65, 66, 67),
    selection_color=(255, 255, 255),
    title_background_color=(47, 48, 51),
    title_font_color=(215, 215, 215),
    widget_font_color=(200, 200, 200)
)

THEME_BLUE = Theme(
    background_color=(228, 230, 246),
    scrollbar_shadow=True,
    scrollbar_slider_color=(150, 200, 230),
    scrollbar_slider_pad=2,
    selection_color=(100, 62, 132),
    title_background_color=(62, 149, 195),
    title_font_color=(228, 230, 246),
    title_shadow=True,
    widget_font_color=(61, 170, 220)
)

THEME_GREEN = Theme(
    background_color=(186, 214, 177),
    scrollbar_slider_color=(125, 121, 114),
    scrollbar_slider_pad=2,
    selection_color=(125, 121, 114),
    title_background_color=(125, 121, 114),
    title_font_color=(228, 230, 246),
    widget_font_color=(255, 255, 255)
)

THEME_ORANGE = Theme(
    background_color=(228, 100, 36),
    selection_color=(255, 255, 255),
    title_background_color=(170, 65, 50),
    widget_font_color=(0, 0, 0),
    widget_font_size=30
)

THEME_SOLARIZED = Theme(
    background_color=(239, 231, 211),
    cursor_color=(0, 0, 0),
    cursor_selection_color=(146, 160, 160, 120),
    selection_color=(207, 62, 132),
    title_background_color=(4, 47, 58),
    title_font_color=(38, 158, 151),
    widget_font_color=(102, 122, 130)
)
