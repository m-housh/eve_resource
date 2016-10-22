=====
Usage
=====

To use EveResource in a project::

    import eve_resource


Example Resource
---------------

persons.py::
    
    import eve_resource
    
    persons = eve_resource.Resource(
        'persons',  # resource name, to register with the app.

        'first_name', 'last_name'  # keys for resource fields.
    )

    @persons.schema
    def schema(key):
        # You can optionally use the key to avoid typo's for your schema
        return {
            key.first_name: {
                'type': 'string',
                'required': True
            },
            key.last_name: {
                'type': 'string',
                'required': True
            }
        }

    @persons.definition
    def definition():
        # we do not need to declare a schema property, our above
        # schema will be added by default, however if you do declare
        # a schema inside the definition, then the resource's schema will
        # not be used.
        return {
            'item_title': 'person',
            'public_methods': ['GET', 'POST', 'DELETE']
        }

    @persons.hooks.mongo('insert', 'replaced', 'updated')
    def lower_strings(items, originals=None):
        # lower case the first and last name before saving to the
        # database.
        for item in items:
            first_name = item.get('first_name')
            if first_name:
                item['first_name'] = first_name.lower()

            last_name = item.get('last_name')
            if last_name:
                item['last_name'] = last_name.lower()


app.py::
    
    from eve import Eve

    from .persons import persons


    app = Eve(settings={'DOMAIN': {}})
    
    # add the resource to the app DOMAIN and register hooks with 
    # the app.
    persons.init_api(app)

    if __name__ == '__main__':
        app.run()
    
