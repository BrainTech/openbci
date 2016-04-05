#!/usr/bin/python

from nose.tools import raises
import warnings

from obci.control.peer import peer_config


class TestPeerConfig(object):

    def setup(self):
        self.pc = peer_config.PeerConfig()

########


    def test_set_config_source(self):
        self.pc.set_config_source("sig_src", peer_id="aaa")
        assert repr(self.pc.config_sources) == "{'sig_src': 'aaa'}"

    @raises(peer_config.ConfigOverwriteWarning)
    def test_set_config_source_overwrite(self):
        self.pc.set_config_source("sig_src", peer_id="aaa")
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pc.set_config_source("sig_src", peer_id="vvv")

    @raises(ValueError)
    def test_set_config_source_name_empty(self):
        self.pc.set_config_source("", peer_id="aaa")

    @raises(ValueError)
    def test_set_config_source_name_not_string(self):
        self.pc.set_config_source(None, peer_id="aaa")

#######


    def test_add_external_param_def(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("some_param", "source_n.src_param")
        assert repr(self.pc.ext_param_defs) == "{'some_param': ('source_n', 'src_param')}"

    @raises(peer_config.ConfigOverwriteWarning)
    def test_add_external_param_def_overwrite(self):
        self.pc.set_config_source("source_n")
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pc.add_external_param_def("some_param", "source_n.src_param")
            self.pc.add_external_param_def("some_param", "source_n.other")


    def test_add_external_param_def_overwrite2(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("some_param", "source_n.src_param")
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.pc.add_external_param_def("some_param", "source_n.other")
        assert repr(self.pc.ext_param_defs) == "{'some_param': ('source_n', 'other')}"
        assert repr(self.pc.param_values) == "{'some_param': None}"


    @raises(peer_config.ConfigOverwriteWarning)
    def test_add_external_param_def_local_exists(self):
        self.pc.set_config_source("source_n")
        self.pc.add_local_param("some_param", "some_value")
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pc.add_external_param_def("some_param", "source_n.src_param")

    def test_add_external_param_def_local_exists2(self):
        self.pc.set_config_source("source_n")
        self.pc.add_local_param("some_param", "some_value")
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.pc.add_external_param_def("some_param", "source_n.src_param")
        assert repr(self.pc.ext_param_defs) == "{'some_param': ('source_n', 'src_param')}"
        assert repr(self.pc.param_values) == "{'some_param': None}"

    @raises(ValueError)
    def test_add_external_param_def_bad_reference(self):
        self.pc.add_external_param_def("some_param", "this reference is invalid")

    @raises(ValueError)
    def test_add_external_param_def_undeclared_source(self):
        self.pc.add_external_param_def("some_param", "source_n.src_param")

    @raises(ValueError)
    def test_add_external_param_def_param_name_not_string(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def(12345, "source_n.src_param")

    @raises(ValueError)
    def test_add_external_param_def_param_name_empty(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("", "source_n.src_param")

########

    def test_update_external_param_def(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("some_param", "source_n.src_param")
        self.pc.update_external_param_def("some_param", "source_n.other")
        assert repr(self.pc.ext_param_defs) == "{'some_param': ('source_n', 'other')}"

    # @raises(peer_config.ConfigOverwriteWarning)
    # def test_update_external_param_def_with_overwrite_warning(self):
    #     self.pc.set_config_source("source_n")
    #     self.pc.add_external_param_def("some_param", "source_n.src_param")
    #     with warnings.catch_warnings():
    #         warnings.simplefilter('error')
    #         self.pc.update_external_param_def("some_param", "source_n.other")


    @raises(ValueError)
    def test_update_external_param_def_param_not_defined(self):
        self.pc.set_config_source("source_n")
        self.pc.update_external_param_def("some_param", "source_n.other")

########

    def test_set_external_param(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("some_param", "source_n.other")
        self.pc._set_external_param("some_param", "some_value")
        assert repr(self.pc.param_values) == "{'some_param': 'some_value'}"

    def test_set_external_param_overwrite(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("some_param", "source_n.other")
        self.pc._set_external_param("some_param", "some_value")
        self.pc._set_external_param("some_param", "other_value")
        assert repr(self.pc.param_values) == "{'some_param': 'other_value'}"

    @raises(ValueError)
    def test_set_external_param_no_def(self):
        self.pc._set_external_param("some_param", "some_value")

########

    def test_add_local_param(self):
        self.pc.add_local_param("par", "val")
        assert repr(self.pc.param_values) == "{'par': 'val'}"

    @raises(peer_config.ConfigOverwriteWarning)
    def test_add_local_param_overwrite(self):
        self.pc.add_local_param("par", "val")
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pc.add_local_param("par", "val2")

    @raises(peer_config.ConfigOverwriteWarning)
    def test_add_local_param_external_exists(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("par", "source_n.other")
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pc.add_local_param("par", "val2")

    def test_add_local_param_external_exists2(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("par", "source_n.other")

        self.pc.add_local_param("par", "val2")
        assert self.pc.ext_param_defs == {}


#######

    def test_update_local_param(self):
        self.pc.add_local_param("par", "val")
        self.pc.update_local_param("par", "new_val")
        assert repr(self.pc.param_values) == "{'par': 'new_val'}"


    @raises(ValueError)
    def test_update_local_param_not_exists(self):
        self.pc.update_local_param("par", "new_val")

#######

    def test_used_config_sources(self):
        self.pc.set_config_source("source_n")
        self.pc.add_external_param_def("par", "source_n.other")
        assert self.pc.used_config_sources() == ["source_n"]

#######

    def test_unassigned_config_sources(self):
        self.pc.set_config_source("source_n")
        self.pc.set_config_source("aaaa", "some_module_id")
        assert self.pc.unassigned_config_sources() == ["source_n"]

#######

    def test_unused_config_sources(self):
        self.pc.set_config_source("source_n")
        self.pc.set_config_source("aaaa")
        self.pc.add_external_param_def("par", "source_n.other")
        assert self.pc.unused_config_sources() == ["aaaa"]




# def test():
#     print __file__
#     assert 0

## init vs. update
## config_sources + ids
## unused_config_sources
