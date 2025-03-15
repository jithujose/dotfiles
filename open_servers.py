#!/usr/bin/env python3.7

import iterm2
import subprocess
import json
# This script was created with the "basic" environment which does not support adding dependencies
# with pip.

sshUser = 'jjose'

async def init_session(current_tab, instance, environment, split=False):
    ipAddress = instance['PublicIpAddress']
    if ipAddress is None:
        return False

    if environment not in instance['Name']:
        return False

    session = (await current_tab.current_session.async_split_pane(vertical=True)) if split else current_tab.current_session
    await session.async_set_name(instance['Name'] + ' - ' + ipAddress)
    await session.async_send_text('ssh ' + sshUser + '@' + ipAddress)
    
    return True

async def main(connection):
    # Your code goes here. Here's a bit of example code that adds a tab to the current window:
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window
    if window is not None:
        current_tab = await window.async_create_tab()

        alert = iterm2.TextInputAlert('Input your AWS profile', '', '', '')
        profile = await alert.async_run(connection)

        alert_environment = iterm2.TextInputAlert('Input your environment', '', '', '')
        environment = await alert_environment.async_run(connection)

        # alert = iterm2.TextInputAlert('Input your AWS Region', '', '', 'eu-west-1')
        # region = await alert.async_run(connection)
        region = 'eu-west-1'

        result = subprocess.run(['/usr/local/bin/aws', 'ec2', 'describe-instances', '--region', region, '--filters', 'Name=instance-state-name,Values=running', '--query', 'Reservations[*].Instances[*].{PublicIpAddress:PublicIpAddress,PrivateIpAddress:PrivateIpAddress,Name:Tags[? Key == \'Name\']|[0].Value,LaunchTime:LaunchTime}', '--profile', profile, '--output', 'json'], stdout=subprocess.PIPE)
        instances_list = json.loads(result.stdout)

        instances_full_list = []
        for instances in instances_list:
            for instance in instances:
                instances_full_list.append(instance)

        initialSessionUsed = False
        for i, instance in enumerate(instances_full_list):
            used = await init_session(current_tab, instance, environment, initialSessionUsed)
            if not initialSessionUsed and used:
                initialSessionUsed = True

    else:
        # You can view this message in the script console.
        print("No current window")

iterm2.run_until_complete(main)
