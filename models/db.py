# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

def format_edge(r):
    if(db.qualifiers(r.qualifier).name == 'None'):
        return '%s <%s> %s' % (db.nodes(r.source_id).name,db.edge_types(r.e_type).name,db.nodes(r.destiny_id).name)
    return '%s <%s> <%s> %s %s' % (db.nodes(r.source_id).name,db.edge_types(r.e_type).name,db.qualifiers(r.qualifier).name,r.q_value,db.nodes(r.destiny_id).name)


if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
    db.define_table('node_types',
      Field('name',length=255,unique=True,label=T("Type Name")),
      Field('shape',label=T("Shape")),
      format = '%(name)s')
    db.node_types.name.represent = lambda name,row: name.title()
    db.node_types.shape.requires = IS_IN_SET(('ellipse','circle','database',
                                              'box','text','diamond','dot',
                                              'star','triangle','triangleDown',
                                              'square'))

    db.define_table('nodes',
      Field('name',length=255,unique=True,label=T("Name")),
      Field('n_type','reference node_types',label=T("Types")),
      Field('synonymous','list:string',label=T("Synonymous")),
      format = '%(name)s')
    db.nodes.n_type.requires = IS_IN_DB(db, db.node_types, '%(name)s')
    db.nodes.name.represent = lambda name,row: name.title()

    db.define_table('edge_types',
      Field('name',length=255,unique=True,label=T("Type Name")),
      format = '%(name)s')
    db.edge_types.name.represent = lambda name,row: name.upper()

    db.define_table('qualifiers',
      Field('name',length=255,unique=True,label=T("Qualifier")),
      format = '%(name)s')

    db.define_table('edges',
      Field('source_id', 'reference nodes',label=T("Source")),
      Field('e_type', 'reference edge_types', label=T("Type")),
      Field('qualifier', 'reference qualifiers', label=T("Qualifier")),
      Field('q_value',length=255,label=T("Qualifier Value")),
      Field('destiny_id', 'reference nodes',label=T("Destiny")),
      format = lambda r: format_edge(r))
    db.edges.source_id.requires = IS_IN_DB(db, db.nodes, '%(name)s')
    db.edges.e_type.requires = IS_IN_DB(db, db.edge_types, '%(name)s')
    db.edges.qualifier.requires = IS_IN_DB(db, db.qualifiers, '%(name)s')
    db.edges.destiny_id.requires = IS_IN_DB(db, db.nodes, '%(name)s')

    db.define_table('bibliographies',
      Field('bibkey',length=255,unique=True,label=T("Key")),
      Field('code',type='text',label=T("Bibtex source")),
      format = '%(bibkey)s')

    db.define_table('informations',
      Field('info',type='text',label=T("Information")),
      Field('edge','list:reference edges',label=T("Edges")),
      Field('citation','list:reference bibliographies',label=T("Citation")),
      format = '%(info)s')
    db.informations.info.requires = IS_NOT_EMPTY()
    db.informations.edge.requires = IS_IN_DB(db, db.edges, db.edges._format, multiple=True)
    db.informations.citation.requires = IS_IN_DB(db, db.bibliographies, '%(bibkey)s', multiple=True)

else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
