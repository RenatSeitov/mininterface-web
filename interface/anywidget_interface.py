import marimo as mo
from dataclasses import fields, is_dataclass
from typing import Any
from interface.widgets.stateful_widget import StatefulWidget

class MarimoInterface:
    
    def __init__(self, data_instance: Any):
        self.data = data_instance
        self._widgets = {}
        self._default_values = {}
    
    def save_form(self, *args):
        for key, widget in self._widgets.items():
            if key not in ["save_button", "reset_button"]:
                value = widget.value
                if isinstance(self.data, dict):
                    self.data[key] = value
                elif is_dataclass(self.data):
                    setattr(self.data, key, value)
        return mo.tree(self._widgets)
    
    def reset_form(self, *args):
        for key, widget in self._widgets.items():
            if key not in ["save_button", "reset_button"]:
                if hasattr(widget, 'widget'):
                    widget.widget.value = self._default_values[key]
                else:
                    widget.value = self._default_values[key]
        return mo.tree(self._widgets)
    
    def form(self):
        if is_dataclass(self.data):
            fields_data = {f.name: getattr(self.data, f.name) for f in fields(self.data)}
        elif isinstance(self.data, dict):
            fields_data = self.data.copy()
        else:
            raise ValueError("Поддерживаются только dataclass и dict!")
        
        self._default_values = fields_data.copy()
        self._widgets = {}
        
        for key, value in fields_data.items():
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
        
        self._widgets["save_button"] = mo.ui.button(
            label="Сохранить",
            on_click=lambda _: self.save_form()
        )
        self._widgets["reset_button"] = mo.ui.button(
            label="Сбросить",
            on_click=lambda _: self.reset_form()
        )
        
        return mo.tree(self._widgets)