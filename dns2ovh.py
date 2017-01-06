import ovh
import re
import time

client = ovh.Client()

with open('go.txt') as fp:
    for line in fp:
        domain = line.strip()
        print(domain)

        # Activate zone
        try:
            client.post('/domain/{}/activateZone'.format(domain))
            print('Zone activated')
            time.sleep(1)
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)

        # Delete task in error
        tasks = client.get('/domain/{}/task'.format(domain), status='error')
        for task in tasks:
            print(task)
            client.post('/domain/{}/task/{}/cancel'.format(domain, task))
            print('Canceled domain task {} that was in error'.format(task))

        tasks = client.get('/domain/zone/{}/task'.format(domain), status='error')
        for task in tasks:
            if client.get('/domain/zone/{}/task/{}'.format(domain, task))['function'] != 'DnssecEnable':
                client.post('/domain/zone/{}/task/{}/cancel'.format(domain, task))
                print('Canceled zone task {} that was in error'.format(task))

        # Retrieve OVH NS
        ovh_ns = client.get('/domain/zone/{zone_name}'.format(zone_name=domain))['nameServers']
        print('OVH NS:', ovh_ns)
        if len(ovh_ns) < 2:
            client.post('/domain/zone/{zone_name}/reset'.format(zone_name=domain), minimized=False)
            time.sleep(10)
            ovh_ns = client.get('/domain/zone/{zone_name}'.format(zone_name=domain))['nameServers']
            print('OVH NS:', ovh_ns)
            if len(ovh_ns) < 2:
                raise Exception('DNS have not been reset')
                exit(1)

        # Fix zone
        zone = open('zones/{}.hosts'.format(domain)).read()
        for i, old_ns in enumerate(re.findall('IN\s+NS\s+(.*)$', zone, re.MULTILINE)):
            zone = zone.replace(old_ns, ovh_ns[i]+'.')
            print('Replaced in zone NS {} by {}'.format(old_ns, ovh_ns[i]+'.'))

        try:
            task = client.post(
                '/domain/zone/{zone_name}/import'.format(zone_name=domain),
                zoneFile=zone)
            print('Import task {id} added'.format(id=task['id']))

            while True:
                print('waiting')
                time.sleep(10)
                if client.get('/domain/zone/{service_name}/task/{id}'.format(service_name=domain, id=task['id']))['status'] == 'done':
                    break

            print('Zone imported')
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)

        # Set NS to external
        try:
            client.put('/domain/{}'.format(domain), nameServerType='external')
            print('Set NS to external')
            time.sleep(1)
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)


        # Fix NS
        try:
            client.post('/domain/{}/nameServers/update'.format(domain), nameServers=[{'host': ns} for ns in ovh_ns])
            print('Fixed NS')
            time.sleep(1)
        except ovh.exceptions.APIError as err:
            print(err)
            if str(err) != 'Name server are already good':
                exit(1)

        # Set NS to hosted
        try:
            client.put('/domain/{}'.format(domain), nameServerType='hosted')
            print('Set NS to hosted')
            time.sleep(1)
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)

        # Activate DNSSEC
        try:
            client.post('/domain/zone/{}/dnssec'.format(domain))
            print('DNSSEC activated')
        except ovh.exceptions.BadParametersError as err:
            print('DNSSEC already activated')

        time.sleep(1)