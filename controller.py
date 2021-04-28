from __future__ import print_function
from vicon_dssdk import ViconDataStream
import argparse
import numpy as np
import math

from rotate3D import *

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('host', nargs='?', help="Host name, in the format of server:port", default = "172.32.3.195:801")
args = parser.parse_args()

client = ViconDataStream.Client()

print("Setting up.")
client.Connect( args.host )

# Check the version
print( 'Version', client.GetVersion() )

# Check setting the buffer size works
client.SetBufferSize( 1 )

#Enable all the data types
client.EnableSegmentData()
client.DisableMarkerData()
client.DisableUnlabeledMarkerData()
client.DisableMarkerRayData()
client.DisableDeviceData()
client.DisableCentroidData()

# Report whether the data types have been enabled
print( 'Segments', client.IsSegmentDataEnabled() )
print( 'Markers', client.IsMarkerDataEnabled() )
print( 'Unlabeled Markers', client.IsUnlabeledMarkerDataEnabled() )
print( 'Marker Rays', client.IsMarkerRayDataEnabled() )
print( 'Devices', client.IsDeviceDataEnabled() )
print( 'Centroids', client.IsCentroidDataEnabled() )

client.SetStreamMode( ViconDataStream.Client.StreamMode.EServerPush )

try:
    client.ConfigureWireless()
except ViconDataStream.DataStreamException as e:
    print( 'Failed to configure wireless', e )



print("Finished setting up.")



def getMarkerLocations():
    """Connect to the Vicon system and get the locations of all the 
    subjects (a.k.a. markers) that the system knows about.

    Return the frame number and a dictionary of marker names (as String) 
    and locations (as Numpy arrays.)
    """

    try:

        HasFrame = False
        while not HasFrame:
            try:
                client.GetFrame()
                HasFrame = True
            except ViconDataStream.DataStreamException as e:
                client.GetFrame()

        frame = client.GetFrameNumber()

        locators = {}
        
        subjectNames = client.GetSubjectNames()
        print("subject names:", subjectNames)
        
        for subjectName in subjectNames:
            print("subject name:", subjectName )
            
                rootSegmentName = client.GetSubjectRootSegmentName(subjectName)
                print("root segment name:", rootSegmentName)
                globalTranslation = client.GetSegmentGlobalTranslation(subjectName, rootSegmentName)
                print("global translation:", globalTranslation)
                globalTranslation = globalTranslation[0]
                xpos, ypos, zpos = globalTranslation
                #xpos = round(xpos)
                #ypos = round(ypos)
                #zpos = round(zpos)
                
                locators[subjectName] = np.array([xpos, ypos, zpos])
                print('frame', client.GetFrameNumber(), subjectName, rootSegmentName, xpos, ypos, zpos)


        #print( 'frame', client.GetFrameNumber(), locators)
        return frame, locators

    except ViconDataStream.DataStreamException as e:
        print( 'Handled data stream error', e )



if __name__ == "__main__":

    originName = 'rbA'
    xPosName = 'rbB'

    frame, markers = getMarkerLocations()
    print("frame:", frame, "markers:", markers)




    """
    Sample data:
    {'rbA': array([ 1819.56044853, -1204.24919905,   -30.55150338]), 'rbE': array([ -19.07449426,  685.0376895 , 1066.10069388]), 'rbD': array([0., 0., 0.]), 'rbB': array([1804.77464868, 1874.82370907,  -10.63022218]), 'rbC': array([0., 0., 0.])}
    """
        
