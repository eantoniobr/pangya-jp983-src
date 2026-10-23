#!/usr/bin/env python3
# tools/f37/fonts983.py (sessão B58) — construtores das fontes do titlefontex do 983 (006f4640–006f5780): classe (RTTI), WTITLEFONT e arquivos -> C++
import struct, capstone, sys
d = open('/root/jp983src/ref/ProjectG_983_dump.exe','rb').read()
B = 0x400000
def u32(va): return struct.unpack_from('<I', d, va - B)[0]
def cstr(va):
    o = va - B; return d[o:d.index(b'\0', o)].decode('latin1')
def rtti(vt):
    col = u32(vt - 4); td = u32(col + 12); return cstr(td + 8)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
OFF = {-0x30: 'filename', -0x2c: 'numPages', -0x28: 'fontw', -0x24: 'fonth', -0x20: 'texw', -0x1c: 'texh', -0x18: 'u18', -0x14: 'pCharSet'}
out = []
starts = [int(a, 16) for a in sys.argv[1:]]
for a in starts:
    code = d[a - B: a - B + 0x100]
    regs = {}; f = {}; vt = None
    for i in md.disasm(code, a):
        if i.mnemonic == 'ret': break
        ops = i.op_str
        if i.mnemonic == 'mov':
            dst, src = [x.strip() for x in ops.split(',', 1)]
            if dst in ('eax', 'ecx', 'edx') and src.startswith('0x'): regs[dst] = int(src, 16)
            if dst == 'dword ptr [esi]': vt = int(src, 16)
            if dst.startswith('dword ptr [ebp - '):
                off = -int(dst[len('dword ptr [ebp - '):-1], 16)
                if off in OFF:
                    v = int(src, 16) if src.startswith('0x') else (int(src) if src.isdigit() else regs.get(src, 0))
                    f[OFF[off]] = v
        if i.mnemonic == 'xor' and ops in ('eax, eax',): regs['eax'] = 0
    name = rtti(vt)[4:-2] if vt else '?'
    arr = f.get('filename', 0); files = []
    k = 0
    while arr and f.get('numPages', 0) > k:
        files.append(cstr(u32(arr + 4 * k))); k += 1
    out.append((a, name, vt, f, files, arr))
for a, name, vt, f, files, arr in out:
    cs = f.get('pCharSet', 0)
    print('// %08x (vtable %08x; nomes de arquivo em %08x)' % (a, vt, arr))
    print('%s::%s()\n{' % (name, name))
    print('\tstatic char* fileName[] = { %s };' % ', '.join('"%s"' % x for x in files))
    print('\tWTITLEFONT info;\n\tmemset(&info, 0, sizeof(info));\n')
    print('\tinfo.filename = fileName;')
    for k in ('fontw', 'fonth', 'numPages', 'texw', 'texh'):
        print('\tinfo.%s = %d;' % (k, f.get(k, 0)))
    if 'u18' in f and f['u18']: print('\t// +0x18 = %#x' % f['u18'])
    print('\tinfo.pCharSet = "%s";' % (cstr(cs).replace('\\', '\\\\').replace('"', '\\"') if cs else ''))
    print('\n\tm_pFont = g_resrcmng->GetTitleFont();\n\tm_pFont->Create(&info);\n}\n')
