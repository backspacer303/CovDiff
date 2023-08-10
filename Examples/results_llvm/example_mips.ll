; ModuleID = '/home/syrmia/Desktop/Praksa/DebugInfoTest/example.c'
source_filename = "/home/syrmia/Desktop/Praksa/DebugInfoTest/example.c"
target datalayout = "E-m:m-p:32:32-i8:8:32-i16:16:32-i64:64-n32-S64"
target triple = "mips"

; Function Attrs: noinline nounwind optnone
define dso_local i32 @foo(i32 noundef signext %a, i32 noundef signext %b) #0 {
entry:
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  %c = alloca i32, align 4
  store i32 %a, ptr %a.addr, align 4
  store i32 %b, ptr %b.addr, align 4
  %0 = load i32, ptr %a.addr, align 4
  %1 = load i32, ptr %b.addr, align 4
  %cmp = icmp sgt i32 %0, %1
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %2 = load i32, ptr %a.addr, align 4
  store i32 %2, ptr %c, align 4
  br label %if.end

if.else:                                          ; preds = %entry
  %3 = load i32, ptr %b.addr, align 4
  store i32 %3, ptr %c, align 4
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  %4 = load i32, ptr %c, align 4
  ret i32 %4
}

attributes #0 = { noinline nounwind optnone "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="mips32r2" "target-features"="+fpxx,+mips32r2,+nooddspreg,-noabicalls" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"frame-pointer", i32 2}
!2 = !{!"clang version 18.0.0 (https://github.com/llvm/llvm-project.git bbe2887f5e9ca005b0f1b96c858969ee3ba646f4)"}
