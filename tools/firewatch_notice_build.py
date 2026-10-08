"""Generates the Blueprint paste text (T3D) for FireWatch 1.1's deprecation notice into tools/out/.
Usage: python tools/firewatch_notice_build.py   (needs the modkit's jmap, see t3d.py)

FireWatch is deprecated in favour of Remote Campfire by Niklas. After a save loads, a yellow notice
sits at the top centre of the screen for NOTICE_SECONDS of real time, then removes itself.
It is placed just under TraitPeek's notice (Y=140, scale 1.6) so both can show at once.

- WBP_FireNotice (Widget BP, parent UserWidget). The designer holds the notice itself (see README);
  the graph: Construct -> click-through; Tick (real time: also counts while paused, not sped up by
  game speed) adds InDeltaTime to Waited and removes the widget after NOTICE_SECONDS.
- BP_MapLoad_notice: a snippet for BP_MapLoad (create WBP_FireNotice, add to viewport). Paste it
  next to the existing graph and splice it in right after the OnLoaded event.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from t3d import *

OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
M = '/Game/Mods/FireWatch/'
NOTICE = M + 'WBP_FireNotice'
NOTICE_SECONDS = '60.0'
KML = '/Script/Engine.KismetMathLibrary'
GEO = STRUCT('/Script/SlateCore.Geometry')

# =========================================================================== WBP_FireNotice
# Variables: Waited (Float)
g = Graph(NOTICE)
cs = g.event('/Script/UMG.UserWidget', 'Construct', [], 'Construct', 0, -300)
vis = g.call('/Script/UMG.Widget:SetVisibility', 'ClickThrough', 300, -300, InVisibility='HitTestInvisible'); ex(cs, vis)
tk = g.event('/Script/UMG.UserWidget', 'Tick', [('MyGeometry', GEO), ('InDeltaTime', FLT)], 'Tick', 0, 0)
wg = g.get('Waited', DBL, 0, 250, name='WaitedGet')
add = g.call(KML + ':Add_DoubleDouble', 'WaitedAdd', 200, 250); link(wg['Waited'], add['A']); link(tk['InDeltaTime'], add['B'])
sa = g.setv('Waited', DBL, 300, 0, name='SetWaited'); link(add['ReturnValue'], sa['Waited']); ex(tk, sa)
ge = g.call(KML + ':GreaterEqual_DoubleDouble', 'TimeUp', 500, 250, B=NOTICE_SECONDS); link(sa['Output_Get'], ge['A'])
bdue = g.branch(600, 0, 'BrTimeUp'); link(ge['ReturnValue'], bdue['Condition']); ex(sa, bdue)
rm = g.call('/Script/UMG.Widget:RemoveFromParent', 'HideNotice', 850, 0); ex(bdue, rm)
open(OUT + '/WBP_FireNotice.txt', 'w').write(g.text())

# =========================================================================== BP_MapLoad snippet
g = Graph(M + 'BP_MapLoad')
pc = g.call('/Script/Engine.GameplayStatics:GetPlayerController', 'NoticePC', 2000, 1400)
cn = g.create_widget(NOTICE, 2000, 1200, name='CreateNotice'); link(pc['ReturnValue'], cn['OwningPlayer'])
av = g.call('/Script/UMG.UserWidget:AddToViewport', 'ShowNotice', 2300, 1200, ZOrder='4')
link(cn['ReturnValue'], av['self']); ex(cn, av)
open(OUT + '/BP_MapLoad_notice.txt', 'w').write(g.text())

# =========================================================================== validation
import re as _re
for gname in ('WBP_FireNotice', 'BP_MapLoad_notice'):
    txt = open(os.path.join(OUT, gname + '.txt'), encoding='utf-8').read()
    names = set(_re.findall(r'Begin Object Class=\S+ Name="([^"]+)"', txt))
    bad = [r.strip() for m in _re.finditer(r'LinkedTo=\(([^)]*)\)', txt) for r in m.group(1).split(',')
           if r.strip() and r.strip().split(' ')[0] not in names]
    print(gname, len(names), 'nodes', 'BAD LINKS' if bad else 'links ok', bad[:5])
