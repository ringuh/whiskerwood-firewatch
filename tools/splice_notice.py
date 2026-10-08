"""Splice the 1.1 deprecation notice into the current BP_MapLoad paste text.
usage: python splice_notice.py current.txt notice_snippet.txt out.txt
Both attach paths (HUD -> Stop1, viewport fallback -> Stop2) run CreateNotice -> ShowNotice -> Stop1; Stop2 is dropped."""
import re, sys
cur = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n')
snip = open(sys.argv[2], encoding='utf-8').read().replace('\r\n', '\n')

def blocks(t):
    return re.findall(r'Begin Object Class=\S+ Name="([^"]+)".*?\nEnd Object', t, re.S), \
           re.findall(r'(Begin Object Class=\S+ Name="[^"]+".*?\nEnd Object)', t, re.S)
def pin_id(block, pname):
    return re.search(r'PinId=([0-9A-F]{32}),PinName="%s"' % pname, block).group(1)
def set_links(block, pname, links):
    pat = re.compile(r'(CustomProperties Pin \(PinId=[0-9A-F]{32},PinName="%s",.*?)(LinkedTo=\([^)]*\),)?(PersistentGuid=)' % pname)
    lk = 'LinkedTo=(%s),' % ''.join('%s %s,' % l for l in links) if links else ''
    new, n = pat.subn(lambda m: m.group(1) + lk + m.group(3), block, count=1)
    assert n == 1, (pname, block[:120]); return new

names, objs = blocks(cur)
B = dict(zip(names, objs))
_, sobjs = blocks(snip)
S = {re.search(r'Name="([^"]+)"', o).group(1): o for o in sobjs}
cn, sn = S['CreateNotice'], S['ShowNotice']
assert 'CreateNotice' not in B and 'Stop2' in B and 'Stop1' in B

cn_exec, cn_then, cn_owner, cn_ret = (pin_id(cn, p) for p in ('execute', 'then', 'OwningPlayer', 'ReturnValue'))
sn_exec, sn_then, sn_self = (pin_id(sn, p) for p in ('execute', 'then', 'self'))
stop1_exec = pin_id(B['Stop1'], 'execute')
pc_ret = pin_id(B['PC'], 'ReturnValue')

# existing links into the two stops -> CreateNotice
B['SetOffs'] = set_links(B['SetOffs'], 'then', [('CreateNotice', cn_exec)])
B['SetVA'] = set_links(B['SetVA'], 'then', [('CreateNotice', cn_exec)])
B['ToViewport'] = set_links(B['ToViewport'], 'then', [('CreateNotice', cn_exec)])
B['Stop1'] = set_links(B['Stop1'], 'execute', [('ShowNotice', sn_then)])
# PC also feeds the notice
m = re.search(r'PinName="ReturnValue",.*?LinkedTo=\(([^)]*)\)', B['PC']).group(1)
B['PC'] = set_links(B['PC'], 'ReturnValue', [tuple(x.split(' ')) for x in m.split(',') if x] + [('CreateNotice', cn_owner)])
del B['Stop2']

cn = set_links(cn, 'execute', [('SetOffs', pin_id(B['SetOffs'], 'then')), ('SetVA', pin_id(B['SetVA'], 'then')),
                               ('ToViewport', pin_id(B['ToViewport'], 'then'))])
cn = set_links(cn, 'OwningPlayer', [('PC', pc_ret)])
cn = set_links(cn, 'then', [('ShowNotice', sn_exec)])
cn = set_links(cn, 'ReturnValue', [('ShowNotice', sn_self)])
sn = set_links(sn, 'execute', [('CreateNotice', cn_then)])
sn = set_links(sn, 'self', [('CreateNotice', cn_ret)])
sn = set_links(sn, 'then', [('Stop1', stop1_exec)])
# place near Stop1
sp = re.search(r'NodePosX=(-?\d+)\n\s*NodePosY=(-?\d+)', B['Stop1']); x, y = int(sp.group(1)), int(sp.group(2))
cn = re.sub(r'NodePosX=-?\d+\n(\s*)NodePosY=-?\d+', 'NodePosX=%d\n\\1NodePosY=%d' % (x - 700, y + 250), cn)
sn = re.sub(r'NodePosX=-?\d+\n(\s*)NodePosY=-?\d+', 'NodePosX=%d\n\\1NodePosY=%d' % (x - 350, y + 250), sn)
cn = cn.replace(':EventGraph.CreateNotice', ':EventGraph.CreateNotice'); 

out = '\n'.join([B[n] for n in names if n in B] + [cn, sn]) + '\n'
# validate links both ways
allnames = set(re.findall(r'Begin Object Class=\S+ Name="([^"]+)"', out))
ids = {}
for o in re.findall(r'(Begin Object Class=\S+ Name="[^"]+".*?\nEnd Object)', out, re.S):
    nm = re.search(r'Name="([^"]+)"', o).group(1)
    for pid, lk in re.findall(r'PinId=([0-9A-F]{32}),PinName="[^"]+",[^\n]*?(?:LinkedTo=\(([^)]*)\))?,PersistentGuid', o):
        ids[(nm, pid)] = [tuple(l.split(' ')) for l in lk.split(',') if l]
bad = [(a, b) for a, ls in ids.items() for b in ls if b not in ids or a not in ids[b]]
print(len(allnames), 'nodes', 'BAD' if bad else 'links ok', bad[:5])
open(sys.argv[3], 'w', encoding='utf-8', newline='\r\n').write(out)
