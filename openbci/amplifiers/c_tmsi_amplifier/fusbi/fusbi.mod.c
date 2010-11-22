#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
 .name = KBUILD_MODNAME,
 .init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
 .exit = cleanup_module,
#endif
 .arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x7d09bae2, "module_layout" },
	{ 0x27a3b3fa, "kmalloc_caches" },
	{ 0x12da5bb2, "__kmalloc" },
	{ 0xcff53400, "kref_put" },
	{ 0x8230781d, "dev_set_drvdata" },
	{ 0x2bb6fde2, "__kfifo_put" },
	{ 0x105e2727, "__tracepoint_kmalloc" },
	{ 0xdc5d6042, "usb_deregister_dev" },
	{ 0x712aa29b, "_spin_lock_irqsave" },
	{ 0x22b25ae5, "usb_unlink_urb" },
	{ 0x3da5eb6d, "kfifo_alloc" },
	{ 0x9ced38aa, "down_trylock" },
	{ 0x7a73f55f, "usb_deregister" },
	{ 0xb72397d5, "printk" },
	{ 0x3656bf5a, "lock_kernel" },
	{ 0xe9db0705, "usb_set_interface" },
	{ 0xa1c76e0a, "_cond_resched" },
	{ 0x2f287f0d, "copy_to_user" },
	{ 0xb4390f9a, "mcount" },
	{ 0x310b8765, "usb_register_dev" },
	{ 0xb4ca9447, "__kfifo_get" },
	{ 0x4b07e779, "_spin_unlock_irqrestore" },
	{ 0xb1f975aa, "unlock_kernel" },
	{ 0xf6318c69, "usb_submit_urb" },
	{ 0x9dd454a7, "kmem_cache_alloc" },
	{ 0xb2fd5ceb, "__put_user_4" },
	{ 0x68a9a674, "usb_get_dev" },
	{ 0x7b1f5c14, "usb_put_dev" },
	{ 0xd575182c, "usb_find_interface" },
	{ 0x3ae831b6, "kref_init" },
	{ 0x37a0cba, "kfree" },
	{ 0x8a1203a9, "kref_get" },
	{ 0x3f1899f1, "up" },
	{ 0x6840d3a6, "usb_register_driver" },
	{ 0xd6c963c, "copy_from_user" },
	{ 0x12b5b0f1, "dev_get_drvdata" },
	{ 0x56e26d4b, "usb_free_urb" },
	{ 0x89949018, "down_timeout" },
	{ 0x49e89882, "usb_alloc_urb" },
	{ 0x15ef2dd9, "kfifo_free" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

MODULE_ALIAS("usb:v0C7Cp0004d*dc*dsc*dp*ic*isc*ip*");

MODULE_INFO(srcversion, "AFB4C22552B4FB1EB945852");
