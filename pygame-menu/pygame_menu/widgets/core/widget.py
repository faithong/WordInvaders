"""
pygame-menu
https://github.com/ppizarror/pygame-menu

WIDGET
Base class for widgets.

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

__all__ = ['Widget']

import pygame
import pygame_menu.baseimage as _baseimage
import pygame_menu.font as _fonts
import pygame_menu.locals as _locals
from pygame_menu.widgets.core.selection import Selection
from pygame_menu.decorator import Decorator
from pygame_menu.sound import Sound
from pygame_menu.utils import make_surface, assert_alignment, assert_color, assert_position, assert_vector, \
    is_callable
from pygame_menu._custom_types import Optional, ColorType, Tuple2IntType, NumberType, PaddingType, Union, \
    List, Tuple, Any, CallbackType, Dict, Callable, TYPE_CHECKING, Tuple4IntType, Tuple2BoolType, Tuple3IntType

from pathlib import Path
from uuid import uuid4
import random
import time
import warnings

if TYPE_CHECKING:
    from pygame_menu.menu import Menu


class Widget(object):
    """
    Widget abstract class.

    .. note::

        Widget cannot be copied or deepcopied.

    :param title: Widget title
    :param widget_id: Widget identifier
    :param onchange: Callback when updating the status of the widget, executed in :py:meth:`pygame_menu.widgets.core.Widget.change`
    :param onreturn: Callback when applying on the widget (return), executed in :py:meth:`pygame_menu.widgets.core.Widget.apply`
    :param onselect: Callback when selecting the widget, executed in :py:meth:`pygame_menu.widgets.core.Widget.set_selected`
    :param args: Optional arguments for callbacks
    :param kwargs: Optional keyword arguments
    """
    _alignment: str
    _angle: NumberType
    _args: List[Any]
    _attributes: Dict[str, Any]
    _background_color: Optional[Union[ColorType, '_baseimage.BaseImage']]
    _background_inflate: Tuple2IntType
    _border_color: ColorType
    _border_inflate: Tuple2IntType
    _border_width: int
    _col_row_index: Tuple3IntType
    _decorator: 'Decorator'
    _default_value: Any
    _draw_callbacks: Dict[str, Callable[['Widget', 'Menu'], Any]]
    _events: List['pygame.event.Event']
    _flip: Tuple2BoolType
    _floating: bool
    _font: Optional['pygame.font.Font']
    _font_antialias: bool
    _font_background_color: Optional[ColorType]
    _font_color: ColorType
    _font_name: str
    _font_readonly_color: ColorType
    _font_readonly_selected_color: ColorType
    _font_selected_color: ColorType
    _font_size: int
    _id: str
    _joystick_enabled: bool
    _kwargs: Dict[Any, Any]
    _last_render_hash: int
    _margin: Tuple2IntType
    _max_height: List[Optional[bool]]
    _max_width: List[Optional[bool]]
    _menu: Optional['Menu']
    _mouse_enabled: bool
    _on_change: CallbackType
    _on_return: CallbackType
    _on_select: CallbackType
    _padding: Tuple4IntType
    _padding_transform: Tuple4IntType
    _rect: 'pygame.Rect'
    _scale: List[Union[bool, NumberType]]
    _selected: bool
    _selection_effect: 'Selection'
    _selection_time: NumberType
    _shadow: bool
    _shadow_color: ColorType
    _shadow_offset: NumberType
    _shadow_position: str
    _shadow_tuple: Tuple2IntType
    _sound: 'Sound'
    _surface: Optional['pygame.Surface']
    _title: str
    _touchscreen_enabled: bool
    _translate: Tuple2IntType
    _update_callbacks: Dict[str, Callable[['Widget', 'Menu'], Any]]
    _visible: bool
    active: bool
    is_selectable: bool
    lock_position: bool
    readonly: bool
    selection_expand_background: bool

    def __init__(self,
                 title: Any = '',
                 widget_id: str = '',
                 onchange: CallbackType = None,
                 onreturn: CallbackType = None,
                 onselect: CallbackType = None,
                 args=None,
                 kwargs=None
                 ) -> None:
        assert isinstance(widget_id, str), 'widget id must be a string'
        if onchange:
            assert is_callable(onchange), 'onchange must be callable (function-type) or None'
        if onreturn:
            assert is_callable(onreturn), 'onreturn must be callable (function-type) or None'
        if onselect:
            assert is_callable(onselect), 'onselect must be callable (function-type) or None'

        # Store ID, if None or empty create new ID based on UUID
        if widget_id is None or len(widget_id) == 0:
            widget_id = uuid4()

        self._alignment = _locals.ALIGN_CENTER
        self._attributes = {}  # Stores widget attributes
        self._background_color = None
        self._background_inflate = (0, 0)
        self._col_row_index = (-1, -1, -1)
        self._decorator = Decorator(self)
        self._default_value = _NoWidgetValue()
        self._events = []
        self._floating = False  # If True, the widget don't contribute width/height to the Menu widget positioning computation. Use .set_float() to modify this status
        self._id = str(widget_id)
        self._margin = (0, 0)
        self._max_height = [None, False, True]  # size, width_scale, smooth
        self._max_width = [None, False, True]  # size, height_scale, smooth
        self._padding = (0, 0, 0, 0)  # top, right, bottom, left
        self._padding_transform = (0, 0, 0, 0)
        self._selected = False  # Use select() to modify this status
        self._selection_time = 0
        self._sound = Sound()
        self._title = str(title)
        self._visible = True  # Use show() or hide() to modify this status

        # Widget transforms
        self._angle = 0  # Rotation angle (degrees)
        self._flip = (False, False)  # x, y
        self._scale = [False, 1, 1, False]  # do_scale, x, y, smooth
        self._translate = (0, 0)

        # Widget rect. This object does not contain padding. For getting the widget+padding
        # use .get_rect() widget method instead. Widget subclass should ONLY modify width/height,
        # in rendering and READ position (rect.x, rect.y) in drawing. Position during rendering
        # is not the same as it will have in menu (menu rendering changes widget position). Some
        # widgets like MenuBar are the exception, as its position never changes during menu execution
        # (unless user triggers a change), then widgets like these may access without problems.
        self._rect = pygame.Rect(0, 0, 0, 0)

        # Callbacks
        self._draw_callbacks = {}
        self._update_callbacks = {}

        self._args = args or []
        self._kwargs = kwargs or {}
        self._on_change = onchange
        self._on_return = onreturn
        self._on_select = onselect

        # Surface of the widget
        self._surface = None

        # Menu reference
        self._menu = None

        # Modified in set_font() method
        self._font = None
        self._font_antialias = True
        self._font_background_color = None
        self._font_color = (0, 0, 0)
        self._font_name = ''
        self._font_readonly_color = (0, 0, 0)
        self._font_readonly_selected_color = (255, 255, 255)
        self._font_selected_color = (255, 255, 255)
        self._font_size = 0

        # Text shadow
        self._shadow = False
        self._shadow_color = (0, 0, 0)
        self._shadow_offset = 2.0
        self._shadow_position = _locals.POSITION_NORTHWEST
        self._shadow_tuple = (0, 0)  # (x px offset, y px offset)

        # Border
        self._border_color = (0, 0, 0)
        self._border_inflate = (0, 0)
        self._border_width = 0

        # Rendering, this variable may be used by render() method
        # If the hash of the variables change respect to the last render hash
        # (hash computed using self._hash_variables() method)
        # then the widget should render and update the hash
        self._last_render_hash = 0

        # Selection effect, for avoiding exception while getting object rect, NullSelection
        # was created. Initially it was None
        self._selection_effect = _NullSelection()

        # Inputs
        self._joystick_enabled = True
        self._mouse_enabled = True  # Accept mouse interaction
        self._touchscreen_enabled = True

        # Public statutes. These values can be changed without calling for methods (safe to update)
        self.active = False  # Widget requests focus
        self.is_selectable = True  # Some widgets cannot be selected like labels
        self.lock_position = False  # If True, the widget don't updates the position if .set_position() is executed
        self.readonly = False  # If True, widget ignores all input
        self.selection_expand_background = False  # If True, the widget background will inflate to match selection margin if selected

    def get_sound(self) -> 'Sound':
        """
        Return widget sound engine.

        :return: Sound API
        """
        return self._sound

    def is_selected(self) -> bool:
        """
        Return ``True`` if the widget is selected.

        :return: Selected status
        """
        return self._selected

    def is_visible(self) -> bool:
        """
        Return ``True`` if widget is visible.

        :return: Visible status
        """
        return self._visible

    def is_floating(self) -> bool:
        """
        Return ``True`` if the widget is floating.

        :return: Float status
        """
        return self._floating

    def __copy__(self) -> 'Menu':
        """
        Copy method.

        :return: Raises copy exception
        """
        raise _WidgetCopyException('Widget class cannot be copied')

    def __deepcopy__(self, memodict: Dict) -> 'Menu':
        """
        Deepcopy method.

        :param memodict: Memo dict
        :return: Raises copy exception
        """
        raise _WidgetCopyException('Widget class cannot be deep-copied')

    def _force_render(self) -> Optional[bool]:
        """
        Forces widget render.

        .. note::

            If this method is used it's not necesary to call Widget methods
            :py:meth:`pygame_menu.widgets.core.Widget.force_menu_surface_update` and
            :py:meth:`pygame_menu.widgets.core.Widget.force_menu_surface_cache_update`.
            As `render` should force Menu render, updating both surface and cache.

        :return: Render return value
        """
        self._last_render_hash = 0
        return self._render()

    def force_menu_surface_update(self) -> 'Widget':
        """
        Forces menu surface update after next rendering call.
        This method automatically updates widget decoration cache as Menu render
        forces it to re-render.

        ..note ::

            This method is expensive, as menu surface update forces re-rendering of
            all widgets (because them can change in size, position, etc...).

        :return: Self reference
        """
        if self._menu is not None:
            # Don't set _menu._widgets_surface to None because if so
            # in the drawing process it may destroy the surface and raising
            # an Error. The usage of _widgets_surface_need_update is only on
            # Menu _render()
            self._menu._widgets_surface_need_update = True
        return self

    def force_menu_surface_cache_update(self) -> 'Widget':
        """
        Forces menu surface cache to update after next drawing call.
        This also updates widget decoration.

        .. note::

            This method only updates the surface cache, without forcing re-rendering
            of all Menu widgets as :py:meth:`pygame_menu.widgets.core.Widget.force_menu_surface_update`
            does.

        :return: Self reference
        """
        if self._menu is not None:
            # Menu _widget_surface_cache_need_update property is only accessed on
            # draw method. This does not set _menu._widgets_surface to None
            self._menu._widget_surface_cache_need_update = True
            self._decorator.force_cache_update()
        return self

    def render(self) -> Optional[bool]:
        """
        Public rendering method.

        .. note::

            Unlike private ``_render`` method, public method forces widget rendering
            (calling :py:meth:`pygame_menu.widgets.core.Widget._force_render`). Use
            this method only if the widget has changed the state. Running this
            function many times may affect the performance.

        .. note::

            Before rendering, check out if the widget font/title/values are
            set. If not, it is probable that a zero-size surface is set.

        :return: ``True`` if widget has rendered a new state, ``None`` if the widget has not changed, so render used a cache
        """
        return self._force_render()

    def _render(self) -> Optional[bool]:
        """
        Render the widget surface.

        This method shall update the attribute ``_surface`` with a :py:class:`pygame.Surface`
        representing the outer borders of the widget.

        .. note::

            Before rendering, check out if the widget font/title/values are
            set. If not, it is probable that a zero-size surface is set.

        .. note::

            Render methods should call :py:meth:`pygame_menu.widget.core.Widget.force_menu_surface_update`
            to force Menu to update the drawing surface.

        :return: ``True`` if widget has rendered a new state, ``None`` if the widget has not changed, so render used a cache
        """
        raise NotImplementedError('override is mandatory')

    def set_attribute(self, key: str, value: Any) -> 'Widget':
        """
        Set a widget attribute.

        :param key: Key of the attribute
        :param value: Value of the attribute
        :return: Self reference
        """
        assert isinstance(key, str)
        self._attributes[key] = value
        return self

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute value.

        :param key: Key of the attribute
        :param default: Value if does not exists
        :return: Attribute data
        """
        assert isinstance(key, str)
        if not self.has_attribute(key):
            return default
        return self._attributes[key]

    def has_attribute(self, key: str) -> bool:
        """
        Return ``True`` if widget has the given attribute.

        :param key: Key of the attribute
        :return: ``True`` if exists
        """
        assert isinstance(key, str)
        return key in self._attributes.keys()

    def remove_attribute(self, key: str) -> 'Widget':
        """
        Removes the given attribute from the widget. Throws ``IndexError`` if given key does not exist.

        :param key: Key of the attribute
        :return: Self reference
        """
        if not self.has_attribute(key):
            raise IndexError('attribute "{0}" does not exists on widget'.format(key))
        del self._attributes[key]
        return self

    @staticmethod
    def _hash_variables(*args) -> int:
        """
        Compute hash from a series of variables.

        :param args: Variables to compute hash
        :return: Hash data
        """
        h = hash(args)
        if h == 0:  # Menu considers 0 as un-rendered status
            h = random.randrange(-100000, 100000)
        return h

    def _render_hash_changed(self, *args) -> bool:
        """
        This method checks if the widget must render because the inner variables changed.
        This method should include all the variables used by the render method, for example,
        visibility, selected, etc.

        :param args: Variables to check the hash
        :return: ``True`` if render has changed the widget
        """
        _hash = self._hash_variables(*args)
        if _hash != self._last_render_hash or self._last_render_hash == 0:
            self._last_render_hash = _hash
            return True
        return False

    def set_title(self, title: str) -> 'Widget':  # lgtm [py/inheritance/incorrect-overridden-signature]
        """
        Update the widget title.

        .. note::

            Not all widgets implements this method, for example, images don't
            accept a title.

        :param title: New title
        :return: Self reference
        """
        self._title = str(title)
        self._apply_font()
        self._force_render()
        return self

    def get_title(self) -> str:
        """
        Return the widget title.

        .. note::

            Not all widgets implements this method, for example, images don't accept
            a title, and such widget would return an empty string if this method is called.

        :return: Widget title
        """
        return self._title

    def set_background_color(self, color: Optional[Union[ColorType, '_baseimage.BaseImage']],
                             inflate: Optional[Tuple2IntType] = (0, 0)) -> 'Widget':
        """
        Set the widget background color.

        :param color: Widget background color
        :param inflate: Inflate background in *(x, y)*. If ``None``, the widget value is not updated
        :return: Self reference
        """
        if color is not None:
            if isinstance(color, _baseimage.BaseImage):
                assert color.get_drawing_mode() == _baseimage.IMAGE_MODE_FILL, \
                    'currently widget only supports IMAGE_MODE_FILL drawing mode'
            else:
                assert_color(color)
        if inflate is None:
            inflate = self._background_inflate
        assert_vector(inflate, 2)
        assert inflate[0] >= 0 and inflate[1] >= 0, \
            'widget background inflate must be equal or greater than zero in both axis'

        self._background_color = color
        self._background_inflate = tuple(inflate)
        self._force_render()
        return self

    def background_inflate_to_selection_effect(self) -> 'Widget':
        """
        Expand background inflate to match the selection effect
        (the widget don't require to be selected).

        This is a permanent change; for dynamic purposes, depending if the widget
        is selected or not, setting ``widget.selection_expand_background`` to ``True`` may help.

        .. note::

            This method may have unexpected results with certain selection effects.

        :return: Self reference
        """
        self._background_inflate = self._selection_effect.get_xy_margin()
        return self

    def _draw_background_color(self, surface: 'pygame.Surface') -> None:
        """
        Fill a surface with the widget background color.

        :param surface: Surface to fill
        :return: None
        """
        if self._background_color is None:
            return
        if not (self.selection_expand_background and self._selected):
            inflate = self._background_inflate
        else:
            inflate = self._selection_effect.get_xy_margin()
        rect = self.get_rect(inflate=inflate)
        if isinstance(self._background_color, _baseimage.BaseImage):
            self._background_color.draw(
                surface=surface,
                area=rect,
                position=(rect.x, rect.y)
            )
        else:
            surface.fill(self._background_color, rect)

    def _draw_border(self, surface: 'pygame.Surface') -> None:
        """
        Draw widget border in the surface.

        :param surface: Surface to draw the border
        :return: None
        """
        if self._border_width == 0:
            return
        rect = self.get_rect(inflate=self._border_inflate)
        pygame.draw.rect(
            surface,
            self._border_color,
            rect,
            self._border_width
        )

    def get_selection_effect(self) -> 'Selection':
        """
        Return the selection effect.

        .. note::

            If no selection has been provided, ``_NullSelection`` class
            will be returned.

        .. warning::

            Use with caution.

        :return: Selection effect
        """
        return self._selection_effect

    def set_selection_effect(self, selection: 'Selection') -> 'Widget':
        """
        Set the selection effect handler.

        .. note::

            If ``selection=None`` the selection effect will be established
            to ``_NullSelection`` class.

        :param selection: Selection effect class
        :return: Self reference
        """
        assert isinstance(selection, (Selection, type(None)))
        if selection is None:
            selection = _NullSelection()
        self._selection_effect = selection
        self._force_render()
        return self

    def apply(self, *args) -> Any:
        """
        Run ``on_return`` callback when return event. A callback function
        receives the following arguments:

        .. code-block:: python

            callback_func(value, *args, *widget._args, **widget._kwargs)

        Where
            - ``value`` if something is returned by :py:meth:`pygame_menu.widgets.core.Widget.get_value`
            - ``args`` given to this method
            - ``args`` of the widget
            - ``kwargs`` of the widget

        .. note::

            Not all widgets have an ``on_return`` method.

        :param args: Extra arguments passed to the callback
        :return: Callback return value
        """
        if self.readonly:
            return
        if self._on_return:
            args = list(args) + list(self._args)
            try:
                args.insert(0, self.get_value())
            except ValueError:
                pass
            return self._on_return(*args, **self._kwargs)

    def change(self, *args) -> Any:
        """
        Run ``on_change`` callback after change event is triggered. A callback function
        receives the following arguments:

        .. code-block:: python

            callback_func(value, *args, *widget._args, **widget._kwargs)

        Where
            - ``value`` if something is returned by :py:meth:`pygame_menu.widgets.core.Widget.get_value`
            - ``args`` given to this method
            - ``args`` of the widget
            - ``kwargs`` of the widget

        .. note::

            Not all widgets have an ``on_change`` method.

        :param args: Extra arguments passed to the callback
        :return: Callback return value
        """
        if self.readonly:
            return
        if self._on_change:
            args = list(args) + list(self._args)
            try:
                args.insert(0, self.get_value())
            except ValueError:
                pass
            return self._on_change(*args, **self._kwargs)

    def draw(self, surface: 'pygame.Surface') -> 'Widget':
        """
        Draw the widget on a given surface.

        :param surface: Surface to draw
        :return: Self reference
        """
        self._render()
        self._draw_background_color(surface)
        self._decorator.draw_prev(surface)
        self._draw(surface)
        self._draw_border(surface)
        self._decorator.draw_post(surface)
        self.apply_draw_callbacks()
        return self

    def _draw(self, surface: 'pygame.Surface') -> None:
        """
        Draw the widget on a given surface.
        This method must be overriden by all classes.

        :param surface: Surface to draw
        :return: None
        """
        raise NotImplementedError('override is mandatory')

    def draw_selection(self, surface: 'pygame.Surface') -> 'Widget':
        """
        Draw the selection widget effect on a given surface.

        :param surface: Surface to draw
        :return: Self reference
        """
        if not self.is_selectable:
            return self
        self._selection_effect.draw(surface, self)
        return self

    def get_margin(self) -> Tuple2IntType:
        """
        Return the widget margin.

        :return: Widget margin *(left, bottom)*
        """
        return self._margin

    def set_margin(self, x: NumberType, y: NumberType) -> 'Widget':
        """
        Set the widget margin *(left, bottom)*.

        :param x: Margin on x axis (left)
        :param y: Margin on y axis (bottom)
        :return: Self reference
        """
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        self._margin = (x, y)
        self._force_render()
        return self

    def get_padding(self, transformed: bool = True) -> Tuple:
        """
        Return the widget padding.

        :param transformed: If ``True``, returns the scaled padding if widget is transformed (flip, scale)
        :return: Widget padding *(top, right, bottom, left)*
        """
        if transformed:
            return self._padding_transform
        return self._padding

    def set_padding(self, padding: PaddingType) -> 'Widget':
        """
        Set the widget padding according to CSS rules.

        - If an integer or float is provided: top, right, bottom and left values will be the same
        - If 2-item tuple is provided: top and bottom takes the first value, left and right the second
        - If 3-item tuple is provided: top will take the first value, left and right the second, and bottom the third
        - If 4-item tuple is provided: padding will be *(top, right, bottom, left)*

        .. note::

            See `CSS W3Schools <https://www.w3schools.com/css/css_padding.asp>`_ for more info about padding.

        :param padding: Can be a single number, or a tuple of 2, 3 or 4 elements following CSS style
        :return: Self reference
        """
        assert isinstance(padding, (int, float, tuple, list))

        if isinstance(padding, (int, float)):
            assert padding >= 0, 'padding cannot be a negative number'
            self._padding = (padding, padding, padding, padding)
        else:
            assert 1 <= len(padding) <= 4, 'padding must be a tuple of 2, 3 or 4 elements'
            for i in range(len(padding)):
                assert isinstance(padding[i], (int, float)), 'all padding elements must be integers or floats'
                assert padding[i] >= 0, 'all padding elements must be equal or greater than zero'
            if len(padding) == 1:
                self._padding = (padding[0], padding[0], padding[0], padding[0])
            elif len(padding) == 2:
                self._padding = (padding[0], padding[1], padding[0], padding[1])
            elif len(padding) == 3:
                self._padding = (padding[0], padding[1], padding[2], padding[1])
            else:
                self._padding = (padding[0], padding[1], padding[2], padding[3])

        self._padding_transform = self._padding
        self._force_render()
        return self

    def get_rect(self, inflate: Optional[Tuple2IntType] = None, apply_padding: bool = True,
                 use_transformed_padding: bool = True) -> 'pygame.Rect':
        """
        Return the ``Rect`` object, this forces the widget rendering.

        :param inflate: Inflate rect *(x, y)* in px
        :param apply_padding: Apply widget padding
        :param use_transformed_padding: Use scaled padding if widget is scaled
        :return: Widget rect object
        """
        self._render()

        # Padding + inflate
        if inflate is None:
            inflate = (0, 0)

        padding = self.get_padding(transformed=use_transformed_padding)  # top,right,bottom,left
        pad_top = padding[0] * apply_padding + inflate[1] / 2
        pad_right = padding[1] * apply_padding + inflate[0] / 2
        pad_bottom = padding[2] * apply_padding + inflate[1] / 2
        pad_left = padding[3] * apply_padding + inflate[0] / 2

        return pygame.Rect(int(self._rect.x - pad_left),
                           int(self._rect.y - pad_top),
                           int(self._rect.width + pad_left + pad_right),
                           int(self._rect.height + pad_bottom + pad_top))

    def get_value(self) -> Any:
        """
        Return the widget value. If exception ``ValueError`` is raised,
        no value will be passed to the callbacks.

        .. warning::

            Not all widgets return a value.

        :return: Widget data value
        """
        raise ValueError('{}({}) does not accept value'.format(self.__class__.__name__,
                                                               self.get_id()))

    def get_id(self) -> str:
        """
        Return the widget ID.

        :return: Widget ID
        """
        return self._id

    def change_id(self, widget_id: str) -> 'Widget':
        """
        Change the widget ID.

        :param widget_id: Widget ID
        :return: Self reference
        """
        assert isinstance(widget_id, str)
        if self._menu is not None:
            # noinspection PyProtectedMember
            self._menu._check_id_duplicated(widget_id)
        self._id = widget_id
        return self

    def add_self_to_kwargs(self, key: str = 'widget') -> 'Widget':
        """
        Adds widget to kwargs, it helps to get the widget reference for callbacks.
        It raises ``KeyError`` if key is duplicated.

        :param key: Name of the parameter
        :return: Self reference
        """
        assert isinstance(key, str)
        if key in self._kwargs.keys():
            raise KeyError('duplicated key')
        self._kwargs[key] = self
        return self

    def _font_render_string(self, text: str, color: ColorType = (0, 0, 0),
                            use_background_color: bool = True) -> 'pygame.Surface':
        """
        Render text. If the font is not defined returns a zero-width surface.

        :param text: Text to render
        :param color: Text color
        :param use_background_color: Use default background color
        :return: Text surface
        """
        assert isinstance(text, str)
        assert isinstance(color, tuple), 'invalid color'
        assert isinstance(use_background_color, bool), 'use_background_color must be boolean'
        bgcolor = self._font_background_color

        # Disable
        if not use_background_color:
            bgcolor = None

        if self._font is None:
            return make_surface(0, 0)

        surface = self._font.render(text, self._font_antialias, color, bgcolor)
        return surface

    def _render_string(self, string: str, color: ColorType) -> 'pygame.Surface':
        """
        Render text and turn it into a surface.

        :param string: Text to render
        :param color: Text color
        :return: Text surface
        """
        text = self._font_render_string(string, color)

        # Create surface
        surface = make_surface(
            width=text.get_width(),
            height=text.get_height(),
            alpha=True
        )

        # Draw shadow first
        if self._shadow:
            text_bg = self._font_render_string(string, self._shadow_color)
            surface.blit(text_bg, self._shadow_tuple)

        surface.blit(text, (0, 0))
        return surface

    def set_shadow(self,
                   enabled: bool = True,
                   color: Optional[ColorType] = None,
                   position: Optional[str] = None,
                   offset: NumberType = 2
                   ) -> 'Widget':
        """
        Set text shadow.

        .. note::

            See :py:mod:`pygame_menu.locals` for valid ``position`` values.

        :param enabled: Shadow is enabled or not
        :param color: Shadow color
        :param position: Shadow position
        :param offset: Shadow offset
        :return: Self reference
        """
        self._shadow = enabled
        if color is not None:
            assert_color(color)
            self._shadow_color = color
        if position is not None:
            assert_position(position)
            self._shadow_position = position
        assert isinstance(offset, (int, float))
        assert offset > 0, 'shadow offset must be greater than zero'
        self._shadow_offset = int(offset)

        # Set position
        x = 0
        y = 0
        if self._shadow_position == _locals.POSITION_NORTHWEST:
            x = -1
            y = -1
        elif self._shadow_position == _locals.POSITION_NORTH:
            y = -1
        elif self._shadow_position == _locals.POSITION_NORTHEAST:
            x = 1
            y = -1
        elif self._shadow_position == _locals.POSITION_EAST:
            x = 1
        elif self._shadow_position == _locals.POSITION_SOUTHEAST:
            x = 1
            y = 1
        elif self._shadow_position == _locals.POSITION_SOUTH:
            y = 1
        elif self._shadow_position == _locals.POSITION_SOUTHWEST:
            x = -1
            y = 1
        elif self._shadow_position == _locals.POSITION_WEST:
            x = -1
        elif self._shadow_position == _locals.POSITION_CENTER:
            pass  # (0, 0)

        self._shadow_tuple = (x * self._shadow_offset, y * self._shadow_offset)
        self._force_render()
        return self

    def _apply_transforms(self) -> None:
        """
        Apply surface transforms: angle, flip and scaling.
        Translation is applied on widget positioning.

        :return: None
        """
        if self._angle != 0:
            self._surface = pygame.transform.rotate(self._surface, self._angle)

        if self._flip[0] or self._flip[1]:
            self._surface = pygame.transform.flip(self._surface, self._flip[0], self._flip[1])

        self._padding_transform = self._padding  # Reset pad scaling
        width, height = self.get_size(apply_padding=False)  # No padding
        new_size, smooth = None, None

        # Compute scale factor
        if self._max_width[0] is None and self._max_height[0] is None:
            if self._scale[0] and (self._scale[1] != 1 or self._scale[2] != 1):
                w = self._scale[1]
                h = self._scale[2]
                new_size = int(w * width), int(h * height)
                smooth = self._scale[3]
        elif self._max_width[0] is not None:
            width_pad, height_pad = self.get_size()
            if width_pad > self._max_width[0]:
                w = width * self._max_width[0] / width_pad
                if self._max_width[1]:  # If scale height
                    height *= self._max_width[0] / width_pad
                new_size = int(w), int(height)
                smooth = self._max_width[2]
        elif self._max_height[0] is not None:
            width_pad, height_pad = self.get_size()
            if height_pad > self._max_height[0]:
                h = height * self._max_height[0] / height_pad
                if self._max_height[1]:  # If scale width
                    width *= self._max_height[0] / height_pad
                new_size = int(width), int(h)
                smooth = self._max_height[2]
        else:
            raise RuntimeError('max_width and max_height cannot be non-None at the same time')

        # Apply scaling
        if new_size is not None and smooth is not None and width > 0 and height > 0:

            # Apply surface transformation
            if smooth and self._surface.get_bitsize() >= 24:
                self._surface = pygame.transform.smoothscale(self._surface, new_size)
            else:
                self._surface = pygame.transform.scale(self._surface, new_size)

            # Scale pad
            w, h = new_size
            pad_width = w / width
            pad_height = h / height

            # (top,right,bottom,left)
            self._padding_transform = (int(self._padding[0] * pad_height),
                                       int(self._padding[1] * pad_width),
                                       int(self._padding[2] * pad_height),
                                       int(self._padding[3] * pad_width))

    def get_font_color_status(self) -> ColorType:
        """
        Return the widget font color based on the widget status.

        :return: Color by widget status
        """
        if self.readonly:
            if self._selected:
                return self._font_readonly_selected_color
            return self._font_readonly_color
        if self._selected:
            return self._font_selected_color
        return self._font_color

    def set_font(self,
                 font: Union[str, 'Path'],
                 font_size: int,
                 color: ColorType,
                 selected_color: ColorType,
                 readonly_color: ColorType,
                 readonly_selected_color: ColorType,
                 background_color: Optional[ColorType],
                 antialias: bool = True
                 ) -> 'Widget':
        """
        Set the widget font.

        :param font: Font name (see :py:class:`pygame.font.match_font` for precise format)
        :param font_size: Size of font in pixels
        :param color: Normal font color
        :param selected_color: Font color if widget is selected
        :param readonly_color: Font color if widget is in readonly mode
        :param readonly_selected_color: Font color if widget is selected and in readonly mode
        :param background_color: Font background color. If ``None`` no background color is used
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :return: Self reference
        """
        assert isinstance(font, (str, Path))
        assert isinstance(font_size, int)
        assert isinstance(antialias, bool)
        assert_color(color)
        assert_color(selected_color)
        assert_color(readonly_color)
        assert_color(readonly_selected_color)

        if background_color is not None:
            assert_color(background_color)

            # If background is a color and it's transparent raise a warning
            # Font background color must be opaque, otherwise the results are quite bad
            if len(background_color) == 4 and background_color[3] != 255:
                background_color = None
                msg = 'font background color must be opaque, alpha channel must be 255'
                warnings.warn(msg)

        font_size = int(font_size)

        self._font = _fonts.get_font(font, font_size)
        self._font_antialias = antialias
        self._font_background_color = background_color
        self._font_color = color
        self._font_name = str(font)
        self._font_readonly_color = readonly_color
        self._font_readonly_selected_color = readonly_selected_color
        self._font_selected_color = selected_color
        self._font_size = font_size

        self._apply_font()
        self._force_render()
        return self

    def update_font(self, style: Dict[str, Any]) -> 'Widget':
        """
        Updates the widget font. This method receives a style dict (non empty).

        Optional style keys
            - ``antialias``                 *(bool)* - Font antialias
            - ``background_color``          *(tuple)* - Background color
            - ``color``                     *(tuple)* - Font color
            - ``name``                      *(str)* - Name of the font
            - ``readonly_color``            *(tuple)* - Readonly color
            - ``readonly_selected_color``   *(tuple)* - Readonly selected color
            - ``selected_color``            *(tuple)* - Selected color
            - ``size``                      *(int)* - Size of the font

        .. note::

            If a key is not defined it will be rewritten using current font style
            from :py:meth:`pygame_menu.widgets.core.Widget.get_font_info` method.

        :param style: Font style dict
        :return: Self reference
        """
        assert isinstance(style, dict)
        assert 1 <= len(style.keys()) <= 6
        current_font = self.get_font_info()
        for k in current_font.keys():
            if k not in style.keys():
                style[k] = current_font[k]
        return self.set_font(
            antialias=style['antialias'],
            background_color=style['background_color'],
            color=style['color'],
            font=style['name'],
            font_size=style['size'],
            readonly_color=style['readonly_color'],
            readonly_selected_color=style['readonly_selected_color'],
            selected_color=style['selected_color']
        )

    def get_font_info(self) -> Dict[str, Any]:
        """
        Return a dict with the information of the widget font.

        :return: Font information dict
        """
        return {
            'antialias': self._font_antialias,
            'background_color': self._font_background_color,
            'color': self._font_color,
            'name': self._font_name,
            'readonly_color': self._font_readonly_color,
            'readonly_selected_color': self._font_readonly_selected_color,
            'selected_color': self._font_selected_color,
            'size': self._font_size
        }

    def set_menu(self, menu: Optional['Menu']) -> 'Widget':
        """
        Set the Menu reference.

        :param menu: Menu object
        :type menu: :py:class:`pygame_menu.Menu`, None
        :return: Self reference
        """
        self._menu = menu
        if menu is None:
            self._col_row_index = (-1, -1, -1)
        return self

    def get_menu(self) -> Optional['Menu']:
        """
        Return the Menu reference, ``None`` if it has not been set.

        .. warning::

            Use with caution.

        :return: Menu reference
        :rtype: :py:class:`pygame_menu.Menu`, None
        """
        return self._menu

    def _apply_font(self) -> None:
        """
        Function triggered after a font is applied to the widget.

        :return: None
        """
        raise NotImplementedError('override is mandatory')

    def set_position(self, posx: NumberType, posy: NumberType) -> 'Widget':
        """
        Set the widget position.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        :param posx: X position in px
        :param posy: Y position in px
        :return: Self reference
        """
        assert isinstance(posx, (int, float))
        assert isinstance(posy, (int, float))
        if self.lock_position:
            return self
        self._rect.x = int(posx) + self._translate[0]
        self._rect.y = int(posy) + self._translate[1]
        return self

    def get_position(self) -> Tuple2IntType:
        """
        Return the widget position tuple *(x, y)*.

        :return: Widget position
        """
        return self._rect.x, self._rect.y

    def flip(self, x: bool, y: bool) -> 'Widget':
        """
        Transformation: This method can flip the widget either vertically, horizontally,
        or both. Flipping a widget is non-destructive and does not change the dimensions.

        .. note::

            Flip is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        :param x: Flip in x axis
        :param y: Flip on y axis
        :return: Self reference
        """
        assert isinstance(x, bool)
        assert isinstance(y, bool)
        self._flip = (x, y)
        self._force_render()
        return self

    def set_max_width(self, width: Optional[NumberType], scale_height: NumberType = False,
                      smooth: bool = True) -> 'Widget':
        """
        Transformation: Set the widget max width, it applies an scaling factor
        if the widget width is greater than the limit.

        .. note::

            If ``width=0`` the widget will use the max column width of the Menu (using
            the column the widget belongs to).

        .. note::

            Max width considers padding.

        .. note::

            Max width is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. warning::

            Final widget size may not be exactly the same as the desired *(width, height)*
            tuple due to rounding errors, expect +-2 px average.

        :param width: Width in px, ``None`` if max width is disabled
        :param scale_height: If ``True`` the height is also scaled if the width exceeds the limit
        :param smooth: Smooth scaling
        :return: Self reference
        """
        assert isinstance(scale_height, bool)
        assert isinstance(smooth, bool)

        self._disable_scale()
        if width is None:
            self._max_width[0] = None
        else:
            assert isinstance(width, (int, float)), 'width must be numeric'
            assert width >= 0, 'width must be equal or greater than zero'
            self._max_width = [width, scale_height, smooth]
            if self._scale[0]:
                msg = 'widget already has a scaling factor applied. Scaling has been' \
                      'disabled'
                warnings.warn(msg)
                return self
            if self._max_height[0] is not None:
                msg = 'widget already has a max_height. Widget max height has been disabled'
                warnings.warn(msg)
                return self

        self._force_render()
        return self

    def set_max_height(self, height: NumberType, scale_width: NumberType = False,
                       smooth: bool = True) -> 'Widget':
        """
        Transformation: Set the widget max height, it applies an scaling factor
        if the widget height is greater than the limit.

        .. note::

            Max height considers padding.

        .. note::

            Max height is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. warning::

            Final widget size may not be exactly the same as the desired *(width, height)*
            tuple due to rounding errors, expect +-2 px average.

        :param height: Height in px, ``None`` if max height is disabled
        :param scale_width: If ``True`` the width is also scaled if the height exceeds the limit
        :param smooth: Smooth scaling
        :return: Self reference
        """
        assert isinstance(scale_width, bool)
        assert isinstance(smooth, bool)

        self._disable_scale()
        if height is None:
            self._max_height[0] = None
        else:
            assert isinstance(height, (int, float)), 'height must be numeric'
            assert height > 0, 'height must be greater than zero'
            self._max_height = [height, scale_width, smooth]
            if self._scale[0]:
                msg = 'widget already has a scaling factor applied. Scaling has been' \
                      'disabled'
                warnings.warn(msg)
                return self
            if self._max_width[0] is not None:
                msg = 'widget already has a max_width. Widget max width has been disabled'
                warnings.warn(msg)
                return self

        self._force_render()
        return self

    def _disable_scale(self) -> None:
        """
        Disables widget scale.

        :return: None
        """
        self._scale[0] = False
        self._scale[1] = 1
        self._scale[2] = 1
        self._max_width[0] = None
        self._max_height[0] = None
        self.render()

    def scale(self, width: NumberType, height: NumberType, smooth: bool = True) -> 'Widget':
        """
        Transformation: Scale the widget to a desired width and height factor.

        .. note::

            Not all widgets are affected by scale.

        .. note::

            Scale considers widget padding.

        .. note::

            Scale is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. warning::

            Widget will scale only if :py:meth:`pygame_menu.widgets.core.Widget.set_max_width`
            and :py:meth:`pygame_menu.widgets.core.Widget.set_max_height` are set to ``None``.

        :param width: Scale factor of the width
        :param height: Scale factor of the height
        :param smooth: Smooth scaling
        :return: Self reference
        """
        assert isinstance(width, (int, float))
        assert isinstance(height, (int, float))
        assert isinstance(smooth, bool)
        assert width > 0 and height > 0, 'width and height must be greater than zero'

        self._disable_scale()
        if self._max_width[0] is not None:
            msg = 'widget max width is not None. Set widget.set_max_width(None) ' \
                  'for disabling such feature. This scaling will be ignored'
            warnings.warn(msg)
            return self
        if self._max_height[0] is not None:
            msg = 'widget max height is not None. Set widget.set_max_height(None) ' \
                  'for disabling such feature. This scaling will be ignored'
            warnings.warn(msg)
            return self
        self._scale = [True, width, height, smooth]
        if width == 1 and height == 1:  # Disables scaling
            self._scale[0] = False

        self._force_render()
        return self

    def resize(self, width: NumberType, height: NumberType, smooth: bool = True) -> 'Widget':
        """
        Transformation: Set the widget size to another size.

        .. note::

            This method calls :py:meth:`pygame_menu.widgets.core.Widget.scale` method;
            thus, some widgets may not support this transformation.

        .. note::

            The resize method uses the base widget size, without any transformation,
            if a scaling factor is applied it unscales and then scales back to get
            the desired width/height.

        .. note::

            Resize is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. warning::

            Final widget size may not be exactly the same as the desired *(width, height)*
            tuple due to rounding errors, expect +-2 px average.

        :param width: New width of the widget in px
        :param height: New height of the widget in px
        :param smooth: Smooth scaling
        :return: Self reference
        """
        self._disable_scale()
        if width == 1 and height == 1:
            msg = 'did you mean widget.scale(1,1) instead of widget.resize(1,1)?'
            warnings.warn(msg)
        self.scale(float(width) / self.get_width(), float(height) / self.get_height(), smooth)
        return self

    def translate(self, x: NumberType, y: NumberType) -> 'Widget':
        """
        Transformation: Translate to *(+x, +y)* according to the default position.

        .. note::

            Translate is only applied when updating the widget position (calling
            :py:meth:`pygame_menu.widgets.core.Widget.set_position`. This is done
            by Menu when rendering the surface. Thus, the position change is not
            immediate. To force translation update you may call Menu render method.

        .. note::

            To revert changes, only set to ``(0,0)``.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        :param x: +X in px
        :param y: +Y in px
        :return: None
        """
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        self._translate = (int(x), int(y))
        self._force_render()
        return self

    def rotate(self, angle: NumberType) -> 'Widget':
        """
        Transformation: Unfiltered counterclockwise rotation. The angle argument represents degrees
        and can be any floating point value. Negative angle amounts will rotate clockwise.

        .. note::

            Not all widgets accepts rotation. Also this rotation only affects the
            text or images, the selection or background is not rotated.

        .. note::

            Rotation is only applied after widget rendering. Thus, the changes are
            not immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        :param angle: Rotation angle (degrees ``0-360``)
        :return: Self reference
        """
        assert isinstance(angle, (int, float))
        self._angle = angle
        self._force_render()
        return self

    def set_alignment(self, align: str) -> 'Widget':
        """
        Set the alignment of the widget.

        .. note::

            Alignment is only applied when updating the widget position, done
            by Menu when rendering the surface. Thus, the alignment change is not
            immediate.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. note::

            See :py:mod:`pygame_menu.locals` for valid ``align`` values.

        :param align: Widget align
        :return: Self reference
        """
        assert_alignment(align)
        self._alignment = align
        self._force_render()
        return self

    def get_alignment(self) -> str:
        """
        Return the widget alignment.

        :return: Widget align
        """
        return self._alignment

    def select(self, status: bool = True, update_menu: bool = False) -> 'Widget':
        """
        Mark the widget as selected and execute the ``on_selected`` callback
        function as follows:

        .. code-block:: python

            callback_func(selected, widget, menu)

        If widget ``is_selectable`` is ``False`` this function is not executed.

        .. note::

            Use :py:meth:`pygame_menu.widgets.core.Widget.render` method to force
            widget rendering after calling this method.

        .. warning::

            This method should only be used by the menu.

        :param status: Selection status
        :param update_menu: If ``True`` this status is also applied on the menu that contains this widget
        :return: Self reference
        """
        assert isinstance(status, bool)
        if not self.is_selectable:
            return self
        self._selected = status
        self.active = False
        if self._selected:
            self._focus()
            self._selection_time = time.time()
        else:
            self._blur()
            self._events = []  # Remove events
        self._force_render()
        if self._on_select is not None:
            self._on_select(self._selected, self, self.get_menu())
        if update_menu:
            assert self._menu is not None
            self._menu.select_widget(self)
        return self

    def get_selected_time(self) -> NumberType:
        """
        Return time the widget has been selected in milliseconds.
        If the widget is not currently selected, return ``0``.

        :return: Time in milliseconds
        """
        if not self._selected:
            return 0
        return (time.time() - self._selection_time) * 1000

    def get_surface(self) -> 'pygame.Surface':
        """
        Return the widget surface.

        .. warning::

            Use with caution.

        :return: Widget surface object
        """
        return self._surface

    def get_width(self, apply_padding: bool = True, apply_selection: bool = False) -> int:
        """
        Return the widget width.

        .. warning::

            If the widget is not rendered, this method will return ``0``.

        :param apply_padding: Apply padding
        :param apply_selection: Apply selection
        :return: Widget width (px)
        """
        assert isinstance(apply_padding, bool)
        assert isinstance(apply_selection, bool)
        rect = self.get_rect(apply_padding=apply_padding)
        width = rect.width
        if apply_selection:
            width += self._selection_effect.get_width()
        return int(width)

    def get_height(self, apply_padding: bool = True, apply_selection: bool = False) -> int:
        """
        Return the widget height.

        .. warning::

            If the widget is not rendered, this method will return ``0``.

        :param apply_padding: Apply padding
        :param apply_selection: Apply selection
        :return: Widget height (px)
        """
        assert isinstance(apply_padding, bool)
        assert isinstance(apply_selection, bool)
        rect = self.get_rect(apply_padding=apply_padding)
        height = rect.height
        if apply_selection:
            height += self._selection_effect.get_height()
        return int(height)

    def get_size(self, apply_padding: bool = True, apply_selection: bool = False) -> Tuple2IntType:
        """
        Return the widget size.

        .. warning::

            If the widget is not rendered this method might return ``(0,0)``.

        :param apply_padding: Apply padding
        :param apply_selection: Apply selection
        :return: Widget *(width, height)*
        """
        return self.get_width(apply_padding=apply_padding, apply_selection=apply_selection), \
               self.get_height(apply_padding=apply_padding, apply_selection=apply_selection)

    def _focus(self) -> None:
        """
        Function that is executed when the widget receives a focus (is selected).

        :return: None
        """
        pass

    def _blur(self) -> None:
        """
        Function that is executed when the widget loses the focus.

        :return: None
        """
        pass

    def set_sound(self, sound: 'Sound') -> 'Widget':
        """
        Set sound engine to the widget.

        :param sound: Sound object
        :return: Self reference
        """
        self._sound = sound
        return self

    def set_controls(self, joystick: bool = True, mouse: bool = True, touchscreen: bool = True) -> 'Widget':
        """
        Enable interfaces to control the widget.

        :param joystick: Use joystick
        :param mouse: Use mouse
        :param touchscreen: Use touchscreen
        :return: Self reference
        """
        assert isinstance(joystick, bool)
        assert isinstance(mouse, bool)
        assert isinstance(touchscreen, bool)
        self._joystick_enabled = joystick
        self._mouse_enabled = mouse
        self._touchscreen_enabled = touchscreen
        return self

    def set_value(self, value: Any) -> None:
        """
        Set the widget value.

        .. note::

            Not all widgets accepts a value, for example the image widget.

        .. warning::

            This method does not fire the callbacks as it is called programmatically.
            This behavior is deliberately chosen to avoid infinite loops.

        :param value: Value to be set on the widget
        :return: None
        """
        raise ValueError('{}({}) does not accept value'.format(self.__class__.__name__,
                                                               self.get_id()))

    def set_default_value(self, value: Any) -> 'Widget':
        """
        Set the widget value, and then make it as default.

        .. note::

            This method is intended to be used along :py:meth:`pygame_menu.widgets.core.Widget.reset_value`
            method that sets the widget value back to the default set with this method.

        .. note::

            Not all widgets accepts a value, for example the image widget.

        :param value: Default widget value
        :return: Self reference
        """
        self.set_value(value)
        self._default_value = value
        return self

    def reset_value(self) -> 'Widget':
        """
        Reset the widget value to the default one.

        :return: Self reference
        """
        if not isinstance(self._default_value, _NoWidgetValue):
            self.set_value(self._default_value)
        return self

    def update(self, events: Union[List['pygame.event.Event'], Tuple['pygame.event.Event']]) -> bool:
        """
        Update according to the given events list and fire the callbacks.
        This method must return ``True`` if it updated (the internal variables
        changed during user input).

        :param events: List/Tuple of pygame events
        :return: ``True`` if updated
        """
        raise NotImplementedError('override is mandatory')

    def add_draw_callback(self, draw_callback: Callable[['Widget', 'Menu'], Any]) -> str:
        """
        Adds a function to the widget to be executed each time the widget is drawn.

        The function that this method receives receives two objects: the widget itself and
        the Menu reference.

        .. code-block:: python

            import math

            def draw_update_function(widget, menu):
                t = widget.get_attribute('t', 0)
                t += menu.get_clock().get_time()
                widget.set_padding(10*(1 + math.sin(t)))) # Oscillating padding

            button = menu.add_button('This button updates its padding', None)
            button.set_draw_callback(draw_update_function)

        After creating a new callback, this functions returns the ID of the call. It can be
        removed anytime using :py:meth:`pygame_menu.widgets.core.Widget.remove_draw_callback`

        .. note::

            If Menu surface cache is enabled this method may run only once. To force run
            the added method each time call ``widget.force_menu_surface_update()`` to force
            Menu update the cache status if the drawing callback does not make the widget
            to render. Remember that rendering the widget forces the Menu to update its
            surface, thus updating the cache too.

        :param draw_callback: Function
        :type draw_callback: callable, None
        :return: Callback ID
        """
        assert is_callable(draw_callback), 'draw callback must be callable (function-type)'
        callback_id = str(uuid4())
        self._draw_callbacks[callback_id] = draw_callback
        return callback_id

    def remove_draw_callback(self, callback_id: str) -> 'Widget':
        """
        Removes draw callback from ID.

        :param callback_id: Callback ID
        :return: Self reference
        """
        assert isinstance(callback_id, str)
        if callback_id not in self._draw_callbacks.keys():
            raise IndexError('callback ID "{0}" does not exist'.format(callback_id))
        del self._draw_callbacks[callback_id]
        return self

    def apply_draw_callbacks(self) -> 'Widget':
        """
        Apply callbacks on widget draw.

        :return: Self reference
        """
        if len(self._draw_callbacks) == 0:
            return self
        for callback in self._draw_callbacks.values():
            callback(self, self._menu)
        return self

    def add_update_callback(self, update_callback: Callable[['Widget', 'Menu'], Any]) -> str:
        """
        Adds a function to the widget to be executed each time the widget is updated.

        The function that this method receives receives two objects: the widget itself and
        the Menu reference. It is similar to :py:meth:`pygame_menu.widgets.core.Widget.add_draw_callback`

        After creating a new callback, this functions returns the ID of the call. It can be removed
        anytime using :py:meth:`pygame_menu.widgets.core.Widget.remove_update_callback`.

        .. note::

            Not all widgets are updated, so the provided function may never be executed
            in some widgets (for example, label or images).

        :param update_callback: Function
        :type update_callback: callable, None
        :return: Callback ID
        """
        assert is_callable(update_callback), 'update callback must be callable (function-type)'
        callback_id = str(uuid4())
        self._update_callbacks[callback_id] = update_callback
        return callback_id

    def remove_update_callback(self, callback_id: str) -> 'Widget':
        """
        Removes update callback from ID.

        :param callback_id: Callback ID
        :return: Self reference
        """
        assert isinstance(callback_id, str)
        if callback_id not in self._update_callbacks.keys():
            raise IndexError('callback ID "{0}" does not exist'.format(callback_id))
        del self._update_callbacks[callback_id]
        return self

    def apply_update_callbacks(self) -> 'Widget':
        """
        Apply callbacks on widget update.

        :return: Self reference
        """
        if len(self._update_callbacks) == 0 or self.readonly:
            return self
        for callback in self._update_callbacks.values():
            callback(self, self._menu)
        return self

    def _add_event(self, event: 'pygame.event.Event') -> None:
        """
        Add a custom event to the widget for the next update.

        :param event: Custom event
        :return: None
        """
        self._events.append(event)

    def _merge_events(self, events: List['pygame.event.Event']) -> List['pygame.event.Event']:
        """
        Append widget events to events list.

        :param events: Event list
        :return: Augmented event list
        """
        if len(self._events) == 0:
            return events
        copy_events = []
        for e in events:
            copy_events.append(e)
        for e in self._events:
            copy_events.append(e)
        self._events = []
        return copy_events

    def set_float(self, float_status: bool = True, menu_render: bool = False) -> 'Widget':
        """
        Set the floating status. If ``True`` the widget don't contributes
        the width/height to the Menu widget positioning computation (for example,
        the surface area or the column/row layout), and don't add one unit to
        the rows (use the same vertical place as the previous widget.

        For example, before floating:

            .. code-block:: python

                ----------------------------
                |    wid1    |    wid3     |
                |    wid2    |    wid4     |
                ----------------------------

        After ``wid3.set_float(True)``:

            .. code-block:: python

                ----------------------------
                |    wid1    |    wid4     |
                | wid2,wid3  |             |
                ----------------------------

        :param float_status: Float status
        :param menu_render: If ``True`` forces the menu to render instantly
        :return: None
        """
        assert isinstance(float_status, bool)
        self._floating = float_status
        self.force_menu_surface_update()
        if menu_render and self._menu is not None:
            self._menu.render()
        return self

    def show(self) -> 'Widget':
        """
        Set the widget visible.

        :return: Self reference
        """
        self._visible = True
        self._render()
        if self._menu is not None:
            # noinspection PyProtectedMember
            self._menu._update_selection_if_hidden()
        return self

    def hide(self) -> 'Widget':
        """
        Hides the widget.

        :return: Self reference
        """
        self._visible = False
        self._render()
        if self._menu is not None:
            # noinspection PyProtectedMember
            self._menu._update_selection_if_hidden()
        return self

    def set_col_row_index(self, col: int, row: int, index: int) -> 'Widget':
        """
        Set the *(column,row,index)* position. If the column or row is ``-1`` then the
        widget is not assigned to a certain column/row (for example, if it's hidden).

        :param col: Column
        :param row: Row
        :param index: Index in Menu widget list
        :return: Self reference
        """
        assert isinstance(col, int) and col >= -1
        assert isinstance(row, int) and row >= -1
        assert isinstance(index, int) and index >= -1
        self._col_row_index = (col, row, index)
        return self

    def get_col_row_index(self) -> Tuple3IntType:
        """
        Get the widget column/row position.

        :return: *(column, row, index)* tuple
        """
        return self._col_row_index

    def set_border(self, width: int, color: ColorType, inflate: Tuple2IntType) -> 'Widget':
        """
        Set widget border.

        :param width: Border width (px)
        :param color: Border color
        :param inflate: Inflate in *(x, y)* axis in px
        :return: Self reference
        """
        assert isinstance(width, int) and width >= 0
        assert_color(color)
        assert isinstance(inflate, tuple) and inflate[0] >= 0 and inflate[1] >= 0
        self._border_width = width
        self._border_color = color
        self._border_inflate = inflate
        return self

    def get_decorator(self) -> 'Decorator':
        """
        Return the Widget decorator API.

        :return: Decorator API
        """
        return self._decorator


# noinspection PyMissingOrEmptyDocstring
class _NullSelection(Selection):
    """
    Null selection. It redefines :py:class:`pygame_menu.widgets.selection.NoneSelection`
    because that class cannot be imported directly from widget.py.

    .. note::

        Prefer using :py:class:`pygame_menu.widgets.selection.NoneSelection` class instead.
    """

    def __init__(self) -> None:
        super(_NullSelection, self).__init__(
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0
        )

    def draw(self, surface: 'pygame.Surface', widget: 'Widget') -> None:
        return


class _WidgetCopyException(Exception):
    """
    If user tries to copy a Widget.
    """
    pass


class _NoWidgetValue(object):
    """
    No value class.
    """

    def __init__(self) -> None:
        pass
