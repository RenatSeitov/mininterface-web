import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


@app.cell
def _():
    from dataclasses import dataclass, field
    from interface.anywidget_interface import MarimoInterface
    from typing import Dict, Optional

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
        Dict,
        MarimoInterface,
        Optional,
        PHMLoadingAnalyser,
        RelaxationParams,
        config,
        dataclass,
        field,
        interface,
    )


if __name__ == "__main__":
    app.run()
