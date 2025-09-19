savedcmd_/home/blindassist/repo/firmware/soft_uart/queue.o :=  aarch64-linux-gnu-gcc-12 -Wp,-MMD,/home/blindassist/repo/firmware/soft_uart/.queue.o.d -nostdinc -I/usr/src/linux-headers-6.12.25+rpt-common-rpi/arch/arm64/include -I./arch/arm64/include/generated -I/usr/src/linux-headers-6.12.25+rpt-common-rpi/include -I./include -I/usr/src/linux-headers-6.12.25+rpt-common-rpi/arch/arm64/include/uapi -I./arch/arm64/include/generated/uapi -I/usr/src/linux-headers-6.12.25+rpt-common-rpi/include/uapi -I./include/generated/uapi -include /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler-version.h -include /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/kconfig.h -include /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler_types.h -D__KERNEL__ -mlittle-endian -DCC_USING_PATCHABLE_FUNCTION_ENTRY -DKASAN_SHADOW_SCALE_SHIFT= -fmacro-prefix-map=/usr/src/linux-headers-6.12.25+rpt-common-rpi/= -std=gnu11 -fshort-wchar -funsigned-char -fno-common -fno-PIE -fno-strict-aliasing -mgeneral-regs-only -DCONFIG_CC_HAS_K_CONSTRAINT=1 -Wno-psabi -mabi=lp64 -fno-asynchronous-unwind-tables -fno-unwind-tables -mbranch-protection=pac-ret -Wa,-march=armv8.5-a -DARM64_ASM_ARCH='"armv8.5-a"' -DKASAN_SHADOW_SCALE_SHIFT= -fno-delete-null-pointer-checks -O2 -fno-allow-store-data-races -fstack-protector-strong -fno-omit-frame-pointer -fno-optimize-sibling-calls -ftrivial-auto-var-init=zero -fno-stack-clash-protection -fpatchable-function-entry=4,2 -falign-functions=8 -fno-strict-overflow -fno-stack-check -fconserve-stack -fno-builtin-wcslen -fno-builtin-wcslen -Wall -Wundef -Werror=implicit-function-declaration -Werror=implicit-int -Werror=return-type -Werror=strict-prototypes -Wno-format-security -Wno-trigraphs -Wno-frame-address -Wno-address-of-packed-member -Wmissing-declarations -Wmissing-prototypes -Wframe-larger-than=2048 -Wno-main -Wno-dangling-pointer -Wvla -Wno-pointer-sign -Wcast-function-type -Wno-stringop-overflow -Wno-array-bounds -Wno-alloc-size-larger-than -Wimplicit-fallthrough=5 -Werror=date-time -Werror=incompatible-pointer-types -Werror=designated-init -Wenum-conversion -Wextra -Wunused -Wno-unused-but-set-variable -Wno-unused-const-variable -Wno-packed-not-aligned -Wno-format-overflow -Wno-format-truncation -Wno-stringop-truncation -Wno-override-init -Wno-missing-field-initializers -Wno-type-limits -Wno-shift-negative-value -Wno-maybe-uninitialized -Wno-sign-compare -Wno-unused-parameter -mstack-protector-guard=sysreg -mstack-protector-guard-reg=sp_el0 -mstack-protector-guard-offset=1424  -DMODULE  -DKBUILD_BASENAME='"queue"' -DKBUILD_MODNAME='"soft_uart"' -D__KBUILD_MODNAME=kmod_soft_uart -c -o /home/blindassist/repo/firmware/soft_uart/queue.o /home/blindassist/repo/firmware/soft_uart/queue.c  

source_/home/blindassist/repo/firmware/soft_uart/queue.o := /home/blindassist/repo/firmware/soft_uart/queue.c

deps_/home/blindassist/repo/firmware/soft_uart/queue.o := \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler-version.h \
    $(wildcard include/config/CC_VERSION_TEXT) \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/kconfig.h \
    $(wildcard include/config/CPU_BIG_ENDIAN) \
    $(wildcard include/config/BOOGER) \
    $(wildcard include/config/FOO) \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler_types.h \
    $(wildcard include/config/DEBUG_INFO_BTF) \
    $(wildcard include/config/PAHOLE_HAS_BTF_TAG) \
    $(wildcard include/config/FUNCTION_ALIGNMENT) \
    $(wildcard include/config/CC_HAS_SANE_FUNCTION_ALIGNMENT) \
    $(wildcard include/config/X86_64) \
    $(wildcard include/config/ARM64) \
    $(wildcard include/config/LD_DEAD_CODE_DATA_ELIMINATION) \
    $(wildcard include/config/LTO_CLANG) \
    $(wildcard include/config/HAVE_ARCH_COMPILER_H) \
    $(wildcard include/config/CC_HAS_COUNTED_BY) \
    $(wildcard include/config/UBSAN_SIGNED_WRAP) \
    $(wildcard include/config/CC_HAS_ASM_INLINE) \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler_attributes.h \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/include/linux/compiler-gcc.h \
    $(wildcard include/config/MITIGATION_RETPOLINE) \
    $(wildcard include/config/ARCH_USE_BUILTIN_BSWAP) \
    $(wildcard include/config/SHADOW_CALL_STACK) \
    $(wildcard include/config/KCOV) \
  /usr/src/linux-headers-6.12.25+rpt-common-rpi/arch/arm64/include/asm/compiler.h \
    $(wildcard include/config/ARM64_PTR_AUTH_KERNEL) \
    $(wildcard include/config/ARM64_PTR_AUTH) \
    $(wildcard include/config/BUILTIN_RETURN_ADDRESS_STRIPS_PAC) \
  /home/blindassist/repo/firmware/soft_uart/queue.h \

/home/blindassist/repo/firmware/soft_uart/queue.o: $(deps_/home/blindassist/repo/firmware/soft_uart/queue.o)

$(deps_/home/blindassist/repo/firmware/soft_uart/queue.o):
