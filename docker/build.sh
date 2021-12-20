#!/bin/bash
IMGNAME=neptune
IMGVERSION=v1.1.2
docker build -t $IMGNAME:$IMGVERSION . 
