import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc, asc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measure = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


# First main page with all routes..
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"For all Precipitation: /api/v1.0/precipitation <br/>"
        f"For all the Station: /api/v1.0/stations <br/>"
        f"For the temperature of the most active station: /api/v1.0/tobs <br/>"
        f"For the temperature from the start date and so on: /api/v1.0/<start_date> <br/>"
        f"For the temperature between the start date and end date: /api/v1.0/<start_date>/<end_date> <br/>"
        f"For the temperature from the start date by givining input into the terminal(another method for getting temperature): /api/v1.0/start"
        
    )

# Precipitation page.

@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    recent_date = session.query(Measure.date).order_by(desc(Measure.date)).first()
    recent_date
    # Calculate the date one year from the last date in data set.
    start_date = dt.date(2016,8,23)
    # Perform a query to retrieve the data and precipitation scores
    precip = session.query(Measure.date, Measure.prcp).filter(Measure.date >= start_date).order_by(Measure.date).all()

    session.close()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    all_precipitation = []
    for date,prcp in precip:
        precip_df = {}
        precip_df["Date"] = date
        precip_df["Precipitation"] = prcp 
        all_precipitation.append(precip_df)
    return jsonify(all_precipitation)

# Display all the stations. 

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    stat = session.query(Station.station).all()
    session.close()
    all_station = list(np.ravel(stat))
    return jsonify(all_station)

# Dispaly the temperatur of the most active station.

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    last_date_temp= session.query(Measure.date).filter(Measure.station=='USC00519281').order_by(desc(Measure.date)).first()
    last_date_temp
    start_date_temp = dt.date(2016,8,18)
    #active_station = session.query(Measure.station).filter(Measure.station=='USC00519281').first()
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    station_temp = session.query(Measure.date, Measure.tobs).filter(Measure.date >= start_date_temp).\
    filter(Measure.station=='USC00519281').order_by(Measure.station).all()
    session.close()
    all_station_temp = list(np.ravel(station_temp))
    return jsonify(all_station_temp)


# Dispaly the temperature from the start date.

@app.route("/api/v1.0/<date_start>")
def start(date_start):
    session = Session(engine)
    #date = session.query(Measure.date).order_by(asc(Measure.date)).first()
    #start_date = dt.date(2010,1,1)
    temp_data = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
    filter(Measure.date >=date_start).all()
    session.close()
    all_temp_data = list(np.ravel(temp_data))
    return f"The Lowest temperature Since {date_start} is {all_temp_data[0]}.<br/> The Highest temperature since {date_start} is {all_temp_data[1]}.<br/> The Average Temperature since {date_start} is {all_temp_data[2]}."

# Display the temperature between two dates.

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    session = Session(engine)
    #start_date = dt.date(2010,1,1)
    #end_date = dt.date(2010,12,31)
    one_year_temp_data = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
    filter(Measure.date >= start_date).filter(Measure.date <= end_date).all()
    session.close()
    one_year_data = list(np.ravel(one_year_temp_data))
    return f"The Lowest temperature between {start_date} and {end_date} was {one_year_data[0]}.<br/> The Highest temperature between {start_date} and {end_date} was {one_year_data[1]}.<br/> The Average Temperature between {start_date} and {end_date} was {one_year_data[2]}."

# Display the temperature from the start date.

# It's an another method where user input is considered into the terminal. 

# When you do this part keep a watch in the terminal where it will ask for the date input. It might take 2-3 tries to run but it works perfect.

# Once you will enter the route into the search bar come back to the terminal down below it will ask you to enter the date.

# enter the date in format 2010-01-01 year-month-date without any "".

# Than go back to the localhost link it will show the result. If not try to rerun the code. It will show for sure.

@app.route("/api/v1.0/start")
def start_try():
    session = Session(engine)
    def temp_start(start_date_try):

        return session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).filter(Measure.date >=start_date_try).all()
    date_input = input("Enter the start date: ")
    all_temp_data = temp_start(date_input)
    all_t = list(np.ravel(all_temp_data))
    session.close()
    return f"The Lowest temperature Since {date_input} is {all_t[0]}.<br/> The Highest temperature since {date_input} is {all_t[1]}.<br/> The Average Temperature since {date_input} is {all_t[2]}."


if __name__ == '__main__':
    app.run(debug=True)