# Main dependency locations
export NEATSYS=$PWD

# Check for root dependency
if [ -z $ROOTSYS ] || [ -z $NEATSYS ] 
then
   echo "Error: missing dependency."
fi

if [ -n "$PYTHONPATH" ]
then
   export PYTHONPATH="$NEATSYS/configs:$NEATSYS/src:$NEATSYS/src/support:$PYTHONPATH"
else
   export PYTHONPATH="$NEATSYS/configs:$NEATSYS/src:$NEATSYS/src/support" 
fi

# Compiling extensions
export EXTRA_COMPILE_ARGS="-Wno-write-strings"
python src/setup.py build --build-lib $PWD 

