import ovh

server = ''

client = ovh.Client()
domains = client.get('/dedicated/server/{}/secondaryDnsDomains'.format(server))

for domain in domains:
    client.delete('/dedicated/server/{}/secondaryDnsDomains/{}'.format(server, domain))
    print('Removed secondary DNS for {}'.format(domain))