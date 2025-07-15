from typing import Sequence
import gradio as gr


def tabbed_interface(
    interface_list: Sequence[gr.Blocks],
    tab_names: Sequence[str] | None = None,
    **kwargs
) -> gr.TabbedInterface:
    if not tab_names:
        tab_names = [
            (
                interface.api_name
                if isinstance(interface, gr.Interface) and interface.api_name
                else f'Tab {1 + index}'
            )
            for index, interface in enumerate(interface_list)
        ]
    return gr.TabbedInterface(
        interface_list=interface_list,
        tab_names=list(tab_names),
        **kwargs
    )
