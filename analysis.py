import duckdb
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

months = ["January","February","March","April",
                        "May","June","July","August","September",
                        "October","November","December"]

def translate(timeframe, time):
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

try:
    con = duckdb.connect(database="emissions.duckdb",read_only=False)
    for color in ["yellow","green"]:
        # Most carbon-intensive trip
        print(f"""Most carbon-intensive trip for {color} taxis: 
            {con.execute(f"""SELECT MAX(trip_co2_kgs) 
            FROM {color}_trips""").fetchone()[0]} kg""")
        # Most (and least) carbon-intensive time-frames
        # sum co2 totals group by hour
        frames = ["hour_of_day", "day_of_week","week_of_year","month_of_year"]
        for frame in frames:
            vals = con.execute(f"""WITH aves AS (SELECT {frame}, AVG(trip_co2_kgs) AS avg_co2 FROM {color}_trips GROUP BY {frame})
                  (SELECT {frame}, avg_co2 FROM aves ORDER BY avg_co2 DESC LIMIT 1)
                  UNION ALL
                  (SELECT {frame}, avg_co2 FROM aves ORDER BY avg_co2 ASC LIMIT 1);""").fetchall()
            print(f"Most carbon-intensive {frame.replace("_", " ")} for {color} taxis: {translate(frame, vals[0][0])}")
            print(f"Least carbon-intensive {frame.replace("_", " ")} for {color} taxis: {translate(frame, vals[1][0])}")
            
        
        # Time plot
        # sum CO2 totals group by month
        df = con.execute(f"""SELECT month_of_year, SUM(trip_co2_kgs)
                            FROM {color}_trips 
                            GROUP BY month_of_year 
                            ORDER BY month_of_year ASC""").fetchall()
        df = pd.DataFrame(df, columns=['month', 'co2'])
        df['logco2'] = np.log(df['co2'])
        sns.lineplot(df, x='month', y='co2', label=color).set_title(f"NYC Taxi Emissions Over 2024")
    plt.xlabel("Month of year")
    plt.ylabel("CO2 emissions (kg)")
    plt.xticks(ticks=np.arange(1,13, step=1), 
               labels=months,
               rotation=45)
    plt.savefig(f"monthly_emissions.png",bbox_inches="tight")
    plt.clf()
    
except Exception as e:
    print(f"Caught exception: {e}")