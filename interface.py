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

    class StatefulWidget(anywidget.AnyWidget):
        """Базовый виджет с состоянием"""
        _esm = """
        export default {
            render({ model, el }) {
                const input = document.createElement("input");
                input.type = "text";
                input.value = model.get("value");
            
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
        value = traitlets.Any().tag(sync=True)

    class MarimoInterface:
        """Интерфейс с использованием anywidget"""
    
        def __init__(self, data_instance: Any):
            self.data = data_instance
            self._widgets = {}
            self._default_values = {}
    
        def save_form(self, *args):
            """Обновляет данные из виджетов"""
            for key, widget in self._widgets.items():
                if key not in ["save_button", "reset_button"]:
                    value = widget.value
                    if isinstance(self.data, dict):
                        self.data[key] = value
                    elif is_dataclass(self.data):
                        setattr(self.data, key, value)
            return mo.tree(self._widgets)
    
        def reset_form(self, *args):
            """Сбрасывает значения к исходным"""
            for key, widget in self._widgets.items():
                if key not in ["save_button", "reset_button"]:
                    if hasattr(widget, 'widget'):
                        widget.widget.value = self._default_values[key]
                    else:
                        widget.value = self._default_values[key]
            return mo.tree(self._widgets)
    
        def form(self):
            """Генерирует UI-форму"""
            if is_dataclass(self.data):
                fields_data = {f.name: getattr(self.data, f.name) for f in fields(self.data)}
            elif isinstance(self.data, dict):
                fields_data = self.data.copy()
            else:
                raise ValueError("Поддерживаются только dataclass и dict!")
        
            self._default_values = fields_data.copy()
            self._widgets = {}
        
            for key, value in fields_data.items():
                # Создаём экземпляр виджета
                widget = StatefulWidget(value=value)
            
                # Добавляем обработчик изменений
                def make_handler(k):
                    def handler(change):
                        if isinstance(self.data, dict):
                            self.data[k] = change.new
                        elif is_dataclass(self.data):
                            setattr(self.data, k, change.new)
                    return handler
            
                widget.observe(make_handler(key), names='value')
            
                # Обёртка marimo
                self._widgets[key] = mo.ui.anywidget(widget)
        
            # Простые кнопки (без anywidget)
            self._widgets["save_button"] = mo.ui.button(
                label="Сохранить",
                on_click=lambda _: self.save_form()
            )
            self._widgets["reset_button"] = mo.ui.button(
                label="Сбросить",
                on_click=lambda _: self.reset_form()
            )
        
            return mo.tree(self._widgets)
    return (
        Any,
        Dict,
        MarimoInterface,
        Optional,
        StatefulWidget,
        anywidget,
        fields,
        is_dataclass,
        mo,
        traitlets,
    )


@app.cell
def _(Dict, MarimoInterface, Optional):
    from dataclasses import dataclass, field


    @dataclass
    class RelaxationParams:
        """Parameters for relaxation."""
        level: int
        duration: float

    @dataclass
    class PHMLoadingAnalyser:
        """Analyzer for PHM underload and overload peaks."""
        model_uuid: Optional[str] = None  # Updated to Optional[str]
        version: str = "0.0.1"
        model_title_short: str = "PHMLoadingAnalyser"
        model_title_long: str = "PHM Underload and Overload Short Peaks Analyser"
        model_url: Optional[str] = None  # Updated to Optional[str]
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

    config = PHMLoadingAnalyser()
    interface = MarimoInterface(config)
    interface.form()
    return (
        PHMLoadingAnalyser,
        RelaxationParams,
        config,
        dataclass,
        field,
        interface,
    )


if __name__ == "__main__":
    app.run()
