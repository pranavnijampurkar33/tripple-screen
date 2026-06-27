"""Ripple / Wave / Tide layer chart generation."""

__all__ = ["generate"]


def __getattr__(name: str):
    if name == "generate":
        from layers.orchestrator import generate

        return generate
    raise AttributeError(name)
