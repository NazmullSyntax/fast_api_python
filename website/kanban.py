import reflex as rx
from datetime import datetime


# ---------- SEED DATA ----------
COLUMNS = [
    {"id": "backlog",     "title": "Backlog",     "color": "#6b7280", "emoji": "📥"},
    {"id": "todo",        "title": "To Do",       "color": "#3b82f6", "emoji": "📝"},
    {"id": "in_progress", "title": "In Progress", "color": "#f59e0b", "emoji": "🚧"},
    {"id": "review",      "title": "Review",      "color": "#a855f7", "emoji": "👀"},
    {"id": "done",        "title": "Done",        "color": "#10b981", "emoji": "✅"},
]

LABELS = {
    "bug":     {"name": "Bug",     "color": "#ef4444"},
    "feature": {"name": "Feature", "color": "#8b5cf6"},
    "design":  {"name": "Design",  "color": "#ec4899"},
    "docs":    {"name": "Docs",    "color": "#06b6d4"},
    "infra":   {"name": "Infra",   "color": "#f59e0b"},
}

PRIORITIES = {
    "low":    {"name": "Low",    "color": "#10b981"},
    "medium": {"name": "Medium", "color": "#f59e0b"},
    "high":   {"name": "High",   "color": "#ef4444"},
}

INITIAL_TASKS = [
    {"id": 1, "title": "Design new landing page",       "desc": "Create hero + feature grid mockups in Figma.",     "status": "backlog",     "label": "design",  "priority": "medium", "assignee": "Alice", "due": "Mar 22", "comments": 3},
    {"id": 2, "title": "Fix login redirect bug",        "desc": "Users redirected to /404 after OAuth callback.",   "status": "backlog",     "label": "bug",     "priority": "high",   "assignee": "Bob",   "due": "Mar 18", "comments": 7},
    {"id": 3, "title": "Write API docs for /users",     "desc": "Cover GET/POST/PATCH/DELETE with examples.",       "status": "todo",        "label": "docs",    "priority": "low",    "assignee": "Carol", "due": "Mar 25", "comments": 1},
    {"id": 4, "title": "Add dark mode support",         "desc": "Persist theme preference in localStorage.",        "status": "todo",        "label": "feature", "priority": "medium", "assignee": "Dave",  "due": "Mar 24", "comments": 2},
    {"id": 5, "title": "Migrate DB to Postgres 16",     "desc": "Test on staging first, then roll out.",            "status": "in_progress", "label": "infra",   "priority": "high",   "assignee": "Eve",   "due": "Mar 20", "comments": 5},
    {"id": 6, "title": "Refactor auth middleware",      "desc": "Split into smaller pure functions.",               "status": "in_progress", "label": "feature", "priority": "medium", "assignee": "Frank", "due": "Mar 21", "comments": 4},
    {"id": 7, "title": "Review PR #482",                "desc": "New payment flow — needs security review.",        "status": "review",      "label": "feature", "priority": "high",   "assignee": "Grace", "due": "Mar 19", "comments": 12},
    {"id": 8, "title": "Update icon set",               "desc": "Replace old icons with Lucide equivalents.",       "status": "review",      "label": "design",  "priority": "low",    "assignee": "Henry", "due": "Mar 23", "comments": 2},
    {"id": 9, "title": "Ship v2.1 release",             "desc": "Tag, changelog, and deploy to production.",        "status": "done",        "label": "infra",   "priority": "high",   "assignee": "Ivy",   "due": "Mar 15", "comments": 8},
    {"id": 10, "title": "Fix typo in README",           "desc": "Also add a quick-start section.",                  "status": "done",        "label": "docs",    "priority": "low",    "assignee": "Jack",  "due": "Mar 14", "comments": 1},
]


# ---------- STATE ----------
class State(rx.State):
    """Kanban board state."""
    tasks: list[dict] = INITIAL_TASKS.copy()
    dark: bool = True
    search: str = ""
    filter_label: str = "all"
    filter_priority: str = "all"
    active_task_id: int = 0
    dragging_id: int = 0
    new_title: str = ""
    new_status: str = "todo"
    show_add: bool = False
    next_id: int = 100

    # ---- UI ----
    def toggle_dark(self):
        self.dark = not self.dark

    def set_search(self, v: str):
        self.search = v

    def set_label_filter(self, v: str):
        self.filter_label = v

    def set_priority_filter(self, v: str):
        self.filter_priority = v

    def open_task(self, tid: int):
        self.active_task_id = tid

    def close_task(self):
        self.active_task_id = 0

    def toggle_add(self):
        self.show_add = not self.show_add
        self.new_title = ""

    # ---- Move tasks ----
    def move_task(self, tid: int, new_status: str):
        for t in self.tasks:
            if t["id"] == tid:
                t["status"] = new_status
                return

    def move_left(self, tid: int):
        ids = [c["id"] for c in COLUMNS]
        for t in self.tasks:
            if t["id"] == tid:
                i = ids.index(t["status"])
                if i > 0:
                    t["status"] = ids[i - 1]
                return

    def move_right(self, tid: int):
        ids = [c["id"] for c in COLUMNS]
        for t in self.tasks:
            if t["id"] == tid:
                i = ids.index(t["status"])
                if i < len(ids) - 1:
                    t["status"] = ids[i + 1]
                return

    # ---- Create / delete ----
    def set_new_title(self, v: str):
        self.new_title = v

    def set_new_status(self, v: str):
        self.new_status = v

    def add_task(self):
        if not self.new_title.strip():
            return
        self.tasks.append({
            "id": self.next_id,
            "title": self.new_title.strip(),
            "desc": "",
            "status": self.new_status,
            "label": "feature",
            "priority": "medium",
            "assignee": "You",
            "due": "—",
            "comments": 0,
        })
        self.next_id += 1
        self.new_title = ""
        self.show_add = False

    def delete_task(self, tid: int):
        self.tasks = [t for t in self.tasks if t["id"] != tid]
        self.active_task_id = 0

    # ---- Computed ----
    @rx.var
    def filtered_tasks(self) -> list[dict]:
        items = self.tasks
        if self.search:
            q = self.search.lower()
            items = [t for t in items if q in t["title"].lower() or q in t["desc"].lower()]
        if self.filter_label != "all":
            items = [t for t in items if t["label"] == self.filter_label]
        if self.filter_priority != "all":
            items = [t for t in items if t["priority"] == self.filter_priority]
        return items

    @rx.var
    def active_task(self) -> dict:
        for t in self.tasks:
            if t["id"] == self.active_task_id:
                return t
        return {}

    @rx.var
    def stats(self) -> dict:
        counts = {c["id"]: 0 for c in COLUMNS}
        for t in self.tasks:
            counts[t["status"]] = counts.get(t["status"], 0) + 1
        return counts


# ---------- THEME ----------
def bg():      return rx.cond(State.dark, "#0a0a12", "#eef0f6")
def card():    return rx.cond(State.dark, "#14141f", "white")
def col_bg():  return rx.cond(State.dark, "#101019", "#f7f8fc")
def text():    return rx.cond(State.dark, "#f5f5ff", "#12121a")
def muted():   return rx.cond(State.dark, "#8888a0", "#6b6b80")
def border():  return rx.cond(State.dark, "#23233a", "#dfe1ec")


# ---------- COMPONENTS ----------
def navbar():
    return rx.hstack(
        rx.hstack(
            rx.text("📋", font_size="1.6em"),
            rx.heading("PyBoard", size="6", color=text()),
            spacing="2",
        ),
        rx.spacer(),
        rx.input(
            placeholder="🔍 Search tasks...",
            value=State.search,
            on_change=State.set_search,
            size="2",
            width=rx.breakpoints(initial="140px", md="260px"),
            background=card(),
            border=f"1px solid {border()}",
            color=text(),
        ),
        rx.button(
            rx.hstack(rx.icon("plus", size=16), rx.text("New Task"), spacing="2", align="center"),
            on_click=State.toggle_add,
            color_scheme="purple",
            size="2",
        ),
        rx.button(
            rx.cond(State.dark, "☀️", "🌙"),
            on_click=State.toggle_dark,
            variant="soft",
            size="2",
        ),
        rx.avatar(fallback="PD", size="2", color_scheme="purple"),
        width="100%",
        padding="1em 2em",
        background=card(),
        border_bottom=f"1px solid {border()}",
        align="center",
        spacing="2",
        position="sticky",
        top="0",
        z_index="20",
    )


def filter_bar():
    def chip(key: str, label: str, color: str, current: str, handler):
        active = current == key
        return rx.button(
            label,
            on_click=lambda: handler(key),
            size="1",
            variant=rx.cond(active, "solid", "soft"),
            color_scheme="purple",
            border_radius="full",
        )

    return rx.hstack(
        rx.text("Labels:", color=muted(), font_size="0.85em"),
        chip("all", "All", "", State.filter_label, State.set_label_filter),
        *[chip(k, v["name"], v["color"], State.filter_label, State.set_label_filter) for k, v in LABELS.items()],
        rx.divider(orientation="vertical", height="20px", border_color=border()),
        rx.text("Priority:", color=muted(), font_size="0.85em"),
        chip("all", "Any", "", State.filter_priority, State.set_priority_filter),
        *[chip(k, v["name"], v["color"], State.filter_priority, State.set_priority_filter) for k, v in PRIORITIES.items()],
        padding="1em 2em",
        spacing="2",
        wrap="wrap",
        align="center",
        border_bottom=f"1px solid {border()}",
    )


def task_card(t: dict):
    label = LABELS.get(t["label"], {"name": "—", "color": "#888"})
    prio = PRIORITIES.get(t["priority"], {"name": "—", "color": "#888"})
    return rx.box(
        rx.vstack(
            # Top row: label + priority
            rx.hstack(
                rx.badge(label["name"], background=label["color"], color="white", variant="solid", size="1"),
                rx.spacer(),
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="full", background=prio["color"]),
                    rx.text(prio["name"], font_size="0.7em", color=muted(), font_weight="500"),
                    spacing="1",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            # Title
            rx.text(t["title"], color=text(), font_weight="600", font_size="0.92em", no_of_lines=2),
            # Description preview
            rx.cond(
                t["desc"] != "",
                rx.text(t["desc"], color=muted(), font_size="0.8em", no_of_lines=2),
            ),
            # Footer: assignee, due, comments
            rx.hstack(
                rx.avatar(fallback=t["assignee"][0], size="1", color_scheme="purple"),
                rx.text(t["assignee"], color=muted(), font_size="0.78em"),
                rx.spacer(),
                rx.hstack(rx.icon("message-square", size=11, color=muted()), rx.text(t["comments"], color=muted(), font_size="0.75em"), spacing="1", align="center"),
                rx.hstack(rx.icon("calendar", size=11, color=muted()), rx.text(t["due"], color=muted(), font_size="0.75em"), spacing="1", align="center"),
                width="100%",
                align="center",
                spacing="2",
            ),
            # Inline move buttons
            rx.hstack(
                rx.icon_button(rx.icon("chevron-left", size=14), on_click=lambda: State.move_left(t["id"]), size="1", variant="ghost"),
                rx.icon_button(rx.icon("maximize-2", size=13), on_click=lambda: State.open_task(t["id"]), size="1", variant="ghost"),
                rx.icon_button(rx.icon("chevron-right", size=14), on_click=lambda: State.move_right(t["id"]), size="1", variant="ghost"),
                width="100%",
                justify="center",
                spacing="0",
                opacity="0",
                transition="opacity 0.2s",
                _group_hover={"opacity": "1"},
            ),
            spacing="2",
            width="100%",
        ),
        padding="0.9em",
        background=card(),
        border=f"1px solid {border()}",
        border_left=f"3px solid {label['color']}",
        border_radius="10px",
        cursor="pointer",
        _hover={"transform": "translateY(-2px)", "box_shadow": "0 6px 18px rgba(0,0,0,0.15)"},
        transition="all 0.15s",
        _group="hover",
        width="100%",
    )


def column(col: dict):
    return rx.vstack(
        # Header
        rx.hstack(
            rx.text(col["emoji"], font_size="1em"),
            rx.text(col["title"], color=text(), font_weight="600", font_size="0.95em"),
            rx.badge(
                State.stats[col["id"]],
                background=f"{col['color']}22",
                color=col["color"],
                variant="soft",
                size="1",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("plus", size=14),
                on_click=lambda: State.toggle_add(),
                variant="ghost",
                size="1",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        # Column underline
        rx.box(height="3px", width="100%", background=col["color"], border_radius="full", opacity="0.6"),
        # Task list
        rx.vstack(
            rx.foreach(
                State.filtered_tasks,
                lambda t: rx.cond(
                    t["status"] == col["id"],
                    task_card(t),
                    rx.fragment(),
                ),
            ),
            spacing="2",
            width="100%",
            min_height="120px",
            padding="0.25em 0",
        ),
        spacing="3",
        padding="1em",
        background=col_bg(),
        border=f"1px solid {border()}",
        border_radius="14px",
        min_width="280px",
        width="280px",
        height="fit-content",
        max_height="calc(100vh - 200px)",
        overflow_y="auto",
    )


def board():
    return rx.hstack(
        rx.foreach(COLUMNS, column),
        spacing="4",
        padding="1.5em 2em",
        overflow_x="auto",
        width="100%",
        align="start",
    )


def add_task_modal():
    return rx.hstack(
        rx.box(
            on_click=State.toggle_add,
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="#00000066",
            z_index="40",
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading("New Task", size="5", color=text()),
                    rx.spacer(),
                    rx.icon_button(rx.icon("x", size=16), on_click=State.toggle_add, variant="ghost"),
                    width="100%",
                    align="center",
                ),
                rx.divider(border_color=border()),
                rx.input(
                    placeholder="Task title...",
                    value=State.new_title,
                    on_change=State.set_new_title,
                    size="3",
                    width="100%",
                    background=col_bg(),
                    border=f"1px solid {border()}",
                    color=text(),
                ),
                rx.select(
                    [c["id"] for c in COLUMNS],
                    value=State.new_status,
                    on_change=State.set_new_status,
                    width="100%",
                    size="3",
                ),
                rx.hstack(
                    rx.button("Cancel", on_click=State.toggle_add, variant="soft", flex="1"),
                    rx.button("Create Task", on_click=State.add_task, color_scheme="purple", flex="1"),
                    spacing="3",
                    width="100%",
                    margin_top="0.5em",
                ),
                spacing="3",
                width="100%",
            ),
            background=card(),
            padding="1.5em",
            border_radius="14px",
            width="400px",
            max_width="90vw",
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            z_index="50",
            box_shadow="0 20px 60px rgba(0,0,0,0.4)",
        ),
        spacing="0",
    )


def task_detail_modal():
    t = State.active_task
    label = LABELS.get(t["label"], {"name": "—", "color": "#888"})
    prio = PRIORITIES.get(t["priority"], {"name": "—", "color": "#888"})
    return rx.hstack(
        rx.box(
            on_click=State.close_task,
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="#00000099",
            backdrop_filter="blur(4px)",
            z_index="40",
        ),
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.badge(label["name"], background=label["color"], color="white", variant="solid"),
                    rx.badge(prio["name"], background=f"{prio['color']}22", color=prio["color"], variant="soft"),
                    rx.spacer(),
                    rx.icon_button(rx.icon("trash-2", size=16), on_click=lambda: State.delete_task(t["id"]), variant="soft", color_scheme="red", size="2"),
                    rx.icon_button(rx.icon("x", size=16), on_click=State.close_task, variant="ghost", size="2"),
                    width="100%",
                    align="center",
                    spacing="2",
                ),
                rx.heading(t["title"], size="6", color=text()),
                rx.divider(border_color=border()),
                rx.text(t["desc"], color=muted(), font_size="0.95em"),

                # Meta grid
                rx.grid(
                    rx.vstack(rx.text("Assignee", color=muted(), font_size="0.75em", font_weight="600"), rx.hstack(rx.avatar(fallback=t["assignee"][0], size="1"), rx.text(t["assignee"], color=text()), spacing="2", align="center"), spacing="1", align="start"),
                    rx.vstack(rx.text("Due date", color=muted(), font_size="0.75em", font_weight="600"), rx.text(t["due"], color=text()), spacing="1", align="start"),
                    rx.vstack(rx.text("Status", color=muted(), font_size="0.75em", font_weight="600"), rx.text(t["status"].replace("_", " ").title(), color=text()), spacing="1", align="start"),
                    rx.vstack(rx.text("Comments", color=muted(), font_size="0.75em", font_weight="600"), rx.text(t["comments"], color=text()), spacing="1", align="start"),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),

                rx.divider(border_color=border()),
                rx.text("Move to", color=muted(), font_size="0.75em", font_weight="600"),
                rx.hstack(
                    *[rx.button(
                        c["title"],
                        on_click=lambda cid=c["id"]: State.move_task(t["id"], cid),
                        size="1",
                        variant=rx.cond(t["status"] == c["id"], "solid", "soft"),
                        color_scheme="purple",
                    ) for c in COLUMNS],
                    spacing="2",
                    wrap="wrap",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            background=card(),
            padding="1.5em",
            border_radius="14px",
            width="520px",
            max_width="90vw",
            max_height="90vh",
            overflow_y="auto",
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            z_index="50",
            box_shadow="0 20px 60px rgba(0,0,0,0.5)",
        ),
        spacing="0",
    )


# ---------- LAYOUT ----------
def index():
    return rx.box(
        navbar(),
        filter_bar(),
        rx.box(
            board(),
            width="100%",
            overflow_x="auto",
        ),
        rx.cond(State.show_add, add_task_modal()),
        rx.cond(State.active_task_id > 0, task_detail_modal()),
        background=bg(),
        min_height="100vh",
        width="100%",
    )


# ---------- APP ----------
app = rx.App()
app.add_page(index, title="PyBoard — Kanban")