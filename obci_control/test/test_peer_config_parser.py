#!/usr/bin/python

from peer import peer_config, peer_config_parser

import io
from nose.tools import raises, with_setup

import warnings
import ConfigParser

class TestPeerConfigParserINI(object):

    def setup(self):
        self.pr = peer_config_parser.PeerConfigParserINI()
        self.conf = peer_config.PeerConfig()


    def test_init_parse_incomplete_sections(self):
        """nothing"""
        inp = """
[config_sources]
[local_params]
        """
        assert self.pr.parse(io.BytesIO(inp), self.conf)

    @raises(peer_config_parser.UnknownConfigSection)
    def test_init_parse_section_unknown(self):
        inp = """
[config_sources]
[ble]
[local_params]
[external_params]
        """
        self.pr.parse(io.BytesIO(inp), self.conf)


    @raises(ConfigParser.Error)
    def test_init_parse_bad_syntax(self):
        inp = """
  [ble]
 """
        self.pr.parse(io.BytesIO(inp), self.conf)


    def test_init_parse_headers_ok(self):
        inp = """
[config_sources]
[local_params]
[external_params]
"""
        assert self.pr.parse(io.BytesIO(inp), self.conf) is True

    @raises(peer_config_parser.ConfigSourceError)
    def test_init_parse_illegal_source_assignment(self):
        inp = """
[config_sources]
abc=asdf1
[local_params]
[external_params]
"""
        self.pr.parse(io.BytesIO(inp), self.conf)


    def test_init_parse_sources_ok(self):
        inp = """
[config_sources]
abc=
[local_params]
[external_params]
"""
        assert self.pr.parse(io.BytesIO(inp), self.conf) is True
        assert repr(self.conf.config_sources) == "{'abc': ''}"


    def test_init_parse_ok_standard(self):
        inp = """
[config_sources]
abc=
[local_params]
zxc=123
[external_params]
ble=abc.uuu
"""
        assert self.pr.parse(io.BytesIO(inp), self.conf) is True
        assert repr(self.conf.config_sources) == "{'abc': ''}"
        assert repr(self.conf.param_values) == "{'ble': None, 'zxc': '123'}"
        assert repr(self.conf.ext_param_defs) == "{'ble': ('abc', 'uuu')}"


    def test_init_parse_double_section(self):
        inp = """
[config_sources]
[local_params]
[config_sources]
[external_params]
        """
        assert self.pr.parse(io.BytesIO(inp), self.conf) is True

    def test_init_parse_double_local_param(self):
        inp = """
[config_sources]
[local_params]
zxc=123
zxc=2
[external_params]
        """
        assert self.pr.parse(io.BytesIO(inp), self.conf) is True
        assert repr(self.conf.param_values) == "{'zxc': '2'}"


    @raises(peer_config.ConfigOverwriteWarning)
    def test_init_parse_param_both_local_ext(self):
        """First are parsed config sources, then external parameters,
        last are local params. Here external param should be overwritten
        to local defined in the same file -- test warning"""
        inp = """
[config_sources]
aaa=
[local_params]
zxc=2
[external_params]
zxc=aaa.ble
        """
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.pr.parse(io.BytesIO(inp), self.conf)

    def test_init_parse_param_both_local_ext2(self):
        """First are parsed config sources, then external parameters,
        last are local params. Here external param should be overwritten
        to local defined in the same file -- test effect"""
        inp = """
[config_sources]
aaa=
[local_params]
zxc=2
[external_params]
zxc=aaa.ble
        """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.pr.parse(io.BytesIO(inp), self.conf)
            assert repr(self.conf.param_values) == "{'zxc': '2'}"

    ############### Update ############################################


    def test_update_parse_change_local_param(self):
        inp = """
[config_sources]
abc=
[local_params]
zxc=123
[external_params]
ble=abc.uuu
"""
        self.pr.parse(io.BytesIO(inp), self.conf)
        upd = """
[local_params]
zxc=oeoeoe
"""
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.pr.parse(io.BytesIO(upd), self.conf, update=True)
        assert self.conf.get_param('zxc') == "oeoeoe"
        # import peer_config_serializer as ser
        # st = ''
        # fp = io.BytesIO(st)
        # ser.PeerConfigSerializerJSON().serialize(self.conf, fp)
        # print fp.getvalue()
        # fp = io.BytesIO(st)
        # ser.PeerConfigSerializerINI().serialize(self.conf, fp)
        # print fp.getvalue()
        # assert 0


    def test_update_parse_local_to_ext(self):
        inp = """
[config_sources]
abc=
[local_params]
zxc=123
[external_params]
ble=abc.uuu
"""
        self.pr.parse(io.BytesIO(inp), self.conf)
        upd = """
[external_params]
zxc=abc.ooo
"""
        self.pr.parse(io.BytesIO(upd), self.conf, update=True)
        assert self.conf.get_param('zxc') is None
        assert repr(self.conf.ext_param_defs) == \
                "{'ble': ('abc', 'uuu'), 'zxc': ('abc', 'ooo')}"

    def test_update_parse_ext_to_local(self):
        inp = """
[config_sources]
abc=
[local_params]
zxc=123
[external_params]
ble=abc.uuu
"""
        self.pr.parse(io.BytesIO(inp), self.conf)
        upd = """
[local_params]
ble=0
"""
        self.pr.parse(io.BytesIO(upd), self.conf, update=True)
        assert self.conf.get_param('ble') == '0'
        assert repr(self.conf.ext_param_defs) == "{}"


    @raises(ValueError)
    def test_update_parse_new_param(self):
        inp = """
[config_sources]
abc=
[local_params]
zxc=123
[external_params]
ble=abc.uuu
"""
        self.pr.parse(io.BytesIO(inp), self.conf)
        upd = """
[local_params]
new=0
"""
        self.pr.parse(io.BytesIO(upd), self.conf, update=True)

    def test_json(self):
        inp = str('{"local_params": {"zxc": "oeoeoe"}, "config_sources": {"abc": ""}, "external_params": {"ble": "abc.uuu"}}')
        pj = peer_config_parser.PeerConfigParserJSON()
        pj.parse(io.BytesIO(inp), self.conf)
        assert repr(self.conf.param_values) == "{u'ble': None, u'zxc': u'oeoeoe'}"


class TestPeerConfigParserJSON(object):

    def setup(self):
        self.pr = peer_config_parser.PeerConfigParserJSON()
        self.conf = peer_config.PeerConfig()