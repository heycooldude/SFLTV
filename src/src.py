import json
from dateutil import rrule
from dateutil.parser import parse


class LTVCalculator:
    def __init__(self):
        self.customers = {}

    def ingest(self, event):
        event_type = event['type']
        customer_id = event['key'] if event_type == 'CUSTOMER' else event['customer_id']
        t = parse(event['event_time'])

        if customer_id not in self.customers:
            self.customers[customer_id] = {
                'visits': 0,
                'images': 0,
                'total_spending': 0.0,
                'event_entry': None,
                'event_exit': None
            }

        customer = self.customers[customer_id]

        ### exit time is always greater or equal to entry time

        if customer['event_exit']:
            customer['event_exit'] = t if t > customer['event_exit'] else customer['event_exit']
        else:
            customer['event_exit'] = t
        # customer['event_exit'] = parse(event['event_time'])
        if event_type == 'CUSTOMER':
            if customer['event_entry'] is None:
                customer['event_entry'] = parse(event['event_time'])

        elif event_type == 'SITE_VISIT':
            customer['visits'] += 1

        elif event_type == 'IMAGE':
            customer['images'] += 1

        elif event_type == 'ORDER':
            customer['total_spending'] += float(event['total_amount'].split(" ")[0])

    def calculate_avg_weekly_expenditure(self, customer_id):
        customer = self.customers[customer_id]
        avg_expenditure_per_visit = customer['total_spending'] / customer['visits']
        weeks = rrule.rrule(rrule.WEEKLY, dtstart=customer['event_entry'], until=customer['event_exit']).count()
        avg_weekly_visit = customer['visits'] / weeks
        return avg_expenditure_per_visit * avg_weekly_visit

    def calculate_top_x_ltv_customers(self, x):

        top_customers = []
        for customer_id in self.customers:
            avg_w_exp = self.calculate_avg_weekly_expenditure(customer_id)
            customer_simple_ltv = avg_w_exp * 52 * 10
            top_customers.append((customer_id, customer_simple_ltv))

        top_customers.sort(key=lambda x: x[1], reverse=True)
        return top_customers[:x]


def ingest_events(events, D):
    for event in events:
        D.ingest(event)


def TopXSimpleLTVCustomers(x, D):
    return D.calculate_top_x_ltv_customers(x)


if __name__ == '__main__':
    D = LTVCalculator()

    with open('input.txt') as infile:
        events = json.load(infile)

    # Ingest events
    ingest_events(events, D)

    x =10
    # Calculate and print top x customers with highest Simple LTV
    top_customers = TopXSimpleLTVCustomers(x, D)

    with open('output.txt', 'w') as outfile:
        for customerID, ltv in top_customers:
            out_str = "Customer ID: " + str(customerID) + ", LTV: " + str(ltv)
            outfile.write("%s\n" % out_str)
