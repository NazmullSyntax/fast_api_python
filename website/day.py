import reflex as rx

# ---------- STATE ----------
class State(rx.State):
    """App state (frontend data + interactions)."""
    name: str = ""
    email: str = ""
    message: str = ""
    submitted: bool = False
    dark_mode: bool = False
    active_tab: str = "home"

    def toggle_dark(self):
        self.dark_mode = not self.dark_mode

    def set_name(self, v: str): self.name = v
    def set_email(self, v: str): self.email = v
    def set_message(self, v: str): self.message = v

    def set_tab(self, tab: str):
        self.active_tab = tab

    def submit_form(self):
        if self.name and self.email and self.message:
            self.submitted = True
            self.name = ""
            self.email = ""
            self.message = ""

    def reset_form(self):
        self.submitted = False


# ---------- DATA ----------
PROJECTS = [
    {"title": "Weather App", "desc": "Live weather dashboard with Flask", "tag": "Flask"},
    {"title": "Todo API", "desc": "REST API with FastAPI + SQLite", "tag": "FastAPI"},
    {"title": "AI Chatbot", "desc": "LLM-powered chat interface", "tag": "Reflex"},
    {"title": "Blog Engine", "desc": "Full CMS with Django", "tag": "Django"},
    {"title": "Photo Gallery", "desc": "Self-hosted image manager", "tag": "Reflex"},
    {"title": "Portfolio", "desc": "This site — pure Python frontend", "tag": "Reflex"},
]

SKILLS = ["Python", "Flask", "Django", "FastAPI", "Reflex", "SQL", "REST APIs", "HTML/CSS"]


# ---------- COMPONENTS ----------
def navbar():
    return rx.hstack(
        rx.heading("PyDev", size="6", color=rx.cond(State.dark_mode, "white", "black")),
        rx.spacer(),
        rx.hstack(
            rx.button("Home", on_click=lambda: State.set_tab("home"), variant="ghost"),
            rx.button("Projects", on_click=lambda: State.set_tab("projects"), variant="ghost"),
            rx.button("About", on_click=lambda: State.set_tab("about"), variant="ghost"),
            rx.button("Contact", on_click=lambda: State.set_tab("contact"), variant="ghost"),
            spacing="2",
        ),
        rx.button(
            rx.cond(State.dark_mode, "☀️", "🌙"),
            on_click=State.toggle_dark,
            variant="soft",
        ),
        width="100%",
        padding="1em 2em",
        border_bottom="1px solid",
        border_color=rx.cond(State.dark_mode, "#333", "#eee"),
        position="sticky",
        top="0",
        z_index="10",
        background=rx.cond(State.dark_mode, "#111", "white"),
    )


def project_card(p: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(p["title"], size="4"),
                rx.spacer(),
                rx.badge(p["tag"], color_scheme="purple", variant="soft"),
                width="100%",
            ),
            rx.text(p["desc"], color=rx.cond(State.dark_mode, "#aaa", "#555")),
            rx.link("View project →", href="#", color="purple"),
            align="start",
            spacing="3",
        ),
        padding="1.5em",
        border="1px solid",
        border_color=rx.cond(State.dark_mode, "#333", "#eee"),
        border_radius="12px",
        background=rx.cond(State.dark_mode, "#1a1a1a", "white"),
        _hover={"transform": "translateY(-4px)", "box_shadow": "0 8px 20px rgba(0,0,0,0.1)"},
        transition="all 0.2s",
        width="100%",
    )


def home_tab():
    return rx.vstack(
        rx.heading("Hi, I'm a Python Developer 👋", size="9", text_align="center"),
        rx.text(
            "I build modern web frontends using only Python.",
            size="5",
            color=rx.cond(State.dark_mode, "#aaa", "#555"),
            text_align="center",
        ),
        rx.hstack(
            rx.button("See Projects", on_click=lambda: State.set_tab("projects"), size="3", color_scheme="purple"),
            rx.button("Contact Me", on_click=lambda: State.set_tab("contact"), size="3", variant="outline"),
            spacing="3",
            margin_top="1em",
        ),
        rx.hstack(
            *[rx.badge(s, size="2", color_scheme="violet", variant="soft") for s in SKILLS],
            wrap="wrap",
            justify="center",
            spacing="2",
            margin_top="2em",
        ),
        spacing="5",
        padding="4em 2em",
        align="center",
        min_height="60vh",
    )


def projects_tab():
    return rx.vstack(
        rx.heading("Projects", size="8"),
        rx.grid(
            *[project_card(p) for p in PROJECTS],
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="4",
            width="100%",
        ),
        spacing="5",
        padding="3em 2em",
        width="100%",
    )


def about_tab():
    return rx.vstack(
        rx.heading("About Me", size="8"),
        rx.text(
            "I'm a full-stack Python developer focused on building clean, "
            "fast web experiences. I love using Flask, Django, FastAPI, and Reflex "
            "to ship products end-to-end without touching JavaScript.",
            font_size="1.1em",
            max_width="700px",
            text_align="center",
            color=rx.cond(State.dark_mode, "#ccc", "#444"),
        ),
        rx.hstack(
            rx.vstack(rx.heading("50+", size="7"), rx.text("Projects"), align="center"),
            rx.vstack(rx.heading("5", size="7"), rx.text("Years Exp"), align="center"),
            rx.vstack(rx.heading("20+", size="7"), rx.text("Clients"), align="center"),
            spacing="8",
            margin_top="2em",
        ),
        align="center",
        spacing="5",
        padding="4em 2em",
    )


def contact_tab():
    return rx.vstack(
        rx.heading("Get in Touch", size="8"),
        rx.cond(
            State.submitted,
            rx.vstack(
                rx.text("✅ Message sent! I'll reply soon.", color="green", font_size="1.1em"),
                rx.button("Send another", on_click=State.reset_form, variant="outline"),
                spacing="3",
                align="center",
            ),
            rx.vstack(
                rx.input(placeholder="Your name", value=State.name, on_change=State.set_name, width="100%"),
                rx.input(placeholder="Email", value=State.email, on_change=State.set_email, width="100%"),
                rx.text_area(placeholder="Message...", value=State.message, on_change=State.set_message, width="100%", rows="5"),
                rx.button("Send Message", on_click=State.submit_form, color_scheme="purple", width="100%"),
                spacing="3",
                width="100%",
            ),
        ),
        width="450px",
        max_width="90vw",
        spacing="5",
        padding="4em 2em",
        align="center",
    )


def footer():
    return rx.box(
        rx.text(
            "© 2026 PyDev — Built entirely in Python with Reflex",
            text_align="center",
            color=rx.cond(State.dark_mode, "#888", "#777"),
            font_size="0.9em",
        ),
        padding="2em",
        border_top="1px solid",
        border_color=rx.cond(State.dark_mode, "#333", "#eee"),
        width="100%",
    )


# ---------- LAYOUT ----------
def index():
    return rx.box(
        navbar(),
        rx.box(
            rx.cond(State.active_tab == "home", home_tab()),
            rx.cond(State.active_tab == "projects", projects_tab()),
            rx.cond(State.active_tab == "about", about_tab()),
            rx.cond(State.active_tab == "contact", contact_tab()),
            min_height="80vh",
            display="flex",
            justify_content="center",
        ),
        footer(),
        background=rx.cond(State.dark_mode, "#111", "white"),
        color=rx.cond(State.dark_mode, "white", "black"),
        min_height="100vh",
        transition="background 0.3s",
    )


# ---------- APP ----------
app = rx.App()
app.add_page(index, title="PyDev Portfolio")