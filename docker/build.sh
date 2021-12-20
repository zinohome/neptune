#!/bin/bash
IMGNAME=jointhero/neptune
IMGVERSION=v1.1.2
docker build -t $IMGNAME:$IMGVERSION . 
