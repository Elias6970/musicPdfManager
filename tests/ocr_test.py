import sys
import os

# Get the parent directory of the current script
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)


from autodetect import autodetect


detect = autodetect.Detect()
detect.detect("HOla2","tests\\jkk.pdf")