import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde

# ───────────────────────────────────────────────────────────────
# Streamlit page setup
# ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VMM Feedback Survey Dashboard",
    layout="wide",
)

st.title("VMM Feedback Survey Dashboard")

# ───────────────────────────────────────────────────────────────
# Load CSV (THIS IS NOW CORRECT FOR YOUR FOLDER)
# ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("Use Me VMM Mock Data.csv")

df = load_data()

# ───────────────────────────────────────────────────────────────
# Column groups
# ───────────────────────────────────────────────────────────────
VALUES_COLS = [
    "Generational Wisdom Rating (1-5)",
    "Vision Rating (1-5)",
    "Community Rating (1-5)",
    "Traditions Rating (1-5)",
]
VALUES_COLORS = ["#70CBD3", "#4A4B4D", "#EB4223", "#F88A61"]
VALUES_LABELS = ["Gen. Wisdom", "Vision", "Community", "Traditions"]

GROWTH_COLS = [
    "Skills Growth Rating (1-5)",
    "Knowledge Growth Rating (1-5)",
    "Transformation Rating (1-5)",
]
GROWTH_COLORS = ["#148281", "#A8462F", "#F16029"]
GROWTH_LABELS = ["Skills Growth", "Knowledge Growth", "Transformation"]

ALL_ROLES = ["All Roles"] + sorted(df["Role"].dropna().unique().tolist())

# ───────────────────────────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────────────────────────
def calc_percentage_4_or_5(series):
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    if len(valid) == 0:
        return "N/A"
    pct = (valid.isin([4, 5]).sum() / len(valid)) * 100
    return f"{pct:.0f}%"


def plot_ridgeline(ax, data_df, cols, colors, title):
    x_range = np.linspace(0, 6, 300)
    overlap = 1.5
    n = len(cols)

    for i, (col, color) in enumerate(zip(cols, colors)):
        vals = pd.to_numeric(data_df[col], errors="coerce").dropna()
        if len(vals) < 2:
            continue

        kde = gaussian_kde(vals, bw_method=0.4)
        y = kde(x_range)
        y = y / y.max()
        base = (n - 1 - i) * overlap * 0.6

        ax.fill_between(x_range, base, base + y, color=color, alpha=0.75)
        ax.plot(x_range, base + y, color="white", linewidth=0.8)
        ax.axhline(base, color="white", linewidth=0.3, alpha=0.4)
        ax.text(
            -0.05,
            base + 0.1,
            col.replace(" Rating (1-5)", ""),
            ha="right",
            va="bottom",
            fontsize=8.5,
            color="#333333",
            transform=ax.get_yaxis_transform(),
        )

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(-0.1, n * overlap * 0.6 + 0.8)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_yticks([])
    ax.set_facecolor("#F9F9F9")
    ax.spines[["top", "right", "left"]].set_visible(False)


def plot_percentage_panel(ax, data_df, cols, colors, labels, title):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_facecolor("#F9F9F9")

    spacing = 1 / (len(cols) + 1)

    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        y = 1 - (i + 1) * spacing
        pct = calc_percentage_4_or_5(data_df[col])

        ax.text(0.5, y + 0.08, label, ha="center", fontsize=10, fontweight="bold")
        ax.text(0.5, y - 0.02, pct, ha="center", fontsize=28, color=color, fontweight="bold")


def build_figure(filtered, subtitle):
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("white")
    fig.suptitle(
        f"VMM Feedback Survey Dashboard\n{subtitle}",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    gs = gridspec.GridSpec(
        2, 2,
        height_ratios=[1, 1],
        width_ratios=[2.5, 1],
        hspace=0.35,
        wspace=0.25,
        left=0.08,
        right=0.95,
        top=0.90,
        bottom=0.2,
    )

    ax_val_ridge = fig.add_subplot(gs[0, 0])
    ax_val_pct = fig.add_subplot(gs[0, 1])
    ax_growth_ridge = fig.add_subplot(gs[1, 0])
    ax_growth_pct = fig.add_subplot(gs[1, 1])

    plot_ridgeline(ax_val_ridge, filtered, VALUES_COLS, VALUES_COLORS, "Values")
    plot_percentage_panel(ax_val_pct, filtered, VALUES_COLS, VALUES_COLORS, VALUES_LABELS, "Experienced the Value")

    plot_ridgeline(ax_growth_ridge, filtered, GROWTH_COLS, GROWTH_COLORS, "Growth")
    plot_percentage_panel(ax_growth_pct, filtered, GROWTH_COLS, GROWTH_COLORS, GROWTH_LABELS, "Experienced Growth")

    return fig

# ───────────────────────────────────────────────────────────────
# Sidebar filter
# ───────────────────────────────────────────────────────────────
st.sidebar.header("Filters")
role = st.sidebar.selectbox("Filter by Role", ALL_ROLES)

if role == "All Roles":
    filtered_df = df.copy()
    subtitle = "All Roles"
else:
    filtered_df = df[df["Role"] == role]
    subtitle = f"Role: {role} (n={len(filtered_df)})"

# ───────────────────────────────────────────────────────────────
# Render dashboard
# ───────────────────────────────────────────────────────────────
fig = build_figure(filtered_df, subtitle)
st.pyplot(fig)

