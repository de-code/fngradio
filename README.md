# FnGradio

This is an experimental library that allows you to define Gradio apps using type hints.

## Install

```
pip install fngradio
```

## Simple Example

Instead of (where type hints are not used for the interface):

```python
import gradio as gr


def add_int_numbers(a: int, b: int) -> int:
    """
    Add two int numbers
    """
    return a + b


demo = gr.Interface(
    fn=add_int_numbers,
    api_name="add_int_numbers",
    inputs=[
        gr.Number(precision=0),
        gr.Number(precision=0)
    ],
    outputs=[gr.Number(precision=0)],
)

if __name__ == '__main__':
    demo.launch(share=False)
```

You can define the Gradio interface around by just adding the `fngr.interface` annotation which will create `inputs` and `outputs` based on the type hints:

```python
import fngradio as fngr


@fngr.interface()
def add_int_numbers(a: int, b: int) -> int:
    """
    Add two int numbers
    """
    return a + b


if __name__ == '__main__':
    add_int_numbers.launch(share=False)
```

## Slider for Integer With Range

You can use [pydantic](https://github.com/pydantic/pydantic)'s `Field` annotation to provide additional information. If `ge` and `le` are defined for an integer, then it will use the Gradio's Slider component.

```python
from typing import Annotated
from pydantic import Field
import fngradio as fngr


@fngr.interface()
def add_int_numbers_with_sliders(
    a: Annotated[int, Field(title="First value", ge=0, le=100)] = 50,
    b: Annotated[int, Field(title="Second value", ge=0, le=100)] = 50
) -> int:
    """
    Add two int numbers
    """
    return a + b
```

## Dropdown for Literal

```python
from typing import Literal
from pydantic import Field
import fngradio as fngr


@fngr.interface
def say(what: Literal["hi", "bye"]) -> str:
    """
    Says Hi! or Bye!
    """
    return "Hi!" if what == "hi" else "Bye!"
```

## Specify Component in Type Annotation

You can also specify the Gradio Component to use by adding it to the type annotation:

```python
from typing import Annotated
import gradio as gr
import fngradio as fngr


@fngr.interface()
def to_upper_case(
    s: Annotated[str, gr.TextArea(label="text", value="Hello")]
) -> Annotated[str, gr.TextArea()]:
    """
    Converts text to upper case
    """
    return s.upper()
```

## Tabbed Interface

A tabbed interface can be useful when you have multiple tools (e.g. multiple MCP tools).

Instead of:

```python
demo = gr.TabbedInterface(
    interface_list=[
        add_int_numbers,
        to_upper_case
    ],
    tab_names=["add_int_numbers", "to_upper_case"]
)
```

You could use the `fngr.tabbed_interface`:

```python
demo = fngr.tabbed_interface([
    add_int_numbers,
    to_upper_case
])
```

The main advantage is that it will try to infer the names from the interface.

Or even simpler use `FnGradioApp` for defining interfaces:

```python
from fngradio import FnGradioApp


app = FnGradioApp()

@app.interface()
def add_int_numbers(a: int, b: int) -> int:
    """
    Add two int numbers
    """
    return a + b


@app.interface()
def to_upper_case(s: str) -> str:
    """
    Converts text to upper case
    """
    return s.upper()


demo = app.tabbed()

if __name__ == '__main__':
    demo.launch(share=False)
```
