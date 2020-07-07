import schemas.wview_extended

schema_with_additionalColumnsEDB = {
    'table': schemas.wview_extended.table + [('c2h5oh', 'REAL')] + [('c3h8', 'REAL')] + [('c4h10', 'REAL')] + [('ch4', 'REAL')] + [('h2', 'REAL')] + [('UV1','REAL')],
    'day_summaries' : schemas.wview_extended.day_summaries + [('c2h5oh', 'SCALAR')] + [('c3h8', 'SCALAR')] + [('c4h10', 'SCALAR')] + [('ch4', 'SCALAR')] + [('h2', 'SCALAR')] + ['UV1', 'SCALAR')]
}

