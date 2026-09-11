import reflex as rx
from datetime import datetime, timedelta


# ---------- SEED DATA ----------
AUTHORS = {
    "alice": {"name": "Alice Chen",  "role": "Backend Engineer",  "bio": "Writes about Django, async, and databases.", "color": "#7c3aed"},
    "bob":   {"name": "Bob Smith",   "role": "Frontend Dev",      "bio": "Reflex, React, and beautiful UIs.",         "color": "#0891b2"},
    "carol": {"name": "Carol Diaz",  "role": "Data Scientist",    "bio": "Pandas, ML, and storytelling with data.",   "color": "#059669"},
    "dave":  {"name": "Dave Kim",    "role": "DevOps Lead",       "bio": "Kubernetes, CI/CD, and reliability.",       "color": "#ea580c"},
}

POSTS = [
    {
        "id": 1,
        "title": "Building Reactive UIs in Pure Python with Reflex",
        "slug": "reflex-reactive-ui",
        "excerpt": "No JavaScript, no HTML — just Python classes and components that update the browser in real time.",
        "body": """Reflex lets you write full-stack web apps in **pure Python**. You define a `State` class for your data and event handlers, then build the UI with composable components.

### Why it's different

- No JavaScript, HTML, or CSS required
- State changes trigger automatic re-renders
- Reactive vars (`@rx.var`) compute values on the fly

### A tiny counter

```python
class State(rx.State):
    count: int = 0
    def inc(self): self.count += 1

def index():
    return rx.button(State.count, on_click=State.inc)