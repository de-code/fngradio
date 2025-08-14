from dataclasses import dataclass
import inspect
import logging
from typing import (
    Annotated,
    Any,
    Callable,
    Literal,
    Sequence,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints
)

import annotated_types
from pydantic.fields import FieldInfo

import gradio as gr


LOGGER = logging.getLogger(__name__)


T = TypeVar('T')


class UnsupportedTypeError(ValueError):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(f'Unsupported type: {type_hint}')
        self.type_hint = type_hint


@dataclass(frozen=True)
class ParsedFieldInfo[T]:
    title: str | None = None
    ge: annotated_types.SupportsGe | None = None
    le: annotated_types.SupportsLe | None = None
    valid_values: Sequence[T] | None = None


DEFAULT_PARSED_FIELD_INFO = ParsedFieldInfo[Any]()


def get_literal_values(literal) -> tuple:
    return get_args(literal)


def parse_pydantic_field_info(
    field_info: FieldInfo,
    valid_values: Sequence[T] | None = None
) -> ParsedFieldInfo:
    ge: annotated_types.SupportsGe | None = None
    le: annotated_types.SupportsLe | None = None
    for meta in field_info.metadata:
        if isinstance(meta, annotated_types.Ge):
            ge = meta.ge
        if isinstance(meta, annotated_types.Le):
            le = meta.le
    return ParsedFieldInfo[T](
        title=field_info.title,
        ge=ge,
        le=le,
        valid_values=valid_values
    )


def parse_pydantic_field(type_hint) -> tuple[Any, ParsedFieldInfo]:
    origin = get_origin(type_hint)
    extras: Sequence[Any] = []
    valid_values: Sequence[Any] | None = None
    if origin is Annotated:
        base, *extras = get_args(type_hint)
        LOGGER.debug('extras: %r', extras)
    else:
        base = type_hint
    if get_origin(base) is Literal:
        valid_values = get_literal_values(base)
        LOGGER.debug('Literal: %r (values: %r)', base, valid_values)
    field_info = next((e for e in extras if isinstance(e, FieldInfo)), None)
    if field_info is not None:
        return base, parse_pydantic_field_info(field_info, valid_values=valid_values)
    return type_hint, ParsedFieldInfo(valid_values=valid_values)


def get_gradio_component(type_hint) -> gr.Component | None:
    origin = get_origin(type_hint)
    if origin is Annotated:
        _base, *extras = get_args(type_hint)
        LOGGER.debug('extras: %r', extras)
        component = next((e for e in extras if isinstance(e, gr.Component)), None)
        return component
    return None


class FnGradio:
    def get_component(  # pylint: disable=too-many-return-statements
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
        if field_info and field_info.valid_values:
            return gr.Dropdown(
                value=default_value,
                label=label,
                choices=list(field_info.valid_values)
            )
        raise UnsupportedTypeError(type_hint)

    def _on_interface(self, interface: gr.Interface):  # pylint: disable=redefined-outer-name
        pass

    def _create_interface(
        self,
        fn: Callable,
        api_name: str,
        inputs: Sequence[gr.Component],
        outputs: Sequence[gr.Component],
        **kwargs
    ) -> gr.Interface:
        _interface = gr.Interface(
            fn=fn,
            api_name=api_name,
            inputs=inputs,
            outputs=outputs,
            **kwargs
        )
        self._on_interface(_interface)
        return _interface

    def interface(
        self,
        *,
        api_name: str | None = None,
        **kwargs
    ) -> Callable[[Callable], gr.Interface]:
        def wrapper(fn: Callable) -> gr.Interface:
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
            return self._create_interface(
                fn=fn,
                api_name=api_name or fn.__name__,
                inputs=inputs,
                outputs=outputs,
                **kwargs
            )
        return wrapper


DEFAULT_FNGRADIO = FnGradio()

interface = DEFAULT_FNGRADIO.interface
