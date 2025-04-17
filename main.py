from dataclasses import dataclass, field
from typing import Optional, Dict
from dataclasses import dataclass
from mininterface import run

from jupiterInterface import JupyterWidgetInterface

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

    def __post_init__(self):
        """Convert relaxation_params from JSON."""
        if isinstance(self.relaxation_params, dict):
            self.relaxation_params = {
                key: RelaxationParams(*value) for key, value in self.relaxation_params.items()
            }

# Example usage:
if __name__ == "__main__":
    json_data = {
        "model_uuid": None,
        "version": "0.0.1",
        "model_title_short": "PHMLoadingAnalyser",
        "model_title_long": "PHM Underload and Overload Short Peaks Analyser",
        "model_url": None,
        "peak_time_limit": 30.0,
        "peak_value_limit": 50,
        "peak_count_limit": 3,
        "peak_relax_duration": 0.0,
        "anal_range": 86400.0,
        "anal_param_loading": 10,
        "type": "Underload",
        "stop_code": 1,
        "stop_count_limit": 3,
        "stop_relax_duration": 7200.0,
        "anal_param_pressure": 4,
        "increase_limit": 1.1,
        "agg_window_size": 3,
        "relaxation_params": {
            "0": [1, 15.0],
            "1": [3, 300.0],
            "3": [5, 600.0]
        }
    }

print(PHMLoadingAnalyser.agg_window_size)
with run(PHMLoadingAnalyser, interface=JupyterWidgetInterface, title="Demo") as m:
    m.form()