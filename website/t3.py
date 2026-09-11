import reflex as rx
import random
from datetime import datetime, timedelta


# ---------- STATE ----------
class State(rx.State):
    """Dashboard state."""
    dark: bool = True
    period: str = "7d"
    search: str = ""
    selected_metric: str = "revenue"

    # Simulated data
    revenue_data: list[dict] = []
    visitors_data: list[dict] = []
    transactions: list[dict] = []

    def toggle_dark(self):
        self.dark = not self.dark

    def set_period(self, p: str):
        self.period = p

    def set_metric(self, m: str):
        self.selected_metric = m

    def set_search(self, v: str):
        self.search = v

    # ---------- COMPUTED ----------
    @rx.var
    def filtered_transactions(self) -> list[dict]:
        if not self.search:
            return self.transactions
        q = self.search.lower()
        return [t for t in self.transactions if q in t["customer"].lower() or q in t["status"].lower()]

    @rx.var
    def total_revenue(self) -> str:
        return f"${sum(d['value'] for d in self.revenue_data):,}"

    @rx.var
    def total_visitors(self) -> str:
        return f"{sum(d['value'] for d in self.visitors_data):,}"

    @rx.var
    def chart_data(self) -> list[dict]:
        return self.revenue_data if self.selected_metric == "revenue" else self.visitors_data


# ---------- SEED DATA ----------
def _seed():
    days = 7
    today = datetime.now()
    for i in range(days):
        d = today - timedelta(days=days - i - 1)
        State.revenue_data.append({
            "day": d.strftime("%a"),
            "value": random.randint(800, 3200),
        })
        State.visitors_data.append({
            "day": d.strftime("%a"),
            "value": random.randint(400, 1800),
        })

    names = ["Alice Chen", "Bob Smith", "Carol Diaz", "David Kim", "Emma Wilson",
             "Frank Zhao", "Grace Lee", "Henry Park", "Ivy Nguyen", "Jack Brown"]
    statuses = ["Paid", "Pending", "Refunded", "Paid", "Paid"]
    for i, n in enumerate(names):
        State.transactions.append({
            "id": f"TXN-{1000 + i}",
            "customer": n,
            "amount": f"${random.randint(20, 950)}",
            "status": random.choice(statuses),
            "date": (today - timedelta(days=i)).strftime("%b %d"),
        })

_seed()


# ---------- THEME HELPERS ----------
def bg():
    return rx.cond(State.dark, "#0d1117", "#f6f8fa")

def card_bg():
    return rx.cond(State.dark, "#161b22", "white")

def border():
    return rx.cond(State.dark, "#30363d", "#e1e4e8")

def text():
    return rx.cond(State.dark, "#e6edf3", "#1f2328")

def muted():
    return rx.cond(State.dark, "#8b949e", "#656d76")


# ---------- COMPONENTS ----------
def sidebar():
    def link(icon: str, label: str):
        return rx.hstack(
            rx.text(icon, font_size="1.1em"),
            rx.text(label, font_weight="500"),
            padding="0.6em 1em",
            border_radius="8px",
            width="100%",
            color=text(),
            _hover={"background": rx.cond(State.dark, "#21262d", "#eaeef2")},
            cursor="pointer",
            spacing="3",
        )

    return rx.vstack(
        rx.hstack(
            rx.text("📊", font_size="1.5em"),
            rx.heading("PyMetrics", size="5", color=text()),
            spacing="2",
        ),
        rx.divider(border_color=border()),
        link("🏠", "Dashboard"),
        link("📈", "Analytics"),
        link("👥", "Customers"),
        link("💳", "Payments"),
        link("⚙️", "Settings"),
        rx.spacer(),
        rx.button(
            rx.cond(State.dark, "☀️ Light", "🌙 Dark"),
            on_click=State.toggle_dark,
            variant="soft",
            width="100%",
        ),
        width="240px",
        height="100vh",
        padding="1.5em 1em",
        border_right=f"1px solid {border()}",
        background=card_bg(),
        position="sticky",
        top="0",
        spacing="2",
        display=rx.breakpoints(initial="none", md="flex"),
    )


def stat_card(title: str, value: str, change: str, positive: bool):
    return rx.box(
        rx.vstack(
            rx.text(title, color=muted(), font_size="0.9em", font_weight="500"),
            rx.heading(value, size="7", color=text()),
            rx.hstack(
                rx.text(
                    ("▲ " if positive else "▼ ") + change,
                    color=rx.cond(positive, "#3fb950", "#f85149"),
                    font_weight="600",
                    font_size="0.9em",
                ),
                rx.text("vs last week", color=muted(), font_size="0.85em"),
                spacing="2",
            ),
            align="start",
            spacing="2",
        ),
        padding="1.5em",
        background=card_bg(),
        border=f"1px solid {border()}",
        border_radius="12px",
        flex="1",
        min_width="200px",
    )


def chart_card():
    def bar(d: dict):
        max_val = 3500
        height_pct = (d["value"] / max_val) * 100
        return rx.vstack(
            rx.text(f"{d['value']}", font_size="0.7em", color=muted()),
            rx.box(
                height=f"{height_pct}%",
                width="100%",
                background="linear-gradient(180deg, #a371f7, #7c3aed)",
                border_radius="6px 6px 0 0",
                transition="height 0.4s",
            ),
            rx.text(d["day"], font_size="0.8em", color=muted()),
            justify="end",
            align="center",
            height="200px",
            flex="1",
            spacing="1",
        )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    rx.cond(State.selected_metric == "revenue", "Revenue", "Visitors"),
                    size="5", color=text(),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        "Revenue",
                        on_click=lambda: State.set_metric("revenue"),
                        size="1",
                        variant=rx.cond(State.selected_metric == "revenue", "solid", "soft"),
                        color_scheme="purple",
                    ),
                    rx.button(
                        "Visitors",
                        on_click=lambda: State.set_metric("visitors"),
                        size="1",
                        variant=rx.cond(State.selected_metric == "visitors", "solid", "soft"),
                        color_scheme="purple",
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.foreach(State.chart_data, bar),
                width="100%",
                height="240px",
                align="end",
                spacing="3",
            ),
            width="100%",
            spacing="4",
        ),
        padding="1.5em",
        background=card_bg(),
        border=f"1px solid {border()}",
        border_radius="12px",
        flex="2",
        min_width="320px",
    )


def status_badge(status: str):
    colors = {
        "Paid": ("#3fb950", "#0d2818"),
        "Pending": ("#d29922", "#2d2410"),
        "Refunded": ("#f85149", "#2d1214"),
    }
    return rx.badge(
        status,
        color=rx.var(lambda: colors.get(status, ("gray", "gray"))[0]),
        background=rx.var(lambda: colors.get(status, ("gray", "gray"))[1]),
        border_radius="full",
        padding="0.2em 0.7em",
    )


def transaction_row(t: dict):
    return rx.table.row(
        rx.table.cell(rx.text(t["id"], font_family="monospace", color=muted(), font_size="0.85em")),
        rx.table.cell(rx.text(t["customer"], color=text(), font_weight="500")),
        rx.table.cell(rx.text(t["amount"], color=text(), font_weight="600")),
        rx.table.cell(status_badge(t["status"])),
        rx.table.cell(rx.text(t["date"], color=muted(), font_size="0.9em")),
        _hover={"background": rx.cond(State.dark, "#1c2128", "#f6f8fa")},
    )


def transactions_card():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("Recent Transactions", size="5", color=text()),
                rx.spacer(),
                rx.input(
                    placeholder="🔍 Search...",
                    value=State.search,
                    on_change=State.set_search,
                    size="2",
                    width="220px",
                ),
                width="100%",
                align="center",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(rx.text("ID", color=muted())),
                        rx.table.column_header_cell(rx.text("Customer", color=muted())),
                        rx.table.column_header_cell(rx.text("Amount", color=muted())),
                        rx.table.column_header_cell(rx.text("Status", color=muted())),
                        rx.table.column_header_cell(rx.text("Date", color=muted())),
                    ),
                ),
                rx.table.body(
                    rx.foreach(State.filtered_transactions, transaction_row),
                ),
                width="100%",
                variant="surface",
            ),
            width="100%",
            spacing="4",
        ),
        padding="1.5em",
        background=card_bg(),
        border=f"1px solid {border()}",
        border_radius="12px",
        width="100%",
    )


def topbar():
    return rx.hstack(
        rx.heading("Dashboard", size="6", color=text()),
        rx.spacer(),
        rx.hstack(
            *[rx.button(
                p.upper(),
                on_click=lambda p=p: State.set_period(p),
                size="2",
                variant=rx.cond(State.period == p, "solid", "soft"),
                color_scheme="purple",
            ) for p in ["1d", "7d", "30d"]],
            spacing="2",
        ),
        rx.avatar(fallback="PD", size="2", color_scheme="purple"),
        width="100%",
        padding="1.5em 2em 0.5em",
        align="center",
    )


# ---------- LAYOUT ----------
def index():
    return rx.hstack(
        sidebar(),
        rx.vstack(
            topbar(),
            rx.vstack(
                # Stat cards
                rx.hstack(
                    stat_card("Total Revenue", State.total_revenue, "12.5%", True),
                    stat_card("Visitors", State.total_visitors, "8.2%", True),
                    stat_card("Conversion", "3.24%", "0.4%", False),
                    stat_card("Avg Order", "$142", "5.1%", True),
                    width="100%",
                    spacing="4",
                    wrap="wrap",
                ),
                # Chart + activity
                rx.hstack(
                    chart_card(),
                    rx.box(
                        rx.vstack(
                            rx.heading("Live Activity", size="5", color=text()),
                            rx.vstack(
                                rx.hstack(rx.text("🟢", font_size="0.7em"), rx.text("User signed up", color=text(), font_size="0.9em"), rx.spacer(), rx.text("2m", color=muted(), font_size="0.8em"), width="100%"),
                                rx.hstack(rx.text("💳", font_size="0.7em"), rx.text("Payment received", color=text(), font_size="0.9em"), rx.spacer(), rx.text("5m", color=muted(), font_size="0.8em"), width="100%"),
                                rx.hstack(rx.text("📦", font_size="0.7em"), rx.text("Order shipped", color=text(), font_size="0.9em"), rx.spacer(), rx.text("12m", color=muted(), font_size="0.8em"), width="100%"),
                                rx.hstack(rx.text("⭐", font_size="0.7em"), rx.text("New review", color=text(), font_size="0.9em"), rx.spacer(), rx.text("18m", color=muted(), font_size="0.8em"), width="100%"),
                                rx.hstack(rx.text("🔔", font_size="0.7em"), rx.text("Alert triggered", color=text(), font_size="0.9em"), rx.spacer(), rx.text("24m", color=muted(), font_size="0.8em"), width="100%"),
                                spacing="3",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        padding="1.5em",
                        background=card_bg(),
                        border=f"1px solid {border()}",
                        border_radius="12px",
                        flex="1",
                        min_width="260px",
                    ),
                    width="100%",
                    spacing="4",
                    wrap="wrap",
                    align="stretch",
                ),
                # Transactions table
                transactions_card(),
                spacing="4",
                width="100%",
                padding="1em 2em 2em",
            ),
            width="100%",
            min_height="100vh",
            background=bg(),
            spacing="2",
        ),
        width="100%",
        align="start",
        spacing="0",
    )


# ---------- APP ----------
app = rx.App()
app.add_page(index, title="PyMetrics Dashboard")