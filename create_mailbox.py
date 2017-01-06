import json
import ovh
import time

client = ovh.Client()

with open('emails.csv') as fp:
    for line in fp:
        domain, mailbox, password = line.strip().split(',')

        print(domain)
        try:
            print('Creating {mailbox}@{domain}'.format(mailbox=mailbox, domain=domain))
            result = client.post('/email/domain/{domain}/account'.format(domain=domain), accountName=mailbox, password=password)
            print('created')
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)