from datetime import timedelta


def date_range(start_date, stop_date):
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta
