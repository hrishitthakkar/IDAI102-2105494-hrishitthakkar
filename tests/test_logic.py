"""Unit tests for ShopImpact's logic. Run with:  pytest -q"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logic  # noqa: E402

TODAY = date(2026, 11, 15)
KEY = "2026-11"


def test_impact_is_price_times_multiplier():
    assert logic.calculate_impact("Leather shoes", 1000) == 9.0


def test_ethical_brand_gets_15_percent_off():
    regular = logic.calculate_impact("Fast-fashion clothing", 1000, "Zara")
    ethical = logic.calculate_impact("Fast-fashion clothing", 1000, "Doodlage")
    assert ethical == round(regular * 0.85, 2)


def test_brand_matching_ignores_case_and_spaces():
    assert logic.is_ethical_brand("  NO NASTIES ")
    assert not logic.is_ethical_brand("")


def test_zero_or_unknown_returns_zero():
    assert logic.calculate_impact("Leather shoes", 0) == 0
    assert logic.calculate_impact("Spaceship", 500) == 0


def test_impact_levels():
    assert logic.impact_level(2) == "Low"
    assert logic.impact_level(10) == "Medium"
    assert logic.impact_level(45) == "High"


def test_monthly_summary_only_counts_that_month():
    purchases = [
        logic.make_purchase("Books (new)", 500, "", date(2026, 11, 2)),
        logic.make_purchase("Books (new)", 500, "", date(2026, 10, 2)),
    ]
    s = logic.monthly_summary(purchases, KEY)
    assert s["count"] == 1 and s["spend"] == 500 and s["co2"] == 1.0


def test_eco_saver_needs_three_purchases_and_half_green():
    two_green = [logic.make_purchase("Second-hand clothing", 500, "", TODAY)] * 2
    assert "Eco Saver of the Month" not in logic.earned_badges(two_green, KEY, 80)
    mix = two_green + [logic.make_purchase("Leather shoes", 500, "", TODAY)]
    assert "Eco Saver of the Month" in logic.earned_badges(mix, KEY, 80)


def test_low_impact_shopper_respects_goal():
    buys = [logic.make_purchase("Fuel / car trips", 2000, "", TODAY)] * 3   # 138 kg
    assert "Low Impact Shopper" not in logic.earned_badges(buys, KEY, 80)
    assert "Low Impact Shopper" in logic.earned_badges(buys, KEY, 200)


def test_goal_status_colours():
    assert logic.goal_status(50, 100) == "good"
    assert logic.goal_status(90, 100) == "close"
    assert logic.goal_status(120, 100) == "over"


def test_co2_saved_by_swapping():
    p = [logic.make_purchase("Second-hand clothing", 1000, "", TODAY)]
    # fast fashion would be 6.5 kg, second-hand is 0.8 kg -> 5.7 kg saved
    assert logic.co2_saved_vs_conventional(p) == 5.7


def test_sample_data_has_15_purchases():
    assert len(logic.sample_purchases(TODAY)) == 15
