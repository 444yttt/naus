"""Reassemble the handoff ZIP, verify hashes, optionally extract to a new folder."""
from pathlib import Path
import argparse, json, hashlib, zipfile

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    m=json.loads((root/'release_parts.json').read_text(encoding='utf8'))
    for part in m['parts']:
        p=root/part['name']
        if not p.is_file() or p.stat().st_size!=part['bytes'] or digest(p)!=part['sha256']:
            raise SystemExit('Missing or damaged part: '+part['name'])
        print('Verified',p.name,flush=True)
    out=root/m['archive']
    if out.exists():
        if digest(out)!=m['archive_sha256']:raise SystemExit('Existing archive hash differs; choose a clean folder.')
    else:
        with out.open('xb') as dst:
            for part in m['parts']:
                with (root/part['name']).open('rb') as src:
                    for block in iter(lambda:src.read(8*1024*1024),b''):dst.write(block)
    if digest(out)!=m['archive_sha256']:raise SystemExit('Reassembled archive hash failed.')
    print('Archive SHA256 verified:',out.name,flush=True)
    if args.extract:
        target=args.extract.resolve()
        if target.exists():raise SystemExit('Extraction destination must be a new directory.')
        with zipfile.ZipFile(out) as z:
            for entry in z.infolist():
                if not (target/entry.filename).resolve().is_relative_to(target):raise SystemExit('Unsafe ZIP path.')
            bad=z.testzip()
            if bad:raise SystemExit('ZIP CRC failed: '+bad)
            target.mkdir(parents=True)
            z.extractall(target)
        print('Extracted:',target,flush=True)

if __name__=='__main__':main()

