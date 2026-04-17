import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from pathlib import Path
from collections import OrderedDict

DIR = Path(__file__).parent

# Read CSV
with open(DIR / "data.csv") as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

# Pivot: rows are methods, columns are environments with SR and Cost sub-columns
methods = list(OrderedDict.fromkeys(r[0] for r in rows))
environments = list(OrderedDict.fromkeys(r[1] for r in rows))

# Build lookup: (method, env) -> (sr, cost)
lookup = {}
for r in rows:
    method, env, sr = r[0], r[1], r[2]
    cost = r[4] if len(r) > 4 else r[3]  # cost_xbase (col 4) or cost_ro_per_ep (col 3)
    lookup[(method, env)] = (sr, cost)

# Build two-row header: first row has env names (merged visually), second row has SR/Cost
# We'll create the env header row as a data row and style it specially
env_header_row = [''] + [env if k % 2 == 0 else '' for env in environments for k in range(2)]
sub_header = ['Method'] + ['SR (%)' if k % 2 == 0 else '×base' for k in range(len(environments) * 2)]

pivot_rows = []
for method in methods:
    row = [method]
    for env in environments:
        sr, cost = lookup.get((method, env), ('', ''))
        row.append(sr)
        row.append(cost)
    pivot_rows.append(row)

# Combine: env_header_row + data rows, with sub_header as colLabels
all_rows = [env_header_row] + pivot_rows
n_cols = len(sub_header)
n_data_rows = len(all_rows)

# Figsize: tight to content
fig_height = 1.5 + 0.35 * (n_data_rows + 1)
fig, ax = plt.subplots(figsize=(14, fig_height))
ax.axis('off')

table = ax.table(cellText=all_rows, colLabels=sub_header, loc='upper center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1, 1.4)

# Style sub-header row (row 0 = colLabels)
for j in range(n_cols):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold', fontsize=7)

# Style environment header row (row 1 = first data row = env_header_row)
for j in range(n_cols):
    table[1, j].set_facecolor('#2F5496')
    table[1, j].set_text_props(color='white', fontweight='bold', fontsize=8)
    # Remove borders between paired env columns for visual merging
    table[1, j].set_edgecolor('#2F5496')

# Alternating row colors for data rows (row 2 onwards)
for i in range(2, n_data_rows + 1):
    color = '#D9E2F3' if i % 2 == 0 else 'white'
    for j in range(n_cols):
        table[i, j].set_facecolor(color)

# Highlight DIAL row (bold)
for i, method in enumerate(methods):
    if method == 'DIAL':
        for j in range(n_cols):
            table[i + 2, j].set_text_props(fontweight='bold')

plt.savefig(DIR / "output.pdf", bbox_inches='tight', dpi=150)
plt.close()
