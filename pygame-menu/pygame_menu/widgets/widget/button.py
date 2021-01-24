"""
pygame-menu
https://github.com/ppizarror/pygame-menu

BUTTON
Button class, manage elements and adds entries to Menu.

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

__all__ = ['Button']

import pygame
from pygame_menu.utils import is_callable
from pygame_menu.widgets.core import Widget
import pygame_menu.controls as _controls
from pygame_menu._custom_types import Any, CallbackType, Callable, TYPE_CHECKING, Union, List, Tuple, Optional

if TYPE_CHECKING:
    from pygame_menu.menu import Menu


# noinspection PyMissingOrEmptyDocstring
class Button(Widget):
    """
    Button widget.

    The arguments and unknown keyword arguments are passed to the ``onreturn``
    function:

    .. code-block:: python

        onreturn(*args, **kwargs)

    :param title: Button title
    :param button_id: Button ID
    :param onreturn: Callback when pressing the button
    :param args: Optional arguments for callbacks
    :param kwargs: Optional keyword arguments
    """
    to_menu: bool

    def __init__(self,
                 title: Any,
                 button_id: str = '',
                 onreturn: CallbackType = None,
                 *args,
                 **kwargs
                 ) -> None:
        super(Button, self).__init__(
            args=args,
            kwargs=kwargs,
            onreturn=onreturn,
            title=title,
            widget_id=button_id
        )
        self.to_menu = False  # True if the button opens a new Menu

    def _apply_font(self) -> None:
        pass

    def set_selection_callback(self, callback: Optional[Callable[[bool, 'Widget', 'Menu'], Any]]) -> None:
        """
        Update the button selection callback, once button is selected, the callback
        function is executed as follows:

        .. code-block:: python

            callback(selected, widget, menu)

        :param callback: Callback when selecting the widget, executed in :py:meth:`pygame_menu.widgets.core.Widget.set_selected`
        :type callback: callable, None
        :return: None
        """
        if callback is not None:
            assert is_callable(callback), 'callback must be callable (function-type) or None'
        self._on_select = callback

    def update_callback(self, callback: Callable, *args) -> None:
        """
        Update function triggered by the button; ``callback`` cannot point to a Menu, that
        behaviour is only valid using :py:meth:`pygame_menu.Menu.add_button` method.

        .. note::

            If button points to a submenu, and the callback is changed to a function,
            the submenu will be removed from the parent Menu. Thus preserving the structure.

        :param callback: Function
        :param args: Arguments used by the function once triggered
        :return: None
        """
        assert is_callable(callback), 'only callable (function-type) are allowed'

        # If return is a Menu object, remove it from submenus list
        if self._menu is not None and self._on_return is not None and self.to_menu:
            assert len(self._args) == 1
            submenu = self._args[0]  # Menu
            assert self._menu.in_submenu(submenu), \
                'pointed menu is not in submenu list of parent container'
            # noinspection PyProtectedMember
            assert self._menu._remove_submenu(submenu), 'submenu could not be removed'
            self.to_menu = False

        self._args = args or []
        self._on_return = callback

    def _draw(self, surface: 'pygame.Surface') -> None:
        surface.blit(self._surface, self._rect.topleft)

    def _render(self) -> Optional[bool]:
        if not self._render_hash_changed(self._selected, self._title, self._visible, self.readonly):
            return True
        self._surface = self._render_string(self._title, self.get_font_color_status())
        self._apply_transforms()
        self._rect.width, self._rect.height = self._surface.get_size()
        self.force_menu_surface_update()

    def update(self, events: Union[List['pygame.event.Event'], Tuple['pygame.event.Event']]) -> bool:
        if self.readonly:
            return False
        updated = False
        rect = self.get_rect()  # Padding increases the extents of the button

        for event in events:

            if event.type == pygame.KEYDOWN and event.key == _controls.KEY_APPLY or \
                    self._joystick_enabled and event.type == pygame.JOYBUTTONDOWN and \
                    event.button == _controls.JOY_BUTTON_SELECT:
                self._sound.play_open_menu()
                self.apply()
                updated = True

            elif self._mouse_enabled and event.type == pygame.MOUSEBUTTONUP:
                self._sound.play_click_mouse()
                if rect.collidepoint(*event.pos):
                    self.apply()
                    updated = True

            elif self._touchscreen_enabled and event.type == pygame.FINGERUP:
                self._sound.play_click_mouse()
                window_size = self.get_menu().get_window_size()
                finger_pos = (event.x * window_size[0], event.y * window_size[1])
                if rect.collidepoint(*finger_pos):
                    self.apply()
                    updated = True

        if updated:
            self.apply_update_callbacks()

        return updated
