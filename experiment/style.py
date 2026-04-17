"""Unified figure style for the FRVC paper.

Import this module in every generate.py to ensure consistent styling.
Usage:
    from style import *
    apply_style()
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Core palette ──────────────────────────────────────────────
# DIAL (our method) — always prominent
DIAL_COLOR   = '#C0392B'   # crimson-red
DIAL_EDGE    = '#922B21'
DIAL_MARKER  = '*'
DIAL_SIZE    = 260

# Two-Source Model types
TYPE_I_COLOR = '#2471A3'   # steel blue  (Info-Poverty)
TYPE_D_COLOR = '#C0392B'   # crimson-red (Decision-Difficulty)
MIXED_COLOR  = '#7F8C8D'   # gray
WEAK_COLOR   = '#BDC3C7'   # light gray

# Bounds (base_only, always_trigger, oracle)
BOUNDS_COLOR = '#7F8C8D'
BOUNDS_MARKER = 'o'
BOUNDS_SIZE  = 50

# Fixed-direction baselines — distinct but harmonious
CB_PALETTE = {
    'CaTS':     '#2980B9',   # blue
    'SEAG':     '#E67E22',   # orange
    'CoRefine': '#27AE60',   # green
    'CATTS':    '#8E44AD',   # purple
    'AUQ':      '#D35400',   # dark orange
    's1_budget':'#16A085',   # teal
}
CB_MARKER = '^'
CB_SIZE   = 55

# Phase / temporal
EARLY_COLOR = '#2980B9'    # same blue as CaTS
LATE_COLOR  = '#C0392B'    # same crimson as DIAL

# Positive / negative direction
POS_COLOR = '#27AE60'      # green  (ρ > 0, Type D side)
NEG_COLOR = '#C0392B'      # red    (ρ < 0, Type I side)
ZERO_COLOR = '#95A5A6'     # silver-gray

# Multi-backbone shades (light → dark)
BB_FIXED = ['#AED6F1', '#5DADE2', '#2471A3']   # blue gradient: Qwen, Phi, Llama
BB_DIAL  = ['#F5B7B1', '#E74C3C', '#922B21']   # red  gradient: Qwen, Phi, Llama

# Heatmap
HEATMAP_CMAP = 'RdBu_r'
HEATMAP_VMIN = -0.7
HEATMAP_VMAX = 0.7

# Entropy bins (cool→warm)
ENTROPY_BIN_COLORS = ['#2980B9', '#5DADE2', '#F5B041', '#E74C3C']

# ── Typography ────────────────────────────────────────────────
FONT_TITLE   = 9
FONT_LABEL   = 8
FONT_TICK    = 7
FONT_ANNOT   = 7
FONT_LEGEND  = 7
FONT_CELL    = 6   # heatmap cell annotations

# ── Grid ──────────────────────────────────────────────────────
GRID_ALPHA   = 0.25
GRID_COLOR   = '#BDC3C7'
GRID_STYLE   = '-'

# ── Helpers ───────────────────────────────────────────────────

def apply_style():
    """Apply global matplotlib RC params for paper-quality figures."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': FONT_TICK,
        'axes.titlesize': FONT_TITLE,
        'axes.labelsize': FONT_LABEL,
        'xtick.labelsize': FONT_TICK,
        'ytick.labelsize': FONT_TICK,
        'legend.fontsize': FONT_LEGEND,
        'figure.dpi': 200,
        'savefig.dpi': 200,
        'savefig.bbox': 'tight',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': False,          # off by default; enable per-figure
        'grid.alpha': GRID_ALPHA,
        'grid.color': GRID_COLOR,
        'grid.linestyle': GRID_STYLE,
    })


def add_ygrid(ax):
    """Add light horizontal grid lines (for bar / line charts)."""
    ax.yaxis.grid(True, alpha=GRID_ALPHA, color=GRID_COLOR, linestyle=GRID_STYLE)
    ax.set_axisbelow(True)


def categorize_method(method):
    """Return category string for a method name."""
    dial = {'se_few5_filter_local', 'principled_adaptive', 'DIAL'}
    bounds = {'base_only', 'always_trigger', 'oracle'}
    cb = set(CB_PALETTE.keys()) | {k.lower() for k in CB_PALETTE}
    if method in dial:
        return 'dial'
    if method in bounds:
        return 'bounds'
    if method in cb:
        return 'cb'
    return 'other'


def cb_color(method):
    """Get color for a fixed-direction baseline."""
    for k, v in CB_PALETTE.items():
        if method.lower() == k.lower():
            return v
    return '#17BECF'


def type_color(env_type):
    """Get color for a Two-Source type string."""
    mapping = {
        'Type I': TYPE_I_COLOR,
        'Type D': TYPE_D_COLOR,
        'Mixed': MIXED_COLOR,
        'Weak': WEAK_COLOR,
        'Information-Poverty': TYPE_I_COLOR,
        'Decision-Difficulty': TYPE_D_COLOR,
        'Weak (harmful)': WEAK_COLOR,
    }
    return mapping.get(env_type, MIXED_COLOR)
