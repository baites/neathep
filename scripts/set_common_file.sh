#! /bin/bash

if [ -z "$NEATSYS" ]
then
echo "Missing NEATSYS: please source setup.csh first."
exit 1
fi

if [ $# -ne 1 ]
then
echo "Set a symbolic link to the proper config file."
echo "Usage: $0 {location of the common file}"
exit 1
fi

echo "Setting common file to $1"
ln -sf $NEATSYS/$1 $NEATSYS/configs/Common.py

