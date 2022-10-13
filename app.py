from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd

from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Float
import json


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = Session(engine)
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)


@app.route("/")
def all():
    return (f"these are all routes")


@app.route("/api/v1.0/precipitation")
# # * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
def prcp():
    date = session.query(measurement.date).filter(
        (measurement.date > '2016-08-23') & (measurement.date < '2017-07-10')).all()
    data_scores = session.query(measurement.prcp).filter(
        (measurement.date > '2016-08-23') & (measurement.date < '2017-07-10')).all()

    prcp_list = []
    for i in range(len(date)):
        zip_iterator = zip(date[i], data_scores[i])
        dict_result = dict(zip_iterator)
        prcp_list.append(dict_result)

    return jsonify(prcp_list)


#   * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    list_of_station = session.query(station.station).all()
    result = [tuple(i) for i in list_of_station]
    return jsonify(result)


# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    selector = pd.DataFrame(session.query(
        measurement.station).all()).value_counts().nlargest(1)
    dates = pd.DataFrame(session.query(measurement.date, measurement.station, measurement.prcp).filter(
        (measurement.date > '2016-08-23') & (measurement.date < '2017-07-10')).all()).set_index('station').loc['USC00519281']
    result = dates.to_json(orient='values')

    return (result)


@app.route('/<start>')
def start_date(start):

    temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(
        measurement.date > start).all()
    result = [tuple(i) for i in temp]
    return jsonify(result)


@app.route('/<start_date>/<end_date>')
def temp_dates(start_date, end_date):

    temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(
        (measurement.date > start_date) & (measurement.date < end_date)).all()
    result = [tuple(i) for i in temp]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
