#!/usr/bin/env python

"""
generate_example.py

Usage:
  generate_example.py SPEC_FILE OUT_DIR
"""
from docopt import docopt
import json
import os
import os.path


def generate_resource_example(schema_dict, path):
    example = {}

    for property_name, property_value in schema_dict.items():
        if property_value['type'] == 'array':
            if 'oneOf' in property_value['items']:
                example[property_name] = [generate_resource_example(['properties'], property_name) for t in property_value['items']['oneOf']]
            elif property_value['items']['type'] == 'object':
                example[property_name] = [generate_resource_example(property_value['items']['properties'], property_name)]
            else:
                if {'example', 'default'} & set(property_value.get('items', {}).keys()):
                    items = property_value['items']
                    example[property_name] = [items.get('example', items.get('default'))]
                elif ('example' not in property_value) and ('default' not in property_value):
                    property_path = '.'.join(path)
                    raise RuntimeError(f'{property_path}.{property_name} has no example or default!')
                else:
                    example[property_name] = property_value.get('example', property_value.get('default'))
        elif property_value['type'] == 'object':
            example[property_name] = generate_resource_example(property_value['properties'], property_name)
        else:
            if ('example' not in property_value) and ('default' not in property_value):
                property_path = '.'.join(path)
                raise RuntimeError(f'{property_path}.{property_name} has no example or default!')
            example[property_name] = property_value.get('example', property_value.get('default'))

    return example



if __name__ == "__main__":
    arguments = docopt(__doc__, version='0')

    # Load spec from file
    with open(arguments['SPEC_FILE'], 'r') as f:
        spec = json.loads(f.read())

    # Create default dir structure
    for i in ['resources', 'requests', 'responses']:
        os.makedirs(os.path.join(arguments['OUT_DIR'], i), exist_ok=True)

    # Generate resources
    for component_name, component_spec in spec['components']['schemas'].items():
        with open(os.path.join(arguments['OUT_DIR'], 'resources', component_name + '.json'), 'w') as f:
            f.write(json.dumps(generate_resource_example(component_spec['properties'], [component_name])))
