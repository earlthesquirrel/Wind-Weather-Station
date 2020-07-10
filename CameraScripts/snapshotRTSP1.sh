#!/bin/sh
DATE=$(date)

#Ping IP-address of camera to see if it's online, otherwise we don't have to grab a snapshot
if ping -c 1 172.16.10.1 > /dev/null ; then  #Grab snapshot from RTSP-stream

rm -f /home/pi/weatherCam/image1.jpg

# Generate a JPG from a single frame
/usr/bin/ffmpeg -rtsp_transport tcp -i "rtsp://172.16.10.1:8555/unicast" -frames 1 /home/pi/weatherCam/image1.jpg

/usr/bin/convert /home/pi/weatherCam/image1.jpg -font "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf" \
   -pointsize 14 -draw "gravity southwest fill white text 14,6 '  Earl Baugh - Raspberry Pi Weather Cam 1 --- $DATE" \
/home/pi/weatherCam/lastsnap1.jpg

# Move the file into the web directory.
mv -f /home/pi/weatherCam/lastsnap1.jpg /var/www/www.baugh.org/shtml/images/

fi
