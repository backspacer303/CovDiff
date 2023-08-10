; ModuleID = '/home/syrmia/Desktop/Praksa/DebugInfoTest/example.c'
source_filename = "/home/syrmia/Desktop/Praksa/DebugInfoTest/example.c"
target datalayout = "E-m:m-p:32:32-i8:8:32-i16:16:32-i64:64-n32-S64"
target triple = "mips"

; Function Attrs: noinline nounwind optnone
define dso_local i32 @foo(i32 noundef signext %a, i32 noundef signext %b) #0 !dbg !7 {
entry:
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  %c = alloca i32, align 4
  store i32 %a, ptr %a.addr, align 4
  call void @llvm.dbg.declare(metadata ptr %a.addr, metadata !13, metadata !DIExpression()), !dbg !14
  store i32 %b, ptr %b.addr, align 4
  call void @llvm.dbg.declare(metadata ptr %b.addr, metadata !15, metadata !DIExpression()), !dbg !16
  call void @llvm.dbg.declare(metadata ptr %c, metadata !17, metadata !DIExpression()), !dbg !18
  %0 = load i32, ptr %a.addr, align 4, !dbg !19
  %1 = load i32, ptr %b.addr, align 4, !dbg !21
  %cmp = icmp sgt i32 %0, %1, !dbg !22
  br i1 %cmp, label %if.then, label %if.else, !dbg !23

if.then:                                          ; preds = %entry
  %2 = load i32, ptr %a.addr, align 4, !dbg !24
  store i32 %2, ptr %c, align 4, !dbg !25
  br label %if.end, !dbg !26

if.else:                                          ; preds = %entry
  %3 = load i32, ptr %b.addr, align 4, !dbg !27
  store i32 %3, ptr %c, align 4, !dbg !28
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  %4 = load i32, ptr %c, align 4, !dbg !29
  ret i32 %4, !dbg !30
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

attributes #0 = { noinline nounwind optnone "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="mips32r2" "target-features"="+fpxx,+mips32r2,+nooddspreg,-noabicalls" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "/home/syrmia/Desktop/Praksa/DebugInfoTest/example.c", directory: "/home/syrmia/llvm_builds/llvm-clang-coverage-build", checksumkind: CSK_MD5, checksum: "5fcb4faf4a37ae34ae503ff87f779b52")
!2 = !{i32 7, !"Dwarf Version", i32 5}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 7, !"frame-pointer", i32 2}
!6 = !{!"clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)"}
!7 = distinct !DISubprogram(name: "foo", scope: !8, file: !8, line: 1, type: !9, scopeLine: 1, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !12)
!8 = !DIFile(filename: "Desktop/Praksa/DebugInfoTest/example.c", directory: "/home/syrmia", checksumkind: CSK_MD5, checksum: "5fcb4faf4a37ae34ae503ff87f779b52")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !11, !11}
!11 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!12 = !{}
!13 = !DILocalVariable(name: "a", arg: 1, scope: !7, file: !8, line: 1, type: !11)
!14 = !DILocation(line: 1, column: 13, scope: !7)
!15 = !DILocalVariable(name: "b", arg: 2, scope: !7, file: !8, line: 1, type: !11)
!16 = !DILocation(line: 1, column: 20, scope: !7)
!17 = !DILocalVariable(name: "c", scope: !7, file: !8, line: 2, type: !11)
!18 = !DILocation(line: 2, column: 9, scope: !7)
!19 = !DILocation(line: 3, column: 8, scope: !20)
!20 = distinct !DILexicalBlock(scope: !7, file: !8, line: 3, column: 8)
!21 = !DILocation(line: 3, column: 12, scope: !20)
!22 = !DILocation(line: 3, column: 10, scope: !20)
!23 = !DILocation(line: 3, column: 8, scope: !7)
!24 = !DILocation(line: 4, column: 13, scope: !20)
!25 = !DILocation(line: 4, column: 11, scope: !20)
!26 = !DILocation(line: 4, column: 9, scope: !20)
!27 = !DILocation(line: 6, column: 13, scope: !20)
!28 = !DILocation(line: 6, column: 11, scope: !20)
!29 = !DILocation(line: 12, column: 12, scope: !7)
!30 = !DILocation(line: 12, column: 5, scope: !7)
