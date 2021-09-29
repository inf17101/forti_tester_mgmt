import json, requests
import urllib3, pickle, os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APICall:

    def login_and_safe_cookies(self, params):
        if not all(k in params and params[k] for k in ('url', 'port', 'command', 'payload', 'request_headers', 'cookiefile', 'https')):
            raise ValueError('error missing parameters in login function. (url, port, command, payload, request_headers, cookiefile, https)')

        if not params.get('cookiefile'):
            raise ValueError('need a cookie filename specified.')
        res, session = self.api_call_post(params)
        if res.status_code == 200 and session:
            self.write_cookie_to_file(params['cookiefile'], session.cookies)
            return True
        return False

    def api_call_post(self, params, use_cookie=False):
        if not all(k in params for k in ('url', 'port', 'command', 'payload', 'request_headers')):
            raise ValueError('error missing parameters in api_call_post function. (url, port, command, payload, request_headers)')
        if params.get('https'):
            prefix = 'https'
        else: prefix = 'http'

        url = f'{prefix}://{params["url"]}:{params["port"]}/{params["command"]}'

        session = requests.Session()
        if params.get('cookiefile') and use_cookie:
            session.cookies.update(self.read_cookie_from_file(params['cookiefile']))
        res = session.post(url,data=json.dumps(params['payload']), headers=params['request_headers'], verify=False)
        return res, session

    def api_call_get(self, params, use_cookie=False):
        if not all(k in params and params[k] for k in ('url', 'port', 'command')):
            raise ValueError('error missing parameters in api_call_get function. (url, port, command)')
        if params.get('https'):
            prefix = 'https'
        else: prefix = 'http'

        url = f'{prefix}://{params["url"]}:{params["port"]}/{params["command"]}'
        session = requests.Session()
        if params.get('cookiefile') and use_cookie:
            session.cookies.update(self.read_cookie_from_file(params['cookiefile']))
        res = session.get(url, verify=False)
        return res, session

    def read_cookie_from_file(self, cookiefile):
        try:
            with open(cookiefile, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("cookie file not found.")
            return ""
        except Exception as e:
            raise Exception(f'unknown error occured while reading cookie from file.\n\n{str(e)}')
            return ""
    
    def write_cookie_to_file(self, cookiefile, cookie):
        try:
            with open(cookiefile, 'wb') as f:
                pickle.dump(cookie, f)
        except Exception as e:
            raise Exception(f'unknown error occured while writing cookie from file.\n\n{str(e)}')

    def logout_and_delete_cookie(self, params):
        if not all(key in params and params[key] for key in ('url', 'port', 'command', 'cookiefile')):
            raise ValueError('error missing parameters to logout. Expected: (url, port, command, cookiefile).')
        res = {}
        res, _ = self.api_call_get(params, use_cookie=True)
        if res.ok:
            try:
                os.remove(params['cookiefile'])
            except OSError as e:
                raise OSError(f'Cannot clean up session while logging out. Errors:{str(e)}')
            except Exception as e:
                raise Exception(f'unknown error occured while logging out. Errors: {str(e)}')
        else:
            raise Exception(f'api response indicates that logout failed.{str(res.text)}')
        
        return res

            


"""
if __name__ == '__main__':
    api_call = APICall()
    params = {
        "url": "192.168.26.155",
        "port": 443,
        "https": True,
        "command": "api/user/login",
        "payload": {'name': 'admin', 'password': 'hallo123'},
        "request_headers": {'Content-Type' : 'application/json'},
        "cookiefile": "somecookie.txt"
    }
    #res = api_call.login_and_safe_cookies('192.168.26.155', 443, 'api/user/login', {'name': 'admin', 'password': 'hallo123'}, {'Content-Type' : 'application/json'}, "somecookie.txt", https=True)
    res = api_call.login_and_safe_cookies(params)
    print(res)
    #res = api_call_post('192.168.26.155', 443, 'api/user/login', {'name': 'admin', 'password': 'hallo123'}, https=True)
    #with open('somecookie.txt', 'wb') as f:
        #pickle.dump(session.cookies, f)
    
    #with open('somecookie.txt', 'rb') as f:
        #session.cookies.update(pickle.load(f))

    #print(session.cookies)


    #res, _ = api_call.api_call_get('192.168.26.155', 443, 'api/case/getByName?testName=CP_ModuleValidation-IPS-Test', https=True, cookiefile='somecookie.txt')
    params['command'] = 'api/case/getByName?testName=CP_ModuleValidation-IPS-Test'
    res, _ = api_call.api_call_get(params, use_cookie=True)
    print(res.json())
    #print(res.json())
"""