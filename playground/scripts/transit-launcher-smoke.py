"""Exercise launcher processes and cleanup against a labeled fixture store."""
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'transit'))
from fixtures.setup_preview import setup
with tempfile.TemporaryDirectory(prefix='percival-launcher-smoke-') as temp:
    setup(Path(temp)/'transit-data')
    env = os.environ | dict(PERCIVAL_CHROMEBOOK_DIR=temp, PERCIVAL_TRANSIT_LOCAL_CHECKOUT=str(root),
                            PERCIVAL_SKIP_PACKAGES='1', PERCIVAL_USE_SYSTEM_NODE='1')
    # Setup is verified by CI npm ci/build; avoid repeating dependency installation here.
    marker = root/'playground/node_modules/.percival-setup-complete'
    existed = marker.exists()
    marker.touch()
    with tempfile.TemporaryFile(mode='w+') as logs:
        child = subprocess.Popen(['bash',str(root/'playground/scripts/percival-chromebook.sh'),'transit'],
            env=env,stdin=subprocess.PIPE,stdout=logs,stderr=logs,text=True)
        child.stdin.write('n\n')
        child.stdin.close()
        try:
            for _ in range(120):
                if child.poll() is not None:
                    logs.seek(0)
                    raise RuntimeError(logs.read())
                try:
                    with urllib.request.urlopen('http://127.0.0.1:4183/transit-api/v1/health',timeout=1) as response:
                        assert response.status==200
                    break
                except OSError:
                    time.sleep(.25)
            else:
                raise RuntimeError('launcher did not become ready')
            with urllib.request.urlopen('http://127.0.0.1:4183/',timeout=2) as response:
                assert b'manifest.webmanifest' in response.read()
        finally:
            child.send_signal(signal.SIGTERM)
            child.wait(timeout=10)
            if not existed:
                marker.unlink(missing_ok=True)
        for port in (8765,4183):
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1)
            except OSError:
                continue
            raise AssertionError(f'owned server {port} survived launcher shutdown')
        print('Launcher passed: existing checkout/data preserved; fixture API + production Metro ready on loopback; SIGTERM cleaned up both owned processes. Dependency installation and ChromeOS forwarding remain hardware checks.')
