import marimo as mo
from dataclasses import fields, is_dataclass
from typing import Any, Dict, Optional, Union
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
        self._widgets = {}  # Для отображения
        self._input_widgets = {}  # Для хранения ссылок на виджеты ввода
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
    
    def save_form(self, *args):
        for key, widget in self._input_widgets.items():
            value = widget.value
            if isinstance(self.data, dict):
                self.data[key] = value
            elif is_dataclass(self.data):
                setattr(self.data, key, value)
        return mo.tree(self._widgets)
    
    def reset_form(self, *args):
        for key, widget in self._input_widgets.items():
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
        self._input_widgets = {}
        
        for key, value in fields_data.items():
            widget_class = self._get_widget_class(value)
            widget = widget_class(value=value)
            self._input_widgets[key] = widget
            
            # Создаем контейнер с меткой и виджетом
            self._widgets[key] = mo.vstack([
                mo.md(f"**{key}**"),
                mo.ui.anywidget(widget)
            ], gap=0.5)
        
        # Кнопки
        self._widgets["save_button"] = mo.ui.button(
            label="Сохранить",
            on_click=lambda _: self.save_form()
        )
        self._widgets["reset_button"] = mo.ui.button(
            label="Сбросить",
            on_click=lambda _: self.reset_form()
        )
        
        return mo.tree(self._widgets)