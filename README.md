# AeroPurity: Prototype City-Specific Weather & AQI Forecast (Delhi & TT Nagar, Bhopal)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamweather-epic142.streamlit.app/)

An interactive **Streamlit** app for exploring historical weather in **Delhi**, historical **AQI** for **TT Nagar, Bhopal**, and generating **Prophet**-based forecasts for temperature, humidity, wind speed, and AQI.

---

## ✨ Features

- **Historical Weather (Delhi)**
  - Monthly trends by year for: **Mean Temperature**, **Humidity**, **Wind Speed** (Seaborn + Matplotlib).
- **Historical AQI (TT Nagar, Bhopal)**
  - Time‑series view and year‑over‑year seasonal view.
- **Forecasts (Prophet)**
  - Interactive Plotly charts with **observed vs predicted** overlays for:
    - Delhi: mean temperature, humidity, wind speed
    - TT Nagar (Bhopal): AQI
  - **Date-specific lookup**: type a date (`YYYY-MM-DD`) to fetch the point forecast if available.
- **Caching**
  - Data loading and some computations are cached for snappier UX.

---

## 🗂 Data Sources

The app reads data directly from GitHub

> **Note**: Since datasets are fetched remotely at runtime, you **don’t** need to store them in this repo. An optional local `datasets/` directory is still fine if you want to ship snapshots.

---

## 📦 Installation

**Prereqs**
- Python **3.9+** (3.10/3.11 are fine)
- A working C/C++ toolchain is recommended for the `prophet` backend (via `cmdstanpy`). On Windows, install **Build Tools for Visual Studio**; on macOS, install **Xcode Command Line Tools**; on Linux, ensure `gcc`/`g++` are present.

**Create a virtual env (recommended)**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

Example `requirements.txt` (you can tweak versions to your environment):
```txt
streamlit
pandas
seaborn
plotly
matplotlib
openpyxl
prophet
cmdstanpy
```

> If `prophet` fails to build on your machine/CI, try pinning versions (e.g., `prophet==1.1.5`, `cmdstanpy==1.2.4`) or pre-building the CmdStan toolchain per the cmdstanpy docs.

---

## ▶️ Run Locally

```bash
streamlit run streamlit_app.py
```

The sidebar has four pages:
- **Historical Weather Data (Delhi)**
- **Historical AQI Data (TT Nagar Bhopal)**
- **AQI Predictor**
- **Weather Predictor (Currently only Delhi)**

> The sidebar also expects an image called **`aero purity.jpg`** in the repo root. Add your own image or remove that line in the code if you don’t want a sidebar image.

---

## 🚀 Deploy

### Streamlit Community Cloud (free & easy)
1. Push this repo to GitHub.
2. Go to **share.streamlit.io** and connect your repo.
3. Set the **entry point** to `streamlit_app.py`.
4. Ensure your `requirements.txt` is committed.

### Docker (optional)
```Dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Build & run:
```bash
docker build -t stream-weather-aqi .
docker run -p 8501:8501 stream-weather-aqi
```

---

## 🔧 Project Structure

```
.
├── streamlit_app.py
├── requirements.txt        # create this (sample above)
├── aero purity.jpg         # optional sidebar image
└── README.md
```

---

## 🧪 How It Works (Brief)

- **Loaders**
  - `load_data()` fetches Delhi weather CSV, parses dates, and derives `year`/`month`.
  - `load_train()` fetches AQI Excel, parses dates, drops `AQI Status` and `Benzene (µg/m3)`, and removes nulls.
- **Exploration**
  - Seaborn/Matplotlib line plots across months grouped by `year`.
  - Plotly line charts for AQI over time.
- **Forecasting**
  - Each target (`meantemp`, `humidity`, `wind_speed`, `AQI No.`) is reshaped to Prophet's **`ds` / `y`** format and modeled.
  - Forecast horizon defaults to **365 days** forward.
  - Plotly overlays **observed vs predicted** series.
- **Date Lookup**
  - Use the text input (`YYYY-MM-DD`) to retrieve the exact forecasted point for that date if it exists in the forecast dataframe.

---

## 🩺 Troubleshooting

- **`prophet` install/build issues**
  - Ensure a working compiler toolchain; try version pinning; allow time for CmdStan to download/compile on first run.
- **`ModuleNotFoundError: No module named 'openpyxl'`**
  - Ensure `openpyxl` is in `requirements.txt`.
- **Sidebar image not found**
  - Add `aero purity.jpg` to the repo root, or comment/remove the image line in `streamlit_app.py`.
- **No prediction for the date you typed**
  - The lookup is an **exact match** on `YYYY-MM-DD`. Ensure the date is within the modeled horizon and formatted exactly.

---


## 📄 License

Choose a license (e.g., MIT) and add it as `LICENSE` in the repo. You can start with <https://choosealicense.com/licenses/mit/>.
