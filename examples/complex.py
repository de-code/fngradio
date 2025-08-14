from typing import Annotated, Literal

from pydantic import Field

import gradio as gr

from fngradio import FnGradioApp


app = FnGradioApp()


@app.interface()
def add_int_numbers_with_sliders(
    a: Annotated[int, Field(title="First value", ge=0, le=100)] = 50,
    b: Annotated[int, Field(title="Second value", ge=0, le=100)] = 50
) -> int:
    """
    Add two int numbers
    """
    return a + b


@app.interface()
def add_float_numbers(
    a: Annotated[int, Field(title="First value")],
    b: Annotated[int, Field(title="Second value")]
) -> int:
    """
    Add two float numbers
    """
    return a + b


@app.interface()
def to_upper_case(
    s: Annotated[str, gr.TextArea(label="text", value="Hello")]
) -> Annotated[str, gr.TextArea()]:
    """
    Converts text to upper case
    """
    return s.upper()


@app.interface()
def say(what: Literal["hi", "bye"]) -> str:
    """
    Says Hi! or Bye!
    """
    return "Hi!" if what == "hi" else "Bye!"


demo = app.tabbed()


if __name__ == '__main__':
    demo.launch(share=False, mcp_server=True)
