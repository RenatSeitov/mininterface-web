import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from dataclasses import fields, is_dataclass
    from typing import Any, Dict, Optional
    import anywidget
    import traitlets
    import copy

    class BaseWidget(anywidget.AnyWidget):
        value = traitlets.Any().tag(sync=True)

        def __init__(self, value: Any, **kwargs):
            super().__init__(value=value, **kwargs)

        def update_value(self, new_value: Any):
            """Обновляет значение виджета и синхронизирует с фронтендом"""
            self.value = new_value
            self.send_state({"value": new_value})

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
            self._initial_data = self._deep_copy(data_instance)  # Сохраняем оригинальные данные
            self._saved_data = self._deep_copy(data_instance)    # Сохраняем данные после сохранения
            self._widgets = {}
            self._input_widgets = {}
            self._widget_types = {
                bool: CheckboxWidget,
                int: NumberWidget,
                float: NumberWidget,
                str: TextWidget
            }
            self._form_state = None
            self._save_button = None
            self._reset_button = None
            self._reset_all_button = None

        def _deep_copy(self, obj):
            """Создает глубокую копию объекта, включая dataclass"""
            if is_dataclass(obj):
                result = {}
                for field in fields(obj):
                    value = getattr(obj, field.name)
                    result[field.name] = self._deep_copy(value)
                return type(obj)(**result)
            elif isinstance(obj, dict):
                return {k: self._deep_copy(v) for k, v in obj.items()}
            else:
                return copy.deepcopy(obj)

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

                type_name = type(value).__name__
                return mo.hstack([
                    mo.md(f"**{type_name}**"),
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

            # Обновляем сохраненное состояние
            self._saved_data = self._deep_copy(self.data)
            return self.form()

        def reset_form(self, *args):
            """Сбрасывает к последнему сохраненному состоянию"""
            self._restore_data(self._saved_data, self.data)
            for key, widget in self._input_widgets.items():
                value = self._get_value_from_data(key)
                widget.update_value(value)
            return self.form()

        def reset_all_form(self, *args):
            """Сбрасывает к первоначальному состоянию (до любых изменений)"""
            self._restore_data(self._initial_data, self.data)
            self._saved_data = self._deep_copy(self._initial_data)  # Также сбрасываем сохраненное состояние
            for key, widget in self._input_widgets.items():
                value = self._get_value_from_data(key)
                widget.update_value(value)
            return self.form()

        def _restore_data(self, src, dest):
            """Рекурсивно восстанавливает данные из src в dest"""
            if is_dataclass(src) and is_dataclass(dest):
                for field in fields(src):
                    src_value = getattr(src, field.name)
                    dest_value = getattr(dest, field.name)
                    if is_dataclass(src_value) and is_dataclass(dest_value):
                        self._restore_data(src_value, dest_value)
                    elif isinstance(src_value, dict) and isinstance(dest_value, dict):
                        self._restore_data(src_value, dest_value)
                    else:
                        setattr(dest, field.name, src_value)
            elif isinstance(src, dict) and isinstance(dest, dict):
                for key in src:
                    if key in dest:
                        src_value = src[key]
                        dest_value = dest[key]
                        if is_dataclass(src_value) and is_dataclass(dest_value):
                            self._restore_data(src_value, dest_value)
                        elif isinstance(src_value, dict) and isinstance(dest_value, dict):
                            self._restore_data(src_value, dest_value)
                        else:
                            dest[key] = src_value

        def _get_value_from_data(self, key: str) -> Any:
            """Получает значение из данных по ключу с точками"""
            keys = key.split('.')
            current = self.data

            for k in keys:
                if is_dataclass(current):
                    current = getattr(current, k)
                elif isinstance(current, dict):
                    current = current[k]

            return current

        def form(self):
            self._widgets = {}
            self._input_widgets = {}

            if is_dataclass(self.data):
                for field in fields(self.data):
                    field_value = getattr(self.data, field.name)
                    self._widgets[field.name] = self._create_widget_for_field(field.name, field_value)
            elif isinstance(self.data, dict):
                for key, value in self.data.items():
                    self._widgets[key] = self._create_widget_for_field(key, value)

            # Создаем кнопки
            self._save_button = mo.ui.button(
                label="Сохранить",
                on_click=lambda _: self.save_form(),
                kind="success"
            )
            self._reset_button = mo.ui.button(
                label="Сбросить",
                on_click=lambda _: self.reset_form(),
                kind="danger"
            )
            self._reset_all_button = mo.ui.button(
                label="Сбросить всё",
                on_click=lambda _: self.reset_all_form(),
                kind="warn"
            )

            buttons_panel = mo.hstack([
                self._save_button,
                self._reset_button,
                self._reset_all_button
            ], gap=1)

            return mo.vstack([
                buttons_panel,
                mo.tree(self._widgets)
            ], gap=1)

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
        version: str = "0.0.1"
        model_title_short: str = "PHMLoadingAnalyser"
        model_title_long: str = "PHM Underload and Overload Short Peaks Analyser"
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
        relaxation_params: RelaxationParams = field(default_factory=RelaxationParams)
        relaxation: Relaxation = field(default_factory=Relaxation)

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
        MarimoInterface,
        NumberWidget,
        Optional,
        PHMLoadingAnalyser,
        Relaxation,
        RelaxationParams,
        TextWidget,
        anywidget,
        config,
        copy,
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
