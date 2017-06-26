# -*- coding: utf-8 -*-
#
# Sphinx extension for documenting polyglot projects.
#
# Written by Arto Bendiken <http://ar.to/>.
#
# This is free and unencumbered software released into the public domain.

def setup(app):
    # See: http://www.sphinx-doc.org/en/stable/extdev/appapi.html
    app.require_sphinx('1.0')
    #app.add_domain(PolyglotDomain) # TODO
    return {'version': '0.0.0', 'parallel_read_safe': True}
