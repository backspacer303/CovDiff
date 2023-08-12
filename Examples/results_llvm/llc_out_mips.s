	.text
	.abicalls
	.option	pic0
	.section	.mdebug.abi32,"",@progbits
	.nan	legacy
	.module	fp=xx
	.module	nooddspreg
	.text
	.file	"example.c"
	.globl	foo                             # -- Begin function foo
	.p2align	2
	.type	foo,@function
	.set	nomicromips
	.set	nomips16
	.ent	foo
foo:                                    # @foo
	.frame	$fp,24,$ra
	.mask 	0xc0000000,-4
	.fmask	0x00000000,0
	.set	noreorder
	.set	nomacro
	.set	noat
# %bb.0:                                # %entry
	addiu	$sp, $sp, -24
	sw	$ra, 20($sp)                    # 4-byte Folded Spill
	sw	$fp, 16($sp)                    # 4-byte Folded Spill
	move	$fp, $sp
	sw	$4, 12($fp)
	sw	$5, 8($fp)
	lw	$1, 12($fp)
	lw	$2, 8($fp)
	slt	$1, $2, $1
	beqz	$1, $BB0_3
	nop
# %bb.1:                                # %entry
	j	$BB0_2
	nop
$BB0_2:                                 # %if.then
	lw	$1, 12($fp)
	j	$BB0_4
	sw	$1, 4($fp)
$BB0_3:                                 # %if.else
	lw	$1, 8($fp)
	j	$BB0_4
	sw	$1, 4($fp)
$BB0_4:                                 # %if.end
	lw	$2, 4($fp)
	move	$sp, $fp
	lw	$fp, 16($sp)                    # 4-byte Folded Reload
	lw	$ra, 20($sp)                    # 4-byte Folded Reload
	jr	$ra
	addiu	$sp, $sp, 24
	.set	at
	.set	macro
	.set	reorder
	.end	foo
$func_end0:
	.size	foo, ($func_end0)-foo
                                        # -- End function
	.ident	"clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)"
	.section	".note.GNU-stack","",@progbits
	.text
