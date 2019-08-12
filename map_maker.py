# map maker library

import folium
import pandas as pd
from datetime import datetime
import geopy.distance
import matplotlib.colors as mplc
import matplotlib.cm as cm
from collections import deque


def get_pic_data(filePath):
  pic_data_lines = open(filePath, 'r').readlines()
  del pic_data_lines[0] # delete header

  pic_data = []
  for line_seg in [x.split(',') for x in pic_data_lines]:
    coords = line_seg[1].split(' ')
    pic_data.append({
      'lat': float(coords[0]),
      'lon': float(coords[1]),
      'date': line_seg[2],
    })
  return pic_data


# returns a dict of {location: time_in_location} by:
# 1) stepping through the images in chronological order,
# 2) stepping ahead and backwards from the current image, 
#    along the way adding all images taken within area_distance_km to my_neighbors
#    until we find an image taken too far away to be considered within this area
# 3) calculating the time in the area by finding the difference in time between the first 
#    and last picture in my_neighbors
# this dict is used later to draw circles on the map of a size scaled by the time in the area
# of the location of the middle picture int(len(my_neighbors)/2)
def get_area_times(pic_data, area_distance_km):
  area_times = {}
  i = 0
  while i < len(pic_data):
    curr_pic = pic_data[i]
    my_neighbors = [curr_pic]

    # keep adding pictures chronologically ahead while within the distance of the curr_pic
    j = i + 1
    while j < len(pic_data) and get_distance_km(curr_pic, pic_data[j]) < area_distance_km:
      my_neighbors.append(pic_data[j])
      j += 1

    # keep adding pictures chronologically behind while within the distance of the curr_pic
    k = i - 1
    while k > 0 and get_distance_km(curr_pic, pic_data[k]) < area_distance_km:
      my_neighbors.append(pic_data[k])
      k -= 1

    time_in_area = get_time_in_area(my_neighbors)
    # TODO: set anchoring point to the geographical centroid of images, not just the middle image.
    area_times[get_coordinates(
                    my_neighbors[int(len(my_neighbors)/2)])] = time_in_area

    # print("pic_data[%s] has %s neighbors within %skm with a total time of %s hours." % (
    #                 i, len(my_neighbors), area_distance_km, time_in_area))

    if len(my_neighbors) == 1:  # no neighbors found, to next pic
      i += 1
    else: # step over pics we've already found within distance chronologically ahead.
      i = j

  return area_times


def get_coordinates(pic):
  return pic['lat'], pic['lon']


def get_time_in_area(my_neighbors):
  first_time_in_area = get_time_pic(my_neighbors[0])
  last_time_in_area = get_time_pic(my_neighbors[0])
  # of the pics within the area, find the time between the first and last pic
  for neighbor in my_neighbors:
    neigh_pic_time = get_time_pic(neighbor)
    if neigh_pic_time < first_time_in_area:
      first_time_in_area = neigh_pic_time
    elif neigh_pic_time > last_time_in_area:
      last_time_in_area = neigh_pic_time

  return (last_time_in_area - first_time_in_area).total_seconds() / 60.0 / 60.0  # hours


def get_distance_km(pic1, pic2):
  return geopy.distance.distance(get_coordinates(pic1), get_coordinates(pic2)).km


def get_time_pic(pic):
  return datetime.strptime(pic['date'].lstrip(), "%Y:%m:%d %H:%M:%S")


def get_time_diff(curr_dtime, prev_dtime):
  dtime_diff = curr_dtime - prev_dtime
  time_diff = dtime_diff.total_seconds() / 60.0 / 60.0  # seconds to hours
  if time_diff < 0.005:
    time_diff = 0.005  # at least 18 seconds (.005 * a minute)
  return time_diff # in seconds


def add_lines_to_map(map, pic_data, config):
  # make scalar color map 
  scmap = cm.ScalarMappable(
      norm=mplc.Normalize(vmin=0, vmax=6),
      cmap=cm.YlOrRd)

  speed_deq = deque(maxlen=config['hops_avg_speed'])

  used_pic_count = 0
  for pic in pic_data:
    lat, lon = get_coordinates(pic)
    curr_dtime = get_time_pic(pic)

    folium.Circle(
        radius=config['standalone_pic_size'],
        location=[lat, lon],
        color='yellow',
        fill=True,
        opacity=0.7,
    ).add_to(map)

    # once we have more than one pic on the map, start drawing lines between them
    if used_pic_count > 0:
      time_diff = get_time_diff(curr_dtime, prev_dtime)
      distance = geopy.distance.distance((lat, lon), (prev_lat, prev_lon)).km

      speed = distance/time_diff
      speed_deq.appendleft(distance/time_diff)

      # make the speed averaged over the last "hops_avg_speed" number of steps
      if len(speed_deq) == config['hops_avg_speed']:
        avg_speed = float(sum(speed_deq))/len(speed_deq)
        speed = avg_speed

      # add line of the color
      map.add_child(folium.ColorLine(
                  [[lat, lon], [prev_lat, prev_lon]],
                  [0],
                  colormap=[mplc.to_hex([*scmap.to_rgba(speed)]),
                            mplc.to_hex([*scmap.to_rgba(speed)])],
                  weight=2,
                  opacity=1))

    prev_lat = lat
    prev_lon = lon
    prev_dtime = curr_dtime
    used_pic_count += 1


def add_area_times_to_map(map, pic_data, config):
  for coord, hours in get_area_times(pic_data, config['area_distance_km']).items():
    if hours > 2:
      if hours < 10: # set all hours above 2 to a minimum of 10 hours
        hours = 10
      if hours > 150:  # set all hours above 150 to a maximum of 150 hours
        print("trimming %s from %s hours" % (coord, hours))
        hours = 150

      folium.Circle(
        radius=hours*config['time_in_area_circle_size_multiplier'],
        location=[coord[0], coord[1]],
        color='yellow',
        fill=True,
        opacity=0.7,
      ).add_to(map)


def get_base_map(pic_data):
  return folium.Map(
      location=[*get_coordinates(pic_data[0])],
      tiles='Stamen Terrain',
      zoom_start=12
  )

# returns a complete map based on pic_data and config
def get_complete_map(pic_data, config):
  # create map
  map = get_base_map(pic_data)
  # add connecting lines between points
  add_lines_to_map(map, pic_data, config)

  # add large circles to signify time spent in an area
  add_area_times_to_map(map, pic_data, config)

  return map