from typing import Sequence

import gradio as gr

from fngradio.decorators import FnGradio
from fngradio.tabbed_interface import tabbed_interface


class FnGradioApp(FnGradio):
    def __init__(self, apps: Sequence['FnGradioApp'] | None = None) -> None:
        super().__init__()
        self._interfaces: list[gr.Interface] = []
        if apps is not None:
            for app in apps:
                self._interfaces.extend(app._interfaces)

    def get_interfaces(self) -> Sequence[gr.Interface]:
        return self._interfaces

    def _on_interface(self, interface: gr.Interface):
        super()._on_interface(interface)
        self._interfaces.append(interface)

    def tabbed(
        self,
        tab_names: Sequence[str] | None = None,
        **kwargs
    ) -> gr.TabbedInterface:
        return tabbed_interface(
            self._interfaces,
            tab_names=tab_names,
            **kwargs
        )
