# -*- coding: utf-8 -*-
#
# Sphinx extension for documenting polyglot projects.
#
# Written by Arto Bendiken <http://ar.to/>.
#
# This is free and unencumbered software released into the public domain.

import re

from docutils import nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _

GO_FUNC_SIG_RE = re.compile(
  r'''^
      (?: \( \S+\s+([^)]+) \) )? \s*  # method receiver
      ([\w]+) \s*                     # function name
      \( ([^)]*) \) \s*               # function parameters
      (.*)$                           # return type
  ''', re.VERBOSE)

class PolyglotObject(ObjectDescription):
    def handle_signature(self, sig, sig_node):
        result = self.describe_signature(sig, sig_node) # TODO
        if result is None:
            return sig
        return result

    def describe_signature(self, _sig, _sig_node):
        raise NotImplementedError()

    def add_target_and_index(self, name, sig, sig_node):
        target_name = '%s-%s' % (self.objtype, name) # for <a href="..."
        if target_name not in self.state.document.ids:
            sig_node['names'].append(target_name)
            sig_node['ids'].append(target_name)
            sig_node['first'] = (not self.names)
            self.state.document.note_explicit_target(sig_node)

            objects = self.env.domaindata[self.domain]['objects']
            key = (self.objtype, name)
            if key in objects:
                self.state_machine.reporter.warning(
                    'duplicate definition of %s %s, ' % (self.objtype, name) +
                    'other instance in ' + self.env.doc2path(objects[key]),
                    line=self.lineno)
            objects[key] = self.env.docname
        index_text = self.get_index_text(self.objtype, name)
        if index_text:
            self.indexnode['entries'].append(('single', index_text, target_name, '', None))

def make_directive(directive_name):
    class PolyglotDirective(PolyglotObject):
        def get_index_text(self, _objtype, name):
            domain_label = self.env.domains[self.domain].label
            return _('%s (%s %s)') % (name, domain_label, directive_name)

        def describe_signature(self, sig, sig_node):
            annot_text = directive_name + ' '
            sig_node += addnodes.desc_annotation(annot_text, annot_text)
            sig_node += addnodes.desc_name(sig, sig)

    return PolyglotDirective

class GoFuncDirective(PolyglotObject):
    def get_index_text(self, _objtype, name):
        return _('%s (Go function)') % name

    def describe_signature(self, sig, sig_node):
        sig_match = GO_FUNC_SIG_RE.match(sig)
        if sig_match is None:
            raise ValueError('no match')
        method_receiver, func_name, func_params, func_return = sig_match.groups()

        sig_node += addnodes.desc_annotation('func ', 'func ')

        if method_receiver is not None:
            param_list = addnodes.desc_parameterlist()
            param_list += addnodes.desc_parameter(method_receiver, method_receiver, noemph=True)
            sig_node += param_list

        sig_node += addnodes.desc_name(func_name, func_name)

        if func_params is not None:
            param_list = addnodes.desc_parameterlist()
            param = addnodes.desc_parameter(func_params, func_params, noemph=True) # TODO: split params
            param_list += param
            sig_node += param_list

        if func_return is not None:
            sig_node += nodes.Text(' ')
            sig_node += addnodes.desc_returns(func_return, func_return)

        return func_name

class PolyglotDomain(Domain):
    """Base class for polyglot domains."""

    # See: http://www.sphinx-doc.org/en/stable/extdev/domainapi.html
    #name, label = 'polyglot', l_('Polyglot')
    object_types = {
      'assembly':  ObjType(l_('assembly'),  'assembly'),
      'channel':   ObjType(l_('channel'),   'channel'),
      'const':     ObjType(l_('constant'),  'constant'),
      'func':      ObjType(l_('function'),  'function'),
      'function':  ObjType(l_('function'),  'function'),
      'header':    ObjType(l_('header'),    'header'),
      'library':   ObjType(l_('library'),   'library'),
      'module':    ObjType(l_('module'),    'module'),
      'namespace': ObjType(l_('namespace'), 'namespace'),
      'package':   ObjType(l_('package'),   'package'),
      'schema':    ObjType(l_('schema'),    'schema'),
      'system':    ObjType(l_('system'),    'system'),
      'table':     ObjType(l_('table'),     'table'),
      'trigger':   ObjType(l_('trigger'),   'trigger'),
      'type':      ObjType(l_('type'),      'type'),
      'view':      ObjType(l_('view'),      'view'),
    }
    directives = {}
    initial_data = {
      'objects': {},  # (objtype, name) -> docname
    }
    data_version = 0 # bump this when the format of self.data changes

class CLDomain(PolyglotDomain):
    name, label = 'lisp', l_('Common Lisp')
    directives = {
      'package': make_directive('package'),
      'system':  make_directive('system'),
    }

class DotnetDomain(PolyglotDomain):
    name, label = 'dotnet', l_('.NET')
    directives = {
      'assembly': make_directive('assembly'),
    }

class ElixirDomain(PolyglotDomain):
    name, label = 'ex', l_('Elixir')
    directives = {
      'module':  make_directive('module'),
      'package': make_directive('package'),
    }

class ErlangDomain(PolyglotDomain):
    name, label = 'erl', l_('Erlang')
    directives = {
      'module':  make_directive('module'),
      'package': make_directive('package'),
    }

class GoDomain(PolyglotDomain):
    name, label = 'go', l_('Go')
    directives = {
      'const':   make_directive('const'),
      'func':    GoFuncDirective,
      'package': make_directive('package'),
      'type':    make_directive('type'),
    }

class JSDomain(PolyglotDomain):
    name, label = 'js', l_('JavaScript')
    directives = {
      'module':  make_directive('module'),
      'package': make_directive('package'),
    }

class JVMDomain(PolyglotDomain):
    name, label = 'jvm', l_('JVM')
    directives = {
      'package': make_directive('package'),
    }

class JavaDomain(JVMDomain):
    name, label = 'java', l_('Java')

class KotlinDomain(JVMDomain):
    name, label = 'kt', l_('Kotlin')

class LuaDomain(PolyglotDomain):
    name, label = 'lua', l_('Lua')
    directives = {
      'module': make_directive('module'),
    }

class OCamlDomain(PolyglotDomain):
    name, label = 'ml', l_('OCaml')
    directives = {
      'module':  make_directive('module'),
      'package': make_directive('package'),
    }

class PHPDomain(PolyglotDomain):
    name, label = 'php', l_('PHP')
    directives = {
      'namespace': make_directive('namespace'),
      'package':   make_directive('package'),
    }

class RubyDomain(PolyglotDomain):
    name, label = 'rb', l_('Ruby')
    directives = {
      'library': make_directive('library'),
      'module':  make_directive('module'),
    }

class SQLDomain(PolyglotDomain):
    name, label = 'sql', l_('SQL')
    directives = {
      'channel':  make_directive('channel'),
      'function': make_directive('function'),
      'schema':   make_directive('schema'),
      'table':    make_directive('table'),
      'trigger':  make_directive('trigger'),
      'type':     make_directive('type'),
      'view':     make_directive('view'),
    }

def setup(app):
    # See: http://www.sphinx-doc.org/en/stable/extdev/appapi.html
    app.require_sphinx('1.0')
    app.add_domain(CLDomain)
    app.add_domain(DotnetDomain)
    app.add_domain(ElixirDomain)
    app.add_domain(ErlangDomain)
    app.add_domain(GoDomain)
    #app.add_domain(JSDomain)
    app.add_domain(JavaDomain)
    app.add_domain(JVMDomain)
    app.add_domain(KotlinDomain)
    app.add_domain(LuaDomain)
    app.add_domain(OCamlDomain)
    app.add_domain(PHPDomain)
    app.add_domain(RubyDomain)
    app.add_domain(SQLDomain)
    return {'version': '0.0.0', 'parallel_read_safe': True}
