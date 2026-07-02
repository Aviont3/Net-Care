#!/usr/bin/env python3
"""
Seed CACFP food library with ~50 common items.

Usage (from backend/ directory):
    python scripts/seed_food_library.py

The script is idempotent — it skips items that already exist by name.
"""
import sys
import os

# Allow running from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.cacfp import CACFPFoodItem


# ---------------------------------------------------------------------------
# Food library data
# (name, component_category, sub_category, serving_description, is_whole_grain_rich)
# ---------------------------------------------------------------------------
FOOD_ITEMS = [
    # ── Milk ─────────────────────────────────────────────────────────────
    ("Whole milk",             "milk", None,           "1 cup (8 fl oz)", False),
    ("Low-fat milk (1%)",      "milk", None,           "1 cup (8 fl oz)", False),
    ("Fat-free milk (skim)",   "milk", None,           "1 cup (8 fl oz)", False),
    ("Lactose-free milk",      "milk", None,           "1 cup (8 fl oz)", False),

    # ── Grains ───────────────────────────────────────────────────────────
    ("Whole wheat bread",      "grains", "whole_grain_rich",  "1 slice (1 oz eq)", True),
    ("Whole grain tortilla",   "grains", "whole_grain_rich",  "1 small (1 oz eq)", True),
    ("Brown rice",             "grains", "whole_grain_rich",  "1/2 cup cooked",    True),
    ("Oatmeal",                "grains", "whole_grain_rich",  "1/2 cup cooked",    True),
    ("Whole grain crackers",   "grains", "whole_grain_rich",  "1 oz",              True),
    ("Whole wheat pasta",      "grains", "whole_grain_rich",  "1/2 cup cooked",    True),
    ("Whole grain cereal",     "grains", "whole_grain_rich",  "3/4 cup dry",       True),
    ("White bread",            "grains", None,               "1 slice (1 oz eq)", False),
    ("White rice",             "grains", None,               "1/2 cup cooked",    False),
    ("White pasta",            "grains", None,               "1/2 cup cooked",    False),
    ("Corn tortilla",          "grains", None,               "1 small (1 oz eq)", False),

    # ── Fruit ────────────────────────────────────────────────────────────
    ("Apple slices",           "fruit", None,  "1/2 cup",          False),
    ("Banana",                 "fruit", None,  "1/2 medium",       False),
    ("Orange segments",        "fruit", None,  "1/2 cup",          False),
    ("Grapes (halved)",        "fruit", None,  "1/2 cup",          False),
    ("Strawberries",           "fruit", None,  "1/2 cup",          False),
    ("Blueberries",            "fruit", None,  "1/2 cup",          False),
    ("Peach slices",           "fruit", None,  "1/2 cup",          False),
    ("Pear slices",            "fruit", None,  "1/2 cup",          False),
    ("Applesauce (no sugar)",  "fruit", None,  "1/2 cup",          False),
    ("100% apple juice",       "fruit", None,  "1/2 cup (4 fl oz)",False),
    ("100% orange juice",      "fruit", None,  "1/2 cup (4 fl oz)",False),
    ("Mixed fruit cup",        "fruit", None,  "1/2 cup",          False),

    # ── Vegetables ───────────────────────────────────────────────────────
    ("Baby carrots",           "vegetable", "red_orange",   "1/2 cup",     False),
    ("Broccoli florets",       "vegetable", "dark_green",   "1/2 cup",     False),
    ("Green beans",            "vegetable", "dark_green",   "1/2 cup",     False),
    ("Peas",                   "vegetable", "starchy",      "1/2 cup",     False),
    ("Corn",                   "vegetable", "starchy",      "1/2 cup",     False),
    ("Sweet potato (mashed)",  "vegetable", "red_orange",   "1/2 cup",     False),
    ("Tomatoes (diced)",       "vegetable", "red_orange",   "1/2 cup",     False),
    ("Cucumber slices",        "vegetable", None,           "1/2 cup",     False),
    ("Spinach",                "vegetable", "dark_green",   "1/2 cup",     False),
    ("Mixed vegetables",       "vegetable", None,           "1/2 cup",     False),
    ("Celery sticks",          "vegetable", None,           "1/2 cup",     False),
    ("Bell pepper strips",     "vegetable", "red_orange",   "1/2 cup",     False),

    # ── Meat / Meat Alternate ────────────────────────────────────────────
    ("Chicken (cooked)",       "meat_alternate", None,          "1.5 oz",       False),
    ("Turkey (cooked)",        "meat_alternate", None,          "1.5 oz",       False),
    ("Ground beef (cooked)",   "meat_alternate", None,          "1.5 oz",       False),
    ("Cheddar cheese",         "meat_alternate", None,          "1.5 oz",       False),
    ("Mozzarella cheese",      "meat_alternate", None,          "1.5 oz",       False),
    ("Scrambled eggs",         "meat_alternate", None,          "1 large egg",  False),
    ("Hard-boiled egg",        "meat_alternate", None,          "1 large egg",  False),
    ("Black beans (cooked)",   "meat_alternate", None,          "1/4 cup",      False),
    ("Pinto beans (cooked)",   "meat_alternate", None,          "1/4 cup",      False),
    ("Yogurt (plain)",         "meat_alternate", None,          "4 oz",         False),
    ("Peanut butter",          "meat_alternate", None,          "2 tbsp",       False),
    ("Tofu (firm)",            "meat_alternate", None,          "2.2 oz",       False),
    ("Tuna (canned in water)", "meat_alternate", None,          "1.5 oz",       False),
]


def seed() -> None:
    db = SessionLocal()
    try:
        # Build set of existing names for idempotency check
        existing = {row.name for row in db.query(CACFPFoodItem.name).all()}

        added = 0
        skipped = 0
        for name, category, sub_cat, serving, wgr in FOOD_ITEMS:
            if name in existing:
                skipped += 1
                continue
            item = CACFPFoodItem(
                name=name,
                component_category=category,
                sub_category=sub_cat,
                serving_description=serving,
                is_whole_grain_rich=wgr,
                is_active=True,
            )
            db.add(item)
            added += 1

        db.commit()
        print(f"✅  Seeded {added} food item(s). Skipped {skipped} already-existing item(s).")
    except Exception as exc:
        db.rollback()
        print(f"❌  Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
