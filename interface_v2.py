import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from dataclasses import fields, is_dataclass
    from typing import Any, Optional, Dict
    import copy
    from interface.widgets.stateful_widget import StatefulWidget
    from dataclasses import dataclass, field
    class MarimoInterface:
        def __init__(self, data_instance: Any, is_sub_interface: bool = False):
            self.data = data_instance
            self._widgets = {}
            self._sub_interfaces = {}
            self._default_values = copy.deepcopy(data_instance)
            self._is_sub_interface = is_sub_interface

        def save_form(self, *args):
            return mo.tree(self._widgets)

        def reset_form(self, *args):
            # Reset sub-interfaces first
            for sub_interface in self._sub_interfaces.values():
                sub_interface.reset_form()
        
            # Reset current widgets
            for key, widget in self._widgets.items():
                if key in ["save_button", "reset_button"]:
                    continue
                if key in self._sub_interfaces:
                    continue
            
                default_value = self._get_default_value(key)
                if hasattr(widget, 'widget'):
                    widget.widget.value = default_value
                else:
                    widget.value = default_value
        
            # Reset data from default values
            self._reset_data_from_defaults()
            return mo.tree(self._widgets)

        def _get_default_value(self, key):
            if is_dataclass(self._default_values):
                return getattr(self._default_values, key, None)
            elif isinstance(self._default_values, dict):
                return self._default_values.get(key, None)
            return None

        def _reset_data_from_defaults(self):
            if is_dataclass(self.data):
                for f in fields(self.data):
                    default_val = getattr(self._default_values, f.name)
                    current_val = getattr(self.data, f.name)
                    if is_dataclass(current_val) or isinstance(current_val, dict):
                        sub_interface = MarimoInterface(current_val, is_sub_interface=True)
                        sub_interface._default_values = default_val
                        sub_interface._reset_data_from_defaults()
                    else:
                        setattr(self.data, f.name, default_val)
            elif isinstance(self.data, dict):
                for k in list(self.data.keys()):
                    default_val = self._default_values.get(k)
                    current_val = self.data[k]
                    if is_dataclass(current_val) or isinstance(current_val, dict):
                        sub_interface = MarimoInterface(current_val, is_sub_interface=True)
                        sub_interface._default_values = default_val
                        sub_interface._reset_data_from_defaults()
                    else:
                        self.data[k] = default_val

        def form(self):
            if is_dataclass(self.data):
                fields_data = {f.name: getattr(self.data, f.name) for f in fields(self.data)}
            elif isinstance(self.data, dict):
                fields_data = self.data.copy()
            else:
                raise ValueError("Поддерживаются только dataclass и dict!")

            self._widgets = {}
            self._sub_interfaces = {}

            for key, value in fields_data.items():
                if is_dataclass(value) or isinstance(value, dict):
                    sub_interface = MarimoInterface(value, is_sub_interface=True)
                    self._sub_interfaces[key] = sub_interface
                    self._widgets[key] = sub_interface.form()
                else:
                    widget = StatefulWidget(value=value)
                
                    def make_handler(k):
                        def handler(change):
                            if isinstance(self.data, dict):
                                self.data[k] = change.new
                            elif is_dataclass(self.data):
                                setattr(self.data, k, change.new)
                        return handler
                
                    widget.observe(make_handler(key), names='value')
                    self._widgets[key] = mo.ui.anywidget(widget)

            if not self._is_sub_interface:
                self._widgets["save_button"] = mo.ui.button(
                    label="Сохранить",
                    on_click=lambda _: self.save_form()
                )
                self._widgets["reset_button"] = mo.ui.button(
                    label="Сбросить",
                    on_click=lambda _: self.reset_form()
                )

            return mo.tree(self._widgets)


    # Пример использования
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

    config = PHMLoadingAnalyser(
        relaxation_params=RelaxationParams(level=1, duration=2.0)
    )
    interface = MarimoInterface(config)
    interface.form()
    return (
        Any,
        Dict,
        MarimoInterface,
        Optional,
        PHMLoadingAnalyser,
        RelaxationParams,
        StatefulWidget,
        config,
        copy,
        dataclass,
        field,
        fields,
        interface,
        is_dataclass,
        mo,
    )


if __name__ == "__main__":
    app.run()
