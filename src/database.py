import sqlite3
import os

DB_PATH = "data/sih26006.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Vessels Master
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vessels (
        imo TEXT PRIMARY KEY,
        mmsi TEXT,
        vessel_name TEXT,
        owner_company TEXT,
        operator_company TEXT,
        manager_company TEXT,
        vessel_class TEXT,
        flag TEXT,
        year_built INTEGER,
        dwt REAL,
        cargo_capacity_tonnes REAL,
        loa_m REAL,
        beam_m REAL,
        draft_m REAL,
        speed_knots REAL,
        laden_speed REAL,
        ballast_speed REAL,
        fuel_consumption_laden REAL,
        fuel_consumption_ballast REAL
    )
    ''')

    # 2. Companies Master
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id TEXT PRIMARY KEY,
        company_name TEXT,
        company_type TEXT,
        country TEXT,
        fleet_size INTEGER,
        handysize_count INTEGER,
        supramax_count INTEGER,
        ultramax_count INTEGER,
        panamax_count INTEGER,
        kamsarmax_count INTEGER,
        capesize_count INTEGER,
        newcastlemax_count INTEGER,
        website TEXT,
        source TEXT,
        last_verified TEXT
    )
    ''')

    # 3. Ports Master
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ports (
        port_id TEXT PRIMARY KEY,
        port_name TEXT,
        country TEXT,
        latitude REAL,
        longitude REAL,
        max_draft_m REAL,
        max_loa_m REAL,
        max_beam_m REAL,
        loading_rate_tpd REAL,
        unloading_rate_tpd REAL,
        berth_restrictions TEXT
    )
    ''')

    # 4. AIS Positions (Time-series)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ais_positions (
        timestamp TEXT,
        mmsi TEXT,
        imo TEXT,
        ship_name TEXT,
        ship_type TEXT,
        owner_company TEXT,
        operator_company TEXT,
        lat REAL,
        lon REAL,
        speed_knots REAL,
        course REAL,
        heading REAL,
        nav_status TEXT,
        draught REAL,
        destination TEXT,
        eta TEXT,
        source TEXT,
        retrieved_at TEXT,
        PRIMARY KEY (timestamp, imo)
    )
    ''')

    # 5. Weather Data (Time-series spatial)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        forecast_created_at TEXT,
        valid_time TEXT,
        location TEXT,
        latitude REAL,
        longitude REAL,
        wave_height REAL,
        wave_direction REAL,
        wave_period REAL,
        wave_peak_period REAL,
        wind_wave_height REAL,
        wind_wave_direction REAL,
        wind_wave_period REAL,
        swell_height REAL,
        swell_direction REAL,
        swell_wave_period REAL,
        ocean_current_velocity REAL,
        ocean_current_direction REAL,
        sea_surface_temperature REAL,
        wind_speed REAL,
        precipitation REAL,
        source TEXT,
        PRIMARY KEY (valid_time, latitude, longitude)
    )
    ''')

    # 6. Freight Rates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS freight_rates (
        date TEXT,
        origin TEXT,
        destination TEXT,
        route TEXT,
        vessel_class TEXT,
        cargo_type TEXT,
        freight_rate REAL,
        freight_unit TEXT,
        currency TEXT,
        contract_type TEXT,
        source TEXT,
        PRIMARY KEY (date, route, vessel_class)
    )
    ''')

    # 7. Trade Data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trade (
        date TEXT,
        reporter_country TEXT,
        partner_country TEXT,
        flow TEXT,
        commodity TEXT,
        trade_value_usd REAL,
        trade_quantity REAL,
        net_weight REAL,
        PRIMARY KEY (date, reporter_country, partner_country, commodity)
    )
    ''')

    # 8. Economic Data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS economic (
        date TEXT,
        gdp REAL,
        inflation REAL,
        industrial_activity REAL,
        exchange_rate REAL,
        trade_indicators REAL,
        commodity_price REAL,
        original_frequency TEXT,
        master_frequency TEXT,
        PRIMARY KEY (date)
    )
    ''')

    # 9. Fuel Data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fuel (
        date TEXT,
        oil_price REAL,
        fuel_type TEXT,
        source TEXT,
        PRIMARY KEY (date, fuel_type)
    )
    ''')

    # 10. News Events
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_events (
        event_id TEXT PRIMARY KEY,
        timestamp TEXT,
        title TEXT,
        content TEXT,
        event_category TEXT,
        event_score REAL,
        severity TEXT,
        location TEXT,
        route_impact TEXT,
        source TEXT
    )
    ''')

    # 11. Model Registry
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_registry (
        model_name TEXT PRIMARY KEY,
        algorithm TEXT,
        version TEXT,
        dataset_version TEXT,
        training_start TEXT,
        training_end TEXT,
        features TEXT,
        training_rows INTEGER,
        validation_rows INTEGER,
        test_rows INTEGER,
        mae REAL,
        rmse REAL,
        r2 REAL,
        mape REAL,
        smape REAL,
        created_at TEXT
    )
    ''')

    # 12. Voyage Scenarios / Results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voyage_results (
        scenario_id TEXT PRIMARY KEY,
        voyage_id TEXT,
        cargo_type TEXT,
        cargo_quantity REAL,
        origin TEXT,
        destination TEXT,
        loading_date TEXT,
        vessel_name TEXT,
        imo TEXT,
        vessel_class TEXT,
        route_type TEXT,
        availability_status TEXT,
        distance_nm REAL,
        freight_cost REAL,
        charter_cost REAL,
        fuel_cost REAL,
        loading_cost REAL,
        unloading_cost REAL,
        port_cost REAL,
        waiting_cost REAL,
        demurrage REAL,
        weather_delay_cost REAL,
        repositioning_cost REAL,
        risk_penalty REAL,
        total_expected_cost REAL,
        cost_per_tonne REAL,
        expected_eta TEXT,
        overall_risk_score REAL,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
