#!/usr/bin/env python3
"""Put the team-password lock into a build, so rebuilding the app never removes it.

The lock is a small blob of ciphertext: the Supabase connection encrypted under the team
password. The password itself is not in it and cannot be recovered from it, so the blob is
safe to keep in the repo and safe to hand to me — it is meant to be public, since it ships
inside the published page.

Two ways to run it:

    # take the blob out of a locked copy and keep it
    python3 gate_bake.py --from Brown_Haven_Critical_Path_LOCKED.html --save gate-lock.json

    # put a kept blob into a fresh build
    python3 gate_bake.py --lock gate-lock.json --into index.html

Baking also blanks the connection written in the clear, because a page carrying both would
be handing back exactly what the password is there to withhold.
"""
import argparse, io, json, re, sys

CFG = re.compile(r'window\.CRITICAL_PATH_CONFIG = \{[^;]*\};')
LOCK = re.compile(r'window\.CRITICAL_PATH_LOCK = [^;]*;')


def read(path):
    return io.open(path, encoding='utf-8').read()


def lock_from_html(path):
    m = LOCK.search(read(path))
    if not m:
        sys.exit(f'{path}: no lock line in that file at all.')
    raw = m.group(0).split('=', 1)[1].strip().rstrip(';').strip()
    if raw in ('null', ''):
        sys.exit(f'{path}: that copy is not locked — its lock is empty.\n'
                 'Make one with Sharing -> Team Password -> Download Locked Copy.')
    blob = json.loads(raw.replace('\\u003c', '<'))
    for k in ('salt', 'iv', 'ct'):
        if not blob.get(k):
            sys.exit(f'{path}: the lock is missing "{k}" — that file looks damaged.')
    return blob


def bake(target, blob):
    s = read(target)
    if not CFG.search(s):
        sys.exit(f'{target}: could not find the connection line to blank.')
    if not LOCK.search(s):
        sys.exit(f'{target}: could not find the lock line to write into.')
    # the connection travels encrypted or not at all
    s = CFG.sub('window.CRITICAL_PATH_CONFIG = {"supabaseUrl":"","supabaseKey":""};', s, count=1)
    js = json.dumps(blob, separators=(',', ':')).replace('<', '\\u003c')
    s = LOCK.sub(lambda _: 'window.CRITICAL_PATH_LOCK = ' + js + ';', s, count=1)
    io.open(target, 'w', encoding='utf-8').write(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='src', help='a locked copy to take the blob out of')
    ap.add_argument('--save', help='write the blob to this file')
    ap.add_argument('--lock', help='a blob file saved earlier')
    ap.add_argument('--into', help='the build to bake it into')
    a = ap.parse_args()

    blob = None
    if a.src:
        blob = lock_from_html(a.src)
        print(f'read the lock out of {a.src}')
    elif a.lock:
        blob = json.loads(read(a.lock))
    if blob is None:
        sys.exit('give me either --from <locked copy> or --lock <blob file>.')

    if a.save:
        io.open(a.save, 'w', encoding='utf-8').write(json.dumps(blob, indent=2))
        print(f'kept it in {a.save} — ciphertext only, no password in there')

    if a.into:
        bake(a.into, blob)
        print(f'baked into {a.into}: connection blanked, lock written')
        s = read(a.into)
        print('  check — connection line:', CFG.search(s).group(0)[:70])
        print('  check — locked         :', '"ct":"' in LOCK.search(s).group(0))


if __name__ == '__main__':
    main()
