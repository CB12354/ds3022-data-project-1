import duckdb
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

logger = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('analysis.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger.addHandler(handler)
logger.propagate = False

def report(msg):
    global logger
    print(msg)
    logger.info(msg)

months = ["January","February","March","April",
                        "May","June","July","August","September",
                        "October","November","December"]

def translate(timeframe, time):
    """
    Translates time variables from SQL into human-readable strings.
    
    Arguments:
    timeframe -- The time frame to translate into
    time -- The time value
    """
    match timeframe:
        case "hour_of_day":
            return str(time) + ":00"
        case "day_of_week":
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                    'Thursday','Friday', 'Saturday']
            return days[time]
        case "month_of_year":
            return months[time - 1]
        case _:
            return time

def analyze_taxi_co2():
    global logger
    """
    Find out key statistics for yellow and green taxis for when
    CO2 production is most and least problematic, and the largest
    CO2 producing trip.
    """
    con = None
    try:
        con = duckdb.connect(database="emissions.duckdb",read_only=False)
        print("Connected to DuckDB instance - Analysis")
        logger.info("Connected to DuckDB instance - Analysis")
        fig, ax1 = plt.subplots(figsize=(8, 6))
        ax2 = ax1.twinx()
        for color in ["yellow","green"]:
            # Most carbon-intensive trip
            row = con.execute(f"""SELECT trip_co2_kgs, trip_distance, pickup_time 
                FROM {color}_trips
                ORDER BY trip_co2_kgs DESC LIMIT 1""").fetchone()
            car_str = f"""Most carbon-intensive trip for {color} taxis: ({row[0]:.2f} kg {row[1]:.2f} mi, picked up {row[2]})"""
            report(car_str)
            # Most (and least) carbon-intensive time-frames
            # sum co2 totals group by hour
            frames = ["hour_of_day", "day_of_week","week_of_year","month_of_year"]
            for frame in frames:
                # sort desc gets highest, sort asc gets lowest
                vals = con.execute(f"""WITH aves AS (SELECT {frame}, AVG(trip_co2_kgs) AS avg_co2 FROM {color}_trips GROUP BY {frame})
                    (SELECT {frame}, avg_co2 FROM aves ORDER BY avg_co2 DESC LIMIT 1)
                    UNION ALL
                    (SELECT {frame}, avg_co2 FROM aves ORDER BY avg_co2 ASC LIMIT 1);""").fetchall() 
                frame_str = f"Most carbon-intensive {frame.replace("_", " ")} for {color} taxis: {translate(frame, vals[0][0])}"
                frame_str_least = f"Least carbon-intensive {frame.replace("_", " ")} for {color} taxis: {translate(frame, vals[1][0])}"
                report(frame_str)
                report(frame_str_least)
                
            
            # Time plot
            # sum CO2 totals group by month
            df = con.execute(f"""SELECT month_of_year, SUM(trip_co2_kgs) / 1000
                                FROM {color}_trips 
                                GROUP BY month_of_year 
                                ORDER BY month_of_year ASC""").fetchall()
            df = pd.DataFrame(df, columns=['month', 'co2'])
            df['logco2'] = np.log(df['co2'])
            axes = ax1 if color == "yellow" else ax2
            col_ticks = color[:1]
            axes.plot(df['month'], df['co2'], color=col_ticks, label=color, marker="o")
            axes.tick_params(axis='y',labelcolor=col_ticks)
            #sns.lineplot(df, x='month', y='co2', label=color).set_title(f"NYC Taxi Emissions Over 2024")
        plt.xlabel("Month of year")
        plt.title("NYC Taxi Emissions over 2024")
        ax1.set_ylabel("CO2 emissions (tonnes)")
        ax2.set_ylabel("CO2 emissions (tonnes)")
        ax1.set_xticks(ticks=np.arange(1,13, step=1), 
                labels=months,
                rotation=45)
        plt.savefig(f"monthly_emissions_duo.png",bbox_inches="tight")
        plt.clf()
        report("Plot generated")
        
    except Exception as e:
        print(f"Caught exception: {e}")
        logger.error(f"Caught exception: {e}")
        exit()
    
if __name__ == "__main__":
    analyze_taxi_co2()