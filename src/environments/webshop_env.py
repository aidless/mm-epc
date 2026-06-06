"""Mini WebShop Environment — simple simulated e-commerce agent task."""

import random

class MiniWebShopEnv:
    """Simulated WebShop environment. No Docker needed."""

    def __init__(self):
        self.state = "start"
        self.current_page_content = "start page with search bar"
        self.done = False
        self.reward = 0.0
        self.task = {"query": "laptop"}

        self.items = {
            "laptop": {"name": "Laptop Pro", "price": 999, "desc": "16GB RAM, 512GB SSD"},
            "phone": {"name": "Phone X", "price": 699, "desc": "6.1 inch, 128GB"},
            "book": {"name": "Python Book", "price": 49, "desc": "Learn Python in 24 hours"},
        }

    def reset(self):
        self.state = "search"
        self.current_page_content = "List View: [Item_A: Laptop Pro $999] [Item_B: Phone X $699] [Item_C: Python Book $49]"
        self.done = False
        self.reward = 0.0
        item = random.choice(list(self.items.keys()))
        self.task = {"query": item}
        return self.current_page_content

    def step(self, action):
        self.reward = 0.0

        if action.startswith("search"):
            self.state = "list"
            query = action.split("[")[1].split("]")[0] if "[" in action else "laptop"
            self.current_page_content = f"List View: [Item_A: Laptop Pro $999] [Item_B: Phone X $699] [Item_C: Python Book $49]"
            self.reward = 0.1

        elif action.startswith("click"):
            self.state = "detail"
            self.current_page_content = "Detail View: Product description, price, and buy button"
            self.reward = 0.2

        elif action == "buy":
            self.state = "cart"
            self.current_page_content = "Cart View: 1 item in cart. Proceed to checkout?"
            self.reward = 0.5

        elif action == "submit":
            self.state = "done"
            self.current_page_content = "Order confirmed! Thank you."
            self.done = True
            self.reward = 1.0

        elif action == "noop":
            self.reward = -0.1

        return self.current_page_content, self.reward, self.done, {"state": self.state}
