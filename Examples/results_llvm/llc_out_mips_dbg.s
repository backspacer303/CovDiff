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
$tmp0:
.set $func_begin0, ($tmp0)
	.file	0 "/home/nikola/llvm_builds/llvm-clang-coverage-build" "/home/nikola/Desktop/CodeCoverage/DebugInfoTest/example.c" md5 0x5fcb4faf4a37ae34ae503ff87f779b52
	.file	1 "/home/nikola" "Desktop/CodeCoverage/DebugInfoTest/example.c" md5 0x5fcb4faf4a37ae34ae503ff87f779b52
	.loc	1 1 0                           # Desktop/CodeCoverage/DebugInfoTest/example.c:1:0
	.cfi_sections .debug_frame
	.cfi_startproc
	.frame	$fp,24,$ra
	.mask 	0xc0000000,-4
	.fmask	0x00000000,0
	.set	noreorder
	.set	nomacro
	.set	noat
# %bb.0:                                # %entry
	addiu	$sp, $sp, -24
	.cfi_def_cfa_offset 24
	sw	$ra, 20($sp)                    # 4-byte Folded Spill
	sw	$fp, 16($sp)                    # 4-byte Folded Spill
	.cfi_offset 31, -4
	.cfi_offset 30, -8
	move	$fp, $sp
	.cfi_def_cfa_register 30
	sw	$5, 8($fp)
$tmp1:
	.loc	1 3 8 prologue_end              # Desktop/CodeCoverage/DebugInfoTest/example.c:3:8
	lw	$1, 12($fp)
	.loc	1 3 12 is_stmt 0                # Desktop/CodeCoverage/DebugInfoTest/example.c:3:12
	lw	$2, 8($fp)
$tmp2:
	.loc	1 3 8                           # Desktop/CodeCoverage/DebugInfoTest/example.c:3:8
	slt	$1, $2, $1
	beqz	$1, $BB0_3
	nop
# %bb.1:                                # %entry
	j	$BB0_2
	nop
$BB0_2:                                 # %if.then
$tmp3:
	.loc	1 4 13 is_stmt 1                # Desktop/CodeCoverage/DebugInfoTest/example.c:4:13
	lw	$1, 12($fp)
	.loc	1 4 9 is_stmt 0                 # Desktop/CodeCoverage/DebugInfoTest/example.c:4:9
	j	$BB0_4
	sw	$1, 4($fp)
$BB0_3:                                 # %if.else
	.loc	1 6 13 is_stmt 1                # Desktop/CodeCoverage/DebugInfoTest/example.c:6:13
	lw	$1, 8($fp)
	j	$BB0_4
	sw	$1, 4($fp)
$tmp4:
$BB0_4:                                 # %if.end
	.loc	1 12 12                         # Desktop/CodeCoverage/DebugInfoTest/example.c:12:12
	lw	$2, 4($fp)
	.loc	1 12 5 is_stmt 0                # Desktop/CodeCoverage/DebugInfoTest/example.c:12:5
	move	$sp, $fp
	lw	$fp, 16($sp)                    # 4-byte Folded Reload
	lw	$ra, 20($sp)                    # 4-byte Folded Reload
	jr	$ra
	addiu	$sp, $sp, 24
$tmp5:
	.set	at
	.set	macro
	.set	reorder
	.end	foo
$func_end0:
	.size	foo, ($func_end0)-foo
	.cfi_endproc
                                        # -- End function
	.section	.debug_abbrev,"",@0x7000001e
	.byte	1                               # Abbreviation Code
	.byte	17                              # DW_TAG_compile_unit
	.byte	1                               # DW_CHILDREN_yes
	.byte	37                              # DW_AT_producer
	.byte	37                              # DW_FORM_strx1
	.byte	19                              # DW_AT_language
	.byte	5                               # DW_FORM_data2
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	114                             # DW_AT_str_offsets_base
	.byte	23                              # DW_FORM_sec_offset
	.byte	16                              # DW_AT_stmt_list
	.byte	23                              # DW_FORM_sec_offset
	.byte	27                              # DW_AT_comp_dir
	.byte	37                              # DW_FORM_strx1
	.byte	17                              # DW_AT_low_pc
	.byte	27                              # DW_FORM_addrx
	.byte	18                              # DW_AT_high_pc
	.byte	6                               # DW_FORM_data4
	.byte	115                             # DW_AT_addr_base
	.byte	23                              # DW_FORM_sec_offset
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	2                               # Abbreviation Code
	.byte	46                              # DW_TAG_subprogram
	.byte	1                               # DW_CHILDREN_yes
	.byte	17                              # DW_AT_low_pc
	.byte	27                              # DW_FORM_addrx
	.byte	18                              # DW_AT_high_pc
	.byte	6                               # DW_FORM_data4
	.byte	64                              # DW_AT_frame_base
	.byte	24                              # DW_FORM_exprloc
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	39                              # DW_AT_prototyped
	.byte	25                              # DW_FORM_flag_present
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	63                              # DW_AT_external
	.byte	25                              # DW_FORM_flag_present
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	3                               # Abbreviation Code
	.byte	5                               # DW_TAG_formal_parameter
	.byte	0                               # DW_CHILDREN_no
	.byte	2                               # DW_AT_location
	.byte	24                              # DW_FORM_exprloc
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	4                               # Abbreviation Code
	.byte	52                              # DW_TAG_variable
	.byte	0                               # DW_CHILDREN_no
	.byte	2                               # DW_AT_location
	.byte	24                              # DW_FORM_exprloc
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	5                               # Abbreviation Code
	.byte	36                              # DW_TAG_base_type
	.byte	0                               # DW_CHILDREN_no
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	62                              # DW_AT_encoding
	.byte	11                              # DW_FORM_data1
	.byte	11                              # DW_AT_byte_size
	.byte	11                              # DW_FORM_data1
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	0                               # EOM(3)
	.section	.debug_info,"",@0x7000001e
$cu_begin0:
	.4byte	($debug_info_end0)-($debug_info_start0) # Length of Unit
$debug_info_start0:
	.2byte	5                               # DWARF version number
	.byte	1                               # DWARF Unit Type
	.byte	4                               # Address Size (in bytes)
	.4byte	.debug_abbrev                   # Offset Into Abbrev. Section
	.byte	1                               # Abbrev [1] 0xc:0x4d DW_TAG_compile_unit
	.byte	0                               # DW_AT_producer
	.2byte	29                              # DW_AT_language
	.byte	1                               # DW_AT_name
	.4byte	($str_offsets_base0)            # DW_AT_str_offsets_base
	.4byte	($line_table_start0)            # DW_AT_stmt_list
	.byte	2                               # DW_AT_comp_dir
	.byte	0                               # DW_AT_low_pc
	.4byte	($func_end0)-($func_begin0)     # DW_AT_high_pc
	.4byte	($addr_table_base0)             # DW_AT_addr_base
	.byte	2                               # Abbrev [2] 0x23:0x31 DW_TAG_subprogram
	.byte	0                               # DW_AT_low_pc
	.4byte	($func_end0)-($func_begin0)     # DW_AT_high_pc
	.byte	1                               # DW_AT_frame_base
	.byte	110
	.byte	3                               # DW_AT_name
	.byte	1                               # DW_AT_decl_file
	.byte	1                               # DW_AT_decl_line
                                        # DW_AT_prototyped
	.4byte	84                              # DW_AT_type
                                        # DW_AT_external
	.byte	3                               # Abbrev [3] 0x32:0xb DW_TAG_formal_parameter
	.byte	2                               # DW_AT_location
	.byte	141
	.byte	12
	.byte	5                               # DW_AT_name
	.byte	1                               # DW_AT_decl_file
	.byte	1                               # DW_AT_decl_line
	.4byte	84                              # DW_AT_type
	.byte	3                               # Abbrev [3] 0x3d:0xb DW_TAG_formal_parameter
	.byte	2                               # DW_AT_location
	.byte	141
	.byte	8
	.byte	6                               # DW_AT_name
	.byte	1                               # DW_AT_decl_file
	.byte	1                               # DW_AT_decl_line
	.4byte	84                              # DW_AT_type
	.byte	4                               # Abbrev [4] 0x48:0xb DW_TAG_variable
	.byte	2                               # DW_AT_location
	.byte	141
	.byte	4
	.byte	7                               # DW_AT_name
	.byte	1                               # DW_AT_decl_file
	.byte	2                               # DW_AT_decl_line
	.4byte	84                              # DW_AT_type
	.byte	0                               # End Of Children Mark
	.byte	5                               # Abbrev [5] 0x54:0x4 DW_TAG_base_type
	.byte	4                               # DW_AT_name
	.byte	5                               # DW_AT_encoding
	.byte	4                               # DW_AT_byte_size
	.byte	0                               # End Of Children Mark
$debug_info_end0:
	.section	.debug_str_offsets,"",@0x7000001e
	.4byte	36                              # Length of String Offsets Set
	.2byte	5
	.2byte	0
$str_offsets_base0:
	.section	.debug_str,"MS",@0x7000001e,1
$info_string0:
	.asciz	"clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)" # string offset=0
$info_string1:
	.asciz	"/home/nikola/Desktop/CodeCoverage/DebugInfoTest/example.c" # string offset=105
$info_string2:
	.asciz	"/home/nikola/llvm_builds/llvm-clang-coverage-build" # string offset=157
$info_string3:
	.asciz	"foo"                           # string offset=208
$info_string4:
	.asciz	"int"                           # string offset=212
$info_string5:
	.asciz	"a"                             # string offset=216
$info_string6:
	.asciz	"b"                             # string offset=218
$info_string7:
	.asciz	"c"                             # string offset=220
	.section	.debug_str_offsets,"",@0x7000001e
	.4byte	($info_string0)
	.4byte	($info_string1)
	.4byte	($info_string2)
	.4byte	($info_string3)
	.4byte	($info_string4)
	.4byte	($info_string5)
	.4byte	($info_string6)
	.4byte	($info_string7)
	.section	.debug_addr,"",@0x7000001e
	.4byte	($debug_addr_end0)-($debug_addr_start0) # Length of contribution
$debug_addr_start0:
	.2byte	5                               # DWARF version number
	.byte	4                               # Address size
	.byte	0                               # Segment selector size
$addr_table_base0:
	.4byte	($func_begin0)
$debug_addr_end0:
	.ident	"clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)"
	.section	".note.GNU-stack","",@progbits
	.text
	.section	.debug_line,"",@0x7000001e
$line_table_start0:
