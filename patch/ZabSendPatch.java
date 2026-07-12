import org.objectweb.asm.*;
import java.io.*;
import java.nio.file.*;

public class ZabSendPatch {
  static final String PLAYER = "org/bukkit/entity/Player";
  static final String COMP_SEND = "(Lnet/kyori/adventure/text/Component;)V";
  static final String LEGACY = "net/kyori/adventure/text/serializer/legacy/LegacyComponentSerializer";
  static final String SENDER = "org/bukkit/command/CommandSender";

  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      System.err.println("Usage: ZabSendPatch <in.class> <out.class>");
      System.exit(2);
    }
    Path in = Paths.get(args[0]);
    Path out = Paths.get(args[1]);
    byte[] src = Files.readAllBytes(in);
    ClassReader cr = new ClassReader(src);
    ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_MAXS);
    final int[] hits = {0};
    cr.accept(new ClassVisitor(Opcodes.ASM9, cw) {
      @Override public MethodVisitor visitMethod(int access, String name, String desc, String sig, String[] ex) {
        MethodVisitor mv = super.visitMethod(access, name, desc, sig, ex);
        return new MethodVisitor(Opcodes.ASM9, mv) {
          @Override public void visitMethodInsn(int opcode, String owner, String name, String descriptor, boolean isInterface) {
            if (opcode == Opcodes.INVOKEINTERFACE
                && PLAYER.equals(owner)
                && "sendMessage".equals(name)
                && COMP_SEND.equals(descriptor)) {
              visitMethodInsn(Opcodes.INVOKESTATIC, LEGACY, "legacySection",
                  "()L" + LEGACY + ";", true);
              visitInsn(Opcodes.SWAP);
              visitMethodInsn(Opcodes.INVOKEINTERFACE, LEGACY, "serialize",
                  "(Lnet/kyori/adventure/text/Component;)Ljava/lang/String;", true);
              visitMethodInsn(Opcodes.INVOKEINTERFACE, SENDER, "sendMessage",
                  "(Ljava/lang/String;)V", true);
              hits[0]++;
              return;
            }
            super.visitMethodInsn(opcode, owner, name, descriptor, isInterface);
          }
        };
      }
    }, 0);
    Files.write(out, cw.toByteArray());
    System.out.println("PATCHED_HITS=" + hits[0]);
    if (hits[0] != 3) {
      throw new IllegalStateException("expected 3 sendMessage(Component) call sites, got " + hits[0]);
    }
  }
}
