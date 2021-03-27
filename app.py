############################################################
# import dependencies
############################################################

import numpy as np 
import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request, render_template

############################################################
# setup database
############################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement 
Station = Base.classes.station 

############################################################
# setup flask
############################################################

app = Flask(__name__)

############################################################
# flask routes
############################################################

@app.route("/")
def welcome():
	return(
		f"vaya con dios amigo. the waves are rolling, the beers are cold.<br/>"
		f"<br/>"
		f"here are a few available apis to get the most out of your time.<br/>"
		f"<br/>"
		f"i'm only happy when it rains<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"<br/>"
		f"information station<br/>"
		f"/api/v1.0/stations<br/>"
		f"<br/>"
		f"some like it hot<br/>"
		f"/api/v1.0/tobs<br/>"
		f"<br/>"
		f"one year ago<br/>"
		f"/api/v1.0/&lt;start&gt; enter date in yyyy-mm-dd format<br/>"
		f"<br/>"
		f"one year ago on the range<br/>"
		f"/api/v1.0/&lt;start&gt;/&lt;end&gt; enter date in yyyy-mm-dd format<br/>"
		)

@app.route("/api/v1.0/precipitation")
def precipitation():
	session=Session(engine)
	results = session.query(Measurement.date, Measurement.prcp).\
		order_by(Measurement.date).all()

	prcp_list = []

	for date, prcp in results:
		new_dict={}
		new_dict[date] = prcp
		prcp_list.append(new_dict)

	session.close()

	return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
	session=Session(engine)
	selection = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
	results = session.query(*selection).all()

	session.close()

	stations = []
	for station, name, lat, lon, el in results:
		station_dict ={}
		station_dict["Station"] = station
		station_dict["Name"] = name
		station_dict["Lat"] = lat
		station_dict["Lon"] = lon
		station_dict["Elevation"] = el
		stations.append(station_dict)

	return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
	session=Session(engine)
	lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
	latestdate = dt.datetime.strptime(lateststr, "%Y-%m-%d")
	querydate = dt.date(latestdate.year-1, latestdate.month, latestdate.day)
	selection = [Measurement.date, Measurement.tobs]
	result = session.query(*selection).filter(Measurement.date >= querydate).all()
	session.close()

	tobsall = []
	for date, tobs in result:
		tobs_dict = {}
		tobs_dict["Date"] = date
		tobs_dict["Temperatire"] = tobs
		tobsall.append(tobs_dict)

	return jsonify(tobsall)

@app.route("/api/v1.0/<start>")
def start(start):
	session=Session(engine)

	"""return a json list of min temps, avg temps, and max temps for a given start date"""

	start_dt = dt.datetime.strptime(start, "%Y-%m-%d")

	results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()
	session.close()

	t_list = []
	for result in results:
		r = {}
		r["Start Date"] = start_dt
		r["tmin"] = result[0]
		r["tavg"] = result[1]
		r["tmax"] = result[2]
		t_list.append(r)

	return jsonify(t_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
	session=Session(engine)

	"""return a json list of min temps, avg temps, and max temps for a given start date and end date"""

	start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
	end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

	results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)
	session.close()

	t_list = []
	for result in results:
		r={}
		r["State Date"] = start_dt
		r["End Date"] = end_dt
		r["tmin"] = result[0]
		r["tavg"] = result[1]
		r["tmax"] = result[2]
		t_list.append(r)

	return jsonify(t_list)

############################################################
# run it
############################################################

if __name__ == "__main__":
	app.run(debug=True)