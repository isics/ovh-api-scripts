import ovh

client = ovh.Client()

with open('mx_to_order.csv') as fp:
    for line in fp:
        domain, plan = line.split(',')
        plan = plan.strip()

        try:
            result = client.post('/order/email/domain/new/12', domain=domain, offer=plan)
            print(domain, result['orderId'], result['url'])
        except ovh.exceptions.APIError as err:
            print(err)
            exit(1)