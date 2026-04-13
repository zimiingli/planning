import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from pathlib import Path

DIR = Path(__file__).parent

# Read CSV
with open(DIR / "data.csv") as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

# Create figure with table - taller to accommodate 30 rows
fig, ax = plt.subplots(figsize=(12, 10))
ax.axis('off')
table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1, 1.3)

# Style header
for j in range(len(headers)):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Alternating row colors + highlight significant rows
for i in range(1, len(rows) + 1):
    row = rows[i - 1]
    is_significant = (row[-1].strip().lower() == 'yes') if row[-1] else False
    if is_significant:
        base_color = '#E2EFDA' if i % 2 == 1 else '#C6EFCE'
    else:
        base_color = '#D9E2F3' if i % 2 == 0 else 'white'
    for j in range(len(headers)):
        table[i, j].set_facecolor(base_color)

plt.savefig(DIR / "output.pdf", bbox_inches='tight', dpi=150)
plt.close()
