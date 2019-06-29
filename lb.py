import sys
import boto3
import requests

try:
    action = sys.argv[1]
    if action not in ['register', 'deregister']:
        raise ValueError('action')
    targets_str = sys.argv[2]
    targets = [(t.split(',')[0].strip(), int(t.split(',')[1].strip()))
               for t in targets_str.split(';')]
except:
    print('python lb.py register|deregister targetArn1,port1;targetArn2,port2')
    exit(1)


requests.adapters.DEFAULT_RETRIES = 5
metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
metadata = requests.get(metadata_url, timeout=10).json()
region = metadata['region']
instance_id = metadata['instanceId']

boto3.setup_default_session(region_name=region)
client = boto3.client('elbv2')
action_method = client.deregister_targets if action == 'deregister' else client.register_targets

for target in targets:
    print (action_method(
        TargetGroupArn=target[0],
        Targets=[
            {
                'Id': instance_id,
                'Port': target[1],
            },
        ]
    ))
