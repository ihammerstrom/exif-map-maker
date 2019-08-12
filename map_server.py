from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from pprint import pprint
import sqlite3
from datetime import datetime
import map_maker


def setup_db(db_name):
  conn = sqlite3.connect(db_name)
  conn.execute('''CREATE TABLE IF NOT EXISTS coords(
            latitude   INT     NOT NULL,
            longitude  INT     NOT NULL,
            pic_time    CHAR(24)     NOT NULL,
            entry_time  CHAR(24)     NOT NULL,
            PRIMARY KEY (latitude, longitude, pic_time)
            );''')

  # pprint(conn.execute("SELECT * FROM coords").fetchall())
  conn.close()


# keep anonymous database of picture location and time data
# could create user heatmaps etc later.
def commit_data(pic_data, db_name):
  request_time = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
  db_pic_data = [(x['lat'], x['lon'], x['date'],
                  request_time) for x in pic_data]

  temp_conn = sqlite3.connect(db_name)
  temp_conn.executemany(
      '''REPLACE INTO coords VALUES (?,?,?,?)''', db_pic_data)
  temp_conn.commit()
  temp_conn.close()


FILENAME_DB = 'coords.db'
setup_db(FILENAME_DB)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://00ff.pw"], headers=['Content-Type'],
     expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)


@app.route('/api/v1/get_map', methods=['POST'])
def get_map():

  # TODO: override defaults below from values from request.
  config = {
      'area_distance_km': 10,
      'hops_avg_speed': 1,
      'time_in_area_circle_size_multiplier': 500,
      'standalone_pic_size': 500,
      # 'color_map': 'YlOrRd',
      'less_than_kmh_for_circle': 4,
      'hours_trim': 150,
      # 'file_path': '/Users/ihammerstrom/Desktop/trip_pics_out_noShanghai_newDate.csv',
      # detect_flight_speed: False,
      # detect_flight_distance: False,
      # detected_flight_color: 'grey',
      # location_obscure_max_distance: 0,
  }

  pic_data = sorted(request.get_json()['picData'], key=lambda i: i['date'])

  commit_data(pic_data, FILENAME_DB)

  map = map_maker.get_complete_map(pic_data, config)

  return render_template_string(map.get_root().render())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
