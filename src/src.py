import json
from dateutil import rrule, parser
import heapq


class Customer:
    """
    A customer object that stores the customer's visit count, image count, total spending, entry and exit event times.
    """

    def __init__(self):
        self.visits = 0
        self.images = 0
        self.total_spending = 0.0
        self.event_entry = None
        self.event_exit = None

    def __repr__(self):
        return (
            f"Customer(visits={self.visits}, images={self.images}, total_spending={self.total_spending}, "
            f"event_entry={self.event_entry}, event_exit={self.event_exit})"
        )


class LTVCalculator:
    """
    A class that calculates the LTV of customers.
    """

    def __init__(self):
        self.customers = {}

    def ingest(self, event):
        """
        Ingests an event and updates the LTV of the corresponding customer.

        Args:
            event (dict): The event to ingest.
        """
        # Extract event properties.
        event_type = event["type"]
        customer_id = event["key"] if event_type == "CUSTOMER" else event["customer_id"]
        event_time = parser.parse(event["event_time"])

        # Create or update customer data.
        if customer_id not in self.customers:
            self.customers[customer_id] = Customer()

        customer = self.customers[customer_id]

        # Update entry and exit event times.
        if customer.event_exit:
            customer.event_exit = max(event_time, customer.event_exit)
        else:
            customer.event_exit = event_time

        if event_type == "CUSTOMER":
            if customer.event_entry is None:
                customer.event_entry = event_time

        elif event_type == "SITE_VISIT":
            customer.visits += 1

        elif event_type == "IMAGE":
            customer.images += 1

        elif event_type == "ORDER":
            customer.total_spending += float(event["total_amount"].split(" ")[0])

    def calculate_avg_weekly_expenditure(self, customer_id):
        """
        Calculates the average weekly expenditure of the customer.

        Args:
            customer_id (str): The customer ID.

        Returns:
            float: The average weekly expenditure.
        """
        customer = self.customers[customer_id]
        avg_expenditure_per_visit = customer.total_spending / customer.visits
        weeks = rrule.rrule(rrule.WEEKLY, dtstart=customer.event_entry, until=customer.event_exit).count()
        avg_weekly_visit = customer.visits / weeks
        return avg_expenditure_per_visit * avg_weekly_visit

    def calculate_top_x_ltv_customers(self, x):
        """
        Calculates the top x customers with the highest LTV.

        Args:
            x (int): The number of customers to return.

        Returns:
            list: The list of top x customers.
        """
        top_customers = []
        for customer_id in self.customers:
            # Calculate the Simple LTV.
            ltv = self.calculate_avg_weekly_expenditure(customer_id) * 52 * 10
            # Use a min-heap to maintain the top x customers.
            if len(top_customers) < x:
                heapq.heappush(top_customers, (ltv, customer_id))
            else:
                heapq.heappushpop(top_customers, (ltv, customer_id))

        # Extract the top x customers from the min-heap.
        top_customers = [(customer_id, ltv) for ltv, customer_id in heapq.nlargest(x, top_customers)]

        return top_customers


def ingest_events(events, ltv_calculator):
    """
    Ingests events into the LTVCalculator.

    Args:
        events (list): The list of events.
        ltv_calculator (LTVCalculator): The LTVCalculator.
    """
    for event in events:
        # Ingest each event into the LTVCalculator.
        ltv_calculator.ingest(event)


def main():
    ltv_calculator = LTVCalculator()

    with open("input.txt", "r") as infile:
        events = json.load(infile)

    # Ingest events.
    ingest_events(events, ltv_calculator)

    x = 10
    # Calculate and print top x customers with the highest Simple LTV.
    top_customers = ltv_calculator.calculate_top_x_ltv_customers(x)

    with open("output.txt", "w") as outfile:
        for customer_id, ltv in top_customers:
            out_str = f"Customer ID: {customer_id}, LTV: {ltv}"
            outfile.write(f"{out_str}\n")


if __name__ == "__main__":
    main()

