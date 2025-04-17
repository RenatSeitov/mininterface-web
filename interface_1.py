import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from dataclasses import fields, is_dataclass
    from typing import Any, Dict, Optional, Union, List, Type
    import anywidget
    import traitlets

    class BaseWidget(anywidget.AnyWidget):
        value = traitlets.Any().tag(sync=True)

        def __init__(self, value: Any, **kwargs):
            super().__init__(value=value, **kwargs)

    class TextWidget(BaseWidget):
        _esm = """
        export default {
            render({ model, el }) {
                const input = document.createElement("input");
                input.type = "text";
                input.value = model.get("value");
                input.style.width = "100%";

                input.addEventListener("input", (e) => {
                    model.set("value", e.target.value);
                    model.save_changes();
                });

                model.on("change:value", () => {
                    input.value = model.get("value");
                });

                el.appendChild(input);
            }
        }
        """

    class NumberWidget(BaseWidget):
        _esm = """
        export default {
            render({ model, el }) {
                const input = document.createElement("input");
                input.type = "number";
                input.value = model.get("value");
                input.style.width = "100%";

                input.addEventListener("input", (e) => {
                    model.set("value", Number(e.target.value));
                    model.save_changes();
                });

                model.on("change:value", () => {
                    input.value = model.get("value");
                });

                el.appendChild(input);
            }
        }
        """

    class CheckboxWidget(BaseWidget):
        _esm = """
        export default {
            render({ model, el }) {
                const container = document.createElement("div");
                container.style.display = "flex";
                container.style.alignItems = "center";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.checked = model.get("value");
                checkbox.style.marginRight = "8px";

                checkbox.addEventListener("change", (e) => {
                    model.set("value", e.target.checked);
                    model.save_changes();
                });

                model.on("change:value", () => {
                    checkbox.checked = model.get("value");
                });

                container.appendChild(checkbox);
                el.appendChild(container);
            }
        }
        """
    class MarimoInterface:
        def __init__(self, data_instance: Any):
            self.data = data_instance
            self._widgets = {}
            self._input_widgets = {}
            self._default_values = {}
            self._widget_types = {
                bool: CheckboxWidget,
                int: NumberWidget,
                float: NumberWidget,
                str: TextWidget
            }

        def _get_widget_class(self, value: Any) -> type:
            value_type = type(value)
            return self._widget_types.get(value_type, TextWidget)

        def _create_widget_for_field(self, key: str, value: Any, prefix: str = "") -> mo.Html:
            full_key = f"{prefix}.{key}" if prefix else key

            if is_dataclass(value):
                nested_widgets = {}
                for field in fields(value):
                    field_value = getattr(value, field.name)
                    nested_widgets[field.name] = self._create_widget_for_field(
                        field.name, field_value, full_key
                    )
                return mo.tree(nested_widgets)
            elif isinstance(value, dict):
                dict_widgets = {}
                for dict_key, dict_value in value.items():
                    dict_widgets[dict_key] = self._create_widget_for_field(
                        dict_key, dict_value, full_key
                    )
                return mo.tree(dict_widgets)
            else:
                widget_class = self._get_widget_class(value)
                widget = widget_class(value=value)
                self._input_widgets[full_key] = widget
                self._default_values[full_key] = value

                return mo.hstack([
                    mo.md(f"**{key}**"),
                    mo.ui.anywidget(widget)
                ], gap=0.5, align="center")

        def save_form(self, *args):
            for key, widget in self._input_widgets.items():
                value = widget.value
                keys = key.split('.')
                current = self.data

                for k in keys[:-1]:
                    if is_dataclass(current):
                        current = getattr(current, k)
                    elif isinstance(current, dict):
                        current = current[k]

                final_key = keys[-1]
                if is_dataclass(current):
                    setattr(current, final_key, value)
                elif isinstance(current, dict):
                    current[final_key] = value

            return mo.tree(self._widgets)

        def reset_form(self, *args):
            # Полностью пересоздаем форму
            self._widgets = {}
            self._input_widgets = {}

            if is_dataclass(self.data):
                for field in fields(self.data):
                    field_value = getattr(self.data, field.name)
                    self._widgets[field.name] = self._create_widget_for_field(field.name, field_value)
            elif isinstance(self.data, dict):
                for key, value in self.data.items():
                    self._widgets[key] = self._create_widget_for_field(key, value)

            self._widgets["_buttons"] = mo.hstack([
                mo.ui.button(
                    label="Сохранить",
                    on_click=lambda _: self.save_form()
                ),
                mo.ui.button(
                    label="Сбросить",
                    on_click=lambda _: self.reset_form()
                )
            ], gap=1)

            return mo.tree(self._widgets)

        def form(self):
            return self.reset_form()  # Используем reset_form для первоначального создания формы


    from dataclasses import dataclass, field

    @dataclass
    class RelaxationParams:
        """Parameters for relaxation."""
        level: int = 1
        duration: float = 3600.0


    @dataclass
    class Relaxation:
        """Parameters for relaxation."""
        one: int = 1
        two: float = 3600.0


    @dataclass
    class PHMLoadingAnalyser:
        """Analyzer for PHM underload and overload peaks."""
        model_uuid: Optional[str] = None
        version: str = "0.0.1"
        model_title_short: str = "PHMLoadingAnalyser"
        model_title_long: str = "PHM Underload and Overload Short Peaks Analyser"
        model_url: Optional[str] = None
        peak_time_limit: float = 30.0
        peak_value_limit: int = 50
        peak_count_limit: int = 3
        peak_relax_duration: float = 0.0
        anal_range: float = 86400.0
        anal_param_loading: int = 10
        type: str = "Underload"
        stop_code: int = 1
        stop_count_limit: int = 3
        stop_relax_duration: float = 7200.0
        anal_param_pressure: int = 4
        increase_limit: float = 1.1
        agg_window_size: int = 3
        relaxation_params: Dict[str, RelaxationParams] = field(default_factory=dict)
        relaxation: Dict[str, RelaxationParams] = field(default_factory=dict)

    # Создаем экземпляр с вложенными параметрами
    config = PHMLoadingAnalyser(
        relaxation_params=RelaxationParams(level=2, duration=1800),
        relaxation=Relaxation(one=2, two=1800)
    )

    # Создаем и отображаем интерфейс
    interface = MarimoInterface(config)
    interface.form()
    return (
        Any,
        BaseWidget,
        CheckboxWidget,
        Dict,
        List,
        MarimoInterface,
        NumberWidget,
        Optional,
        PHMLoadingAnalyser,
        Relaxation,
        RelaxationParams,
        TextWidget,
        Type,
        Union,
        anywidget,
        config,
        dataclass,
        field,
        fields,
        interface,
        is_dataclass,
        mo,
        traitlets,
    )


if __name__ == "__main__":
    app.run()
