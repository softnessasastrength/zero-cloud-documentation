"""Create an isolated clearly fictional three-feed store for browser/launcher tests."""
import io
import sys
from pathlib import Path
from fixtures.make_demo import TABLES, build
from fixtures.make_preview import tables
from percival_transit.core import import_feed
from percival_transit.feeds import feed_store


def setup(root):
    buffer = io.BytesIO()
    build(buffer, tables())
    import_feed(buffer.getvalue(), root, 'fixture:rail-preview', True)
    for feed in ('pvta', 'cttransit'):
        data = dict(TABLES)
        route_ids = [('G5','G5'),('R10','R10'),('R14','R14')] if feed == 'pvta' else [('16507','80'),('16508','82'),('16509','82/84'),('16510','83'),('16511','84'),('16545','905')]
        data['routes'] = 'route_id,agency_id,route_short_name,route_long_name,route_type\n' + ''.join(f'{rid},a,{label},FICTIONAL {label},3\n' for rid,label in route_ids)
        data['stops'] = ('stop_id,stop_name,stop_lat,stop_lon\n10006,MassMutual Enfield,42.01819,-72.584911\n1862,Jewish House,42.064024,-72.551578\n5111,Union Station Bay 11,42.105,-72.59\n' if feed=='pvta' else 'stop_id,stop_name,stop_lat,stop_lon\n7919,Bright Meadow Blvd @ Mass Mutual,42.018165,-72.58491\n13577,Windsor Locks RR Stn @ 229 Main St,41.932911,-72.627502\n')
        data['trips'] = 'route_id,service_id,trip_id,trip_headsign,direction_id\n'
        data['stop_times'] = 'trip_id,arrival_time,departure_time,stop_id,stop_sequence\n'
        for rid,label in route_ids:
            a,b = ('10006','1862') if feed=='pvta' else ('7919','13577')
            for suffix,src,dst,dep,arr,direction in [('out',a,b,'06:55:00','07:15:00','0'),('home',b,a,'15:08:00','15:25:00','1')]:
                tid = f'fixture-{feed}-{rid}-{suffix}'
                data['trips'] += f'{rid},daily,{tid},DEMO {label} {suffix},{direction}\n'
                data['stop_times'] += f'{tid},{dep},{dep},{src},1\n{tid},{arr},{arr},{dst},2\n'
        buffer = io.BytesIO()
        build(buffer,data)
        import_feed(buffer.getvalue(), feed_store(root,feed), 'fixture:'+feed, True)


if __name__ == '__main__':
    setup(Path(sys.argv[1]))
