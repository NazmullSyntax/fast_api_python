import reflex as rx


# ---------- SEED DATA ----------
MOVIES = [
    {"id": 1, "title": "The Pythonist", "year": 2024, "rating": 8.7, "genre": "Thriller", "duration": "2h 14m", "emoji": "🐍", "color": "#7c3aed", "desc": "A rogue developer discovers a hidden backdoor in the world's largest social network."},
    {"id": 2, "title": "Django Unchained Data", "year": 2023, "rating": 8.2, "genre": "Action", "duration": "1h 58m", "emoji": "🤠", "color": "#dc2626", "desc": "An ORM-wielding cowboy fights corrupt databases in the wild west of servers."},
    {"id": 3, "title": "Flask of Fury", "year": 2024, "rating": 7.9, "genre": "Action", "duration": "1h 42m", "emoji": "⚗️", "color": "#0891b2", "desc": "A microframework rebel takes on monolithic empires."},
    {"id": 4, "title": "FastAPI Nights", "year": 2025, "rating": 9.1, "genre": "Drama", "duration": "2h 06m", "emoji": "⚡", "color": "#059669", "desc": "Async love story between a coder and their 100ms latency budget."},
    {"id": 5, "title": "Reflex Protocol", "year": 2024, "rating": 8.4, "genre": "Sci-Fi", "duration": "2h 21m", "emoji": "🔄", "color": "#ea580c", "desc": "When state and UI merge, nothing is what it seems."},
    {"id": 6, "title": "The Matrix Reloaded", "year": 2003, "rating": 7.2, "genre": "Sci-Fi", "duration": "2h 18m", "emoji": "🟢", "color": "#16a34a", "desc": "Follow the white rabbit into the source code."},
    {"id": 7, "title": "Pandas & Prejudice", "year": 2022, "rating": 7.6, "genre": "Romance", "duration": "1h 55m", "emoji": "🐼", "color": "#db2777", "desc": "Two dataframes find love in a merge gone right."},
    {"id": 8, "title": "Numpy Nights", "year": 2023, "rating": 8.0, "genre": "Drama", "duration": "1h 48m", "emoji": "📐", "color": "#4f46e5", "desc": "Vectorized dreams in a scalar world."},
    {"id": 9, "title": "The Last Commit", "year": 2025, "rating": 8.9, "genre": "Thriller", "duration": "2h 02m", "emoji": "💾", "color": "#b91c1c", "desc": "One developer. One repo. One chance to revert everything."},
    {"id": 10, "title": "Kubernetes Rising", "year": 2024, "rating": 7.8, "genre": "Action", "duration": "2h 09m", "emoji": "☸️", "color": "#2563eb", "desc": "Containers battle for control of the cluster."},
    {"id": 11, "title": "Redis Revenant", "year": 2023, "rating": 7.5, "genre": "Horror", "duration": "1h 37m", "emoji": "🟥", "color": "#e11d48", "desc": "Data that never dies... returns from cache."},
    {"id": 12, "title": "Docker Deep", "year": 2024, "rating": 8.1, "genre": "Sci-Fi", "duration": "1h 51m", "emoji": "🐳", "color": "#0284c7", "desc": "It works on my machine — and yours, and yours, and yours."},
]

CATEGORIES = ["All", "Action", "Thriller", "Sci-Fi", "Drama", "Romance", "Horror"]


# ---------- STATE ----------
class State(rx.State):
    """Streaming UI state."""
    dark: bool = True
    category: str = "All"
    search: str = ""
    active_movie_id: int = 0
    my_list: list[int] = []
    hero_index: int = 0

    # UI events
    def toggle_dark(self):
        self.dark = not self.dark

    def set_category(self, c: str):
        self.category = c

    def set_search(self, v: str):
        self.search = v

    def open_movie(self, mid: int):
        self.active_movie_id = mid

    def close_movie(self):
        self.active_movie_id = 0

    def toggle_my_list(self, mid: int):
        if mid in self.my_list:
            self.my_list.remove(mid)
        else:
            self.my_list.append(mid)

    # Computed
    @rx.var
    def active_movie(self) -> dict:
        for m in MOVIES:
            if m["id"] == self.active_movie_id:
                return m
        return {}

    @rx.var
    def hero_movie(self) -> dict:
        return MOVIES[self.hero_index % len(MOVIES)]

    @rx.var
    def filtered(self) -> list[dict]:
        items = MOVIES
        if self.category != "All":
            items = [m for m in items if m["genre"] == self.category]
        if self.search:
            q = self.search.lower()
            items = [m for m in items if q in m["title"].lower()]
        return items

    @rx.var
    def trending(self) -> list[dict]:
        return sorted(MOVIES, key=lambda m: m["rating"], reverse=True)[:6]

    @rx.var
    def my_list_movies(self) -> list[dict]:
        return [m for m in MOVIES if m["id"] in self.my_list]


# ---------- THEME ----------
def bg():      return rx.cond(State.dark, "#08080f", "#f5f5fa")
def card():    return rx.cond(State.dark, "#12121e", "white")
def text():    return rx.cond(State.dark, "#f5f5ff", "#101018")
def muted():   return rx.cond(State.dark, "#8888a0", "#6b6b80")
def border():  return rx.cond(State.dark, "#22223a", "#e5e5f0")


# ---------- COMPONENTS ----------
def navbar():
    return rx.hstack(
        rx.hstack(
            rx.text("🎬", font_size="1.6em"),
            rx.heading("PyFlix", size="6", color=text(), letter_spacing="tight"),
            spacing="2",
        ),
        rx.hstack(
            rx.button("Home", variant="ghost", size="2", color=text()),
            rx.button("Movies", variant="ghost", size="2", color=muted()),
            rx.button("Series", variant="ghost", size="2", color=muted()),
            rx.button("My List", variant="ghost", size="2", color=muted()),
            spacing="1",
            display=rx.breakpoints(initial="none", md="flex"),
        ),
        rx.spacer(),
        rx.input(
            placeholder="🔍 Search titles...",
            value=State.search,
            on_change=State.set_search,
            size="2",
            width=rx.breakpoints(initial="150px", md="280px"),
            background=card(),
            border=f"1px solid {border()}",
            color=text(),
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
        background=rx.cond(State.dark, "#08080fdd", "#ffffffdd"),
        backdrop_filter="blur(12px)",
        border_bottom=f"1px solid {border()}",
        align="center",
        position="sticky",
        top="0",
        z_index="30",
    )


def hero():
    h = State.hero_movie
    return rx.box(
        rx.box(
            rx.vstack(
                rx.badge("🔥 #1 Trending this week", color_scheme="red", variant="solid", size="2"),
                rx.heading(h["title"], size="9", color="white", text_align="left"),
                rx.hstack(
                    rx.text("⭐", font_size="0.9em"),
                    rx.text(h["rating"], color="#ffffffcc", font_weight="600"),
                    rx.text("•", color="#ffffff88"),
                    rx.text(h["year"], color="#ffffffcc"),
                    rx.text("•", color="#ffffff88"),
                    rx.text(h["duration"], color="#ffffffcc"),
                    rx.text("•", color="#ffffff88"),
                    rx.badge(h["genre"], color_scheme="purple", variant="soft"),
                    spacing="2",
                    align="center",
                ),
                rx.text(h["desc"], color="#ffffffcc", font_size="1.05em", max_width="520px"),
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon("play", size=16), rx.text("Play"), spacing="2", align="center"),
                        on_click=lambda: State.open_movie(h["id"]),
                        color_scheme="purple",
                        size="3",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon(rx.cond(h["id"].in_(State.my_list), "check", "plus"), size=16),
                            rx.text(rx.cond(h["id"].in_(State.my_list), "In My List", "Add to List")),
                            spacing="2", align="center",
                        ),
                        on_click=lambda: State.toggle_my_list(h["id"]),
                        variant="outline",
                        size="3",
                        color="white",
                        border_color="#ffffff44",
                        _hover={"background": "#ffffff22"},
                    ),
                    spacing="3",
                ),
                spacing="4",
                align="start",
                max_width="620px",
            ),
            padding="5em 3em",
            position="relative",
            z_index="2",
        ),
        background=f"linear-gradient(90deg, {h['color']}ee 0%, {h['color']}55 40%, transparent 100%), radial-gradient(circle at 20% 50%, {h['color']}aa, transparent 60%)",
        border_radius="0 0 24px 24px",
        min_height="420px",
        display="flex",
        align_items="center",
        position="relative",
        overflow="hidden",
        width="100%",
    )


def category_chip(c: str):
    active = State.category == c
    return rx.button(
        c,
        on_click=lambda: State.set_category(c),
        size="2",
        variant=rx.cond(active, "solid", "soft"),
        color_scheme="purple",
        border_radius="full",
    )


def filter_bar():
    return rx.hstack(
        rx.foreach(CATEGORIES, category_chip),
        width="100%",
        padding="2em 2em 0.5em",
        spacing="2",
        wrap="wrap",
    )


def movie_card(m: dict):
    return rx.box(
        rx.vstack(
            # Poster
            rx.box(
                rx.text(m["emoji"], font_size="3.5em"),
                rx.box(
                    rx.badge(f"⭐ {m['rating']}", color_scheme="yellow", variant="solid", size="1"),
                    position="absolute",
                    top="0.5em",
                    right="0.5em",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("play", size=14),
                            on_click=lambda: State.open_movie(m["id"]),
                            size="2",
                            color_scheme="purple",
                        ),
                        rx.icon_button(
                            rx.icon(rx.cond(m["id"].in_(State.my_list), "check", "plus"), size=14),
                            on_click=lambda: State.toggle_my_list(m["id"]),
                            size="2",
                            variant="soft",
                            color_scheme="purple",
                        ),
                        spacing="2",
                    ),
                    position="absolute",
                    top="50%",
                    left="50%",
                    transform="translate(-50%, -50%)",
                    opacity="0",
                    transition="opacity 0.25s",
                    _group_hover={"opacity": "1"},
                ),
                background=f"linear-gradient(135deg, {m['color']} 0%, {m['color']}99 100%)",
                border_radius="12px",
                width="100%",
                height="220px",
                display="flex",
                align_items="center",
                justify_content="center",
                position="relative",
                overflow="hidden",
                _group_hover={"transform": "scale(1.03)"},
                transition="transform 0.3s",
            ),
            rx.vstack(
                rx.text(m["title"], font_weight="600", color=text(), font_size="0.95em", no_of_lines=1),
                rx.hstack(
                    rx.text(m["year"], color=muted(), font_size="0.8em"),
                    rx.text("•", color=muted(), font_size="0.8em"),
                    rx.text(m["genre"], color=muted(), font_size="0.8em"),
                    spacing="1",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        padding="0.5em",
        border_radius="14px",
        _hover={"background": card()},
        transition="background 0.2s",
        cursor="pointer",
        _group="hover",
    )


def row(title: str, movies, show_all: bool = False):
    return rx.vstack(
        rx.hstack(
            rx.heading(title, size="5", color=text()),
            rx.spacer(),
            rx.cond(
                show_all,
                rx.button("View all →", variant="ghost", size="1", color=muted()),
            ),
            width="100%",
            align="center",
        ),
        rx.grid(
            rx.foreach(movies, movie_card),
            columns=rx.breakpoints(initial="2", sm="3", md="4", lg="6"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        width="100%",
        padding="1em 2em",
    )


def movie_modal():
    m = State.active_movie
    return rx.hstack(
        # Backdrop
        rx.box(
            on_click=State.close_movie,
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="#000000cc",
            backdrop_filter="blur(6px)",
            z_index="40",
        ),
        # Modal
        rx.box(
            rx.vstack(
                # Poster header
                rx.box(
                    rx.hstack(
                        rx.text(m["emoji"], font_size="5em"),
                        rx.spacer(),
                        rx.icon_button(
                            rx.icon("x", size=18),
                            on_click=State.close_movie,
                            variant="soft",
                            color_scheme="gray",
                        ),
                        width="100%",
                        align="start",
                    ),
                    background=f"linear-gradient(135deg, {m['color']} 0%, {m['color']}88 100%)",
                    padding="1.5em",
                    border_radius="16px 16px 0 0",
                    width="100%",
                ),
                # Info
                rx.vstack(
                    rx.heading(m["title"], size="7", color=text()),
                    rx.hstack(
                        rx.badge(f"⭐ {m['rating']}", color_scheme="yellow", variant="solid"),
                        rx.badge(m["genre"], color_scheme="purple", variant="soft"),
                        rx.text(m["year"], color=muted()),
                        rx.text("•", color=muted()),
                        rx.text(m["duration"], color=muted()),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(m["desc"], color=muted(), font_size="1em"),
                    rx.hstack(
                        rx.button(
                            rx.hstack(rx.icon("play", size=16), rx.text("Play Now"), spacing="2", align="center"),
                            color_scheme="purple",
                            size="3",
                            flex="1",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon(rx.cond(m["id"].in_(State.my_list), "check", "plus"), size=16),
                                rx.text(rx.cond(m["id"].in_(State.my_list), "In My List", "Add to List")),
                                spacing="2", align="center",
                            ),
                            on_click=lambda: State.toggle_my_list(m["id"]),
                            variant="outline",
                            size="3",
                            color=text(),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="3",
                    align="start",
                    padding="1.5em",
                    width="100%",
                ),
                spacing="0",
                width="100%",
            ),
            background=card(),
            border_radius="16px",
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


def footer():
    return rx.box(
        rx.hstack(
            rx.text("© 2026 PyFlix — Stream everything, built with Python", color=muted(), font_size="0.9em"),
            rx.spacer(),
            rx.hstack(
                rx.text("Help", color=muted(), font_size="0.9em", cursor="pointer"),
                rx.text("Account", color=muted(), font_size="0.9em", cursor="pointer"),
                rx.text("Devices", color=muted(), font_size="0.9em", cursor="pointer"),
                spacing="4",
            ),
            width="100%",
        ),
        padding="2em",
        border_top=f"1px solid {border()}",
        background=card(),
        margin_top="3em",
        width="100%",
    )


# ---------- LAYOUT ----------
def index():
    return rx.box(
        navbar(),
        hero(),
        filter_bar(),
        rx.cond(
            State.category == "All" and State.search == "",
            rx.vstack(
                row("🔥 Trending Now", State.trending, show_all=True),
                row("🎬 All Movies", State.filtered),
                rx.cond(
                    State.my_list.length() > 0,
                    row("❤️ My List", State.my_list_movies),
                ),
                spacing="4",
                width="100%",
                padding="1em 0",
            ),
            rx.vstack(
                row(
                    rx.cond(State.search != "", f"Results for \"{State.search}\"", f"{State.category} Movies"),
                    State.filtered,
                ),
                spacing="4",
                width="100%",
                padding="1em 0",
            ),
        ),
        footer(),
        rx.cond(State.active_movie_id > 0, movie_modal()),
        background=bg(),
        min_height="100vh",
        width="100%",
    )


# ---------- APP ----------
app = rx.App()
app.add_page(index, title="PyFlix — Stream Movies")