from typing import Annotated
import gradio as gr
from pydantic import Field
import pytest

from fngradio.decorators import FnGradio, UnsupportedTypeError


@pytest.fixture(name='fngr')
def _fngr() -> FnGradio:
    return FnGradio()


class TestFnGradio:
    class TestGetComponent:
        def test_should_map_str_to_textbox(self, fngr: FnGradio):
            component = fngr.get_component(str)
            assert isinstance(component, gr.Textbox)

        def test_should_map_str_with_label_to_textbox(self, fngr: FnGradio):
            component = fngr.get_component(
                Annotated[str, Field(title='Label 1')],
                default_value='Default 1'
            )
            assert isinstance(component, gr.Textbox)
            assert component.value == 'Default 1'
            assert component.label == 'Label 1'

        def test_should_map_int_to_number_with_zero_precision(self, fngr: FnGradio):
            component = fngr.get_component(int, default_value=10)
            assert isinstance(component, gr.Number)
            assert component.precision == 0
            assert component.value == 10

        def test_should_map_float_to_number_with_default_precision(self, fngr: FnGradio):
            component = fngr.get_component(float, default_value=10.5)
            assert isinstance(component, gr.Number)
            assert component.precision != 0
            assert component.value == 10.5

        def test_should_map_bool_to_checkbox_without_default(self, fngr: FnGradio):
            component = fngr.get_component(
                type_hint=bool,
                default_value=None
            )
            assert isinstance(component, gr.Checkbox)
            assert component.value is False

        def test_should_map_bool_to_checkbox_with_true_default(self, fngr: FnGradio):
            component = fngr.get_component(
                type_hint=bool,
                default_value=True
            )
            assert isinstance(component, gr.Checkbox)
            assert component.value is True

        def test_should_map_int_field_with_range_to_slider(self, fngr: FnGradio):
            component = fngr.get_component(
                type_hint=Annotated[int, Field(ge=10, le=100, title='Label 1')],
                default_value=50
            )
            assert isinstance(component, gr.Slider)
            assert component.minimum == 10
            assert component.maximum == 100
            assert component.value == 50
            assert component.step == 1
            assert component.label == 'Label 1'

    class TestInterface:
        def test_should_fail_without_type_hints(
            self,
            fngr: FnGradio
        ):
            def fn(s):
                return s.upper()

            with pytest.raises(UnsupportedTypeError):
                fngr.interface(fn)

        def test_should_create_gradio_interface_with_simple_type(
            self,
            fngr: FnGradio
        ):
            def fn(s: str) -> str:
                return s.upper()

            interface = fngr.interface(fn)
            assert interface.input_components and len(interface.input_components) == 1
            assert isinstance(interface.input_components[0], gr.Textbox)
            assert len(interface.output_components) == 1
            assert isinstance(interface.output_components[0], gr.Textbox)

        def test_should_create_gradio_interface_with_slider(
            self,
            fngr: FnGradio
        ):
            def fn(n: Annotated[int, Field(ge=10, le=100)] = 50) -> int:
                return n

            interface = fngr.interface(fn)
            assert interface.input_components and len(interface.input_components) == 1
            input_component = interface.input_components[0]
            assert isinstance(input_component, gr.Slider)
            assert input_component.minimum == 10
            assert input_component.maximum == 100
            assert input_component.value == 50

        def test_should_set_api_name_to_function_name(
            self,
            fngr: FnGradio
        ):
            def fn(s: str) -> str:
                return s.upper()

            interface = fngr.interface(fn)
            assert interface.api_name == 'fn'
