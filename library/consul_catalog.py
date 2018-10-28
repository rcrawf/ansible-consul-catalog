#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview']
}

DOCUMENTATION = '''
---
module: consul_catalog

short_description: Module to register and deregister nodes to the Consul catalog.

version_added: "2.7"

author:
    - @lobstermania
'''

from ansible.module_utils.basic import *
import consul,json,ast

def main():
    
    fields = {
        "consul_host": {"required": False, "type":"str", "default":"localhost"},
        "consul_port": {"required": False, "type":"int", "default":8500},
        "token": {"required": False, "type":"str", "default":""},
        "node": {"required": True, "type":"str"},
        "dc": {"required": False, "type":"str", "default":"dc1"},
        "address": {"required": True, "type":"str"},
        "scheme": {"required": False, "type":"str", "choices":['http','https'],"default":"http"},
        "verify": {"required": False, "type":"bool", "default":False},
        "state": {"required": False, "type":"str", "choices":['present','absent'],"default":"present"},
        "service": {"required": False, "type": "raw", "default":""}
    }

    module = AnsibleModule(argument_spec=fields,supports_check_mode=False)
    c,cc = load_consul(module.params,module)

    if module.params["state"] == "present":
        has_changed,result = register_node(module.params,cc)
    elif module.params["state"] == "absent":
        has_changed,result = deregister_node(module.params,cc)
    
    module.exit_json(changed=has_changed,meta=result)

def load_consul(params,module):
    try:
        c = consul.Consul(host=params['consul_host'],verify=params['verify'],token=params['token'],dc=params['dc'],port=params['consul_port'],scheme=params['scheme'])
    except Exception as e:
        sys.exit(1)
    cc = c.catalog
    return c,cc

def check_node_exists(params,cc):
    nodes = cc.nodes()[1]
    exists = False
    for node in nodes:
        if node['Node'] == params['node']:
            exists = True
    return exists
    
def register_node(params,cc):
    svc = ast.literal_eval(params['service'])
    r = cc.register(params['node'],params['address'],dc=params['dc'],service=svc)
    has_changed = True
    result = r
    return has_changed,result

def deregister_node(params,cc):
    node_exists = check_node_exists(params,cc)
    if node_exists:
        r = cc.deregister(params['node'])
        has_changed = True
        result = r
    else:
        has_changed = False
        result = ""
    return has_changed,result

if __name__ == '__main__':
	main()
