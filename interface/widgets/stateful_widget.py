import anywidget
import traitlets

class StatefulWidget(anywidget.AnyWidget):
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