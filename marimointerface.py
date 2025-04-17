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

    def save_form(self):
        # Логика сохранения формы
        print("Форма сохранена")
        self.apply_form()

    def reset_form(self):
        # Логика сброса формы
        print("Форма сброшена")
        for key, widget in self._widgets.items():
            if key not in ["save_button", "reset_button", "clear_button"]:
                if isinstance(widget, mo.ui.checkbox):
                    widget.value = False
                elif isinstance(widget, mo.ui.number):
                    widget.value = 0
                else:
                    widget.value = ""

    def clear_form(self):
        # Логика очистки формы
        print("Форма очищена")
        for key, widget in self._widgets.items():
            if key not in ["save_button", "reset_button", "clear_button"]:
                if isinstance(widget, mo.ui.checkbox):
                    widget.value = False
                elif isinstance(widget, mo.ui.number):
                    widget.value = 0
                else:
                    widget.value = ""

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

        ui_tree = {}

        for key, value in fields_to_edit.items():
            if isinstance(value, bool):
                self._widgets[key] = mo.ui.checkbox(label=key, value=value)
                ui_tree[key] = self._widgets[key]
            elif isinstance(value, int) or (value is None and key.endswith('_number')):
                self._widgets[key] = mo.ui.number(label=key, value=value if value is not None else 0)
                ui_tree[key] = self._widgets[key]
            elif isinstance(value, str):
                self._widgets[key] = mo.ui.text(label=key, value=value)
                ui_tree[key] = self._widgets[key]
            elif isinstance(value, float):
                self._widgets[key] = mo.ui.number(label=key, value=value, step=0.1)
                ui_tree[key] = self._widgets[key]
            else:
                self._widgets[key] = mo.ui.text(label=key, value=str(value))
                ui_tree[key] = self._widgets[key]

        self._save_button = mo.ui.button(label="Сохранить", on_click=lambda _: self.save_form())
        ui_tree["save_button"] = self._save_button

        self._reset_button = mo.ui.button(label="Сбросить", on_click=lambda _: self.reset_form())
        ui_tree["reset_button"] = self._reset_button

        self._clear_button = mo.ui.button(label="Очистить", on_click=lambda _: self.clear_form())
        ui_tree["clear_button"] = self._clear_button

        return mo.tree(ui_tree)

    def apply_form(self, data_instance=None):
        if data_instance is None:
            data_instance = self.env

        for key, widget in self._widgets.items():
            if key not in ["save_button", "reset_button", "clear_button"]:
                val = widget.value
                if isinstance(widget, mo.ui.checkbox):
                    val = bool(val)
                elif isinstance(widget, mo.ui.number):
                    if isinstance(val, int):
                        val = int(val)
                    else:
                        val = float(val)
                else:
                    val = str(val)

                if isinstance(data_instance, dict):
                    data_instance[key] = val
                elif is_dataclass(data_instance):
                    setattr(data_instance, key, val)
                elif isinstance(data_instance, SimpleNamespace):
                    setattr(data_instance, key, val)

        return data_instance