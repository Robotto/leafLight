#!/bin/bash
mogrify -resize 64x64 +dither -format xbm leafsLogo.bmp && cat leafsLogo.xbm | sed s/static/const/ | sed s/=/PROGMEM=/  > leafs.h
