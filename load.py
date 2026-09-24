import duckdb
import os
import logging

#Complete the load.py script to create a local, persistent DuckDB database that creates and loads (at most) three tables:

# A full table of YELLOW taxi trips for all of 2024.
# A full table of GREEN taxi trips for all of 2024.
# A lookup table of vehicle_emissions based on the included CSV file above.

logger = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('load.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger.addHandler(handler)
logger.propagate = False

def report(msg):
    global logger
    print(msg)
    logger.info(msg)

def load_parquet_files():
    """
    Loads three tables from parquet files: 
    NYC yellow taxi data, January to December 2024.
    NYC green taxi data, January to December 2024.
    Vehicle emissions data for different vehicle types.
    """
    global logger
    con = None

    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        report("Connected to DDB instance - Load")

        con.execute(f"""
            DROP TABLE IF EXISTS vehicle_emissions;
            DROP TABLE IF EXISTS yellow_trips;
            DROP TABLE IF EXISTS green_trips;
            CREATE TABLE vehicle_emissions AS 
            SELECT * FROM read_csv_auto(
                'data/vehicle_emissions.csv');
        """)
        report("Dropped tables if exists")
        n = con.execute("SELECT COUNT(*) FROM vehicle_emissions").fetchone()[0]
        report(f"vehicle_emissions: {n} rows loaded")
        for color, lead in zip(['yellow','green'],['t','l']):
            report(f"Loading {color} taxi dataset...")
            for month in range(1, 13):
                cmd = f"CREATE TABLE {color}_trips AS" if month==1 else f"INSERT INTO {color}_trips"
                url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_2024-{month:02d}.parquet'
                con.execute(f"""
                    {cmd} 
                    SELECT 
                        VendorID, 
                        {lead}pep_pickup_datetime AS pickup_time, 
                        {lead}pep_dropoff_datetime AS dropoff_time, 
                        passenger_count, 
                        trip_distance 
                    FROM read_parquet('{url}');
                            """)
                report(f"Fetched data for month: {month}")
                report(f"Average trip distance: {con.execute(f"""SELECT AVG(trip_distance) FROM {color}_trips""").fetchone()[0]}")
                
                

    except Exception as e:
        print(f"Caught exception: {e}")
        logger.error(f"Caught exception: {e}")
        exit()

if __name__ == "__main__":
    load_parquet_files()