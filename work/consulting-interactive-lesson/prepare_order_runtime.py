"""Workspace-local PHP and the official, checksummed Dompdf distribution."""
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, zipfile

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / '.runtime'
MODULE = HERE / 'checkout-module'


def install(url, expected, target):
    target.mkdir(parents=True, exist_ok=True)
    archive = RUNTIME / (target.name + '.zip')
    if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        data = urlopen(Request(url, headers={'User-Agent': 'TopEngineer-local-build'}), timeout=60).read()
        assert hashlib.sha256(data).hexdigest() == expected, 'Official archive checksum mismatch'
        archive.write_bytes(data)
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            assert (target / member.filename).resolve().is_relative_to(target.resolve())
        package.extractall(target)
    return {'url': url, 'sha256': expected}


if __name__ == '__main__':
    RUNTIME.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = [
            pool.submit(install, 'https://downloads.php.net/~windows/releases/php-8.4.27-nts-Win32-vs17-x64.zip', '93bd8a815a52156606fb906d0573437908c61f96e2cc52c03a51e36a41bf5236', RUNTIME / 'php84'),
            pool.submit(install, 'https://github.com/dompdf/dompdf/releases/download/v3.1.6/dompdf-3.1.6.zip', '05df8ee4907325ed2e09a139de9784325f761b43a049297155499270163ac94d', MODULE / 'vendor'),
        ]
        versions = [task.result() for task in tasks]
    extension = (RUNTIME / 'php84/ext').as_posix()
    (RUNTIME / 'php84/php.ini').write_text(f'''extension_dir="{extension}"
extension=mbstring
extension=openssl
extension=pdo_sqlite
extension=sqlite3
extension=gd
extension=fileinfo
extension=zip
date.timezone=Europe/Belgrade
memory_limit=256M
max_execution_time=45
display_errors=Off
log_errors=On
''', encoding='utf-8')
    (RUNTIME / 'versions.json').write_text(json.dumps(versions, indent=2), encoding='utf-8')
    print('Official PHP 8.4.27 and Dompdf 3.1.6 verified and installed locally.')
