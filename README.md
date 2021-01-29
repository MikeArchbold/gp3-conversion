# GP-3 Conversion

A new EBS volume type, GP3, is available in AWS. GP3 offers up to 20% better pricing than previous GP2 Volumes. There are no configurations where a GP2 volume is more cost effective than a GP3. Updating can be done in place with no down time so there is no reason to wait to switch. 

[Announcement](https://aws.amazon.com/about-aws/whats-new/2020/12/introducing-new-amazon-ebs-general-purpose-volumes-gp3/)

[Blog Post](https://www.lastweekinaws.com/blog/the-best-release-of-reinvent-2020/)

[Understanding Throughtput and IOPs](https://www.rhythmictech.com/blog/aws/understanding-gp2-volume-performance/)

## Cost Calculation and Conversion
| Volume Size | Throughput |
| --- | --- |
| < 170 GBs | 128 MB/s |
| > 170 GBs | 250 MB/s |

| Volume Size | IOPs |
| --- | --- |
| < 100 GBs | 100 IOPs (temporarily up to 3000 IOPs when using burst credits) |
| > 100 GBs | 3 * GB Size of Volume |


## Usage

Using python3 run the following two files. The first file will output myConversionFile.csv in the current working directory. The conversion file is a CSV that converts current gp2 usage to gp3. You can directly adjust the IOPs and throughtput you would like to use by editing the csv. 

```python3
python3 createListOfGP2VolumesToConvert.py
```

```python3
python3 convertVolumesToGP3.py --conversionFile myConversionFile.csv
```

## Components 
Three threads run in convert volumes
1. modify_volume - runs the request to convert the volume
2. describe_volume_modifications - describes all volumes modifications every ten seconds. Notifies sepearate threads to check on their modification progress
3. monitor_volume_modification_progress - checks the progress for when the volume is fully available. AWS switches the volume over to gp3 within 10-20 seconds, but it takes up to 30 minutes to "optimize" the volume. Volume progress seems to only have 3 values as well 0%, 99%, and 100%

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.