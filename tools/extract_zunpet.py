"""Pull the "Romantic Tp" (ZUNpet) multisamples out of a SoundFont 2 file.

SF2 is a RIFF container, so this needs nothing but the standard library plus numpy.
Writes zunpet.npz (raw PCM per zone) and zunpet_zones.json (key ranges, root keys,
loop points) next to this script - both are gitignored, since they are derived from
a soundfont you supply rather than something this repo should redistribute.

    python extract_zunpet.py "TOUHOU INSTRUMENT + DRUM KIT.sf2" [--preset "Romantic Tp"]
"""
import argparse, json, os, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def read_chunks(f):
    """Walk the RIFF tree and record the offset/size of every leaf chunk."""
    f.seek(0)
    _riff, size, _form = struct.unpack('<4sI4s', f.read(12))
    chunks = {}

    def walk(end):
        while f.tell() < end - 8:
            cid = f.read(4)
            if len(cid) < 4:
                break
            (csz,) = struct.unpack('<I', f.read(4))
            pos = f.tell()
            if cid == b'LIST':
                f.read(4)
                walk(pos + csz)
            else:
                chunks[cid.decode('latin1')] = (pos, csz)
            f.seek(pos + csz + (csz & 1))

    walk(8 + size)
    return chunks


def records(f, chunks, name, fmt, size):
    pos, sz = chunks[name]
    f.seek(pos)
    return [struct.unpack(fmt, f.read(size)) for _ in range(sz // size)]


def extract(sf2_path, preset_name):
    with open(sf2_path, 'rb') as f:
        chunks = read_chunks(f)
        smpl_pos, _ = chunks['smpl']

        phdr = []
        pos, sz = chunks['phdr']
        f.seek(pos)
        for _ in range(sz // 38):
            d = f.read(38)
            phdr.append((d[:20].split(b'\0')[0].decode('latin1'),) + struct.unpack('<HHH', d[20:26]))

        pbag = records(f, chunks, 'pbag', '<HH', 4)
        pgen = records(f, chunks, 'pgen', '<HH', 4)
        ibag = records(f, chunks, 'ibag', '<HH', 4)
        igen = records(f, chunks, 'igen', '<HH', 4)

        inst = []
        pos, sz = chunks['inst']
        f.seek(pos)
        for _ in range(sz // 22):
            d = f.read(22)
            inst.append((d[:20].split(b'\0')[0].decode('latin1'), struct.unpack('<H', d[20:22])[0]))

        shdr = []
        pos, sz = chunks['shdr']
        f.seek(pos)
        for _ in range(sz // 46):
            d = f.read(46)
            shdr.append(dict(
                name=d[:20].split(b'\0')[0].decode('latin1').strip(),
                start=struct.unpack('<I', d[20:24])[0], end=struct.unpack('<I', d[24:28])[0],
                loops=struct.unpack('<I', d[28:32])[0], loope=struct.unpack('<I', d[32:36])[0],
                sr=struct.unpack('<I', d[36:40])[0], pitch=d[40],
                corr=struct.unpack('<b', d[41:42])[0]))

        # preset -> instrument (generator 41) -> sample (53), with key range (43) and root (58)
        zones, data = [], {}
        for i, (nm, _pno, _bank, pbagndx) in enumerate(phdr[:-1]):
            if nm.strip() != preset_name:
                continue
            for z in range(pbagndx, phdr[i + 1][3]):
                instid = next((pgen[g][1] for g in range(pbag[z][0], pbag[z + 1][0]) if pgen[g][0] == 41), None)
                if instid is None:
                    continue
                for iz in range(inst[instid][1], inst[instid + 1][1]):
                    sid = kr = root = None
                    for g in range(ibag[iz][0], ibag[iz + 1][0]):
                        op, amt = igen[g]
                        if op == 53:
                            sid = amt
                        elif op == 43:
                            kr = (amt & 0xFF, amt >> 8)
                        elif op == 58:
                            root = amt
                    if sid is None:
                        continue
                    s = shdr[sid]
                    zones.append(dict(name=s['name'], lo=kr[0], hi=kr[1], root=root or s['pitch'],
                                      start=s['start'], end=s['end'], loops=s['loops'],
                                      loope=s['loope'], sr=s['sr'], corr=s['corr']))
                    f.seek(smpl_pos + s['start'] * 2)
                    raw = f.read((s['end'] - s['start']) * 2)
                    data[s['name']] = np.frombuffer(raw, dtype='<i2').astype(np.float64) / 32768.0

    if not zones:
        raise SystemExit(f'preset {preset_name!r} not found in {sf2_path}')
    np.savez_compressed(os.path.join(HERE, 'zunpet.npz'), **data)
    with open(os.path.join(HERE, 'zunpet_zones.json'), 'w', encoding='utf-8') as out:
        json.dump(zones, out, indent=1)
    for z in zones:
        print(f"  {z['name']:<20} keys {z['lo']:3d}-{z['hi']:3d} root {z['root']:3d} "
              f"{len(data[z['name']]) / z['sr']:6.3f}s")
    print(f'{len(zones)} zones -> zunpet.npz, zunpet_zones.json')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('sf2')
    ap.add_argument('--preset', default='Romantic Tp')
    a = ap.parse_args()
    extract(a.sf2, a.preset)
