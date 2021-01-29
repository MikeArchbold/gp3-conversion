#!/usr/bin/env python3
import boto3
import json
from botocore.exceptions import ClientError

ec2_client = boto3.client('ec2', region_name='us-west-2')
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name' : 'volume-type',
            'Values' : ['gp2']
        }
    ]
)

csv_output = []
for v in volumes['Volumes']:
    # if disk size is less than 100 set to the minimum of 3000
    # otherwise if disk is larger set to the current IOPs it has with gp2
    iops_change = ""
    if v['Size'] <= 100:
        iops_change = 3000
    else:
        iops_change = v['Size']*3

    # if disk is less than 170 gbs then set throughput to 128 mb/s
    # otherwise if disk is larger set to 250 mb/s
    thoughput_change = ""
    if v['Size'] <= 170:
        current_throughput = 128
        throughput_change = 128
    else:
        current_throughput = 250
        throughput_change = 250


    volume_values = [ str(v['VolumeId']), v['Iops'], current_throughput, iops_change, throughput_change ]
    csv_output.append(volume_values)

with open('gp3_change_set', mode='w') as filehandle:
    json.dump(csv_output, filehandle)
    filehandle.close()