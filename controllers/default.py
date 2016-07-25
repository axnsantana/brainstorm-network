# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def index():
    nodes = db(db.nodes.n_type == db.node_types.id).select()
    sql='SELECT id, source_id, destiny_id FROM edges;'
    edges = db.executesql(sql,as_dict=True)
    types = db().select(db.node_types.ALL)
    lstnodes={}
    for n in nodes:
        node = {"name":n.nodes.name, "info":n.nodes.name, "group":n.nodes.n_type, "shape":n.node_types.shape, "weight":0}
        lstnodes[n.nodes.id]=node
    links={}
    for e in edges:
        edkey="%d#%d" % tuple(sorted([e['source_id'],e['destiny_id']]))
        lstnodes[e['source_id']]['weight']+=1
        lstnodes[e['destiny_id']]['weight']+=1
        label = "%s <-> %s" % (lstnodes[e['source_id']]['name'],lstnodes[e['destiny_id']]['name'])
        link=links.get(edkey,{"info":label, "source_id":e['source_id'], "destiny_id":e['destiny_id'], "id":e['id'], "weight":0})
        link["weight"]+=1
        links[edkey]=link
    #widget = SQLFORM.widgets.autocomplete(request, db.nodes.name, limitby=(0,10), min_length=3)   
    #search_widget=SQLFORM.factory(Field('search',label=T("Search"),widget=widget),buttons=[])
    search_widget=SQLFORM.factory(Field('search','list:reference nodes',label=T("Search"),
				  requires = IS_IN_DB(db, db.nodes, '%(name)s', multiple=True)),
				  buttons=[])
    return dict(message=T('Brainstorm Network'),nodes=lstnodes,links=links,types=types,search=search_widget)

def error():
    return dict()

def search_nodes():
    data = ['bli', 'bla', 'ble']
    return data

def display_info():
    edges = request.vars['edges[]']
    nodes = request.vars['nodes[]']
    html=""

    # if nodes:
    #     for n in nodes:
    #         node = db.nodes[n]
    #         node_type = db.types[node.type]
    #         html+= "ID: %s = %s<br>" % (node.name,node_type.name)
    html+="<table class='pure-table pure-table-bordered' style='table-layout: fixed; width: 100%'><thead>"
    html+="<th>%s</th><th>%s</th><th>%s</th></thead>" % (T("Source"),T("Relationship"),T("Destiny"))
    if edges:
        if (not (type(edges) is list)):
            edges = [edges]
        for e in edges:
            edge = db.edges[e]
            source_id = db.nodes[edge.source_id].name
            relationship = db.edge_types[edge.e_type].name
            qualifier = db.qualifiers[edge.qualifier].name
            if(qualifier == "None"):
                qualifier = ""
            q_value = edge.q_value
            destiny_id = db.nodes[edge.destiny_id].name
            l_relationship = "%s<br> %s %s" % (relationship,qualifier,q_value)
            l_relationship = l_relationship.rstrip()
            html+="<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (source_id,l_relationship,destiny_id)
            infos = db(db.informations.edge.contains(e)).select().as_list()
            for i in infos:
                bibs = i['citation']
                bib = db.informations.citation.represent(bibs)
                html+="<tr><td colspan='2'>%s</td><td>%s</td></tr>" % (i['info'],bib)
            html+="<tr bgcolor='#cbcbcb'><td colspan='3'></td></tr>"
    html+="</table>"
    return html

def table_list(table,label,orderby,create=True):
    table.id.readable=False
    if auth.has_membership(group_id='administrators'):
        return dict(grid=SQLFORM.grid(table,create=create,
            orderby=orderby,maxtextlength=64, paginate=25),
            label=label)
    else:
        return dict(grid=SQLFORM.grid(table,
            create=False,deletable=False,editable=False,
            orderby=orderby,maxtextlength=64, paginate=25),
            label=label)

def mark_destiny_connections():
    source_id = request.vars['source_id']
    edtype = request.vars['e_type']
    qualifier = request.vars['qualifier']
    q_value = request.vars['q_value']
    rows = db((db.edges.source_id == source_id)&
              (db.edges.e_type == edtype)&
              (db.edges.qualifier == qualifier)&
              (db.edges.q_value == q_value)).select(db.edges.destiny_id)
    destinies = []
    for r in rows:
        destinies.append(r['destiny_id'])
    return ",".join(str(v) for v in destinies)

def connections_info():
    source_id = request.vars['source_id']
    edtype = request.vars['e_type']
    qualifier = request.vars['qualifier']
    q_value = request.vars['q_value']
    rows = db((db.edges.source_id == source_id)&
              (db.edges.e_type == edtype)&
              (db.edges.qualifier == qualifier)&
              (db.edges.q_value == q_value)).select(db.edges.destiny_id)
    destinies = []
    for r in rows:
        destinies.append(r['destiny_id'])
    return ",".join(str(v) for v in destinies)

def connections():
    conn_form = SQLFORM.factory(
        Field('source_id', 'reference nodes',label=T("Source"),
        requires = IS_IN_DB(db, db.nodes, '%(name)s',zero=T("Choose one"))),
        Field('edtype', 'reference edge_types',label=T("Type"),
        requires = IS_IN_DB(db, db.edge_types, '%(name)s',zero=T("Choose one"))),
        Field('qualifier', 'reference qualifiers', label=T("Qualifier"),
        requires = IS_IN_DB(db, db.qualifiers, '%(name)s',zero=T("Choose one"))),
        Field('q_value',length=255,label=T("Qualifier Value")),
        Field('destinies', 'list:reference nodes',label=T("Destinies"),
        requires = IS_IN_DB(db, db.nodes, '%(name)s', multiple=True)),
    )
    if conn_form.process().accepted:
        if(request.vars.destinies):
            db.commit()
            source_id = request.vars.source_id
            destinies = request.vars.destinies
            edtype = request.vars.edtype
            qualifier = request.vars.qualifier
            q_value = request.vars.q_value
            if (not (type(destinies) is list)):
                destinies = [destinies]
            response.flash = T('Connection Created!')
            for d in destinies:
                conn_id=db.edges.update_or_insert(source_id=source_id,e_type=edtype,qualifier=qualifier,q_value=q_value,destiny_id=d)
            db.commit()
        else:
            response.flash = T('Select a destiny')
    elif conn_form.errors:
        response.flash = T('Erro! Please, verify your form!')

    content = table_list(db.edges,T("Edges"),db.edges.source_id,create=False)
    content['form']=conn_form
    return content

def edges():
	table=db.edges
	return table_list(table,T("Edges"),table.source_id)

def qualifiers():
	table=db.qualifiers
	return table_list(table,T("Qualifiers"),table.name)

def info():
    table=db.informations
    return table_list(table,T("Informations"),table.edge)

def nodes():
	table=db.nodes
	return table_list(table,T("Nodes"),table.name)

def node_types():
	table=db.node_types
	return table_list(table,T("Node Types"),table.name)

def edge_types():
	table=db.edge_types
	return table_list(table,T("Edge Types"),table.name)

def bib():
    from pybtex.database.input import bibtex
    from pybtex.database import BibliographyData
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")

    parser = bibtex.Parser()
    bib_form = FORM(T('Bibtex file:'),INPUT(_name='bib_file',_type='file'),INPUT(_type='submit'))
    db.commit()
    if bib_form.accepts(request.vars,session,formname='bib_form'):
        if(request.vars['bib_file']==''):
          response.flash = T('Please, select a file!')
        else:
          bib_data = parser.parse_string(request.vars['bib_file'].value)
          for key in bib_data.entries.keys():
            tmp = BibliographyData()
            tmp.add_entry(key,bib_data.entries.get(key))
            source_id = tmp.to_string('bibtex')
            bibid=db.bibliographies.insert(bibkey=key,code=source_id)
            if(bibid < 0):
                db.rollback()
                break
          redirect(URL('bib'))
    elif bib_form.errors:
        response.flash = T('File has errors')
    db.commit()
    bibs = db().select(db.bibliographies.ALL,orderby=db.bibliographies.bibkey)
    list_bibs = {}
    idx = []
    for bib in bibs:
        bib_data = parser.parse_string(bib.code)
        bibstr = ""
        fields = bib_data.entries[bib.bibkey].rich_fields.values()
        for f in fields:
            bibstr += "%s." % f.render_as('html')
        list_bibs[bib.bibkey]=bibstr
        idx.append(bib.bibkey)
    return dict(form=bib_form,list=list_bibs,idx=idx)
