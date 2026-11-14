"""FICTIONAL preview: bidirectional trains, never an agency timetable."""
from pathlib import Path
from fixtures.make_demo import TABLES, build


def tables():
    result = dict(TABLES)
    for tid, first, last, a, b in [
        ('demo-out', '16:00:00', '16:30:00', 'fixture-w', 'fixture-h'),
        ('demo-return', '21:30:00', '22:00:00', 'fixture-h', 'fixture-w'),
        ('demo-last', '23:00:00', '23:30:00', 'fixture-h', 'fixture-w')]:
        result['trips'] += f'r,daily,{tid},FICTIONAL preview\n'
        result['stop_times'] += f'{tid},{first},{first},{a},1\n{tid},{last},{last},{b},2\n'
    return result


if __name__ == '__main__':
    build(Path(__file__).with_name('preview.zip'), tables())
