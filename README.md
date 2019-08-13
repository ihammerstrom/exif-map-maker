# exif-map-maker
Tools to create an HTML route map from the location data in image Exif fields.
A hosted version with a simple client written in ReactJS is available at https://00ff.pw. Feel free to use the images in the [samplePics](https://github.com/ihammerstrom/exif-map-maker/tree/master/samplePics "samplePics") directory to try out the hosted version.

This project is still under development, open sourced as of 08/12/2019.

# Installation
Recommended: Create a virtual env:
```
python3 -m venv env
```
Then, to active the env:
```
source env/bin/activate
```
And finally, install the requirements:
```
(env) pip3 install -r requirements.txt
```

# Usage

There are two main ways to use exif-map-maker from this source if you don't want to use the web client available at https://00ff.pw

**1) (easiest) Locally from a directory:**
For example, using the images in the directory [samplePics](https://github.com/ihammerstrom/exif-map-maker/tree/master/samplePics "samplePics"), run 

```
(env) python3 map_local_pics.py samplePics/
creating: pic_coords_time.csv
samplePics/IMG_7829.JPG, 49.36127777777778 -124.48165, 2017:06:20 06:20:27,
samplePics/IMG_7778.JPG, 48.87889444444445 -123.58876111111111, 2017:06:19 19:56:52,
...
*snip*
...
samplePics/IMG_7749.JPG, 48.57064722222223 -122.8836888888889, 2017:06:18 14:01:21,
samplePics/IMG_7819.JPG, 49.115436111111116 -123.8981638888889, 2017:06:19 22:51:06,
created: pic_coords_time.csv
created: my_map.html
```
Now, you have your html file, ```my_map.html```  which shows the the map created from your images.

**2) As a server:**
The file [map_server.py](https://github.com/ihammerstrom/exif-map-maker/blob/master/map_server.py "map_server.py") serves the [map_maker.py](https://github.com/ihammerstrom/exif-map-maker/blob/master/map_maker.py "map_maker.py") functionality by returning an HTML map when a client does a ```POST``` a the endpoint ```/api/v1/get_map``` with the the payload containing image data such as: ```{picData: [{lat: 47.6, lon: 122.3, date:2017:06:19 19:56:52},  ... ]}``` 

It is the API server used by https://00ff.pw
There is no client provided in this repo but you can try out the functionality by following the instructions below.

Using two terminals, run:
Terminal 1:
```
(env) python3 map_server.py
```
Terminal 2:
```
curl -XPOST -H "Content-type: application/json" -d '{"picData":[{"lat":48.45285833333334,"lon":-122.9133388888889,"date":"2017:06:18 05:44:28"},{"lat":48.57064722222223,"lon":-122.8836888888889,"date":"2017:06:18 07:01:21"},{"lat":48.57231388888889,"lon":-122.88055555555555,"date":"2017:06:18 07:12:43"},{"lat":48.48168611111111,"lon":-123.35990277777778,"date":"2017:06:18 14:55:00"},{"lat":48.88177777777778,"lon":-123.57231944444445,"date":"2017:06:19 12:16:03"},{"lat":48.881727777777776,"lon":-123.5765611111111,"date":"2017:06:19 12:53:27"},{"lat":48.87889444444445,"lon":-123.58876111111111,"date":"2017:06:19 12:56:52"}]}' 'http://localhost:5000/api/v1/get_map' > map.html
```
And then in Terminal 2 you can open ```map.html``` to view your map.


# Example output:
<html>
<iframe width="100%" height="560" src="https://objective-bhaskara-82ec61.netlify.com" frameborder="0" allowfullscreen></iframe>
</html>
