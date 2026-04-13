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

# Create figure with table
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.axis('off')
table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.4)

# Style header
for j in range(len(headers)):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Alternating row colors
for i in range(1, len(rows) + 1):
    color = '#D9E2F3' if i % 2 == 0 else 'white'
    for j in range(len(headers)):
        table[i, j].set_facecolor(color)

plt.savefig(DIR / "output.pdf", bbox_inches='tight', dpi=150)
plt.close()
