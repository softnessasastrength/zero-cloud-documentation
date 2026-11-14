"""Generate deterministic SYNTHETIC data, never an operational schedule."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

TABLES = {
'agency': 'agency_id,agency_name,agency_url,agency_timezone\na,FICTIONAL FIXTURE,https://example.invalid,America/New_York\n',
'stops': 'stop_id,stop_name,stop_lat,stop_lon\nfixture-h,Hartford Union Station,41.768,-72.682\nfixture-w,Windsor Locks,41.913,-72.626\nfixture-end,DEMO Terminus,42,-72\n',
'routes': 'route_id,agency_id,route_short_name,route_long_name,route_type\nr,a,DEMO,FICTIONAL,2\n',
'calendar': 'service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\ndaily,1,1,1,1,1,1,1,20260101,20271231\n',
'calendar_dates': 'service_id,date,exception_type\ndaily,20261225,2\nholiday,20261225,1\n',
 'trips': 'route_id,service_id,trip_id,trip_headsign\nr,daily,fixture-overnight,DEMO overnight\nr,holiday,fixture-holiday,DEMO holiday\nr,daily,fixture-day,DEMO daily\n',
'stop_times': 'trip_id,arrival_time,departure_time,stop_id,stop_sequence\nfixture-overnight,24:30:00,24:30:00,fixture-h,1\nfixture-overnight,24:50:00,24:50:00,fixture-w,2\nfixture-overnight,25:10:00,25:10:00,fixture-end,3\nfixture-holiday,10:00:00,10:00:00,fixture-h,1\nfixture-holiday,10:20:00,10:20:00,fixture-w,2\nfixture-holiday,10:40:00,10:40:00,fixture-end,3\nfixture-day,12:00:00,12:00:00,fixture-h,1\nfixture-day,12:20:00,12:20:00,fixture-w,2\nfixture-day,12:40:00,12:40:00,fixture-end,3\n'}


def build(path, tables=None):
    with ZipFile(path, 'w') as archive:
        for name, contents in sorted((tables or TABLES).items()):
            info = ZipInfo(name + '.txt', (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, contents)


if __name__ == '__main__':
    build(Path(__file__).with_name('demo.zip'))
