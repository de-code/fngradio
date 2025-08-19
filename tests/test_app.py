import pytest

import gradio as gr

from fngradio.app import FnGradioApp


@pytest.fixture(name='fngr_app')
def _fngr_app() -> FnGradioApp:
    return FnGradioApp()


class TestFnGradioApp:
    def test_should_create_gradio_interface_with_simple_type(
        self,
        fngr_app: FnGradioApp
    ):
        @fngr_app.interface()
        def fn(s: str) -> str:
            return s.upper()

        assert fn.input_components and len(fn.input_components) == 1
        assert isinstance(fn.input_components[0], gr.Textbox)
        assert len(fn.output_components) == 1
        assert isinstance(fn.output_components[0], gr.Textbox)

    def test_should_remember_interfaces(
        self,
        fngr_app: FnGradioApp
    ):
        @fngr_app.interface()
        def fn(s: str) -> str:
            return s.upper()

        interfaces = fngr_app.get_interfaces()
        assert interfaces == [fn]

    def test_should_create_tabbed_interface(
        self,
        fngr_app: FnGradioApp
    ):
        @fngr_app.interface()
        def fn(s: str) -> str:
            return s.upper()

        demo = fngr_app.tabbed()
        assert isinstance(demo, gr.TabbedInterface)

    def test_should_combine_apps(
        self
    ):
        app_1 = FnGradioApp()
        app_2 = FnGradioApp()

        @app_1.interface()
        def upper(s: str) -> str:
            return s.upper()

        @app_2.interface()
        def lower(s: str) -> str:
            return s.lower()

        fngr_app = FnGradioApp(apps=[app_1, app_2])
        assert fngr_app.get_interfaces() == (
            list(app_1.get_interfaces()) + list(app_2.get_interfaces())
        )
