# F3.5 (sessão 41): trocas em arquivos ainda importados pedidas pelas unidades Fresh adotadas. Lido por tools/f32/ajustes.py no fim.
# FrTabButton::AddTab(const char* imgNames[], index) perdeu o 3º argumento no 983 (00c07e10, ret 8).
NEW12 = [
 ('todos', 'src/projectg/shopmain.cpp', 'AddTab(names, %s, NULL)' % x, 'AddTab(names, %s)' % x,
  '983: FrTabButton::AddTab de lista de imagens não recebe mais o tamanho (00c07e10)')
 for x in ('i - 1', 'i', '5', '0x1a', '0x1b', '0x20', '0x21', '0x22', '10', '0xc')
]
