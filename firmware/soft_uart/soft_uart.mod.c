#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};



static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0xc1514a3b, "free_irq" },
	{ 0x1db5c2ad, "gpiod_get_raw_value" },
	{ 0x47a7fc63, "tty_flip_buffer_push" },
	{ 0xea82d349, "hrtimer_init" },
	{ 0xf01ce0d5, "gpiod_set_raw_value" },
	{ 0xa6f50b3, "gpiod_to_irq" },
	{ 0x8285c7ed, "tty_port_link_device" },
	{ 0xfcec0987, "enable_irq" },
	{ 0xbd394d8, "tty_termios_baud_rate" },
	{ 0xfe990052, "gpio_free" },
	{ 0xc7ce12e4, "__tty_alloc_driver" },
	{ 0xb286baf3, "tty_unregister_driver" },
	{ 0x122c3a7e, "_printk" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0x67b27ec1, "tty_std_termios" },
	{ 0x676a1fb6, "gpiod_set_debounce" },
	{ 0x92d5838e, "request_threaded_irq" },
	{ 0x3e5d99eb, "gpiod_direction_output_raw" },
	{ 0x54e5a03b, "gpiod_direction_input" },
	{ 0x9e7b72df, "__tty_insert_flip_string_flags" },
	{ 0x4dfa8d4b, "mutex_lock" },
	{ 0x848e1941, "tty_port_init" },
	{ 0xcefb0c9f, "__mutex_init" },
	{ 0xc0b7c197, "hrtimer_start_range_ns" },
	{ 0x3213f038, "mutex_unlock" },
	{ 0xe31ebe74, "tty_register_driver" },
	{ 0xb43f9365, "ktime_get" },
	{ 0x13929d91, "gpio_to_desc" },
	{ 0x47229b5c, "gpio_request" },
	{ 0x102fe6de, "hrtimer_cancel" },
	{ 0x135bb7ec, "hrtimer_forward" },
	{ 0xcb2e80c6, "hrtimer_active" },
	{ 0xdc43cf22, "param_ops_int" },
	{ 0xf9a482f9, "msleep" },
	{ 0x4b49ef70, "tty_driver_kref_put" },
	{ 0x3ce4ca6f, "disable_irq" },
	{ 0x39ff040a, "module_layout" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "2BD5F3FC67AC46B9F3D8A3B");
