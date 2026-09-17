import duckdb
import os
import logging

#Complete the load.py script to create a local, persistent DuckDB database that creates and loads (at most) three tables:

# A full table of YELLOW taxi trips for all of 2024.
# A full table of GREEN taxi trips for all of 2024.
# A lookup table of vehicle_emissions based on the included CSV file above.


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

def load_parquet_files():

    con = None

    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(database='emissions.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        con.execute(f"""
            DROP TABLE IF EXISTS vehicle_emissions;
            DROP TABLE IF EXISTS yellow_trips;
            DROP TABLE IF EXISTS green_trips;
            CREATE TABLE vehicle_emissions AS 
            SELECT * FROM read_csv_auto(
                'data/vehicle_emissions.csv');
        """)
        logger.info("Dropped table if exists")
        n = con.execute("SELECT COUNT(*) FROM vehicle_emissions").fetchone()[0]
        logger.info(f"vehicle_emissions: {n} rows loaded")
#        for color_vars in [('yellow', "t"), ('green',"l")]:
#            for month in range(1, 13):
#                url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{color_vars[0]}_tripdata_2024-{month:02d}.parquet'
#                con.execute(f"""
#                    INSERT INTO {color_vars[0]}_trips 
#                    SELECT 
#                        VendorID, 
#                        {color_vars[1]}pep_pickup_datetime AS pickup_time, 
#                        {color_vars[1]}pep_dropoff_datetime AS dropoff_time, 
#                        passenger_count, 
#                        trip_distance 
#                    FROM read_parquet('{url}');
#                            """)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    load_parquet_files()