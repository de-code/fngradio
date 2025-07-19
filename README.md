# FnGradio

Define Gradio apps using type hints.

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


@fngr.interface
def add_int_numbers(a: int, b: int) -> int:
    """
    Add two int numbers
    """
    return a + b


if __name__ == '__main__':
    add_int_numbers.launch(share=False)
```

