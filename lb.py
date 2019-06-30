import os
import signal
import sys
import time

import boto3
import requests

run = True


def handler_stop_signals(signum, frame):
    global run
    run = False


def parse_targets():
    try:
        targets_str = os.environ.get('LB_TARGETS')
        targets = []
        for target_str in targets_str.split(';'):
            if '|' in target_str:
                tmp = target_str.split('|')
                if len(tmp) != 2:
                    raise ValueError('target')
                targets.append((tmp[0].strip(), int(tmp[1].strip())))
            else:
                targets.append(target_str.strip())
        if not targets:
            raise ValueError('target')

        print("Targets: %s" % str(targets))
        return targets
    except:
        print("Example: LB_TARGETS=arn1;arn2|port2;arn3|port3")
        exit(1)


def fetch_instance_id():
    requests.adapters.DEFAULT_RETRIES = 5
    metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
    metadata = requests.get(metadata_url, timeout=10).json()
    region = metadata['region']
    boto3.setup_default_session(region_name=region)
    return metadata['instanceId']


def elb_hook(action_method, targets, instance_id):
    for target in targets:
        resp = action_method(
            TargetGroupArn=target[0],
            Targets=[
                {
                    'Id': instance_id,
                    'Port': target[1],
                },
            ]
        )
        print("%s %s" % (str(target), resp))


def register(targets, instance_id):
    client = boto3.client('elbv2')
    action_method = client.register_targets
    print('Start register targets')
    elb_hook(action_method, targets, instance_id)


def deregister(targets, instance_id):
    client = boto3.client('elbv2')
    action_method = client.deregister_targets
    print('Start deregister targets')
    elb_hook(action_method, targets, instance_id)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    targets = parse_targets()
    instance_id = fetch_instance_id()
    register(targets, instance_id)

    while True:
        time.sleep(1000)

        if not run:
            print('Receive SIGINT or SIGTERM')
            deregister(targets, instance_id)
            exit(0)
