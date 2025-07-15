from dataclasses import dataclass
import inspect
import logging
from typing import Annotated, Any, Callable, cast, get_args, get_origin, get_type_hints

import annotated_types
from pydantic.fields import FieldInfo

import gradio as gr


LOGGER = logging.getLogger(__name__)


class UnsupportedTypeError(ValueError):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(f'Unsupported type: {type_hint}')
        self.type_hint = type_hint


@dataclass(frozen=True)
class ParsedFieldInfo:
    title: str | None = None
    ge: annotated_types.SupportsGe | None = None
    le: annotated_types.SupportsLe | None = None


DEFAULT_PARSED_FIELD_INFO = ParsedFieldInfo()


def parse_pydantic_field_info(field_info: FieldInfo) -> ParsedFieldInfo:
    ge: annotated_types.SupportsGe | None = None
    le: annotated_types.SupportsLe | None = None
    for meta in field_info.metadata:
        if isinstance(meta, annotated_types.Ge):
            ge = meta.ge
        if isinstance(meta, annotated_types.Le):
            le = meta.le
    return ParsedFieldInfo(title=field_info.title, ge=ge, le=le)


def parse_pydantic_field(type_hint) -> tuple[Any, ParsedFieldInfo]:
    origin = get_origin(type_hint)
    if origin is Annotated:
        base, *extras = get_args(type_hint)
        LOGGER.debug('extras: %r', extras)
        field_info = next((e for e in extras if isinstance(e, FieldInfo)), None)
        if field_info is not None:
            return base, parse_pydantic_field_info(field_info)
    return type_hint, DEFAULT_PARSED_FIELD_INFO


def get_gradio_component(type_hint) -> gr.Component | None:
    origin = get_origin(type_hint)
    if origin is Annotated:
        _base, *extras = get_args(type_hint)
        LOGGER.debug('extras: %r', extras)
        component = next((e for e in extras if isinstance(e, gr.Component)), None)
        return component
    return None


class FnGradio:
    def get_component(
        self,
        type_hint: Any,
        default_value: Any | None = None
    ) -> gr.Component:
        gradio_component = get_gradio_component(type_hint)
        if gradio_component is not None:
            return gradio_component
        parsed_type_hint, field_info = parse_pydantic_field(type_hint)
        LOGGER.debug('field_info: %r', field_info)
        label = field_info.title
        if parsed_type_hint is bool:
            return gr.Checkbox(value=bool(default_value), label=label)
        if parsed_type_hint is int and field_info is not None:
            if field_info.ge is not None and field_info.le is not None:
                return gr.Slider(
                    minimum=cast(float, field_info.ge),
                    maximum=cast(float, field_info.le),
                    value=default_value,
                    label=label,
                    step=1
                )
        if parsed_type_hint is int:
            return gr.Number(precision=0, value=default_value, label=label)
        if parsed_type_hint is float:
            return gr.Number(value=default_value, label=label)
        if parsed_type_hint is str:
            return gr.Textbox(value=default_value, label=label)
        raise UnsupportedTypeError(type_hint)

    def interface(self, fn: Callable, **kwargs) -> gr.Interface:
        hints = get_type_hints(fn, include_extras=True)
        sig = inspect.signature(fn)
        inputs = [
            self.get_component(
                type_hint=hints.get(name),
                default_value=param.default if param.default is not param.empty else None
            )
            for name, param in sig.parameters.items()
        ]
        outputs = [
            self.get_component(hints.get('return'))
        ]
        return gr.Interface(
            fn=fn,
            api_name=fn.__name__,
            inputs=inputs,
            outputs=outputs,
            **kwargs
        )


DEFAULT_FNGRADIO = FnGradio()

interface = DEFAULT_FNGRADIO.interface
