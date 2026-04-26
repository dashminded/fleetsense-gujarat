-- ============================================================
--  FleetSense Gujarat — MySQL Setup + 12 Business Queries
--  Database : fleetsense_gujarat
--  Author   : Ashutosh (DA Portfolio Project)
-- ============================================================

-- ──────────────────────────────────────────────────────────
--  STEP 1: CREATE DATABASE
-- ──────────────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS fleetsense_gujarat;
USE fleetsense_gujarat;

-- ──────────────────────────────────────────────────────────
--  STEP 2: CREATE TABLES
--  (Run these BEFORE importing CSVs via Import Wizard)
-- ──────────────────────────────────────────────────────────

-- Table 1: routes
CREATE TABLE IF NOT EXISTS routes (
    route_id              INT           PRIMARY KEY,
    route_name            VARCHAR(50)   NOT NULL,
    origin                VARCHAR(50)   NOT NULL,
    destination           VARCHAR(50)   NOT NULL,
    distance_km           INT           NOT NULL,
    route_tier            VARCHAR(10)   NOT NULL,   -- Tier1 / Tier2 / Tier3
    base_buses_per_day    INT           NOT NULL,
    base_nonac_price_inr  INT           NOT NULL
);

-- Table 2: bus_inventory
CREATE TABLE IF NOT EXISTS bus_inventory (
    bus_id                  VARCHAR(10)    PRIMARY KEY,
    route_id                INT            NOT NULL,
    bus_type                VARCHAR(30)    NOT NULL,   -- Non-AC Seater / AC Seater Volvo / etc.
    capacity_seats          INT            NOT NULL,
    is_ac                   TINYINT(1)     NOT NULL,   -- 0 = No, 1 = Yes
    fuel_efficiency_kmpl    DECIMAL(5,2)   NOT NULL,
    price_multiplier        DECIMAL(4,2)   NOT NULL,
    tank_capacity_litres    INT            NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Table 3: festivals
CREATE TABLE IF NOT EXISTS festivals (
    festival_id         INT           PRIMARY KEY AUTO_INCREMENT,
    festival_name       VARCHAR(60)   NOT NULL,
    start_date          DATE          NOT NULL,
    end_date            DATE          NOT NULL,
    impact_level        VARCHAR(20)   NOT NULL,   -- Low / Medium / High / Very High
    demand_multiplier   DECIMAL(4,2)  NOT NULL,
    routes_affected     VARCHAR(20)   NOT NULL    -- 'ALL' or route ids like '4,10'
);

-- Table 4: daily_bookings  (main fact table — 43,129 rows)
CREATE TABLE IF NOT EXISTS daily_bookings (
    booking_id                  INT            PRIMARY KEY,
    date                        DATE           NOT NULL,
    year                        INT            NOT NULL,
    month                       INT            NOT NULL,
    day_of_week                 VARCHAR(12)    NOT NULL,
    season                      VARCHAR(10)    NOT NULL,
    is_weekend                  TINYINT(1)     NOT NULL,
    is_festival                 TINYINT(1)     NOT NULL,
    festival_name               VARCHAR(60),
    festival_impact_level       VARCHAR(20),
    route_id                    INT            NOT NULL,
    route_name                  VARCHAR(50)    NOT NULL,
    route_tier                  VARCHAR(10)    NOT NULL,
    origin                      VARCHAR(50)    NOT NULL,
    destination                 VARCHAR(50)    NOT NULL,
    distance_km                 INT            NOT NULL,
    bus_id                      VARCHAR(10)    NOT NULL,
    bus_type                    VARCHAR(30)    NOT NULL,
    is_ac                       TINYINT(1)     NOT NULL,
    total_seats                 INT            NOT NULL,
    booked_seats                INT            NOT NULL,
    occupancy_rate              DECIMAL(6,4)   NOT NULL,
    demand_label                VARCHAR(15)    NOT NULL,   -- Low/Normal/High/Overcrowded
    fleet_recommendation        VARCHAR(20)    NOT NULL,
    base_ticket_price_inr       INT            NOT NULL,
    actual_ticket_price_inr     INT            NOT NULL,
    total_revenue_inr           INT            NOT NULL,
    fuel_cost_inr               DECIMAL(10,2)  NOT NULL,
    driver_cost_inr             INT            NOT NULL,
    conductor_cost_inr          INT            NOT NULL,
    toll_cost_inr               INT            NOT NULL,
    maintenance_cost_inr        INT            NOT NULL,
    total_operational_cost_inr  DECIMAL(10,2)  NOT NULL,
    profit_loss_inr             DECIMAL(10,2)  NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(route_id),
    FOREIGN KEY (bus_id)   REFERENCES bus_inventory(bus_id)
);


-- ============================================================
--  STEP 3: 12 BUSINESS QUERIES
--  (Run AFTER importing all 4 CSVs via Import Wizard)
-- ============================================================


-- ─────────────────────────────────────────────
--  Q1. Which route generates the highest total revenue?
--      Business use: Identify star routes worth investing in
-- ─────────────────────────────────────────────
SELECT
    route_name,
    origin,
    destination,
    distance_km,
    SUM(total_revenue_inr)              AS total_revenue_inr,
    SUM(total_operational_cost_inr)     AS total_cost_inr,
    SUM(profit_loss_inr)                AS total_profit_inr,
    ROUND(AVG(occupancy_rate) * 100, 2) AS avg_occupancy_pct
FROM daily_bookings
GROUP BY route_name, origin, destination, distance_km
ORDER BY total_revenue_inr DESC;


-- ─────────────────────────────────────────────
--  Q2. Average occupancy rate by route — which routes run half-empty?
--      Business use: Routes below 55% avg are wasting fuel
-- ─────────────────────────────────────────────
SELECT
    route_name,
    route_tier,
    ROUND(AVG(occupancy_rate) * 100, 2)   AS avg_occupancy_pct,
    ROUND(MIN(occupancy_rate) * 100, 2)   AS min_occupancy_pct,
    ROUND(MAX(occupancy_rate) * 100, 2)   AS max_occupancy_pct,
    COUNT(*)                               AS total_trips
FROM daily_bookings
GROUP BY route_name, route_tier
ORDER BY avg_occupancy_pct DESC;


-- ─────────────────────────────────────────────
--  Q3. Festival days vs Normal days — revenue & occupancy comparison
--      Business use: Quantify how much festivals boost the business
-- ─────────────────────────────────────────────
SELECT
    CASE WHEN is_festival = 1 THEN 'Festival Day' ELSE 'Normal Day' END  AS day_type,
    COUNT(*)                                    AS total_records,
    ROUND(AVG(occupancy_rate) * 100, 2)         AS avg_occupancy_pct,
    ROUND(AVG(total_revenue_inr), 0)            AS avg_revenue_per_bus_inr,
    ROUND(AVG(profit_loss_inr), 0)              AS avg_profit_per_bus_inr,
    SUM(total_revenue_inr)                      AS total_revenue_inr
FROM daily_bookings
GROUP BY is_festival
ORDER BY is_festival DESC;


-- ─────────────────────────────────────────────
--  Q4. Weekend vs Weekday performance
--      Business use: Decide how many extra buses to deploy on weekends
-- ─────────────────────────────────────────────
SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END  AS day_type,
    ROUND(AVG(occupancy_rate) * 100, 2)    AS avg_occupancy_pct,
    ROUND(AVG(total_revenue_inr), 0)       AS avg_revenue_per_bus_inr,
    ROUND(AVG(profit_loss_inr), 0)         AS avg_profit_per_bus_inr,
    COUNT(*)                               AS total_trips,
    SUM(total_revenue_inr)                 AS total_revenue_inr
FROM daily_bookings
GROUP BY is_weekend
ORDER BY is_weekend DESC;


-- ─────────────────────────────────────────────
--  Q5. Monthly revenue trend — which months make the most money?
--      Business use: Annual planning, bus procurement schedule
-- ─────────────────────────────────────────────
SELECT
    year,
    month,
    CASE month
        WHEN 1  THEN 'January'   WHEN 2  THEN 'February' WHEN 3  THEN 'March'
        WHEN 4  THEN 'April'     WHEN 5  THEN 'May'      WHEN 6  THEN 'June'
        WHEN 7  THEN 'July'      WHEN 8  THEN 'August'   WHEN 9  THEN 'September'
        WHEN 10 THEN 'October'   WHEN 11 THEN 'November' WHEN 12 THEN 'December'
    END                                         AS month_name,
    season,
    SUM(total_revenue_inr)                      AS total_revenue_inr,
    SUM(total_operational_cost_inr)             AS total_cost_inr,
    SUM(profit_loss_inr)                        AS net_profit_inr,
    ROUND(AVG(occupancy_rate) * 100, 2)         AS avg_occupancy_pct
FROM daily_bookings
GROUP BY year, month, season
ORDER BY year, month;


-- ─────────────────────────────────────────────
--  Q6. Which bus type earns the most profit? AC or Non-AC?
--      Business use: Fleet investment decision (buy AC vs Non-AC)
-- ─────────────────────────────────────────────
SELECT
    bus_type,
    CASE WHEN is_ac = 1 THEN 'AC' ELSE 'Non-AC' END   AS ac_category,
    COUNT(*)                                            AS total_trips,
    ROUND(AVG(occupancy_rate) * 100, 2)                AS avg_occupancy_pct,
    ROUND(AVG(actual_ticket_price_inr), 0)             AS avg_ticket_price_inr,
    ROUND(AVG(total_revenue_inr), 0)                   AS avg_revenue_per_trip,
    ROUND(AVG(fuel_cost_inr), 0)                       AS avg_fuel_cost,
    ROUND(AVG(profit_loss_inr), 0)                     AS avg_profit_per_trip,
    SUM(profit_loss_inr)                               AS total_profit_inr
FROM daily_bookings
GROUP BY bus_type, is_ac
ORDER BY avg_profit_per_trip DESC;


-- ─────────────────────────────────────────────
--  Q7. Loss-making analysis — how often does each route lose money?
--      Business use: Decide whether to cut unprofitable routes/timings
-- ─────────────────────────────────────────────
SELECT
    route_name,
    COUNT(*)                                                        AS total_trips,
    SUM(CASE WHEN profit_loss_inr < 0 THEN 1 ELSE 0 END)           AS loss_making_trips,
    ROUND(
        SUM(CASE WHEN profit_loss_inr < 0 THEN 1 ELSE 0 END)
        / COUNT(*) * 100, 2)                                        AS loss_trip_pct,
    ROUND(SUM(CASE WHEN profit_loss_inr < 0
              THEN profit_loss_inr ELSE 0 END), 0)                  AS total_loss_inr,
    ROUND(AVG(occupancy_rate) * 100, 2)                             AS avg_occupancy_pct
FROM daily_bookings
GROUP BY route_name
ORDER BY loss_trip_pct DESC;


-- ─────────────────────────────────────────────
--  Q8. Top 10 highest single-day revenue records (per bus per day)
--      Business use: Understand what conditions create peak revenue
-- ─────────────────────────────────────────────
SELECT
    date,
    route_name,
    bus_type,
    day_of_week,
    festival_name,
    booked_seats,
    total_seats,
    ROUND(occupancy_rate * 100, 1)  AS occupancy_pct,
    actual_ticket_price_inr,
    total_revenue_inr,
    profit_loss_inr
FROM daily_bookings
ORDER BY total_revenue_inr DESC
LIMIT 10;


-- ─────────────────────────────────────────────
--  Q9. Fuel cost as % of revenue per route — efficiency check
--      Business use: Long routes have higher fuel burden; flag them
-- ─────────────────────────────────────────────
SELECT
    route_name,
    distance_km,
    ROUND(AVG(fuel_cost_inr), 0)                              AS avg_fuel_cost_inr,
    ROUND(AVG(total_revenue_inr), 0)                          AS avg_revenue_inr,
    ROUND(AVG(fuel_cost_inr) / AVG(total_revenue_inr) * 100, 2) AS fuel_pct_of_revenue,
    ROUND(AVG(total_operational_cost_inr) /
          AVG(total_revenue_inr) * 100, 2)                    AS total_cost_pct_of_revenue
FROM daily_bookings
GROUP BY route_name, distance_km
ORDER BY fuel_pct_of_revenue DESC;


-- ─────────────────────────────────────────────
--  Q10. Which specific festival causes the biggest demand spike?
--       Business use: Prioritize fleet planning around top 5 festivals
-- ─────────────────────────────────────────────
SELECT
    festival_name,
    festival_impact_level,
    COUNT(*)                                    AS affected_trip_records,
    ROUND(AVG(occupancy_rate) * 100, 2)         AS avg_occupancy_pct,
    ROUND(AVG(total_revenue_inr), 0)            AS avg_revenue_per_bus_inr,
    ROUND(AVG(profit_loss_inr), 0)              AS avg_profit_per_bus_inr,
    SUM(total_revenue_inr)                      AS total_festival_revenue_inr
FROM daily_bookings
WHERE is_festival = 1
GROUP BY festival_name, festival_impact_level
ORDER BY avg_occupancy_pct DESC;


-- ─────────────────────────────────────────────
--  Q11. Fleet recommendation frequency per route
--       Business use: Core output of this project — how often does each
--       route need extra buses, and on which routes can we cut?
-- ─────────────────────────────────────────────
SELECT
    route_name,
    route_tier,
    fleet_recommendation,
    COUNT(*)                                AS days_count,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER
          (PARTITION BY route_name), 2)     AS pct_of_days
FROM daily_bookings
GROUP BY route_name, route_tier, fleet_recommendation
ORDER BY route_name, days_count DESC;


-- ─────────────────────────────────────────────
--  Q12. Day-of-week demand pattern — which day needs most buses?
--       Business use: Weekly scheduling template for operators
--       Uses WINDOW FUNCTION (rank by occupancy within each route)
-- ─────────────────────────────────────────────
WITH daily_avg AS (
    SELECT
        route_name,
        day_of_week,
        ROUND(AVG(occupancy_rate) * 100, 2)  AS avg_occupancy_pct,
        ROUND(AVG(total_revenue_inr), 0)     AS avg_revenue_inr
    FROM daily_bookings
    GROUP BY route_name, day_of_week
),
ranked AS (
    SELECT *,
        RANK() OVER (
            PARTITION BY route_name
            ORDER BY avg_occupancy_pct DESC
        ) AS occupancy_rank
    FROM daily_avg
)
SELECT
    route_name,
    day_of_week,
    avg_occupancy_pct,
    avg_revenue_inr,
    occupancy_rank,
    CASE
        WHEN occupancy_rank = 1 THEN '🔴 Highest Demand Day'
        WHEN occupancy_rank = 7 THEN '🟢 Lowest Demand Day'
        ELSE ''
    END AS flag
FROM ranked
ORDER BY route_name, occupancy_rank;


-- ============================================================
--  END OF FILE
--  Next step: Open Jupyter Notebook for EDA + Prophet model
-- ============================================================
