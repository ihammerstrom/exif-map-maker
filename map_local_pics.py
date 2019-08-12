import os
from pprint import pprint
from GPSPhoto import gpsphoto
from datetime import datetime
import sys
import map_maker

def to_timestamp(date, utc_time):
  date_arr = date.split('/')

  month = int(date_arr[0])
  day = int(date_arr[1])
  year = int(date_arr[2])

  time_arr = utc_time.split(':')
  hour = int(time_arr[0])
  minute = int(time_arr[1])
  second = int(float(time_arr[2]))

  return str(datetime(year, month, day, hour, minute, second).strftime("%Y:%m:%d %H:%M:%S"))


# traverse directories and create csv of all the pictures
# with exif img data found.
def make_pic_data_csv(paths_arr):
  file_name = 'pic_coords_time.csv'  # TODO: not hardcode this

  print("creating: %s" % file_name)
  outfile = open(file_name, 'w+')
  outfile.write('path, coordinates, date\n')
  for path in paths_arr:
    for root, dirs, files in os.walk(path):
      for name in files:
        full_path = os.path.join(root, name)
        try:
          data = gpsphoto.getGPSData(full_path)
          if data != {}: 
            print(data)
            csv_str = "%s, %s %s, %s,\n" % (
                full_path,
                data.get('Latitude'), 
                data.get('Longitude'),
                to_timestamp(data['Date'], data['UTC-Time']))
            
            print(csv_str.rstrip())
            outfile.write(csv_str)

        except (ValueError, KeyError) as e:
          print("---ERROR---")
          print(full_path)
          print(e)

  outfile.close()
  print("created: %s" % file_name)
  return file_name


# load csv into list of img data dicts
def get_pic_data(filePath):
  pic_data_lines = open(filePath, 'r').readlines()
  if 'path' in pic_data_lines[0]:  # delete header
    del pic_data_lines[0]

  pic_data = []
  for line_seg in [x.split(',') for x in pic_data_lines]:
    coords = line_seg[1].lstrip().split(' ')
    pic_data.append({
        'lat': float(coords[0]),
        'lon': float(coords[1]),
        'date': line_seg[2],
    })
  pic_data = sorted(pic_data, key=lambda i: i['date'])
  return pic_data


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: python3 map_local_pics.py some_dir_with_exif_pics/ ")
    sys.exit(1)

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
  
  # make csv from pic data in directory.
  outfile_name = make_pic_data_csv(sys.argv[1:])
  pic_data = get_pic_data(outfile_name)

  if len(pic_data) < 1:
    print("error: no image data found in directory")
    sys.exit(1)

  map = map_maker.get_complete_map(pic_data, config)

  map_filename = 'my_map.html'  # TODO: not hardcode this
  print("created: %s" % map_filename)
  map.save(map_filename)
