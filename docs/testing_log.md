# Stage 4 — Testing log

## 1. Test purchases (15 items: cheap, expensive, eco, non-eco)

These are the items in the **Load 15 sample purchases** button. Items 1–7 fall in the previous month, 8–15 in the current month. Expected CO₂ = price × multiplier (×0.85 for ethical brands).

| # | Product type | Brand | Price | Multiplier | Expected CO₂ (kg) | Level | Green? |
|---|---|---|---|---|---|---|---|
| 1 | Fast-fashion clothing | Zara | ₹1,499 | 0.0065 | 9.74 | Medium | No |
| 2 | Leather shoes | Woodland | ₹4,999 | 0.009 | 44.99 | High | No |
| 3 | Meat & poultry | Licious | ₹650 | 0.01 | 6.50 | Medium | No |
| 4 | Fuel / car trips | Indian Oil | ₹2,500 | 0.023 | 57.50 | High | No |
| 5 | New electronics | Samsung | ₹18,999 | 0.0015 | 28.50 | High | No |
| 6 | Plant-based groceries | Local market | ₹900 | 0.0015 | 1.35 | Low | Yes |
| 7 | Plastic household goods | Milton | ₹799 | 0.0045 | 3.60 | Low | No |
| 8 | Second-hand clothing | Thrift store | ₹600 | 0.0008 | 0.48 | Low | Yes |
| 9 | Refurbished electronics | Cashify (ethical) | ₹12,499 | 0.0004 | 4.25 | Low | Yes |
| 10 | Plant-based groceries | Local market | ₹1,200 | 0.0015 | 1.80 | Low | Yes |
| 11 | Bamboo / reusable goods | Local craft store | ₹349 | 0.001 | 0.35 | Low | Yes |
| 12 | Public transport / cycling | Ahmedabad Metro | ₹500 | 0.0005 | 0.25 | Low | Yes |
| 13 | Fast-fashion clothing | H&M | ₹999 | 0.0065 | 6.49 | Medium | No |
| 14 | Second-hand clothing | Thrift store | ₹450 | 0.0008 | 0.36 | Low | Yes |
| 15 | Books (new) | Crossword | ₹499 | 0.002 | 1.00 | Low | No |

**Expected monthly totals (goal = 80 kg)**

| Month | Purchases | Spend | CO₂ | Green share | Badges expected |
|---|---|---|---|---|---|
| Previous | 7 | ₹30,346 | 152.2 kg (over goal → red footprint) | 14% | First Step, Second Life Hero, Mindful Tracker |
| Current | 8 | ₹17,096 | 15.0 kg (under goal → green footprint) | 75% | + Eco Saver of the Month, Low Impact Shopper |

Ethical Supporter should stay **locked** (only one ethical brand this month). CO₂ avoided by green swaps: ≈ 50.8 kg.

## 2. Functional checks

| Check | Expected | Result |
|---|---|---|
| Change price/brand/type | CO₂ tag updates instantly, before logging | ✅ Pass |
| Type an ethical brand (e.g. "Doodlage") | Note appears, estimate drops 15% | ✅ Pass |
| Log a purchase | Dashboard totals update in the same click | ✅ Pass |
| Log a green item | Turtle draws a leaf (Auto mode) | ✅ Pass |
| Earn a new badge | Turtle draws a medal + "New badge" caption | ✅ Pass |
| Switch month | Metrics, charts and badges change to that month | ✅ Pass |
| Move CO₂ goal slider | Progress bar, footprint colour and Low Impact badge react | ✅ Pass |
| Price = 0 | Log button disabled | ✅ Pass |
| Undo last / Clear all | Removes purchases, dashboard resets | ✅ Pass |
| Download CSV → upload it again | Same purchases come back | ✅ Pass |
| High-contrast mode | Colours switch to black/white/dark green | ✅ Pass |
| Unit tests (`pytest -q`) | 11 tests pass | ✅ Pass |

*(Re-run these on the live Streamlit Cloud link and add a screenshot or two as evidence.)*

## 3. Fixes made during development

| Issue found | Fix |
|---|---|
| `import turtle` crashes on Streamlit Cloud (no screen/Tkinter) | Built `SVGTurtle` with the same turtle commands, rendered as SVG; kept `turtle_local.py` for the real module |
| Footprint drawing looked like a blob, toes floating | Rebuilt the sole from five arcs into an upright oval; moved toes closer |
| "Undo" and "Clear" buttons got cut off in the sidebar | Stacked them full-width with clearer labels |
| Metric numbers looked too small for the brief's "large fonts" | Increased metric font size via CSS |
| Sample data earned every badge, so locked badges were never shown | Adjusted one sample brand so a locked badge is visible in the demo |

## 4. User feedback (fill in after testing with friends/family)

| Tester | What they tried | What confused them | What I changed |
|---|---|---|---|
| 1. | | | |
| 2. | | | |
| 3. | | | |

Questions to ask testers: Was it clear what to do first? Did the CO₂ number make sense? Did anything feel preachy? Would you use it before a real purchase?
