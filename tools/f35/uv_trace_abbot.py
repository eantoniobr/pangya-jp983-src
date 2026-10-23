#!/usr/bin/env python3
"""A183: uv_trace.py + sala de prática sempre no Abbot Mine (0x14) para reproduzir o A182.1 (só na cópia)."""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uv_trace.py')).read())
patch('src/projectg/lobbymain.cpp', [(b'course = PickRandomCourse983();', b'course = 0x14;')])
print('uv_trace_abbot: ok')
