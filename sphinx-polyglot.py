# -*- coding: utf-8 -*-
#
# Sphinx extension for documenting polyglot projects.
#
# Written by Arto Bendiken <http://ar.to/>.
#
# This is free and unencumbered software released into the public domain.

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _

class PolyglotObject(ObjectDescription):
    def handle_signature(self, sig, signode):
        self.describe_signature(sig, signode) # TODO
        return sig

    def describe_signature(self, _sig, _signode):
        raise NotImplementedError()

    def add_target_and_index(self, name, sig, signode):
        target_name = '%s-%s' % (self.objtype, name) # for <a href="..."
        if target_name not in self.state.document.ids:
            signode['names'].append(target_name)
            signode['ids'].append(target_name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

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

        def describe_signature(self, sig, signode):
            annot_text = directive_name + ' '
            signode += addnodes.desc_annotation(annot_text, annot_text)
            signode += addnodes.desc_name(sig, sig)

    return PolyglotDirective

class PolyglotDomain(Domain):
    """Base class for polyglot domains."""

    # See: http://www.sphinx-doc.org/en/stable/extdev/domainapi.html
    #name, label = 'polyglot', l_('Polyglot')
    object_types = {
      'assembly':  ObjType(l_('assembly'),  'assembly'),
      'header':    ObjType(l_('header'),    'header'),
      'library':   ObjType(l_('library'),   'library'),
      'module':    ObjType(l_('module'),    'module'),
      'namespace': ObjType(l_('namespace'), 'namespace'),
      'package':   ObjType(l_('package'),   'package'),
      'schema':    ObjType(l_('schema'),    'schema'),
      'system':    ObjType(l_('system'),    'system'),
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
      'package': make_directive('package'),
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
      'schema': make_directive('schema'),
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
