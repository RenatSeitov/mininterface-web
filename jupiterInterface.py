import ipywidgets as widgets
from IPython.display import display
from dataclasses import fields, is_dataclass
from types import SimpleNamespace

# Импортируем базовый класс Mininterface из библиотеки
# Обратите внимание на точный путь — он может отличаться в зависимости от вашей структуры.
# Если у вас "from .base_interface import Mininterface", используйте соответствующий import.
from mininterface.mininterface import Mininterface

class JupyterWidgetInterface(Mininterface):
    """
    Пример интерфейса для mininterface, который использует ipywidgets
    в Jupyter Notebook для редактирования полей dataclass.
    """

    def __init__(self, *args, **kwargs):
        """
        Вызовем родительский конструктор Mininterface, который инициализирует self.env.
        """
        super().__init__(*args, **kwargs)
        # Вспомогательные переменные, чтобы хранить текущие виджеты и вывод
        self._widget_controls = {}
        self._last_form_output = widgets.Output()

    def form(self, form=None, title="", *, submit=True):
        """
        Переопределяем метод form() так, чтобы он создавал ipywidgets на основе
        полей dataclass (или dict) и отображал их в Jupyter.
        
        В данном примере метод НЕ блокирует выполнение кода.
        Как только пользователь нажмёт Submit, значения сохраняются в self.env.
        """
        # Если form не передан, редактируем self.env (обычно dataclass)
        if form is None:
            data_instance = self.env
        else:
            data_instance = form

        # Если это dict — работаем с ним как с набором полей.
        # Если это dataclass — перечислим поля.
        # Если что-то иное, упростим пример, предполагая, что либо dict, либо dataclass.
        fields_to_edit = {}
        
        if isinstance(data_instance, dict):
            # Перебираем ключи словаря
            for key, value in data_instance.items():
                fields_to_edit[key] = value
        elif is_dataclass(data_instance):
            # Для dataclass возьмём имена полей и их значения
            for f in fields(data_instance):
                key = f.name
                value = getattr(data_instance, key)
                fields_to_edit[key] = value
        elif isinstance(data_instance, SimpleNamespace):
            # Для SimpleNamespace тоже можно извлечь vars(...)
            for key, value in vars(data_instance).items():
                fields_to_edit[key] = value
        else:
            print("Формат данных не поддерживается (не dataclass и не dict).")
            return data_instance
        
        # Если есть заголовок формы, просто выведем
        if title:
            print(f"=== {title} ===")

        # Создаём виджеты на основе типа данных
        self._widget_controls = {}
        widget_list = []
        
        for fld_name, value in fields_to_edit.items():
            if isinstance(value, bool):
                ctrl = widgets.Checkbox(value=value, description=fld_name)
            elif isinstance(value, int):
                ctrl = widgets.IntText(value=value, description=fld_name)
            else:
                # Всё остальное приводим к строке для Text
                ctrl = widgets.Text(value=str(value), description=fld_name)

            self._widget_controls[fld_name] = ctrl
            widget_list.append(ctrl)

        # Кнопка Submit
        submit_btn = widgets.Button(description='Submit', button_style='success')

        # При нажатии обновляем self.env (или dict), выводим результат
        def on_submit_clicked(_):
            # Перебираем все виджеты и сохраняем их значения
            for fld_name, ctrl in self._widget_controls.items():
                val = ctrl.value
                # Приведём тип обратно, если нужно (сейчас только int/bool/str).
                # Если поле было bool, ctrl == widgets.Checkbox.
                if isinstance(ctrl, widgets.Checkbox):
                    val = bool(val)
                elif isinstance(ctrl, widgets.IntText):
                    val = int(val)  # на всякий случай
                else:
                    val = str(val)

                if isinstance(data_instance, dict):
                    data_instance[fld_name] = val
                elif is_dataclass(data_instance):
                    setattr(data_instance, fld_name, val)
                elif isinstance(data_instance, SimpleNamespace):
                    setattr(data_instance, fld_name, val)

            # Покажем в Output, что форма сохранена
            with self._last_form_output:
                self._last_form_output.clear_output()
                print("Form submitted with values:", data_instance)

        submit_btn.on_click(on_submit_clicked)

        # Собираем вертикальный лэйаут
        form_box = widgets.VBox(widget_list + [submit_btn, self._last_form_output])
        display(form_box)

        # Возвращаем объект (на момент вызова), но не ждём, пока пользователь нажмёт Submit
        return data_instance
