import boto3
import json
from threading import BoundedSemaphore, Thread, Event
import time
import datetime
import sys

# change the volume to a gp3
# wait until the volume is in 'available' state before ending 
class modify_volume( Thread ):
    def __init__( self, volume_id, iops, throughput, modification_in_progress, container ):
        Thread.__init__(self)
        self.volume_id = volume_id
        self.iops = iops
        self.throughput = throughput
        self.modification_in_progress = modification_in_progress
        self.container = container

    # changes the volume and notifies monitor volume thread to begin 
    def run(self):
        container.acquire()
        ec2_client.modify_volume(
            VolumeId = self.volume_id,
            Iops = self.iops,
            Throughput = self.throughput,
            VolumeType = 'gp3'
        )
        container.release()
        modification_in_progress.set()

# todo create a producer which will run the describe volumes modification method on all volumes
# being modified
class describe_volume_modifications ( Thread ):
    def __init__( self, volume_ids, number_of_volumes_still_in_progress ):
        Thread.__init__(self)
        self.volume_ids = volume_ids
        self.number_of_volumes_still_in_progress
 
    def run( self ):
        # run until all volumes have been modified. use counter to check on status 
        # volume_modification_progress = ec2_client.describe_volumes_modifications()        

# todo create volume modification progress thread which is separate from the modification itself
# wait for a producer to run describe volume status on all volumes
class monitor_volume_modification_progress ( Thread ):
    def __init__( self, volume_id, modification_in_progress ):
        Thread.__init__(self)
        self.volume_id = volume_id
        self.modification_in_progress = modification_in_progress
    
    def run( self ):
        self.modification_in_progress.wait()

        volume_modification_progress = ec2_client.describe_volumes_modifications(
                VolumeIds=[self.volume_id]
            )["VolumesModifications"][0]["Progress"]
        
        while volume_modification_progress != 100:
            time.sleep(10)
            volume_modification_progress = ec2_client.describe_volumes_modifications(
                VolumeIds=[self.volume_id]
            )["VolumesModifications"][0]["Progress"]
            print('{:%Y-%m-%d %H:%M:%S} UTC'.format(datetime.datetime.now()))
            print(f"Volume modification progress for {self.volume_id} at {volume_modification_progress}")

ec2_client = boto3.client('ec2', region_name='us-west-2')

with open('gp3_change_set', mode='r') as filehandle:
    volumes_to_change = json.load(filehandle)
    filehandle.close()

for volume_info in volumes_to_change:
    print(f"Modifying {volume_info[0]} from " + 
        f"[{volume_info[1]} iops and {volume_info[2]} thoughput] " +
        f"to [{volume_info[3]} iops and {volume_info[4]} throughput]")

if not input("Are you sure these are the changes you want? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)

# only allow 10 simultaneous modify volume requests at a time 
max_amount_modify_requests = 10
container = BoundedSemaphore(max_amount_modify_requests)

# have one producer run a single describe ebs volumes every ten seconds
number_of_volumes_still_in_progress = len(volumes_to_change)


for volume_info in volumes_to_change:
    modification_in_progress = Event()
    
    modify_volume_thread = modify_volume(volume_info[0], volume_info[3], volume_info[4], modification_in_progress,
        container ) 
    modify_volume_thread.start()
    modify_volume_thread.join()

    monitor_volume_thread = monitor_volume_modification_progress(volume_info[0], modification_in_progress)
    monitor_volume_thread.start()
    monitor_volume_thread.join()