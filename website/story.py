import reflex as rx


# ---------- PRODUCTS (seed) ----------
PRODUCTS = [
    {"id": 1, "name": "Python Hoodie", "price": 49.99, "category": "Apparel", "emoji": "🧥", "rating": 4.8, "tag": "Hot"},
    {"id": 2, "name": "Django T-Shirt", "price": 24.99, "category": "Apparel", "emoji": "👕", "rating": 4.6, "tag": ""},
    {"id": 3, "name": "Flask Mug", "price": 14.99, "category": "Home", "emoji": "☕", "rating": 4.9, "tag": "New"},
    {"id": 4, "name": "Reflex Sticker Pack", "price": 5.99, "category": "Accessories", "emoji": "🎨", "rating": 4.5, "tag": ""},
    {"id": 5, "name": "Mechanical Keyboard", "price": 129.99, "category": "Tech", "emoji": "⌨️", "rating": 4.7, "tag": "Hot"},
    {"id": 6, "name": "Python Mug", "price": 12.99, "category": "Home", "emoji": "🍵", "rating": 4.4, "tag": ""},
    {"id": 7, "name": "Code Notebook", "price": 18.50, "category": "Accessories", "emoji": "📓", "rating": 4.6, "tag": ""},
    {"id": 8, "name": "Wireless Mouse", "price": 39.99, "category": "Tech", "emoji": "🖱️", "rating": 4.3, "tag": "New"},
    {"id": 9, "name": "Dev Cap", "price": 22.00, "category": "Apparel", "emoji": "🧢", "rating": 4.5, "tag": ""},
    {"id": 10, "name": "Desk Lamp", "price": 34.99, "category": "Home", "emoji": "💡", "rating": 4.7, "tag": ""},
    {"id": 11, "name": "USB Hub", "price": 29.99, "category": "Tech", "emoji": "🔌", "rating": 4.4, "tag": ""},
    {"id": 12, "name": "Water Bottle", "price": 19.99, "category": "Home", "emoji": "🍶", "rating": 4.6, "tag": ""},
]

CATEGORIES = ["All", "Apparel", "Home", "Tech", "Accessories"]


# ---------- STATE ----------
class State(rx.State):
    """Storefront state."""
    cart: list[dict] = []
    category: str = "All"
    search: str = ""
    sort: str = "featured"
    cart_open: bool = False
    dark: bool = True
    checkout_done: bool = False

    # ----- UI events -----
    def toggle_dark(self):
        self.dark = not self.dark

    def toggle_cart(self):
        self.cart_open = not self.cart_open

    def close_cart(self):
        self.cart_open = False

    def set_category(self, c: str):
        self.category = c

    def set_search(self, v: str):
        self.search = v

    def set_sort(self, v: str):
        self.sort = v

    # ----- Cart actions -----
    def add_to_cart(self, product_id: int):
        for item in self.cart:
            if item["id"] == product_id:
                item["qty"] += 1
                return
        product = next(p for p in PRODUCTS if p["id"] == product_id)
        self.cart.append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "emoji": product["emoji"],
            "qty": 1,
        })

    def remove_from_cart(self, product_id: int):
        self.cart = [i for i in self.cart if i["id"] != product_id]

    def inc_qty(self, product_id: int):
        for item in self.cart:
            if item["id"] == product_id:
                item["qty"] += 1
                return

    def dec_qty(self, product_id: int):
        for item in self.cart:
            if item["id"] == product_id:
                if item["qty"] > 1:
                    item["qty"] -= 1
                else:
                    self.remove_from_cart(product_id)
                return

    def checkout(self):
        self.cart = []
        self.cart_open = False
        self.checkout_done = True

    def dismiss_checkout(self):
        self.checkout_done = False

    # ----- Computed -----
    @rx.var
    def cart_count(self) -> int:
        return sum(i["qty"] for i in self.cart)

    @rx.var
    def cart_total(self) -> float:
        return round(sum(i["price"] * i["qty"] for i in self.cart), 2)

    @rx.var
    def cart_total_str(self) -> str:
        return f"${self.cart_total:.2f}"

    @rx.var
    def filtered_products(self) -> list[dict]:
        items = PRODUCTS
        if self.category != "All":
            items = [p for p in items if p["category"] == self.category]
        if self.search:
            q = self.search.lower()
            items = [p for p in items if q in p["name"].lower()]
        if self.sort == "price_low":
            items = sorted(items, key=lambda p: p["price"])
        elif self.sort == "price_high":
            items = sorted(items, key=lambda p: p["price"], reverse=True)
        elif self.sort == "rating":
            items = sorted(items, key=lambda p: p["rating"], reverse=True)
        return items


# ---------- THEME ----------
def bg():      return rx.cond(State.dark, "#0a0a0f", "#f7f7fb")
def card():    return rx.cond(State.dark, "#141420", "white")
def border():  return rx.cond(State.dark, "#26263a", "#e5e5ef")
def text():    return rx.cond(State.dark, "#f0f0ff", "#12121a")
def muted():   return rx.cond(State.dark, "#8888a0", "#6b6b80")
def accent():  return "#7c3aed"


# ---------- COMPONENTS ----------
def navbar():
    return rx.hstack(
        rx.hstack(
            rx.text("🛍️", font_size="1.6em"),
            rx.heading("PyShop", size="6", color=text()),
            spacing="2",
        ),
        rx.hstack(
            rx.input(
                placeholder="🔍 Search products...",
                value=State.search,
                on_change=State.set_search,
                size="2",
                width=rx.breakpoints(initial="150px", md="320px"),
                background=card(),
                border=f"1px solid {border()}",
                color=text(),
            ),
            spacing="3",
            display=rx.breakpoints(initial="none", sm="flex"),
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.cond(State.dark, "☀️", "🌙"),
                on_click=State.toggle_dark,
                variant="soft",
                size="2",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("shopping-cart", size=18),
                    rx.cond(State.cart_count > 0, rx.badge(State.cart_count, color_scheme="purple", variant="solid")),
                    spacing="2",
                    align="center",
                ),
                on_click=State.toggle_cart,
                color_scheme="purple",
                size="2",
            ),
            spacing="2",
        ),
        width="100%",
        padding="1em 2em",
        background=card(),
        border_bottom=f"1px solid {border()}",
        align="center",
        position="sticky",
        top="0",
        z_index="20",
    )


def hero():
    return rx.box(
        rx.vstack(
            rx.badge("🎉 Free shipping over $50", color_scheme="purple", variant="soft", size="2"),
            rx.heading("Developer Essentials", size="9", color="white", text_align="center"),
            rx.text(
                "Gear up with merch, tech, and tools made for Pythonistas.",
                color="#ffffffcc",
                font_size="1.15em",
                text_align="center",
            ),
            rx.button(
                "Shop Now ↓",
                on_click=lambda: rx.scroll_to("products"),
                size="3",
                color_scheme="purple",
                margin_top="1em",
            ),
            spacing="3",
            align="center",
        ),
        background="linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #06b6d4 100%)",
        padding="5em 2em",
        border_radius="0 0 24px 24px",
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
        rx.spacer(),
        rx.select(
            ["featured", "price_low", "price_high", "rating"],
            value=State.sort,
            on_change=State.set_sort,
            size="2",
            width="180px",
        ),
        width="100%",
        wrap="wrap",
        spacing="2",
        align="center",
        padding="1.5em 2em 0.5em",
    )


def product_card(p: dict):
    return rx.box(
        rx.vstack(
            # Image area
            rx.box(
                rx.text(p["emoji"], font_size="4em"),
                background=rx.cond(State.dark, "#1c1c2e", "#f0f0fa"),
                border_radius="12px",
                width="100%",
                height="160px",
                display="flex",
                align_items="center",
                justify_content="center",
                position="relative",
                _hover={"transform": "scale(1.05)"},
                transition="all 0.3s",
            ),
            # Tag
            rx.cond(
                p["tag"] != "",
                rx.badge(
                    p["tag"],
                    color_scheme=rx.cond(p["tag"] == "Hot", "red", "green"),
                    variant="solid",
                    size="1",
                    position="absolute",
                    top="0.6em",
                    left="0.6em",
                ),
            ),
            # Info
            rx.vstack(
                rx.text(p["name"], font_weight="600", color=text(), font_size="1em"),
                rx.hstack(
                    rx.text("⭐", font_size="0.8em"),
                    rx.text(p["rating"], font_size="0.85em", color=muted()),
                    rx.text("•", color=muted(), font_size="0.8em"),
                    rx.text(p["category"], font_size="0.85em", color=muted()),
                    spacing="1",
                ),
                rx.hstack(
                    rx.heading(f"${p['price']}", size="5", color=text()),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=16),
                        on_click=lambda: State.add_to_cart(p["id"]),
                        size="2",
                        color_scheme="purple",
                        border_radius="full",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        padding="1em",
        background=card(),
        border=f"1px solid {border()}",
        border_radius="14px",
        position="relative",
        _hover={"border_color": accent(), "transform": "translateY(-4px)"},
        transition="all 0.2s",
    )


def product_grid():
    return rx.vstack(
        rx.grid(
            rx.foreach(State.filtered_products, product_card),
            columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding="1em 2em 3em",
        spacing="4",
    )


def cart_line(item: dict):
    return rx.hstack(
        rx.box(
            rx.text(item["emoji"], font_size="1.5em"),
            background=rx.cond(State.dark, "#1c1c2e", "#f0f0fa"),
            border_radius="8px",
            padding="0.4em",
            width="46px",
            height="46px",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        rx.vstack(
            rx.text(item["name"], font_weight="500", color=text(), font_size="0.9em"),
            rx.text(f"${item['price']}", color=muted(), font_size="0.85em"),
            spacing="0",
            align="start",
            flex="1",
        ),
        rx.hstack(
            rx.icon_button(rx.icon("minus", size=14), on_click=lambda: State.dec_qty(item["id"]), size="1", variant="soft"),
            rx.text(item["qty"], color=text(), font_weight="600", min_width="20px", text_align="center"),
            rx.icon_button(rx.icon("plus", size=14), on_click=lambda: State.inc_qty(item["id"]), size="1", variant="soft"),
            spacing="1",
            align="center",
        ),
        rx.icon_button(
            rx.icon("trash-2", size=14),
            on_click=lambda: State.remove_from_cart(item["id"]),
            size="1",
            variant="soft",
            color_scheme="red",
        ),
        width="100%",
        spacing="3",
        align="center",
    )


def cart_drawer():
    return rx.hstack(
        # Backdrop
        rx.box(
            on_click=State.close_cart,
            position="fixed",
            top="0", left="0",
            width="100vw", height="100vh",
            background="#00000066",
            z_index="40",
        ),
        # Drawer
        rx.vstack(
            rx.hstack(
                rx.heading("Your Cart", size="5", color=text()),
                rx.spacer(),
                rx.icon_button(rx.icon("x", size=18), on_click=State.close_cart, variant="ghost"),
                width="100%",
                align="center",
            ),
            rx.divider(border_color=border()),
            rx.cond(
                State.cart.length() == 0,
                rx.vstack(
                    rx.text("🛒", font_size="3em"),
                    rx.text("Your cart is empty", color=muted()),
                    rx.text("Add some products to get started!", color=muted(), font_size="0.9em"),
                    spacing="2",
                    align="center",
                    padding="4em 0",
                ),
                rx.vstack(
                    rx.foreach(State.cart, cart_line),
                    spacing="3",
                    width="100%",
                    overflow_y="auto",
                    max_height="50vh",
                ),
            ),
            rx.spacer(),
            rx.cond(
                State.cart.length() > 0,
                rx.vstack(
                    rx.divider(border_color=border()),
                    rx.hstack(
                        rx.text("Subtotal", color=muted()),
                        rx.spacer(),
                        rx.text(State.cart_total_str, color=text(), font_weight="700", font_size="1.1em"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Shipping", color=muted()),
                        rx.spacer(),
                        rx.text(rx.cond(State.cart_total >= 50, "FREE", "$5.00"),
                                color=rx.cond(State.cart_total >= 50, "#3fb950", text()),
                                font_weight="600"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Total", color=text(), font_weight="700", font_size="1.1em"),
                        rx.spacer(),
                        rx.text(
                            rx.cond(State.cart_total >= 50,
                                    State.cart_total_str,
                                    f"${State.cart_total + 5:.2f}"),
                            color=text(), font_weight="700", font_size="1.2em",
                        ),
                        width="100%",
                    ),
                    rx.button(
                        "Checkout →",
                        on_click=State.checkout,
                        color_scheme="purple",
                        size="3",
                        width="100%",
                        margin_top="0.5em",
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            width="380px",
            max_width="90vw",
            height="100vh",
            padding="1.5em",
            background=card(),
            border_left=f"1px solid {border()}",
            position="fixed",
            top="0",
            right="0",
            z_index="50",
            spacing="3",
        ),
        spacing="0",
    )


def checkout_toast():
    return rx.box(
        rx.hstack(
            rx.text("✅", font_size="1.4em"),
            rx.vstack(
                rx.text("Order placed!", font_weight="600", color=text()),
                rx.text("Thanks for shopping with PyShop.", color=muted(), font_size="0.9em"),
                spacing="0",
                align="start",
            ),
            rx.icon_button(rx.icon("x", size=16), on_click=State.dismiss_checkout, variant="ghost", size="1"),
            spacing="3",
            align="center",
        ),
        position="fixed",
        bottom="2em",
        right="2em",
        padding="1em 1.2em",
        background=card(),
        border=f"1px solid {border()}",
        border_radius="12px",
        box_shadow="0 8px 24px rgba(0,0,0,0.2)",
        z_index="60",
    )


def footer():
    return rx.box(
        rx.hstack(
            rx.text("© 2026 PyShop — Built in Python with Reflex", color=muted(), font_size="0.9em"),
            rx.spacer(),
            rx.hstack(
                rx.text("Terms", color=muted(), font_size="0.9em", cursor="pointer"),
                rx.text("Privacy", color=muted(), font_size="0.9em", cursor="pointer"),
                rx.text("Contact", color=muted(), font_size="0.9em", cursor="pointer"),
                spacing="4",
            ),
            width="100%",
        ),
        padding="2em",
        border_top=f"1px solid {border()}",
        background=card(),
        margin_top="2em",
        width="100%",
    )


# ---------- LAYOUT ----------
def index():
    return rx.box(
        navbar(),
        hero(),
        rx.box(
            filter_bar(),
            product_grid(),
            id="products",
        ),
        footer(),
        rx.cond(State.cart_open, cart_drawer()),
        rx.cond(State.checkout_done, checkout_toast()),
        background=bg(),
        min_height="100vh",
        width="100%",
    )


# ---------- APP ----------
app = rx.App()
app.add_page(index, title="PyShop — Developer Store")