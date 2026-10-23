#!/usr/bin/env python3
# F3.2: o VS2010 que temos (Express/SDK 7.1) não traz ATL; o ATL 7.1 do rebang não compila no cl 16 (C2299, C3203).
# Gera em build/atl71 (fora do git) uma cópia de tools/VC7.1/atlmfc/include do rebang com os consertos mínimos de
# conformidade. Cada conserto é uma troca de texto exata; se o texto não existir, falha (cabeçalho mudou).
import os, sys, shutil
SRC = '/root/rebang/tools/VC7.1/atlmfc/include'
dst = sys.argv[1]
FIX = {
 'atlcomcli.h': [("\ttemplate <>\n\tT* operator=(const CComPtr<T>& lp) throw()", "\tT* operator=(const CComPtr<T>& lp) throw()")],
 'atlcom.h': [("dispid, (void (__stdcall _atl_event_classtype::*)())fn, info},", "dispid, (void (__stdcall _atl_event_classtype::*)())&_atl_event_classtype::fn, info},")],  # C4867
 'atlbase.h': [
  ("\ttemplate<>\n\tCAutoPtr( CAutoPtr< T >& p ) throw()", "\tCAutoPtr( CAutoPtr< T >& p ) throw()"),
  ("\ttemplate<>\n\tCAutoPtr< T >& operator=( CAutoPtr< T >& p ) throw()", "\tCAutoPtr< T >& operator=( CAutoPtr< T >& p ) throw()"),
  ("public CAtlAutoThreadModuleT<CComAutoThreadModule, ThreadAllocator, dwWait>",
   "public CAtlAutoThreadModuleT<CComAutoThreadModule<ThreadAllocator, dwWait>, ThreadAllocator, dwWait>"),
 ],
}
if os.path.isdir(dst): shutil.rmtree(dst)
shutil.copytree(SRC, dst)
n = 0
for f, subs in FIX.items():
    p = os.path.join(dst, f); s = open(p, 'rb').read().decode('latin-1').replace('\r\n', '\n')
    for a, b in subs:
        if a not in s: sys.exit('atlfix: texto não achado em %s: %r' % (f, a[:60]))
        s = s.replace(a, b); n += 1
    open(p, 'wb').write(s.encode('latin-1'))
print('atl71: %d consertos em %d arquivos -> %s' % (n, len(FIX), dst))
