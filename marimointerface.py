import marimo as mo
from dataclasses import fields, is_dataclass
from types import SimpleNamespace
from mininterface.mininterface import Mininterface

class MarimoInterface(Mininterface):
    """
    Интерфейс Mininterface с использованием marimo.ui вместо ipywidgets.
    Поддерживает dataclass и dict.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widgets = {}
        self._default_values = {}

    def form(self, form=None, title="", *, submit=True):
        if form is None:
            data_instance = self.env
        else:
            data_instance = form

        fields_to_edit = {}
        if isinstance(data_instance, dict):
            fields_to_edit = data_instance.copy()
        elif is_dataclass(data_instance):
            fields_to_edit = {f.name: getattr(data_instance, f.name) for f in fields(data_instance)}
        elif isinstance(data_instance, SimpleNamespace):
            fields_to_edit = vars(data_instance).copy()
        else:
            raise ValueError("Unsupported data format")

        self._default_values = fields_to_edit.copy()
        self._widgets = {}

        ui_elements = []
        if title:
            # Просто текстовый заголовок — можно использовать mo.md()
            ui_elements.append(mo.ui.anyWidget(mo.md(f"### {title}")))

        for key, value in fields_to_edit.items():
            if isinstance(value, bool):
                widget = mo.ui.checkbox(label=key, value=value)
            elif isinstance(value, int):
                widget = mo.ui.number(label=key, value=value)
            else:
                widget = mo.ui.text(label=key, value=str(value))
            self._widgets[key] = widget
            ui_elements.append(mo.ui.anyWidget(widget))

        # Возвращаем список anyWidget-обёрнутых элементов
        return ui_elements


    def apply_form(self, data_instance=None):
        if data_instance is None:
            data_instance = self.env

        for key, widget in self._widgets.items():
            val = widget.value
            if isinstance(widget, mo.ui.checkbox):
                val = bool(val)
            elif isinstance(widget, mo.ui.number):
                val = int(val)
            else:
                val = str(val)

            if isinstance(data_instance, dict):
                data_instance[key] = val
            elif is_dataclass(data_instance):
                setattr(data_instance, key, val)
            elif isinstance(data_instance, SimpleNamespace):
                setattr(data_instance, key, val)

        return data_instance
