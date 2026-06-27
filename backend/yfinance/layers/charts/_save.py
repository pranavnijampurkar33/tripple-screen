"""Save matplotlib figures to disk."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def save_figure(fig, path: Path, *, dpi: int = 150) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
