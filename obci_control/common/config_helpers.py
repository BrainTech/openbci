#!/usr/bin/python

CONFIG_SOURCES = "config_sources"
EXT_PARAMS = "external_params"
LOCAL_PARAMS = "local_params"
LAUNCH_DEPENDENCIES = "launch_dependencies"

PEER_CONFIG_SECTIONS = [CONFIG_SOURCES, EXT_PARAMS, LOCAL_PARAMS, LAUNCH_DEPENDENCIES]

def module_id_type_check(p_module_id):
	if not (isinstance(p_module_id, str) or isinstance(p_module_id, unicode)):
		raise ValueError("Module IDs can only be strings (got {})".format(
														repr(p_module_id)))


def param_name_type_check(p_param_name):
	if not (isinstance(p_param_name, str) or isinstance(p_param_name, unicode)):
		raise ValueError("Parameter names can only be strings (got {})".format(
														repr(p_param_name)))

def reference_type_check(p_reference):
	if not (isinstance(p_reference, str) or isinstance(p_reference, unicode)):
		raise ValueError("References can only be strings (got {})".format(
														repr(p_reference)))

def argument_not_empty_check(p_arg):
	if p_arg == '':
		raise ValueError("empty string")


def reference_split(p_reference):
	reference_type_check(p_reference)
	if not '.' in p_reference:
		raise ValueError("Invalid reference! \
			Should be 'source_name.param_name', got {}".format(p_reference))
	return p_reference.split('.', 1)


class OBCISystemError(Exception):
	pass
