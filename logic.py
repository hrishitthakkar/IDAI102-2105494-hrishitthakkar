"""
logic.py — the "engine" of ShopImpact.

Everything here is plain Python (lists, dictionaries, functions, datetime),
with no Streamlit code, so it can be unit-tested on its own (see tests/).

How the CO₂ estimate works
--------------------------
Each product type has a multiplier: estimated kg of CO₂e per ₹1 spent.
    impact (kg CO₂e) = price (₹) × multiplier
If the brand is on our curated ethical-brands list, the estimate is reduced by
ETHICAL_BRAND_DISCOUNT, because those brands use recycled, upcycled or
low-waste production.

The multipliers are simplified, illustrative values inspired by spend-based
emission factors. They are meant to show relative impact (leather shoes vs
second-hand clothes), not exact lab measurements.
"""

from datetime import date, datetime, timedelta
import random

# ---------------------------------------------------------------------------
# 1. CURATED DATA (dictionaries + lists)
# ---------------------------------------------------------------------------

# product type -> details
# multiplier : kg CO₂e per ₹ spent
# eco        : True if this is the greener choice in its group
# alternatives: greener options we suggest before the user buys
PRODUCTS = {
    "Fast-fashion clothing": {
        "emoji": "👕", "multiplier": 0.0065, "eco": False,
        "alternatives": ["Second-hand / thrift clothing", "Organic cotton (No Nasties)",
                         "Upcycled wear (Doodlage)", "Rent or swap outfits for events"],
    },
    "Second-hand clothing": {
        "emoji": "🧥", "multiplier": 0.0008, "eco": True,
        "alternatives": ["You're already choosing well — try clothes swaps with friends"],
    },
    "Leather shoes": {
        "emoji": "👞", "multiplier": 0.0090, "eco": False,
        "alternatives": ["Recycled-material sneakers", "Canvas shoes",
                         "Resoling your current pair", "Second-hand shoes"],
    },
    "Canvas / recycled shoes": {
        "emoji": "👟", "multiplier": 0.0030, "eco": True,
        "alternatives": ["Look for brands with take-back programmes"],
    },
    "New electronics": {
        "emoji": "📱", "multiplier": 0.0015, "eco": False,
        "alternatives": ["Refurbished devices (Cashify, Back Market)",
                         "Repairing your current device", "Modular phones (Fairphone)"],
    },
    "Refurbished electronics": {
        "emoji": "🔋", "multiplier": 0.0004, "eco": True,
        "alternatives": ["Recycle your old device properly when you upgrade"],
    },
    "Meat & poultry": {
        "emoji": "🍗", "multiplier": 0.0100, "eco": False,
        "alternatives": ["Paneer, tofu or soya chunks", "Lentils and chickpeas",
                         "One or two meat-free days a week"],
    },
    "Plant-based groceries": {
        "emoji": "🥦", "multiplier": 0.0015, "eco": True,
        "alternatives": ["Buy seasonal and local from your sabzi market"],
    },
    "Dairy products": {
        "emoji": "🧀", "multiplier": 0.0060, "eco": False,
        "alternatives": ["Smaller portions or local dairy", "Oat or soy milk sometimes"],
    },
    "Plastic household goods": {
        "emoji": "🧴", "multiplier": 0.0045, "eco": False,
        "alternatives": ["Bamboo or steel versions", "Refill stations",
                         "Zero-waste stores (Bare Necessities)"],
    },
    "Bamboo / reusable goods": {
        "emoji": "🎋", "multiplier": 0.0010, "eco": True,
        "alternatives": ["Make it last — reuse is the real win"],
    },
    "Beauty & personal care": {
        "emoji": "💄", "multiplier": 0.0035, "eco": False,
        "alternatives": ["Refillable packaging", "Shampoo bars", "Fewer, multi-use products"],
    },
    "Books (new)": {
        "emoji": "📚", "multiplier": 0.0020, "eco": False,
        "alternatives": ["Second-hand books", "Library or e-books", "Book swaps"],
    },
    "Fuel / car trips": {
        "emoji": "⛽", "multiplier": 0.0230, "eco": False,
        "alternatives": ["Metro or BRTS", "Carpooling", "Cycling for short trips"],
    },
    "Public transport / cycling": {
        "emoji": "🚲", "multiplier": 0.0005, "eco": True,
        "alternatives": ["Keep it up — you're the lowest-impact way to travel"],
    },
}

# Brands we treat as ethical / low-impact (lower-case for easy matching).
# Curated, illustrative list for this project.
ETHICAL_BRANDS = [
    "no nasties", "doodlage", "bare necessities", "brown living", "patagonia",
    "fairphone", "back market", "cashify", "ecoright", "bombay shirt company",
    "mamaearth",
]

ETHICAL_BRAND_DISCOUNT = 0.15   # ethical brands get a 15% lower estimate

ECO_TIPS = [
    "Bamboo grows so fast it can be harvested in 3–5 years with no replanting.",
    "Washing clothes in cold water cuts the energy of each wash by about 90%.",
    "Keeping a phone one extra year saves a big share of its lifetime footprint.",
    "Buying second-hand clothes skips almost all the emissions of making new ones.",
    "Carrying your own cloth bag avoids hundreds of plastic bags a year.",
    "Seasonal, local vegetables usually travel far less than imported ones.",
    "Repairing shoes or electronics is almost always greener than replacing them.",
    "A single cotton T-shirt can take around 2,700 litres of water to make.",
]

QUOTES = [
    ("The greatest threat to our planet is the belief that someone else will save it.", "Robert Swan"),
    ("We don't need a handful of people doing zero waste perfectly. We need millions doing it imperfectly.", "Anne-Marie Bonneau"),
    ("Buy less, choose well, make it last.", "Vivienne Westwood"),
    ("What you do makes a difference, and you have to decide what kind of difference you want to make.", "Jane Goodall"),
    ("The Earth is what we all have in common.", "Wendell Berry"),
]

# Handy real-world comparisons so numbers feel meaningful
KG_PER_KM_CAR = 0.17        # average petrol car, kg CO₂ per km
KG_PER_TREE_DAY = 0.06      # one tree absorbs roughly 21 kg CO₂ a year


# ---------------------------------------------------------------------------
# 2. CALCULATIONS
# ---------------------------------------------------------------------------

def is_ethical_brand(brand):
    """True if any curated ethical brand name appears in what the user typed."""
    text = brand.strip().lower()
    if not text:
        return False
    return any(ethical in text for ethical in ETHICAL_BRANDS)


def calculate_impact(product_type, price, brand=""):
    """Return estimated kg CO₂e for one purchase (price × multiplier)."""
    if product_type not in PRODUCTS or price <= 0:
        return 0.0
    impact = price * PRODUCTS[product_type]["multiplier"]
    if is_ethical_brand(brand):
        impact *= (1 - ETHICAL_BRAND_DISCOUNT)
    return round(impact, 2)


def impact_level(impact_kg):
    """Label a single purchase as Low / Medium / High impact."""
    if impact_kg < 5:
        return "Low"
    if impact_kg < 20:
        return "Medium"
    return "High"


def make_purchase(product_type, price, brand, purchase_date):
    """Build one purchase record (a dictionary) ready to store in the list."""
    impact = calculate_impact(product_type, price, brand)
    return {
        "date": purchase_date,                       # datetime.date
        "product_type": product_type,
        "brand": brand.strip() or "Unbranded",
        "price": float(price),
        "co2_kg": impact,
        "eco_choice": PRODUCTS[product_type]["eco"],
        "ethical_brand": is_ethical_brand(brand),
    }


def is_green_purchase(purchase):
    """A purchase counts as 'green' if it's an eco product OR an ethical brand."""
    return purchase["eco_choice"] or purchase["ethical_brand"]


def month_key(d):
    """'2026-11' style key for grouping purchases by month."""
    return d.strftime("%Y-%m")


def purchases_in_month(purchases, key):
    return [p for p in purchases if month_key(p["date"]) == key]


def monthly_summary(purchases, key):
    """Totals for one month — used by the dashboard."""
    month = purchases_in_month(purchases, key)
    total_spend = sum(p["price"] for p in month)
    total_co2 = sum(p["co2_kg"] for p in month)
    green = sum(1 for p in month if is_green_purchase(p))
    return {
        "count": len(month),
        "spend": round(total_spend, 2),
        "co2": round(total_co2, 2),
        "green_count": green,
        "green_share": (green / len(month)) if month else 0.0,
    }


def co2_saved_vs_conventional(purchases):
    """
    How much CO₂ the user avoided by choosing eco options, compared with
    buying the 'regular' version at the same price.
    """
    swaps = {
        "Second-hand clothing": "Fast-fashion clothing",
        "Canvas / recycled shoes": "Leather shoes",
        "Refurbished electronics": "New electronics",
        "Plant-based groceries": "Meat & poultry",
        "Bamboo / reusable goods": "Plastic household goods",
        "Public transport / cycling": "Fuel / car trips",
    }
    saved = 0.0
    for p in purchases:
        regular = swaps.get(p["product_type"])
        if regular:
            saved += p["price"] * PRODUCTS[regular]["multiplier"] - p["co2_kg"]
    return round(max(saved, 0), 2)


def everyday_equivalents(co2_kg):
    """Turn kg CO₂ into km driven and tree-days to make it relatable."""
    return {
        "km_driven": round(co2_kg / KG_PER_KM_CAR, 1),
        "tree_days": round(co2_kg / KG_PER_TREE_DAY),
    }


# ---------------------------------------------------------------------------
# 3. BADGES (rule-based)
# ---------------------------------------------------------------------------

BADGES = {
    "First Step": ("🌱", "Logged your first purchase"),
    "Eco Saver of the Month": ("♻️", "Half or more of this month's purchases were green (min. 3)"),
    "Low Impact Shopper": ("🍃", "Stayed under your monthly CO₂ goal (min. 3 purchases)"),
    "Ethical Supporter": ("🤝", "Bought from 2+ ethical brands this month"),
    "Second Life Hero": ("🔁", "3+ second-hand or refurbished buys overall"),
    "Mindful Tracker": ("📊", "Logged 10+ purchases"),
}


def earned_badges(purchases, key, monthly_goal):
    """Return the list of badge names earned, using simple rules."""
    badges = []
    month = monthly_summary(purchases, key)
    month_items = purchases_in_month(purchases, key)

    if len(purchases) >= 1:
        badges.append("First Step")
    if month["count"] >= 3 and month["green_share"] >= 0.5:
        badges.append("Eco Saver of the Month")
    if month["count"] >= 3 and month["co2"] <= monthly_goal:
        badges.append("Low Impact Shopper")
    if sum(1 for p in month_items if p["ethical_brand"]) >= 2:
        badges.append("Ethical Supporter")
    second_life = ("Second-hand clothing", "Refurbished electronics")
    if sum(1 for p in purchases if p["product_type"] in second_life) >= 3:
        badges.append("Second Life Hero")
    if len(purchases) >= 10:
        badges.append("Mindful Tracker")
    return badges


def goal_status(co2, goal):
    """'good' / 'close' / 'over' — drives the footprint colour."""
    if goal <= 0:
        return "over"
    ratio = co2 / goal
    if ratio <= 0.75:
        return "good"
    if ratio <= 1.0:
        return "close"
    return "over"


# ---------------------------------------------------------------------------
# 4. MESSAGES & EXTRAS
# ---------------------------------------------------------------------------

def feedback_message(purchase):
    """Friendly, guilt-free message shown right after logging."""
    level = impact_level(purchase["co2_kg"])
    if is_green_purchase(purchase):
        return "Nice choice! That one's kinder to the planet. 🌿"
    if level == "High":
        return "That's a heavier one. Peek at the greener options next time."
    if level == "Medium":
        return "Logged. A greener swap could cut this down a lot."
    return "Logged. Small footprint — good stuff."


def random_tip():
    return random.choice(ECO_TIPS)


def random_quote():
    return random.choice(QUOTES)


def sample_purchases(today=None):
    """15 realistic test purchases across 2 months (for demo + testing)."""
    today = today or date.today()
    this_m = today.replace(day=1)
    # previous month, safely
    prev_m = (this_m - timedelta(days=1)).replace(day=1)

    def d(base, day):
        day = min(day, 28)
        return base.replace(day=day)

    rows = [
        ("Fast-fashion clothing", 1499, "Zara", d(prev_m, 3)),
        ("Leather shoes", 4999, "Woodland", d(prev_m, 7)),
        ("Meat & poultry", 650, "Licious", d(prev_m, 10)),
        ("Fuel / car trips", 2500, "Indian Oil", d(prev_m, 14)),
        ("New electronics", 18999, "Samsung", d(prev_m, 18)),
        ("Plant-based groceries", 900, "Local market", d(prev_m, 21)),
        ("Plastic household goods", 799, "Milton", d(prev_m, 25)),
        ("Second-hand clothing", 600, "Thrift store", d(this_m, 2)),
        ("Refurbished electronics", 12499, "Cashify", d(this_m, 4)),
        ("Plant-based groceries", 1200, "Local market", d(this_m, 6)),
        ("Bamboo / reusable goods", 349, "Local craft store", d(this_m, 8)),
        ("Public transport / cycling", 500, "Ahmedabad Metro", d(this_m, 9)),
        ("Fast-fashion clothing", 999, "H&M", d(this_m, 11)),
        ("Second-hand clothing", 450, "Thrift store", d(this_m, 12)),
        ("Books (new)", 499, "Crossword", d(this_m, 13)),
    ]
    return [make_purchase(t, p, b, dt) for t, p, b, dt in rows]


def to_date(value):
    """Convert a CSV string / datetime / date back into a date."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
