from vicon_dssdk import ViconDataStream

shogun_ip = '172.32.3.195'

 
client = ViconDataStream.Client()
frames = []
 
print( 'Connecting' )
while not client.IsConnected():
    print( '.' )
    client.Connect( shogun_ip )
print( 'Connected' )
 
try:
    while client.IsConnected():
        if client.GetFrame():
            #store data here
            frames.append(client.GetFrameNumber() )
 
except ViconDataStream.DataStreamException as e:
    print( 'Error', e )
 
#do something here
print(frames)