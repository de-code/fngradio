from typing import Annotated, Literal
import gradio as gr
from pydantic import Field
import pytest

from fngradio.decorators import FnGradio, UnsupportedTypeError, get_literal_values


@pytest.fixture(name='fngr')
def _fngr() -> FnGradio:
    return FnGradio()


class TestGetLiteralValues:
    def test_should_return_values(self):
        assert get_literal_values(Literal['a', 'b']) == ('a', 'b')


class TestFnGradio:
    class TestGetComponent:
        def test_should_use_gradio_component_if_present(self, fngr: FnGradio):
            component = fngr.get_component(Annotated[str, gr.TextArea()])
            assert isinstance(component, gr.TextArea)

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

        def test_should_map_literal_to_dropdown(self, fngr: FnGradio):
            component = fngr.get_component(
                type_hint=Literal['value_1', 'value_2', 'value_3'],
                default_value='value_2'
            )
            assert isinstance(component, gr.Dropdown)
            assert component.choices == [
                ('value_1', 'value_1'),
                ('value_2', 'value_2'),
                ('value_3', 'value_3')
            ]
            assert component.value == 'value_2'

        def test_should_map_annotated_literal_to_dropdown(self, fngr: FnGradio):
            component = fngr.get_component(
                type_hint=Annotated[
                    Literal['value_1', 'value_2', 'value_3'],
                    Field(title='Label 1')
                ],
                default_value='value_2'
            )
            assert isinstance(component, gr.Dropdown)
            assert component.choices == [
                ('value_1', 'value_1'),
                ('value_2', 'value_2'),
                ('value_3', 'value_3')
            ]
            assert component.value == 'value_2'
            assert component.label == 'Label 1'

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
                fngr.interface()(fn)

        def test_should_create_gradio_interface_with_simple_type(
            self,
            fngr: FnGradio
        ):
            @fngr.interface()
            def fn(s: str) -> str:
                return s.upper()

            assert fn.input_components and len(fn.input_components) == 1
            assert isinstance(fn.input_components[0], gr.Textbox)
            assert len(fn.output_components) == 1
            assert isinstance(fn.output_components[0], gr.Textbox)

        def test_should_create_gradio_interface_with_slider(
            self,
            fngr: FnGradio
        ):
            @fngr.interface()
            def fn(n: Annotated[int, Field(ge=10, le=100)] = 50) -> int:
                return n

            assert fn.input_components and len(fn.input_components) == 1
            input_component = fn.input_components[0]
            assert isinstance(input_component, gr.Slider)
            assert input_component.minimum == 10
            assert input_component.maximum == 100
            assert input_component.value == 50

        def test_should_set_api_name_to_function_name(
            self,
            fngr: FnGradio
        ):
            @fngr.interface()
            def fn(s: str) -> str:
                return s.upper()

            assert fn.api_name == 'fn'

        def test_should_allow_overriding_api_name(
            self,
            fngr: FnGradio
        ):
            @fngr.interface(api_name='fn_1')
            def fn(s: str) -> str:
                return s.upper()

            assert fn.api_name == 'fn_1'
