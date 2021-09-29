import sys
sys.path.insert(0, "/home/ansible/custom_Ansible_Libs/custom_fortitester_mgmt/")
from ansible.module_utils.basic import AnsibleModule
from APICall import APICall
import uuid

def dict_is_1dim(data):
    if not data:
        return True
    return not any(isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple) for value in data.values())

def main():
    fields = {
        "fortitester_ip": {"required": True, "type": "str"},
        "fortitester_port": {"required": True, "type": "int"},
        "fortitester_command": {
            "required": True, "type": "dict", "options": {
                "login": {
                    "type": "dict", "options": {
                        "user": {
                            "type": "str", "required": True
                        },
                        "password": {
                            "type": "str", "required": True
                        }
                    }
                },
                "request": {
                    "type": "dict", "options": {
                        "method": {
                            "required": True, "type": "str", "choices": ["get", "post"]
                            },
                        "api_command_collection": {
                            "required": True, "type": "dict", "options": {
                                "command": {"required": True, "type": "str"},
                                "payload": {"required": False, "type": "dict"},
                                "session": {"required": True, "type": "str"}
                            }
                            },
                    }
                },
                "logout": {
                    "type": "dict", "options": {
                        "session": { "type": "str", "required": True }
                    }
                }

            }
        },
        "session": {"required": False, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)

    changed = False
    failed = False
    msg = ""
    response = {}
    cookiefile = str(uuid.uuid4())

    api_call = APICall()
    msg = module.params['fortitester_command']['login']

    if module.params['fortitester_command'].get('login'):
        res = api_call.login_and_safe_cookies({
            'url': module.params['fortitester_ip'],
            'port': module.params['fortitester_port'],
            'https': True,
            'command': 'api/user/login',
            'payload': {'name': module.params['fortitester_command']['login']['user'], 'password': module.params['fortitester_command']['login']['password']},
            'request_headers': {'Content-Type' : 'application/json'},
            'cookiefile': cookiefile
        })

        if res:
            changed = True
            msg = "Login to fortitester successful."
        else:
            failed = True
            msg = "Login failed."
            cookiefile = ""

    elif module.params['fortitester_command'].get('logout'):
        try:
            res = api_call.logout_and_delete_cookie({
                'url': module.params['fortitester_ip'],
                'port': module.params['fortitester_port'],
                'https': True,
                'command': 'api/user/logout',
                'cookiefile': module.params['fortitester_command']['logout']['session']
            })
            changed = True
            msg = f'logout of session {module.params["fortitester_command"]["logout"]["session"]} successfull.'
            response = res.json()
        except Exception as e:
            failed = True
            msg = str(e.args)
            response = res.text

    elif module.params['fortitester_command'].get('request') and module.params['fortitester_command']['request']['method'] == 'get':
        api_command_collection = module.params['fortitester_command']['request']['api_command_collection']
        if not dict_is_1dim(api_command_collection['payload']):
            failed = True
            msg = "nested parameter list. Only 1 dimension of key/value pairs are supported."
        else:
            if api_command_collection.get('payload'):
                command = api_command_collection['command'] + '?' + '&'.join(f'{name}={value}' for name,value in api_command_collection['payload'].items())
            else: command = api_command_collection['command']

            res, _ = api_call.api_call_get({
                "url": module.params['fortitester_ip'],
                "port": module.params['fortitester_port'],
                "command": command,
                "cookiefile": api_command_collection['session'],
                "https": True
            }, use_cookie=True)

            
            if res.ok:
                changed = True
                msg = f"ran command {command} successfull."
                response = res.json()
            else:
                failed = True
                msg = f"error while running command {command}."
                response = res.text
    elif module.params['fortitester_command'].get('request') and module.params['fortitester_command']['request']['method'] == 'post':
        api_command_collection = module.params['fortitester_command']['request']['api_command_collection']
        res, _ = api_call.api_call_post({
                "url": module.params['fortitester_ip'],
                "port": module.params['fortitester_port'],
                "command": api_command_collection['command'],
                "payload": api_command_collection['payload'],
                "cookiefile": api_command_collection['session'],
                "request_headers": {'Content-Type' : 'application/json'},
                "https": True
        }, use_cookie=True)
        
        if res.ok:
            changed = True
            msg = f'ran command {api_command_collection["command"]} succsessfull.'
            response = res.json()
        else:
            failed = True
            msg = f'error while running command {api_command_collection["command"]}.'
            response = res.text

    module.exit_json(changed=changed, failed=failed, meta=msg, session=cookiefile, response=response)


if __name__ == '__main__':
    exit(main())





