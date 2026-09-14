"""Read the latest value of a localStorage key out of Chrome's LevelDB files, compressed blocks included."""
import os, glob, json, re, struct
import cramjam

LDB = os.path.join(os.environ['LOCALAPPDATA'], 'Google/Chrome/User Data/Default/Local Storage/leveldb')

def _varint(b, i):
    r = 0; sh = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7f) << sh; sh += 7
        if not c & 0x80: return r, i

def _block(f, off, size):
    data = f[off:off + size]; typ = f[off + size]
    if typ == 1: data = bytes(cramjam.snappy.decompress_raw(data))
    return data

def _entries(block):
    """Yield (key, value) from a LevelDB block (ignores restart array)."""
    n_restarts = struct.unpack('<I', block[-4:])[0]
    end = len(block) - 4 - 4 * n_restarts
    i = 0; key = b''
    while i < end:
        shared, i = _varint(block, i); non_shared, i = _varint(block, i); vlen, i = _varint(block, i)
        key = key[:shared] + block[i:i + non_shared]; i += non_shared
        val = block[i:i + vlen]; i += vlen
        yield key, val

def _ldb_values(path):
    f = open(path, 'rb').read()
    if len(f) < 48: return
    footer = f[-48:]
    _, p = _varint(footer, 0); _, p = _varint(footer, p)          # metaindex handle
    ioff, p = _varint(footer, p); isize, p = _varint(footer, p)    # index handle
    for _, v in _entries(_block(f, ioff, isize)):
        off, q = _varint(v, 0); size, q = _varint(v, q)
        for k, val in _entries(_block(f, off, size)):
            yield k, val

def _log_values(path):
    """Write-ahead log: scan raw bytes for the key and the JSON that follows."""
    b = open(path, 'rb').read()
    for m in re.finditer(rb'hundredApps\.v1', b):
        yield b'hundredApps.v1', b[m.end():m.end() + 200000]

def _decode(val):
    if not val: return None
    if val[0] == 0: s = val[1:].decode('utf-16-le', 'replace')
    elif val[0] == 1: s = val[1:].decode('latin1')
    else:
        s = val.decode('latin1')
        j = s.find('{"apps"'); s = s[j:] if j >= 0 else s
    j = s.find('{"apps"')
    if j < 0: return None
    depth = 0; out = ''
    for ch in s[j:]:
        out += ch
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: break
    try: return json.loads(out)
    except Exception: return None

def latest_state(key=b'hundredApps.v1'):
    best = None
    files = sorted(glob.glob(os.path.join(LDB, '*.ldb')) + glob.glob(os.path.join(LDB, '*.log')), key=os.path.getmtime)
    for path in files:
        try:
            it = _log_values(path) if path.endswith('.log') else _ldb_values(path)
            for k, v in it:
                if key in k:
                    d = _decode(v)
                    if d: best = d
        except Exception as e:
            pass
    return best

if __name__ == '__main__':
    d = latest_state()
    print('found' if d else 'nothing', [(a['n'], a['name']) for a in d['apps'] if a.get('name')] if d else '')
