from typing import Annotated

from pydantic import Field

import fngradio as fngr


@fngr.interface
def add_int_numbers_with_sliders(
    a: Annotated[int, Field(title="First value", ge=0, le=100)] = 50,
    b: Annotated[int, Field(title="Second value", ge=0, le=100)] = 50
) -> int:
    """
    Add two int numbers
    """
    return a + b


@fngr.interface
def add_float_numbers(
    a: Annotated[int, Field(title="First value")],
    b: Annotated[int, Field(title="Second value")]
) -> int:
    """
    Add two float numbers
    """
    return a + b


demo = fngr.tabbed_interface([
    add_int_numbers_with_sliders,
    add_float_numbers
])


if __name__ == '__main__':
    demo.launch(share=False)
