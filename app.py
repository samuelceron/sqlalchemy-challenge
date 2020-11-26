import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"<h1 style='color:red'>Available Routes:</h1><br/>"
        f"<li>Precipitation: /api/v1.0/precipitation</li><br/>"
        f"<li>Stations: /api/v1.0/stations</li><br/>"
        f"<li>Tobs: /api/v1.0/tobs</li><br/>"
        f"<li>Temperature from the start date: /api/v1.0/start</li><br/>"
        f"<li>Temperature stat from start to end date: /api/v1.0/start-end</li>"
    )
#/api/v1.0/precipitation
#Return a list of dates and precipitations
@app.route('/api/v1.0/precipitation')
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query precipitations
    data = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*data).all()
    session.close()

    #Storage data on a precipitation list withdate and prcp fields
    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query data stations
    data = [Station.station,Station.name]
    queryresult = session.query(*data).all()
    session.close()

     #Set data on a stations list with stations and name fields
    stations = []
    for station,name in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        stations.append(station_dict)

    return jsonify(stations)

#/api/v1.0/tobs
@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    date_yearago = dt.date(last_date_date.year-1, last_date_date.month, last_date_date.day)
    
    data = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*data).filter(Measurement.date >= date_yearago).all()

    session.close()
    tobs_list = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


#/api/v1.0/<start>
@app.route('/api/v1.0/<start>')
def get_t_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    

    #Set data on a misc list with the result
    misc_list = []
    for min,avg,max in queryresult:
        misc_dict = {}
        misc_dict["Min"] = min
        misc_dict["Average"] = avg
        misc_dict["Max"] = max
        misc_list.append(misc_dict)

    return jsonify(misc_list)

#/api/v1.0/<start>
@app.route('/api/v1.0/<start><end>')
def get_t_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    

    #Set data on a misc list with the result
    misc_list = []
    for min,avg,max in queryresult:
        misc_dict = {}
        misc_dict["Min"] = min
        misc_dict["Average"] = avg
        misc_dict["Max"] = max
        misc_list.append(misc_dict)

    return jsonify(misc_list)

if __name__ == '__main__':
    app.run(debug=True)
