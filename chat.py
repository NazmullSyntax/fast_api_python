import reflex as rx
from datetime import datetime
import random


# ---------- STATE ----------
class State(rx.State):
    """Chat app state."""
    draft: str = ""
    messages: list[dict] = []
    is_typing: bool = False
    dark: bool = True
    current_user: str = "You"

    def set_draft(self, v: str):
        self.draft = v

    def toggle_dark(self):
        self.dark = not self.dark

    def send_message(self):
        if not self.draft.strip():
            return
        self.messages.append({
            "id": len(self.messages),
            "author": "You",
            "text": self.draft.strip(),
            "time": datetime.now().strftime("%H:%M"),
            "mine": True,
        })
        self.draft = ""

    def clear_chat(self):
        self.messages = []
        self._seed_welcome()


# ---------- BOT (simulated reply) ----------
class BotState(rx.State):
    """Separate state so bot typing doesn't block UI."""
    typing: bool = False

    async def reply(self, user_text: str):
        self.typing = True
        yield
        import asyncio
        await asyncio.sleep(1.2)
        self.typing = False
        yield

        # Fake responses
        responses = [
            f"That's interesting! Tell me more about '{user_text[:20]}...'",
            "Got it. Can you elaborate?",
            "Hmm, I see what you mean 🤔",
            "Nice! Anything else on your mind?",
            "Cool cool. What else?",
            "Sure thing! Let me think about that.",
        ]
        State.messages.append({
            "id": len(State.messages),
            "author": "PyBot",
            "text": random.choice(responses),
            "time": datetime.now().strftime("%H:%M"),
            "mine": False,
        })


def _seed_welcome():
    State.messages = [
        {
            "id": 0,
            "author": "PyBot",
            "text": "Hey there! 👋 I'm PyBot, your Python-powered assistant. Ask me anything!",
            "time": datetime.now().strftime("%H:%M"),
            "mine": False,
        },
    ]

_seed_welcome()


# ---------- THEME ----------
def bg():      return rx.cond(State.dark, "#0b141a", "#efeae2")
def card_bg(): return rx.cond(State.dark, "#111b21", "#ffffff")
def panel():   return rx.cond(State.dark, "#202c33", "#f0f2f5")
def text():    return rx.cond(State.dark, "#e9edef", "#111b21")
def muted():   return rx.cond(State.dark, "#8696a0", "#667781")
def border():  return rx.cond(State.dark, "#2a3942", "#e9edef")


# ---------- COMPONENTS ----------
def message_bubble(m: dict):
    is_mine = m["mine"]
    return rx.hstack(
        rx.spacer() if not is_mine else rx.fragment(),
        rx.box(
            rx.vstack(
                rx.cond(
                    not is_mine,
                    rx.text(
                        m["author"],
                        font_size="0.75em",
                        font_weight="600",
                        color="#a371f7",
                    ),
                ),
                rx.text(m["text"], color="white" if is_mine else text(), font_size="0.95em"),
                rx.hstack(
                    rx.text(m["time"], font_size="0.7em",
                            color=rx.cond(is_mine, "#ffffffaa", muted())),
                    rx.cond(
                        is_mine,
                        rx.text("✓✓", font_size="0.7em", color="#53bdeb"),
                    ),
                    spacing="1",
                    justify="end",
                    width="100%",
                ),
                spacing="1",
                align="start",
            ),
            background=rx.cond(is_mine, "#005c4b", card_bg()),
            border=rx.cond(is_mine, "none", f"1px solid {border()}"),
            padding="0.6em 0.9em",
            border_radius="12px",
            max_width="70%",
            box_shadow="0 1px 2px rgba(0,0,0,0.1)",
        ),
        rx.spacer() if is_mine else rx.fragment(),
        width="100%",
        align="end",
    )


def typing_bubble():
    return rx.hstack(
        rx.box(
            rx.hstack(
                rx.text("PyBot is typing", font_size="0.8em", color=muted()),
                rx.hstack(
                    rx.box(width="6px", height="6px", border_radius="full", background="#a371f7",
                           animation="bounce 1s infinite"),
                    rx.box(width="6px", height="6px", border_radius="full", background="#a371f7",
                           animation="bounce 1s infinite 0.2s"),
                    rx.box(width="6px", height="6px", border_radius="full", background="#a371f7",
                           animation="bounce 1s infinite 0.4s"),
                    spacing="1",
                ),
                spacing="2",
                align="center",
            ),
            background=card_bg(),
            border=f"1px solid {border()}",
            padding="0.6em 0.9em",
            border_radius="12px",
        ),
        width="100%",
    )


def sidebar():
    def contact(name: str, emoji: str, online: bool):
        return rx.hstack(
            rx.avatar(fallback=emoji, size="2", color_scheme="purple"),
            rx.vstack(
                rx.text(name, font_weight="500", color=text(), font_size="0.9em"),
                rx.text(
                    "online" if online else "offline",
                    font_size="0.75em",
                    color=rx.cond(online, "#3fb950", muted()),
                ),
                spacing="0",
                align="start",
            ),
            padding="0.6em 0.8em",
            border_radius="8px",
            width="100%",
            _hover={"background": panel()},
            cursor="pointer",
            spacing="3",
        )

    return rx.vstack(
        rx.hstack(
            rx.heading("Chats", size="5", color=text()),
            rx.spacer(),
            rx.icon("pencil", size=16, color=muted()),
            width="100%",
            align="center",
        ),
        rx.input(
            placeholder="🔍 Search",
            size="2",
            width="100%",
            background=panel(),
            border="none",
        ),
        rx.divider(border_color=border()),
        contact("PyBot", "🤖", True),
        contact("Alice", "👩", True),
        contact("Bob", "🧑", False),
        contact("Carol", "👩‍💻", True),
        rx.spacer(),
        rx.button(
            rx.cond(State.dark, "☀️ Light mode", "🌙 Dark mode"),
            on_click=State.toggle_dark,
            variant="soft",
            width="100%",
            size="2",
        ),
        width="300px",
        height="100vh",
        padding="1em",
        background=card_bg(),
        border_right=f"1px solid {border()}",
        spacing="3",
        display=rx.breakpoints(initial="none", md="flex"),
    )


def chat_header():
    return rx.hstack(
        rx.avatar(fallback="🤖", size="3", color_scheme="purple"),
        rx.vstack(
            rx.text("PyBot", font_weight="600", color=text()),
            rx.text("online", font_size="0.8em", color="#3fb950"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            rx.icon("phone", size=18, color=muted(), cursor="pointer"),
            rx.icon("video", size=18, color=muted(), cursor="pointer"),
            rx.icon("search", size=18, color=muted(), cursor="pointer"),
            rx.tooltip(
                rx.icon("trash-2", size=18, color=muted(), cursor="pointer",
                        on_click=State.clear_chat),
                content="Clear chat",
            ),
            spacing="4",
        ),
        width="100%",
        padding="0.8em 1.2em",
        background=panel(),
        border_bottom=f"1px solid {border()}",
        align="center",
    )


def composer():
    return rx.hstack(
        rx.icon("smile", size=20, color=muted(), cursor="pointer"),
        rx.input(
            placeholder="Type a message...",
            value=State.draft,
            on_change=State.set_draft,
            on_key_down=lambda key: rx.cond(key == "Enter", State.send_message(), rx.noop()),
            flex="1",
            size="3",
            background=panel(),
            border="none",
            color=text(),
        ),
        rx.icon("paperclip", size=20, color=muted(), cursor="pointer"),
        rx.button(
            rx.icon("send", size=16),
            on_click=[State.send_message, BotState.reply(State.draft)],
            color_scheme="green",
            size="3",
        ),
        width="100%",
        padding="0.8em 1.2em",
        background=panel(),
        border_top=f"1px solid {border()}",
        align="center",
        spacing="3",
    )


# ---------- LAYOUT ----------
def index():
    return rx.hstack(
        sidebar(),
        rx.vstack(
            chat_header(),
            rx.box(
                rx.vstack(
                    rx.foreach(State.messages, message_bubble),
                    rx.cond(BotState.typing, typing_bubble()),
                    spacing="3",
                    width="100%",
                    padding="1.5em 2em",
                ),
                flex="1",
                width="100%",
                overflow_y="auto",
                background=bg(),
                background_image="radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)",
                background_size="20px 20px",
            ),
            composer(),
            width="100%",
            height="100vh",
            spacing="0",
        ),
        width="100%",
        spacing="0",
        align="start",
    )


# ---------- APP ----------
app = rx.App(
    style={
        "@keyframes bounce": {
            "0%, 100%": {"transform": "translateY(0)"},
            "50%": {"transform": "translateY(-4px)"},
        },
    }
)
app.add_page(index, title="PyChat")