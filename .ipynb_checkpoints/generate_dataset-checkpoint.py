"""
FleetSense Gujarat — Dataset Generator
Generates 4 realistic CSV files based on actual Gujarat bus routes,
ticket prices, festivals, and fuel economics.

Output files:
  1. routes.csv          (~12 rows)
  2. bus_inventory.csv   (~59 rows)
  3. festivals.csv       (~30 rows)
  4. daily_bookings.csv  (~43,000 rows)
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta

# Reproducibility
np.random.seed(42)

# ─────────────────────────────────────────────
# CONSTANTS (real-world values from research)
# ─────────────────────────────────────────────
DIESEL_RATE_PER_LITRE = 95          # ₹/litre (as given)
NON_AC_MILEAGE_KMPL   = 4.5         # km/litre average for non-AC
AC_MILEAGE_KMPL       = 2.65        # km/litre average for AC Volvo
TANK_CAPACITY_LITRES  = 350         # litres (mid-range of 300–400)

# ─────────────────────────────────────────────
# 1. ROUTES TABLE
# ─────────────────────────────────────────────
# Sources: Google Maps + MakeMyTrip + AbhiBus research
routes_raw = [
    # (route_id, name, origin, destination, distance_km, tier, base_buses/day, base_non_ac_price)
    (1,  'AMD→Surat',      'Ahmedabad', 'Surat',       265, 'Tier1', 8,  250),
    (2,  'AMD→Rajkot',     'Ahmedabad', 'Rajkot',      215, 'Tier1', 7,  200),
    (3,  'AMD→Vadodara',   'Ahmedabad', 'Vadodara',    110, 'Tier1', 10, 120),
    (4,  'AMD→Bhuj',       'Ahmedabad', 'Bhuj',        340, 'Tier2', 5,  450),
    (5,  'AMD→Jamnagar',   'Ahmedabad', 'Jamnagar',    318, 'Tier2', 4,  420),
    (6,  'AMD→Junagadh',   'Ahmedabad', 'Junagadh',    320, 'Tier2', 4,  400),
    (7,  'AMD→Dwarka',     'Ahmedabad', 'Dwarka',      450, 'Tier2', 3,  550),
    (8,  'AMD→Somnath',    'Ahmedabad', 'Somnath',     400, 'Tier2', 3,  500),
    (9,  'AMD→Porbandar',  'Ahmedabad', 'Porbandar',   390, 'Tier3', 3,  480),
    (10, 'AMD→Gandhidham', 'Ahmedabad', 'Gandhidham',  360, 'Tier3', 3,  470),
    (11, 'Rajkot→Surat',   'Rajkot',   'Surat',       360, 'Tier2', 4,  450),
    (12, 'Surat→Vadodara', 'Surat',    'Vadodara',    155, 'Tier2', 5,  180),
]

routes_df = pd.DataFrame(routes_raw, columns=[
    'route_id','route_name','origin','destination',
    'distance_km','route_tier','base_buses_per_day','base_nonac_price_inr'
])

# Price multipliers per bus type (relative to Non-AC Seater base price)
BUS_TYPE_PROPS = {
    #  bus_type            capacity  fuel_kmpl  price_mult  is_ac
    'Non-AC Seater':     (45,       4.5,        1.00,       False),
    'AC Seater Volvo':   (41,       2.65,       2.50,       True),
    'Non-AC Sleeper':    (32,       4.20,       1.50,       False),
    'AC Sleeper':        (32,       2.30,       3.00,       True),
}

# ─────────────────────────────────────────────
# 2. BUS INVENTORY TABLE
# ─────────────────────────────────────────────
# Realistic bus type mix per route
# (bus_type, count)  — designed to match observed operator fleets
route_bus_mix = {
    1:  [('Non-AC Seater',3),('AC Seater Volvo',3),('Non-AC Sleeper',1),('AC Sleeper',1)],  # AMD-Surat: busiest
    2:  [('Non-AC Seater',3),('AC Seater Volvo',2),('AC Sleeper',2)],                        # AMD-Rajkot
    3:  [('Non-AC Seater',5),('AC Seater Volvo',3),('Non-AC Sleeper',2)],                    # AMD-Vadodara: short, high freq
    4:  [('Non-AC Seater',2),('AC Sleeper',2),('Non-AC Sleeper',1)],                         # AMD-Bhuj: long, overnight
    5:  [('Non-AC Seater',2),('AC Seater Volvo',1),('AC Sleeper',1)],                        # AMD-Jamnagar
    6:  [('Non-AC Seater',2),('Non-AC Sleeper',1),('AC Seater Volvo',1)],                    # AMD-Junagadh
    7:  [('Non-AC Seater',1),('AC Sleeper',1),('Non-AC Sleeper',1)],                         # AMD-Dwarka: pilgrimage
    8:  [('Non-AC Seater',1),('AC Sleeper',1),('Non-AC Sleeper',1)],                         # AMD-Somnath: pilgrimage
    9:  [('Non-AC Seater',2),('Non-AC Sleeper',1)],                                          # AMD-Porbandar
    10: [('Non-AC Seater',2),('AC Sleeper',1)],                                              # AMD-Gandhidham
    11: [('Non-AC Seater',2),('AC Seater Volvo',1),('AC Sleeper',1)],                        # Rajkot-Surat
    12: [('Non-AC Seater',3),('AC Seater Volvo',1),('Non-AC Sleeper',1)],                    # Surat-Vadodara
}

inventory = []
bus_id_counter = 1
for route_id, mix in route_bus_mix.items():
    for bus_type, count in mix:
        cap, kmpl, pmult, is_ac = BUS_TYPE_PROPS[bus_type]
        for _ in range(count):
            inventory.append({
                'bus_id':                 f'BUS{bus_id_counter:03d}',
                'route_id':               route_id,
                'bus_type':               bus_type,
                'capacity_seats':         cap,
                'is_ac':                  int(is_ac),
                'fuel_efficiency_kmpl':   kmpl,
                'price_multiplier':       pmult,
                'tank_capacity_litres':   TANK_CAPACITY_LITRES,
            })
            bus_id_counter += 1

bus_inventory_df = pd.DataFrame(inventory)
print(f"Total buses in fleet: {len(bus_inventory_df)}")

# ─────────────────────────────────────────────
# 3. FESTIVALS TABLE
# ─────────────────────────────────────────────
# 15+ actual Gujarat festivals for 2023 & 2024
# demand_multiplier: how much above normal the demand goes (1.9 = 90% extra)
# routes_affected: 'ALL' or specific route ids (for regional festivals)

festivals_raw = [
    # 2023
    ('Uttarayan (Kite Festival)', '2023-01-14','2023-01-15', 'Very High', 1.85, 'ALL'),
    ('Mahashivratri',             '2023-02-18','2023-02-18', 'Medium',    1.35, 'ALL'),
    ('Holi',                      '2023-03-08','2023-03-09', 'High',      1.60, 'ALL'),
    ('Ram Navami',                '2023-03-30','2023-03-30', 'Medium',    1.25, 'ALL'),
    ('Ambedkar Jayanti',          '2023-04-14','2023-04-14', 'Low',       1.15, 'ALL'),
    ('Eid al-Fitr',               '2023-04-21','2023-04-23', 'High',      1.60, 'ALL'),
    ('Gujarat Sthapana Divas',    '2023-05-01','2023-05-01', 'Low',       1.12, 'ALL'),
    ('Summer Vacation Peak',      '2023-05-15','2023-06-15', 'High',      1.50, 'ALL'),
    ('Rath Yatra',                '2023-06-20','2023-06-20', 'High',      1.55, 'ALL'),
    ('Independence Day',          '2023-08-15','2023-08-15', 'Medium',    1.30, 'ALL'),
    ('Janmashtami',               '2023-09-06','2023-09-07', 'High',      1.55, 'ALL'),
    ('Ganesh Chaturthi',          '2023-09-19','2023-09-28', 'Medium',    1.30, 'ALL'),
    ('Navratri',                  '2023-10-15','2023-10-24', 'Very High', 1.92, 'ALL'),
    ('Diwali + Gujarati New Year','2023-11-10','2023-11-15', 'Very High', 1.95, 'ALL'),
    ('Rann Utsav Season',         '2023-11-01','2024-02-29', 'High',      1.50, '4,10'),  # Bhuj & Gandhidham only
    ('Christmas',                 '2023-12-25','2023-12-26', 'Low',       1.18, 'ALL'),
    ('New Year Eve',              '2023-12-31','2024-01-01', 'High',      1.65, 'ALL'),
    # 2024
    ('Uttarayan (Kite Festival)', '2024-01-14','2024-01-15', 'Very High', 1.85, 'ALL'),
    ('Mahashivratri',             '2024-03-08','2024-03-08', 'Medium',    1.35, 'ALL'),
    ('Holi',                      '2024-03-25','2024-03-26', 'High',      1.60, 'ALL'),
    ('Ambedkar Jayanti',          '2024-04-14','2024-04-14', 'Low',       1.15, 'ALL'),
    ('Ram Navami',                '2024-04-17','2024-04-17', 'Medium',    1.25, 'ALL'),
    ('Eid al-Fitr',               '2024-04-10','2024-04-11', 'High',      1.60, 'ALL'),
    ('Gujarat Sthapana Divas',    '2024-05-01','2024-05-01', 'Low',       1.12, 'ALL'),
    ('Summer Vacation Peak',      '2024-05-15','2024-06-15', 'High',      1.50, 'ALL'),
    ('Rath Yatra',                '2024-07-07','2024-07-07', 'High',      1.55, 'ALL'),
    ('Independence Day',          '2024-08-15','2024-08-15', 'Medium',    1.30, 'ALL'),
    ('Janmashtami',               '2024-08-26','2024-08-26', 'High',      1.55, 'ALL'),
    ('Ganesh Chaturthi',          '2024-09-07','2024-09-17', 'Medium',    1.30, 'ALL'),
    ('Navratri',                  '2024-10-03','2024-10-12', 'Very High', 1.92, 'ALL'),
    ('Diwali + Gujarati New Year','2024-11-01','2024-11-05', 'Very High', 1.95, 'ALL'),
    ('Christmas',                 '2024-12-25','2024-12-26', 'Low',       1.18, 'ALL'),
    ('New Year Eve',              '2024-12-31','2024-12-31', 'High',      1.65, 'ALL'),
]

festivals_df = pd.DataFrame(festivals_raw, columns=[
    'festival_name','start_date','end_date',
    'impact_level','demand_multiplier','routes_affected'
])

# ─────────────────────────────────────────────
# BUILD LOOKUP: date → {route_id → (festival_name, multiplier, impact)}
# ─────────────────────────────────────────────
festival_lookup = {}   # key: (date, route_id) → (name, mult, impact)

for _, row in festivals_df.iterrows():
    start = pd.to_datetime(row['start_date']).date()
    end   = pd.to_datetime(row['end_date']).date()
    affected = row['routes_affected']
    if affected == 'ALL':
        affected_ids = set(range(1, 13))
    else:
        affected_ids = set(int(x.strip()) for x in affected.split(','))

    d = start
    while d <= end:
        for rid in affected_ids:
            # Keep higher-multiplier festival if two overlap same day
            key = (d, rid)
            if key not in festival_lookup or festival_lookup[key][1] < row['demand_multiplier']:
                festival_lookup[key] = (row['festival_name'], row['demand_multiplier'], row['impact_level'])
        d += timedelta(days=1)

# ─────────────────────────────────────────────
# SEASON MAP  month → (season_name, multiplier)
# ─────────────────────────────────────────────
season_map = {
    1:  ('Winter',  1.10),
    2:  ('Winter',  1.05),
    3:  ('Spring',  1.08),
    4:  ('Spring',  1.05),
    5:  ('Summer',  1.20),
    6:  ('Summer',  1.25),   # school summer break
    7:  ('Monsoon', 0.88),
    8:  ('Monsoon', 0.90),
    9:  ('Monsoon', 0.93),
    10: ('Festive', 1.30),
    11: ('Festive', 1.25),
    12: ('Winter',  1.15),
}

# Day-of-week multiplier (0=Mon … 6=Sun)
DOW_MULT = {0: 0.83, 1: 0.80, 2: 0.86, 3: 0.90, 4: 1.05, 5: 1.32, 6: 1.28}
DOW_NAME = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}

# Base occupancy rates per route tier
BASE_OCC = {'Tier1': 0.72, 'Tier2': 0.62, 'Tier3': 0.54}

# Route metadata dict for fast access
route_meta = {r['route_id']: r for _, r in routes_df.iterrows()}

# ─────────────────────────────────────────────
# 4. DAILY BOOKINGS (main fact table)
# ─────────────────────────────────────────────
bookings = []
booking_id = 1

for current_date in (date(2023,1,1) + timedelta(n)
                     for n in range((date(2025,1,1) - date(2023,1,1)).days)):

    dow         = current_date.weekday()
    month       = current_date.month
    season_name, season_mult = season_map[month]
    is_weekend  = 1 if dow >= 5 else 0
    dow_mult    = DOW_MULT[dow]

    for _, bus in bus_inventory_df.iterrows():
        route_id = bus['route_id']
        route    = route_meta[route_id]
        distance = route['distance_km']

        # Festival for this specific route on this date
        fest_key = (current_date, route_id)
        if fest_key in festival_lookup:
            fest_name, fest_mult, fest_impact = festival_lookup[fest_key]
            is_festival = 1
        else:
            fest_name, fest_mult, fest_impact = None, 1.0, None
            is_festival = 0

        # ── Demand / occupancy ──
        combined_mult = dow_mult * season_mult * fest_mult
        base_occ = BASE_OCC[route['route_tier']]
        raw_occ  = base_occ * combined_mult + np.random.normal(0, 0.045)
        occ_rate = float(np.clip(raw_occ, 0.10, 1.00))

        capacity     = int(bus['capacity_seats'])
        booked_seats = int(np.clip(round(occ_rate * capacity), 2, capacity))

        # ── Ticket pricing (surge on festival/weekend) ──
        base_price   = int(route['base_nonac_price_inr'])
        ticket_price = base_price * bus['price_multiplier']
        if is_festival:
            ticket_price *= 1.20     # 20% festival surge
        elif is_weekend:
            ticket_price *= 1.10     # 10% weekend surge
        ticket_price = round(ticket_price, 0)

        total_revenue = ticket_price * booked_seats

        # ── Cost calculation ──
        fuel_per_km        = DIESEL_RATE_PER_LITRE / bus['fuel_efficiency_kmpl']
        fuel_cost          = round(fuel_per_km * distance, 2)
        driver_cost        = 950 if bus['is_ac'] else 720
        conductor_cost     = 500
        toll_cost          = round(distance * 0.85, 0)   # ₹0.85/km (NH toll avg)
        maintenance_cost   = 700 if bus['is_ac'] else 480
        total_op_cost      = fuel_cost + driver_cost + conductor_cost + toll_cost + maintenance_cost
        profit_loss        = round(total_revenue - total_op_cost, 2)

        # ── Demand label for easy SQL filtering ──
        if occ_rate >= 0.90:
            demand_label = 'Overcrowded'
        elif occ_rate >= 0.75:
            demand_label = 'High'
        elif occ_rate >= 0.55:
            demand_label = 'Normal'
        else:
            demand_label = 'Low'

        # ── Fleet recommendation ──
        if occ_rate >= 0.90:
            recommendation = 'Add 2 Buses'
        elif occ_rate >= 0.80:
            recommendation = 'Add 1 Bus'
        elif occ_rate < 0.45:
            recommendation = 'Remove 1 Bus'
        else:
            recommendation = 'Keep As-Is'

        bookings.append({
            'booking_id':               booking_id,
            'date':                     current_date.isoformat(),
            'year':                     current_date.year,
            'month':                    month,
            'day_of_week':              DOW_NAME[dow],
            'season':                   season_name,
            'is_weekend':               is_weekend,
            'is_festival':              is_festival,
            'festival_name':            fest_name,
            'festival_impact_level':    fest_impact,
            'route_id':                 route_id,
            'route_name':               route['route_name'],
            'route_tier':               route['route_tier'],
            'origin':                   route['origin'],
            'destination':              route['destination'],
            'distance_km':              distance,
            'bus_id':                   bus['bus_id'],
            'bus_type':                 bus['bus_type'],
            'is_ac':                    int(bus['is_ac']),
            'total_seats':              capacity,
            'booked_seats':             booked_seats,
            'occupancy_rate':           round(occ_rate, 4),
            'demand_label':             demand_label,
            'fleet_recommendation':     recommendation,
            'base_ticket_price_inr':    base_price,
            'actual_ticket_price_inr':  int(ticket_price),
            'total_revenue_inr':        int(total_revenue),
            'fuel_cost_inr':            fuel_cost,
            'driver_cost_inr':          driver_cost,
            'conductor_cost_inr':       conductor_cost,
            'toll_cost_inr':            int(toll_cost),
            'maintenance_cost_inr':     maintenance_cost,
            'total_operational_cost_inr': round(total_op_cost, 2),
            'profit_loss_inr':          profit_loss,
        })
        booking_id += 1

bookings_df = pd.DataFrame(bookings)

# ─────────────────────────────────────────────
# SAVE ALL CSVs
# ─────────────────────────────────────────────
import os
out_dir = '/home/claude'
routes_df.to_csv(        f'{out_dir}/routes.csv',         index=False)
bus_inventory_df.to_csv( f'{out_dir}/bus_inventory.csv',  index=False)
festivals_df.to_csv(     f'{out_dir}/festivals.csv',       index=False)
bookings_df.to_csv(      f'{out_dir}/daily_bookings.csv',  index=False)

print("\n========== DATASET SUMMARY ==========")
print(f"routes.csv          → {len(routes_df):>6,} rows  | Columns: {list(routes_df.columns)}")
print(f"bus_inventory.csv   → {len(bus_inventory_df):>6,} rows  | Columns: {list(bus_inventory_df.columns)}")
print(f"festivals.csv       → {len(festivals_df):>6,} rows  | Columns: {list(festivals_df.columns)}")
print(f"daily_bookings.csv  → {len(bookings_df):>6,} rows  | Columns: {len(bookings_df.columns)} columns")
print(f"\nDate range: {bookings_df['date'].min()} to {bookings_df['date'].max()}")
print(f"Routes covered: {bookings_df['route_name'].nunique()}")
print(f"Total buses: {bookings_df['bus_id'].nunique()}")
print(f"Total revenue simulated: ₹{bookings_df['total_revenue_inr'].sum():,.0f}")
print(f"Total operational cost:  ₹{bookings_df['total_operational_cost_inr'].sum():,.0f}")
print(f"Net profit/loss:         ₹{bookings_df['profit_loss_inr'].sum():,.0f}")
print("\nOccupancy distribution:")
print(bookings_df['demand_label'].value_counts())
print("\nFleet recommendations across all records:")
print(bookings_df['fleet_recommendation'].value_counts())
print("\n✅ All 4 CSV files saved successfully.")
