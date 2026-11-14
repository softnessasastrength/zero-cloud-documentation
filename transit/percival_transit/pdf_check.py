"""Capture official PDF text/OCR for reproducible timetable review; never invent overrides."""
import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

PDFS = {
 '82-84-weekday':'https://www.cttransit.com/sites/default/files/schedules/82_84_Weekday_Tolland.pdf',
 '82-84-saturday':'https://www.cttransit.com/sites/default/files/schedules/82_84_Saturday_Tolland.pdf',
 '905-weekday':'https://www.cttransit.com/sites/default/files/schedules/905_Weekday.pdf',
 '905-weekend':'https://www.cttransit.com/sites/default/files/schedules/h_905_sched_7.pdf',
}


def main():
    report = {}
    for key,url in PDFS.items():
        entry = dict(url=url, status='Unknown')
        try:
            request = urllib.request.Request(url,headers={'User-Agent':'PercivalTransit/0.1 timetable verification'})
            with urllib.request.urlopen(request,timeout=30) as response:
                raw = response.read(15_000_000)
            if not raw.startswith(b'%PDF'):
                raise ValueError('not a PDF')
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
            with tempfile.TemporaryDirectory() as temp:
                pdf = Path(temp)/'timetable.pdf'
                pdf.write_bytes(raw)
                output = subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
                if len(output.strip()) < 500:
                    subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(Path(temp)/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    output = '\n'.join(subprocess.check_output(['tesseract',str(page),'stdout'],text=True,stderr=subprocess.DEVNULL) for page in sorted(Path(temp).glob('page-*.png')))
                    entry['method']='OCR; inspect columns before asserting matches'
                else:
                    entry['method']='PDF text'
                entry['text']=output
                entry['status']='Retrieved'
        except Exception as exc:
            entry['error']=str(exc)
        report[key]=entry
    Path('pdf-smoke.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
