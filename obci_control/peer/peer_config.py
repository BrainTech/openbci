#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings

from common.config_helpers import *

class PeerConfig(object):
	"""
	This class represents core configuration of an OpenBCI peer. It is
	meant to be used both as an output of a config parser and as
	a configuration holder for the running peer (wrapped in a controller
	with networking capabilities).

	Peer configuration consists of local parameters, external parameters,
	config sources definitions and launch dependencies.

	Local parameters:
			param_name : value
	are owned by the peer itself, whereas external parameters have to be
	obtained from other peers.

	External parameter definition:
			local_parameter_name : config_source_name.parameter_name

	Config source names are symbolic names for dependencies.
	In run time real peer ID's are assingned to those names; parameter_name
	is the remote parameter that is requested from source.

	Launch dependencies are similar to config sources: the definitions
	are identical and symbolic name pool is common with config source names
	i.e. all names are global in the configuration file.
	Launch dependencies are used when we want to delay peer start
	until all dependncies report that they are ready to work.
	"""
	def __init__(self, peer_id=None):
		# system ID of the peer
		#TODO - is this necessary in config core?
		self.peer_id = peer_id

		# keys are source names, values are real peer IDs
		self._config_sources = {}

		# keys are symbolic names, values are peer IDs
		self._launch_deps = {}

		# the other way: keys are peer IDs, values are lists of source names
		# to which the ID is assigned
		self._src_ids = {}

		# the other way: keys are peer IDs, values are lists of launch
		# dependencies to which the ID is assigned
		self._dep_ids = {}

		# external parameter definitions: keys are local param names, values
		# are source names and remote parameter names
		self._ext_param_defs = {}

		# already acquired external parameters
		self._set_ext_params = []

		# all parameter values, for not-yet-obtained external params
		# None is stored
		self._param_values = {}


	def __repr__(self):
		st = "PEER CONFIG [{0}]".format(self.peer_id)
		st = ''.join([st, "\nPeer ID: {0}".format(self.peer_id)])
		st = ''.join([st, "\nConfig_sources: {0}".format(
														self._config_sources)])
		st = ''.join([st, "\nLaunch dependencies: {0}".format(
														self._launch_deps)])
		st = ''.join([st, "\nExternal param definitions: {0}".format(
														self._ext_param_defs)])
		st = ''.join([st, "\nParameter values: {0}".format(
														self._param_values)])
		st = ''.join([st, "\nAcquired external params: {0}".format(
														self._set_ext_params)])
		return st

	@property
	def config_sources(self):
		"""
		Configuration sources' symbolic names and their assigned real peer IDs.
		(A dictionary)
		"""
		return self._config_sources

	@property
	def launch_deps(self):
		"""
		Launch dependencies' symbolic names and their assigned real peer IDs.
		(A dictionary)
		"""
		return self._launch_deps

	@property
	def source_ids(self):
		"""
		Peer ID's of the config sources and lists of their symbolic names.
		(A dictionary)
		"""
		return self._src_ids

	@property
	def dep_ids(self):
		"""
		Peer ID's of the launch dependencies and lists of their symbolic names.
		(A dictionary)
		"""
		return self._src_ids

	@property
	def param_values(self):
		"""
		A dictionary of all parameter values.
		"""
		return self._param_values

	@property
	def ext_param_defs(self):
		"""
		External parameter definitions. A definition consists of a local
		parameter name and a reference: pair of symbolic source name and
		remote parameter name.
		"""
		return self._ext_param_defs


	@property
	def ready_ext_params(self):
		"""
		External parameters with values succesfully obtained from sources.
		"""
		return self._set_ext_params

	@property
	def local_params(self):
		"""
		Local parameters and values (dict)
		"""
		params = {}
		for name in self._param_values:
			if name not in self._ext_param_defs:
				params[name] = self._param_values[name]
		return params

	def assign_id_to_name(self, sym_name, peer_id):
		if sym_name in self._config_sources:
			self.set_config_source(sym_name, peer_id)
		elif sym_name in self._launch_deps:
			self.set_launch_dependency(sym_name, peer_id)


	def set_config_source(self, source_name, peer_id='', _set_dep=True):
		"""
		Store a configuration symbolic source name and its real peer_id.
		Default ID is empty and can be updated later.
		Warns on overwrite.
		"""
		param_name_type_check(source_name)
		module_id_type_check(peer_id)
		argument_not_empty_check(source_name)

		srcs = self._config_sources
		if source_name in srcs:
			old_id = srcs[source_name]
			self._overwrite_warn("""Config source overwrite! \
Name: {0}, old id: {1}, new id: {2}""".format(
							source_name, old_id, peer_id))
			self._src_ids[old_id].remove(source_name)

		self._config_sources[source_name] = peer_id
		if not peer_id in self._src_ids:
			self._src_ids[peer_id] = []
		self._src_ids[peer_id].append(source_name)
		if source_name in self._launch_deps and _set_dep:
			self.set_launch_dependency(source_name, peer_id, _set_src=False)

	def set_launch_dependency(self, dep_name, peer_id='', _set_src=True):
		"""
		"""
		print "DEPSDEPSDEPS"
		param_name_type_check(dep_name)
		module_id_type_check(peer_id)
		argument_not_empty_check(dep_name)

		deps = self._launch_deps
		if dep_name in deps:
			old_id = deps[dep_name]
			self._overwrite_warn("""Dependency overwrite! \
Name: {0}, old id: {1}, new id: {2}""".format(
							dep_name, old_id, peer_id))
			self._dep_ids[old_id].remove(dep_name)

		self._launch_deps[dep_name] = peer_id
		if not peer_id in self._dep_ids:
			self._dep_ids[peer_id] = []
		self._dep_ids[peer_id].append(dep_name)
		if dep_name in self._config_sources and _set_src:
			self.set_config_source(dep_name, peer_id, _set_dep=False)


	def get_param(self, param_name):
		"""
		Return value of a parameter param_name. Parameter may be local
		or external.
		"""
		return self._param_values[param_name]

	def add_external_param_def(self, param_name, reference):
		"""
		Store an external parameter definition. param_name is the
		local name of the parameter, reference is a string
		'source_name.remote_param_name'.
		Warns about overwriting definitions, especially when a
		previously local parameter becomes external.
		"""
		#TODO - API change, split reference to 2 method params.
		param_name_type_check(param_name)
		argument_not_empty_check(param_name)

		df = [source_name, source_param] = reference_split(reference)

		if source_name not in self._config_sources:
			raise ValueError("Source name {0} from reference ('{1}') \
not declared in configuration!".format(source_name, reference))

		defs = self._ext_param_defs
		if param_name in defs:
			self._overwrite_warn(msg_overwrite_ext_def.format(
							param_name, defs[param_name], df))

		elif param_name in self._param_values:
			self._overwrite_warn(msg_overwrite_local_to_ext.format(
							param_name, source_name, source_param))

		self._ext_param_defs[param_name] = (source_name, source_param)
		self._param_values[param_name] = None

	def update_external_param_def(self, param_name, reference):
		"""
		Update external parameter definition. Works as add_external_param_def()
		but the definition should already be stored in PeerConfig. Otherwise
		raises ValueError.
		"""
		self._update_check(param_name)

		self.add_external_param_def(param_name, reference)


	def _set_external_param(self, param_name, value):

		# Store a value for external parameter

		if param_name not in self._ext_param_defs:
			raise ValueError("Parameter {0} not defined as \
							external parameter".format(param_name))
		else:
			self._param_values[param_name] = value
			self._set_ext_params.append(param_name)


	def set_param_from_source(self, src_id, src_param, value):
		"""
		Store a value of a remote parameter.
		src_id - peer ID of the source
		src_param - remote parameter name
		value - parameter value
		"""
		src_names = self._src_ids[src_id]

		for src_name in src_names:
			src_params = self.params_for_source(src_name)
			if src_param in src_params:
				self._set_external_param(src_params[src_param], value)



	def add_local_param(self, param_name, value):
		"""
		Store a value of a local parameter.
		Warn when a parameter is overwritten, especially when a previously
		external parameter becomes local.
		"""
		param_name_type_check(param_name)
		argument_not_empty_check(param_name)

		if param_name in self._ext_param_defs:
			self._overwrite_warn(msg_overwrite_ext_to_local.format(
														param_name, value))
			del self._ext_param_defs[param_name]
			if param_name in self._set_ext_params:
				del self._set_ext_params[param_name]
		elif param_name in self._param_values:
			self._overwrite_warn(msg_overwrite_local.format(
							param_name, self._param_values[param_name], value))

		self._param_values[param_name] = value


	def update_local_param(self, param_name, value):
		"""
		Update local parameter. Works like as add_local_param()
		but the parameter should already exist in PeerConfig.
		Otherwise raise ValueError.
		"""
		self._update_check(param_name)
		return self.add_local_param(param_name, value)


################### Helper methods ############################################


	def config_ready(self):
		"""
		Return True if the configuration is usable, i.e. all used
		config sources have peer ID's assigned and all external parameter
		values are already obtained.
		"""
		return self.config_sources_ready() and self.external_params_ready() \
					and self.launch_deps_ready()

	def config_sources_ready(self):
		"""
		Return  True if all used config sources have peer ID's assigned.
		"""
		unused = self.unused_config_sources()
		for src, peer_id in self._config_sources.iteritems():
			if not peer_id and not src in unused:
				return False
		return True

	def launch_deps_ready(self):
		"""
		Return  True if all launch deps have peer ID's assigned.
		"""
		for dep, peer_id in self._launch_deps.iteritems():
			if not peer_id:
				return False
		return True

	def external_params_ready(self):
		"""
		Return True if the values of all external parameters have been
		successfully obtained.
		"""
		for name in self._ext_param_defs.keys():
			if name not in self._set_ext_params:
				return False
		return True

	def params_for_source(self, p_src):
		"""
		Return a list of parameters coming from this source (symbolic name).
		"""
		params = {}
		for loc_name, (src, src_par) in self._ext_param_defs.iteritems():
			if src == p_src:
				params[src_par] = loc_name
		return params

	def unset_params_for_source(self, p_src):
		"""
		Return a list of parameters coming from this source (symbolic name)
		which are not yet set.
		"""
		params = {}
		for loc_name, (src, src_par) in self._ext_param_defs.iteritems():
			if src == p_src and loc_name not in self._set_ext_params:
				params[src_par] = loc_name
		return params


	def used_config_sources(self):
		"""
		Return a list of symbolic source names which are referenced in
		external parameter definitions.
		"""
		used = [reference[0] for reference in self._ext_param_defs.values()]
		return list(set(used))

	def unused_config_sources(self):
		"""
		Return a list of symbolic source names which are NOT referenced in
		external parameter definitions.
		"""
		used = self.used_config_sources()
		unused = [src for src in self._config_sources.keys() if src not in used]
		return unused

	def unassigned_config_sources(self):
		"""
		Return a list of configuration source names which do not have real
		peer ID assigned.
		"""
		ss = self._config_sources
		return [src for src in ss.keys() if ss[src] == '']

	def unassigned_launch_deps(self):
		"""
		Return a list of launch dependency names which do not have real
		peer ID assigned.
		"""
		deps = self._launch_deps
		return [dep for dep in deps.keys() if deps[dep] == '']


	def _update_check(self, param_name):
		if param_name not in self._param_values:
			raise ValueError("Parameter {0} does not exist in configuration,\
								 cannot update!".format(param_name))


	def _overwrite_warn(self, p_message):
		warnings.warn(ConfigOverwriteWarning(p_message), stacklevel=2)




msg_overwrite_ext_to_local = "Changing external parameter '{0}' to Local! \
New value: {1}."

msg_overwrite_local_to_ext = "Changing local parameter {0} to external! \
Source: {1}, src_param: {2}."

msg_overwrite_local = "Overwriting local param '{0}'! Old value: {1}, \
new value: {2}"

msg_overwrite_ext_def = "External parameter definition overwrite! \
Name: {0}, old ref: {1}, new ref: {2}."


########################## Warnings, exceptions ###############################


class ConfigWarning(Warning):
	def __init__(self, value=None):
		self.value = value

	def __str__(self):
		if self.value is not None:
			return repr(self.value)
		else:
			return repr(self)

class ConfigOverwriteWarning(ConfigWarning):
	pass

if __name__ == '__main__':
	pass