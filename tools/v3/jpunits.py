"""V7: unidades novas do JP (frente B) no formato de pgbuild.units() — lista em src/projectg/jp/units.txt (um .cpp por linha,
`#` comenta). Mesmos includes do tools/f37/jpbuild.py: include/jp e src/projectg/jp na frente, stdafx.h do exe por /FI, sem pch."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def units():
    lst = R + '/src/projectg/jp/units.txt'
    if not os.path.exists(lst): return []
    us = ['src/projectg/jp/' + l.split('#')[0].strip() for l in open(lst) if l.split('#')[0].strip()]
    return [(u, None, None, ['/FIstdafx.h'], ['include/jp', 'src/projectg/jp']) for u in us if os.path.exists(R + '/' + u)]
