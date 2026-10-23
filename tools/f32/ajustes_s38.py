# F3.5 (sessão 38): chamadas de fora da Fresh a funções do FrWnd cuja assinatura mudou no 983. Lido por tools/f32/ajustes.py no fim.
# Os arquivos da Fresh já adotados (map/adotados.txt) são editados direto e não passam por aqui.
NEW10 = [
 ('sub', 'src/projectg/realmyroomtask.cpp', 'GetDesktop()->OnDisplay(true, false, true);', 'GetDesktop()->OnDisplay(true, false, true, true);',
  '983: FrWnd::OnDisplay tem 4 argumentos (00be8400, ret 0x10)'),
 ('sub', 'src/projectg/avatar_task.cpp', 'pDesktop->OnDisplay(true, false, true);', 'pDesktop->OnDisplay(true, false, true, true);',
  '983: FrWnd::OnDisplay tem 4 argumentos (00be8400, ret 0x10)'),
]
