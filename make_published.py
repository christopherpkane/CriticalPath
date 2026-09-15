#!/usr/bin/env python3
"""Turn a locked copy into the page that gets published.

The locked copy the app produces is already almost right — connection encrypted, no
schedule data in it. Two things this fixes:

  * The Sharing tab keeps a rendered note saying "Storing the schedule at <project URL>".
    It is only a leftover of what was on screen when the copy was made, and the app
    rewrites it on load anyway — but on a public page it names the project for no reason.
    Scrubbed here, and 'connectedWhere' is added to the app's own blank-on-save list so
    the next locked copy never has it in the first place.

  * Confirms, rather than assumes, that nothing readable is left: no key, no project URL,
    connection blanked, lock present.
"""
import io, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
s = io.open(SRC, encoding='utf-8').read()
did = []


def sub(tag, pattern, repl, count=1, regex=True):
    global s
    if regex:
        n = len(re.findall(pattern, s))
        assert n >= count, f'{tag}: expected at least {count} match(es), found {n}'
        s = re.sub(pattern, repl, s, count=count)
    else:
        n = s.count(pattern)
        assert n == count, f'{tag}: expected {count} match(es), found {n}'
        s = s.replace(pattern, repl, count)
    did.append(tag)


# ---------------------------------------------------------------- 1. scrub the leftover
sub('note',
    r'(<p class="info-note" id="connectedWhere"[^>]*>).*?(</p>)',
    r'\1\2')

# ---------------------------------------------------------------- 2. and stop it recurring
sub('blanklist',
    "'riAskBar','riLockBar','coAskBar','ajJobManage','jvBody','jvHead','jvCount','jvJob']",
    "'riAskBar','riLockBar','coAskBar','ajJobManage','jvBody','jvHead','jvCount','jvJob',"
    "'connectedWhere']",
    regex=False)

io.open(OUT, 'w', encoding='utf-8').write(s)
print(f'{SRC} -> {OUT}   fixed: {", ".join(did)}')

# ---------------------------------------------------------------- 3. prove it is clean
checks = {
  'connection blanked':
      bool(re.search(r'window\.CRITICAL_PATH_CONFIG = \{"supabaseUrl":"","supabaseKey":""\};', s)),
  'lock present':
      bool(re.search(r'window\.CRITICAL_PATH_LOCK = \{[^;]*"ct":"', s)),
  'no project URL anywhere':
      'supabase.co' not in s or not re.search(r'https://[a-z0-9]{15,}\.supabase\.co', s),
  'no publishable key anywhere':
      not re.search(r'sb_publishable_[A-Za-z0-9_\-]{10,}', s),
  'no schedule data':
      '"jobs":["' not in s or s.count('"jobs":[""') > 0,
}
print()
for k, v in checks.items():
    print(f'  {"OK  " if v else "FAIL"} {k}')
if not all(checks.values()):
    sys.exit('that copy is not safe to publish')
print('\nsafe to publish')
