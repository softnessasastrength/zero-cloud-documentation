"""A walking link needs evidence; coordinates alone never prove a transfer."""
from datetime import timedelta
from .core import instant


def check_transfer(arrival, departure, walk_seconds=None, buffer_seconds=120, walk_source=None):
    result = dict(status='Unknown', available_seconds=(instant(departure)-instant(arrival)).total_seconds(),
                  walking_seconds=walk_seconds, buffer_seconds=buffer_seconds, walking_source=walk_source)
    if walk_seconds is None or not walk_source:
        return result | {'reason':'Exact walking path and walking time are unverified.'}
    if walk_seconds < 0 or buffer_seconds < 0:
        return result | {'reason':'Invalid transfer margin.'}
    enough = instant(arrival) + timedelta(seconds=walk_seconds+buffer_seconds) <= instant(departure)
    return result | dict(status='Scheduled' if enough else 'Infeasible', reason='Scheduled transfer allowance satisfies the verified walk and buffer.' if enough else 'Insufficient time for the walking path and buffer.')


INTERCHANGES = {
    'bright-meadow': dict(stops={'cttransit':'7919','pvta':'10006'},
        source='https://www.pvta.com/schedules/G5.pdf',
        reason='Agency timetable advertises connections, but an exact pedestrian path and minimum walking time have not been independently verified.'),
    'windsor-locks': dict(stops={'rail':'8','cttransit':'13577'},
        source='https://www.cttransit.com/services/service-adjustments',
        reason='Both services call at the new station; a platform-to-bus pedestrian path and minimum walking time remain unverified.'),
}
