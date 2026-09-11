import reflex as rx
from datetime import datetime


# ---------- SEED DATA ----------
TRACKS = [
    {"id": 1, "title": "Midnight Compiler", "artist": "The Bytecode Band", "album": "Stack Overflow", "duration": 218, "emoji": "🎸", "color": "#7c3aed"},
    {"id": 2, "title": "Recursion Dreams", "artist": "Luna Lambda", "album": "Infinite Loop", "duration": 245, "emoji": "🌙", "color": "#4f46e5"},
    {"id": 3, "title": "Async Love", "artist": "The Coroutines", "album": "Event Loop", "duration": 192, "emoji": "💜", "color": "#ec4899"},
    {"id": 4, "title": "Null Pointer Blues", "artist": "Seg Fault", "album": "Core Dump", "duration": 276, "emoji": "🎷", "color": "#0891b2"},
    {"id": 5, "title": "Kernel Panic", "artist": "Blue Screen", "album": "Fatal Error", "duration": 201, "emoji": "⚡", "color": "#dc2626"},
    {"id": 6, "title": "Merge Sort Serenade", "artist": "The Algorithms", "album": "Big O", "duration": 233, "emoji": "🎻", "color": "#059669"},
    {"id": 7, "title": "Docker Whale Song", "artist": "Containers", "album": "Isolation", "duration": 187, "emoji": "🐳", "color": "#0284c7"},
    {"id": 8, "title": "Regex Heartbreak", "artist": "Pattern Matchers", "album": "Lookahead", "duration": 259, "emoji": "💔", "color": "#db2777"},
]


def fmt_time(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


# ---------- STATE ----------
class State(rx.State):
    """Music player state."""
    dark: bool = True
    current_id: int = 1
    playing: bool = False
    position: int = 0
    volume: int = 70
    shuffle: bool = False
    repeat: bool = False
    view: str = "library"

    # ---- Player controls ----
    def play_track(self, tid: int):
        self.current_id = tid
        self.position = 0
        self.playing = True

    def toggle_play(self):
        self.playing = not self.playing

    def next_track(self):
        ids = [t["id"] for t in TRACKS]
        i = ids.index(self.current_id)
        self.current_id = ids[(i + 1) % len(ids)]
        self.position = 0
        self.playing = True

    def prev_track(self):
        ids = [t["id"] for t in TRACKS]
        i = ids.index(self.current_id)
        self.current_id = ids[(i - 1) % len(ids)]
        self.position = 0
        self.playing = True

    def seek(self, value: list[float]):
        if value:
            self.position = int(value[0])

    def set_volume(self, value: list[float]):
        if value:
            self.volume = int(value[0])

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

    def toggle_repeat(self):
        self.repeat = not self.repeat

    def set_view(self, v: str):
        self.view = v

    def toggle_dark(self):
        self.dark = not self.dark

    # ---- Computed ----
    @rx.var
    def current(self) -> dict:
        for t in TRACKS:
            if t["id"] == self.current_id:
                return t
        return TRACKS[0]

    @rx.var
    def progress_pct(self) -> float:
        dur = self.current.get("duration", 1)
        return (self.position / dur) * 100 if dur else 0

    @rx.var
    def position_str(self) -> str:
        return fmt_time(self.position)

    @rx.var
    def duration_str(self) -> str:
        return fmt_time(self.current.get("duration", 0))

    @rx.var
    def queue(self) -> list[dict]:
        ids = [t["id"] for t in TRACKS]
        i = ids.index(self.current_id)
        return TRACKS[i:] + TRACKS[:i]


# ---------- THEME ----------
def bg():      return rx.cond(State.dark, "#0a0a12", "#f7f7fb")
def card():    return rx.cond(State.dark, "#14141f", "white")
def panel():   return rx.cond(State.dark, "#1c1c2b", "#f0f0f5")
def text():    return rx.cond(State.dark, "#f5f5ff", "#12121a")
def muted():   return rx.cond(State.dark, "#8888a0", "#6b6b80")
def border():  return rx.cond(State.dark, "#26263a", "#e5e5ef")


# ---------- COMPONENTS ----------
def sidebar():
    def nav_item(icon: str, label: str, key: str):
        active = State.view == key
        return rx.hstack(
            rx.icon(icon, size=18),
            rx.text(label, font_weight="500"),
            padding="0.6em 1em",
            border_radius="8px",
            width="100%",
            cursor="pointer",
            background=rx.cond(active, rx.cond(State.dark, "#2a2a44", "#e5e5f5"), "transparent"),
            color=rx.cond(active, "#a371f7", text()),
            on_click=lambda: State.set_view(key),
            spacing="3",
            align="center",
            _hover={"background": panel()},
            transition="all 0.15s",
        )
    return rx.vstack(
        rx.hstack(
            rx.text("🎧", font_size="1.6em"),
            rx.heading("PyTune", size="6", color=text()),
            spacing="2",
        ),
        rx.divider(border_color=border(), margin="0.5em 0"),
        nav_item("library", "Library", "library"),
        nav_item("list-music", "Playlist", "playlist"),
        nav_item("heart", "Favorites", "favorites"),
        nav_item("clock", "Recent", "recent"),
        rx.spacer(),
        rx.divider(border_color=border(), margin="0.5em 0"),
        rx.button(
            rx.cond(State.dark, "☀️ Light", "🌙 Dark"),
            on_click=State.toggle_dark,
            variant="soft",
            width="100%",
            size="2",
        ),
        width="220px",
        height="100vh",
        padding="1.2em 1em",
        background=card(),
        border_right=f"1px solid {border()}",
        spacing="1",
        position="sticky",
        top="0",
        display=rx.breakpoints(initial="none", md="flex"),
    )


def visualizer_bar(i: int):
    return rx.box(
        width="3px",
        height=rx.cond(
            State.playing,
            f"{20 + (i * 7) % 60}px",
            "8px",
        ),
        background="#a371f7",
        border_radius="full",
        animation=rx.cond(State.playing, f"eq 0.8s infinite {i * 0.1}s", "none"),
        transition="height 0.3s",
    )


def album_art():
    c = State.current
    return rx.box(
        rx.vstack(
            rx.text(c["emoji"], font_size="6em"),
            rx.cond(
                State.playing,
                rx.hstack(
                    *[visualizer_bar(i) for i in range(9)],
                    spacing="1",
                    align="end",
                    height="60px",
                ),
                rx.text("⏸ Paused", color="#ffffffaa", font_size="0.8em"),
            ),
            spacing="3",
            align="center",
        ),
        background=f"linear-gradient(135deg, {c['color']} 0%, {c['color']}88 100%)",
        width="280px",
        height="280px",
        border_radius="24px",
        display="flex",
        align_items="center",
        justify_content="center",
        box_shadow=f"0 20px 60px {c['color']}55",
        transition="all 0.4s",
    )


def player_controls():
    return rx.vstack(
        rx.heading(State.current["title"], size="7", color=text(), text_align="center"),
        rx.text(State.current["artist"], color=muted(), font_size="1em"),
        rx.text(State.current["album"], color=muted(), font_size="0.85em"),

        # Progress bar
        rx.vstack(
            rx.slider(
                value=[State.position],
                on_value_commit=State.seek,
                min=0,
                max=State.current["duration"].to(int),
                width="100%",
                color_scheme="purple",
            ),
            rx.hstack(
                rx.text(State.position_str, color=muted(), font_size="0.8em"),
                rx.spacer(),
                rx.text(State.duration_str, color=muted(), font_size="0.8em"),
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),

        # Control buttons
        rx.hstack(
            rx.icon_button(
                rx.icon("shuffle", size=18),
                on_click=State.toggle_shuffle,
                variant=rx.cond(State.shuffle, "solid", "ghost"),
                color_scheme="purple",
                size="2",
            ),
            rx.icon_button(rx.icon("skip-back", size=20), on_click=State.prev_track, variant="ghost", size="2"),
            rx.icon_button(
                rx.icon(rx.cond(State.playing, "pause", "play"), size=26),
                on_click=State.toggle_play,
                color_scheme="purple",
                size="4",
                border_radius="full",
            ),
            rx.icon_button(rx.icon("skip-forward", size=20), on_click=State.next_track, variant="ghost", size="2"),
            rx.icon_button(
                rx.icon("repeat", size=18),
                on_click=State.toggle_repeat,
                variant=rx.cond(State.repeat, "solid", "ghost"),
                color_scheme="purple",
                size="2",
            ),
            spacing="3",
            align="center",
            justify="center",
        ),

        # Volume
        rx.hstack(
            rx.icon("volume-2", size=16, color=muted()),
            rx.slider(
                value=[State.volume],
                on_value_commit=State.set_volume,
                min=0,
                max=100,
                width="140px",
                color_scheme="purple",
            ),
            rx.text(f"{State.volume}", color=muted(), font_size="0.8em", min_width="28px"),
            spacing="2",
            align="center",
        ),

        spacing="4",
        align="center",
        width="100%",
        max_width="420px",
    )


def track_row(t: dict):
    is_current = State.current_id == t["id"]
    return rx.hstack(
        # Index / play indicator
        rx.box(
            rx.cond(
                is_current & State.playing,
                rx.hstack(
                    rx.box(width="2px", height="10px", background="#a371f7", animation="eq 0.6s infinite"),
                    rx.box(width="2px", height="14px", background="#a371f7", animation="eq 0.6s infinite 0.15s"),
                    rx.box(width="2px", height="8px", background="#a371f7", animation="eq 0.6s infinite 0.3s"),
                    spacing="1",
                    align="end",
                    height="16px",
                ),
                rx.text(
                    str(TRACKS.index(t) + 1),
                    color=rx.cond(is_current, "#a371f7", muted()),
                    font_size="0.9em",
                    font_weight=rx.cond(is_current, "600", "400"),
                ),
            ),
            width="30px",
            display="flex",
            justify_content="center",
            align_items="center",
        ),
        rx.text(t["emoji"], font_size="1.4em"),
        rx.vstack(
            rx.text(
                t["title"],
                font_weight=rx.cond(is_current, "600", "500"),
                color=rx.cond(is_current, "#a371f7", text()),
                font_size="0.95em",
            ),
            rx.text(t["artist"], color=muted(), font_size="0.8em"),
            spacing="0",
            align="start",
            flex="1",
        ),
        rx.text(t["album"], color=muted(), font_size="0.85em", display=rx.breakpoints(initial="none", md="block")),
        rx.text(fmt_time(t["duration"]), color=muted(), font_size="0.85em"),
        rx.icon_button(
            rx.icon(rx.cond(is_current & State.playing, "pause", "play"), size=16),
            on_click=lambda: rx.cond(
                is_current,
                State.toggle_play(),
                State.play_track(t["id"]),
            ),
            variant="ghost",
            color_scheme="purple",
            size="2",
        ),
        padding="0.7em 1em",
        border_radius="10px",
        width="100%",
        align="center",
        spacing="3",
        background=rx.cond(is_current, panel(), "transparent"),
        cursor="pointer",
        _hover={"background": panel()},
        transition="all 0.15s",
    )


def library_view():
    return rx.vstack(
        rx.hstack(
            rx.heading("Your Library", size="7", color=text()),
            rx.spacer(),
            rx.badge(f"{len(TRACKS)} tracks", color_scheme="purple", variant="soft"),
            width="100%",
            align="center",
        ),
        rx.hstack(
            rx.text("Title", color=muted(), font_size="0.8em", font_weight="600", width="290px"),
            rx.text("Album", color=muted(), font_size="0.8em", font_weight="600", flex="1", display=rx.breakpoints(initial="none", md="block")),
            rx.text("Duration", color=muted(), font_size="0.8em", font_weight="600", width="70px"),
            rx.box(width="40px"),
            padding="0 1em",
            width="100%",
            spacing="3",
        ),
        rx.divider(border_color=border()),
        rx.vstack(
            rx.foreach(TRACKS, track_row),
            spacing="1",
            width="100%",
        ),
        spacing="3",
        width="100%",
        padding="2em",
    )


def queue_panel():
    def queue_item(t: dict, idx: int):
        is_current = State.current_id == t["id"]
        return rx.hstack(
            rx.text(str(idx + 1), color=muted(), font_size="0.75em", min_width="20px"),
            rx.text(t["emoji"], font_size="1.2em"),
            rx.vstack(
                rx.text(
                    t["title"],
                    font_size="0.85em",
                    font_weight=rx.cond(is_current, "600", "400"),
                    color=rx.cond(is_current, "#a371f7", text()),
                    no_of_lines=1,
                ),
                rx.text(t["artist"], color=muted(), font_size="0.75em"),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.text(fmt_time(t["duration"]), color=muted(), font_size="0.75em"),
            padding="0.5em 0.8em",
            border_radius="8px",
            background=rx.cond(is_current, panel(), "transparent"),
            cursor="pointer",
            on_click=lambda: State.play_track(t["id"]),
            width="100%",
            spacing="2",
            align="center",
            _hover={"background": panel()},
        )

    return rx.vstack(
        rx.hstack(
            rx.heading("Up Next", size="5", color=text()),
            rx.spacer(),
            rx.badge(f"{len(TRACKS)}", color_scheme="purple", variant="soft"),
            width="100%",
            align="center",
        ),
        rx.divider(border_color=border()),
        rx.vstack(
            rx.foreach(State.queue, queue_item),
            spacing="1",
            width="100%",
            overflow_y="auto",
            max_height="calc(100vh - 180px)",
        ),
        spacing="3",
        width="340px",
        height="100vh",
        padding="1.5em 1em",
        background=card(),
        border_left=f"1px solid {border()}",
        position="sticky",
        top="0",
        display=rx.breakpoints(initial="none", lg="flex"),
    )


# ---------- LAYOUT ----------
def index():
    return rx.hstack(
        sidebar(),
        rx.vstack(
            # Top bar
            rx.hstack(
                rx.input(
                    placeholder="🔍 Search songs, artists, albums...",
                    size="2",
                    width="380px",
                    background=panel(),
                    border="none",
                    color=text(),
                ),
                rx.spacer(),
                rx.badge("🎵 Now Playing", color_scheme="purple", variant="soft"),
                width="100%",
                padding="1em 2em",
                align="center",
                border_bottom=f"1px solid {border()}",
            ),
            # Main split: player + library
            rx.hstack(
                # Left: Player
                rx.vstack(
                    album_art(),
                    player_controls(),
                    spacing="6",
                    align="center",
                    padding="3em 2em",
                    width="440px",
                    min_width="360px",
                    border_right=f"1px solid {border()}",
                ),
                # Right: Library
                rx.box(
                    library_view(),
                    flex="1",
                    overflow_y="auto",
                    height="calc(100vh - 65px)",
                ),
                spacing="0",
                width="100%",
                align="start",
            ),
            width="100%",
            spacing="0",
            height="100vh",
        ),
        queue_panel(),
        width="100%",
        spacing="0",
        align="start",
        background=bg(),
    )


# ---------- APP ----------
app = rx.App(
    style={
        "@keyframes eq": {
            "0%, 100%": {"height": "8px"},
            "50%": {"height": "30px"},
        },
    }
)
app.add_page(index, title="PyTune — Music Player")