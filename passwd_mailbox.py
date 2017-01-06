import ovh

client = ovh.Client()

with open('emails.csv') as fp:
    for line in fp:
        domain, mailbox, password = line.strip().split(',')

        print(domain)
        try:
            print('Changing {mailbox}@{domain} password to {password}'.format(mailbox=mailbox, domain=domain, password=password))
            result = client.post('/email/domain/{domain}/account/{accountName}/changePassword'.format(domain=domain, accountName=mailbox), password=password)
            print('password updated')
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)