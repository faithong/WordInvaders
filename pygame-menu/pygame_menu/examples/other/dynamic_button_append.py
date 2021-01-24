"""
pygame-menu
https://github.com/ppizarror/pygame-menu

EXAMPLE - DYNAMIC BUTTON
Menu with dynamic buttons.

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

__all__ = ['main']

import pygame_menu
from pygame_menu.examples import create_example_window

from random import randrange

surface = create_example_window('Example - Dynamic Button Append', (600, 400))
menu = pygame_menu.Menu(
    height=300,
    theme=pygame_menu.themes.THEME_BLUE,
    title='Welcome',
    width=400
)


def add_dynamic_button() -> None:
    """
    Append a button to the menu on demand.

    :return: None
    """
    print('Adding a button dynamically')
    btn = menu.add_button(randrange(0, 10), None)

    def _update_button() -> None:
        count = btn.get_attribute('count', int(btn.get_title())) + 1
        btn.set_title(count)
        btn.set_attribute('count', count)

    btn.update_callback(_update_button)


menu.add_text_input('Name: ', default='John Doe')
menu.add_button('Play', add_dynamic_button)
menu.add_button('Quit', pygame_menu.events.EXIT)


def main(test: bool = False) -> None:
    """
    Main function.

    :param test: Indicate function is being tested
    :return: None
    """
    menu.mainloop(surface, disable_loop=test)


if __name__ == '__main__':
    main()
