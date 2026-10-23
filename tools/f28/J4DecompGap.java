// J4: descompila as funções pedidas (args: arquivo de saída, endereços...) e lista chamadas, strings e chamadores.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class J4DecompGap extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        PrintWriter w = new PrintWriter(new FileWriter(a[0]));
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        Listing l = currentProgram.getListing();
        ReferenceManager rm = currentProgram.getReferenceManager();
        for (int i = 1; i < a.length; i++) {
            Address ad = toAddr(a[i]);
            Function f = getFunctionContaining(ad);
            if (f == null) { disassemble(ad); f = createFunction(ad, null); }
            if (f == null) { w.println("#### " + a[i] + " SEM FUNCAO"); continue; }
            w.println("#### " + a[i] + " " + f.getName(true) + " @" + f.getEntryPoint() + " corpo=" + f.getBody().getNumAddresses());
            w.print("## chamadores/refs:");
            for (Reference r : getReferencesTo(f.getEntryPoint())) {
                Function cf = getFunctionContaining(r.getFromAddress());
                w.print(" " + r.getFromAddress() + "(" + r.getReferenceType() + (cf != null ? "," + cf.getName() + "@" + cf.getEntryPoint() : "") + ")");
            }
            w.println();
            TreeMap<String,Integer> calls = new TreeMap<>();
            List<String> strs = new ArrayList<>();
            InstructionIterator it = l.getInstructions(f.getBody(), true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                for (Reference r : ins.getReferencesFrom()) {
                    if (r.getReferenceType().isCall()) {
                        Symbol s = getSymbolAt(r.getToAddress());
                        Function tf = getFunctionAt(r.getToAddress());
                        String n = tf != null ? tf.getName(true) : (s != null ? s.getName(true) : r.getToAddress().toString());
                        if (tf != null && tf.isThunk()) n = tf.getThunkedFunction(true).getName(true);
                        n = n + "@" + r.getToAddress();
                        calls.merge(n, 1, Integer::sum);
                    } else if (r.getReferenceType().isData()) {
                        Data dt = l.getDataAt(r.getToAddress());
                        if (dt != null && dt.hasStringValue()) strs.add(ins.getAddress() + ":" + dt.getValue());
                        else if (dt != null && dt.isPointer() && dt.getValue() instanceof Address) {
                            Symbol s = getSymbolAt((Address) dt.getValue());
                            if (s != null) calls.merge("[" + s.getName(true) + "]@" + r.getToAddress(), 1, Integer::sum);
                        }
                    }
                }
            }
            w.println("## chamadas: " + calls);
            w.println("## strings: " + strs);
            DecompileResults res = d.decompileFunction(f, 180, monitor);
            w.println(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "DECOMP FALHOU: " + res.getErrorMessage());
        }
        w.close();
    }
}
