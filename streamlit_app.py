from __future__ import annotations

import pandas as pd
import streamlit as st
from rich.console import Console

from database.game_database import GameDatabase
from hardware.detector import HardwareDetector, build_hardware_profile
from predictor.engine import RuleBasedPredictionEngine
from utils.paths import resource_path


st.set_page_config(
    page_title="RunWise AI",
    page_icon="RW",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .runwise-hero {
        border: 1px solid rgba(46, 160, 67, 0.35);
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        background: linear-gradient(135deg, rgba(46, 160, 67, 0.16), rgba(88, 166, 255, 0.10));
    }
    .runwise-hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 2.2rem;
        letter-spacing: 0;
    }
    .runwise-hero p {
        margin: 0;
        color: #b7c4d4;
        font-size: 1.02rem;
    }
    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .good { background: rgba(46, 160, 67, 0.2); color: #49d17d; }
    .warn { background: rgba(210, 153, 34, 0.2); color: #f0c36a; }
    .bad { background: rgba(248, 81, 73, 0.2); color: #ff8b86; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_database() -> GameDatabase:
    return GameDatabase(resource_path("data/games.json"))


@st.cache_resource
def load_engine() -> RuleBasedPredictionEngine:
    return RuleBasedPredictionEngine()


@st.cache_data(show_spinner=False)
def detect_hardware() -> dict:
    detector = HardwareDetector(Console())
    return detector.detect_available()


def main() -> None:
    database = load_database()
    engine = load_engine()

    st.markdown(
        """
        <div class="runwise-hero">
            <h1>RunWise AI</h1>
            <p>Local laptop performance prediction for games, streaming, and creative software.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Detecting laptop hardware..."):
        detected = detect_hardware()

    st.sidebar.header("Hardware Profile")
    st.sidebar.caption("Detected values are filled in automatically. Edit anything you want to override.")

    missing = [label for label, value in _missing_labels(detected).items() if value]
    if missing:
        st.sidebar.warning("Missing: " + ", ".join(missing))
    else:
        st.sidebar.success("All hardware fields detected.")

    cpu = st.sidebar.text_input("CPU", value=detected.get("cpu") or "")
    ram_gb = st.sidebar.number_input(
        "RAM (GB)",
        min_value=1.0,
        max_value=256.0,
        step=1.0,
        value=float(detected.get("ram_gb") or 8.0),
    )
    gpu = st.sidebar.text_input("GPU", value=detected.get("gpu") or "")
    storage_type = st.sidebar.selectbox(
        "Storage Type",
        ["NVMe SSD", "SSD", "HDD", "Hybrid", "Unknown"],
        index=_storage_index(detected.get("storage_type")),
    )
    battery = st.sidebar.text_input("Battery", value=detected.get("battery") or "Unknown")
    os_name = st.sidebar.text_input("Operating System", value=detected.get("os") or "")
    screen_resolution = st.sidebar.text_input(
        "Screen Resolution",
        value=detected.get("screen_resolution") or "",
        placeholder="1920x1080",
    )

    if not all([cpu.strip(), gpu.strip(), os_name.strip(), screen_resolution.strip()]):
        st.info("Fill the missing hardware fields in the sidebar to enable prediction.")
        return

    hardware = build_hardware_profile(
        cpu=cpu.strip(),
        ram_gb=float(ram_gb),
        gpu=gpu.strip(),
        storage_type=storage_type,
        battery=battery.strip() or "Unknown",
        os_name=os_name.strip(),
        screen_resolution=screen_resolution.strip(),
    )

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.subheader("System Summary")
        st.dataframe(_hardware_dataframe(hardware), use_container_width=True, hide_index=True)

    with right:
        st.subheader("Hardware Scores")
        score_cols = st.columns(4)
        score_cols[0].metric("CPU", hardware.cpu_score)
        score_cols[1].metric("GPU", hardware.gpu_score)
        score_cols[2].metric("RAM", hardware.ram_score)
        score_cols[3].metric("Storage", hardware.storage_score)
        st.progress(round((hardware.cpu_score + hardware.gpu_score + hardware.ram_score + hardware.storage_score) / 400, 2))

    st.divider()
    st.subheader("Search Game or Software")

    query = st.text_input("Search", value="", placeholder="Try Cyberpunk, Valorant, Blender, OBS...")
    matches = database.search(query) if query.strip() else database.all()
    if not matches:
        st.warning("No matches found. Try a different title.")
        return

    names = [item["name"] for item in matches]
    selected_name = st.selectbox("Choose target", names)
    target = next(item for item in matches if item["name"] == selected_name)

    if st.button("Analyze Performance", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing {target['name']}..."):
            prediction = engine.predict(hardware, target)
        _render_prediction(target, prediction)


def _missing_labels(detected: dict) -> dict[str, bool]:
    return {
        "CPU": not detected.get("cpu"),
        "RAM": not detected.get("ram_gb"),
        "GPU": not detected.get("gpu"),
        "Storage": not detected.get("storage_type"),
        "Battery": not detected.get("battery"),
        "OS": not detected.get("os"),
        "Resolution": not detected.get("screen_resolution"),
    }


def _storage_index(storage: str | None) -> int:
    if not storage:
        return 1
    normalized = storage.lower()
    if "nvme" in normalized:
        return 0
    if "ssd" in normalized:
        return 1
    if "hdd" in normalized:
        return 2
    if "hybrid" in normalized or "sshd" in normalized:
        return 3
    return 4


def _hardware_dataframe(hardware) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Component": "CPU", "Detected Value": hardware.cpu, "Score": hardware.cpu_score},
            {"Component": "GPU", "Detected Value": hardware.gpu, "Score": hardware.gpu_score},
            {"Component": "RAM", "Detected Value": f"{hardware.ram_gb:.1f} GB", "Score": hardware.ram_score},
            {"Component": "Storage", "Detected Value": hardware.storage_type, "Score": hardware.storage_score},
            {"Component": "Battery", "Detected Value": hardware.battery, "Score": "-"},
            {"Component": "Operating System", "Detected Value": hardware.os, "Score": "-"},
            {"Component": "Screen Resolution", "Detected Value": hardware.screen_resolution, "Score": "-"},
        ]
    )


def _render_prediction(target: dict, prediction) -> None:
    st.subheader(f"Prediction: {target['name']}")

    cols = st.columns(5)
    cols[0].metric("Compatibility", f"{prediction.compatibility_score}/100")
    cols[1].metric("Estimated FPS", prediction.estimated_fps)
    cols[2].markdown(f"**Lag Chance**<br>{_pill(prediction.lag_chance)}", unsafe_allow_html=True)
    cols[3].markdown(f"**Battery Drain**<br>{_pill(prediction.battery_drain)}", unsafe_allow_html=True)
    cols[4].markdown(f"**Thermals**<br>{_pill(prediction.thermal_stress)}", unsafe_allow_html=True)

    st.progress(prediction.compatibility_score / 100)
    st.info(f"Recommended settings: {prediction.recommended_settings}")

    st.write("Notes")
    for note in prediction.notes:
        st.write(f"- {note}")

    with st.expander("Requirement score targets"):
        requirements = target["requirements"]
        st.dataframe(
            pd.DataFrame(
                [
                    {"Tier": "Minimum", **requirements["minimum"]},
                    {"Tier": "Recommended", **requirements["recommended"]},
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )


def _pill(value: str) -> str:
    style = "good"
    if value in {"Medium", "Moderate", "Warm"}:
        style = "warn"
    if value in {"High", "Heavy", "Hot"}:
        style = "bad"
    return f'<span class="status-pill {style}">{value}</span>'


if __name__ == "__main__":
    main()
