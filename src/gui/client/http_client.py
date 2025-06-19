"""
Modular HTTP client for TECMFS-CE
Responsibilities are separated by module
"""
import urllib.request
import urllib.parse
import json
from config import SERVER_CONFIG

class HTTPClient:
    """Basic HTTP client without business logic"""
    
    def __init__(self, base_url, timeout=None):
        self.base_url = base_url
        # Use config timeout if not specified
        self.timeout = timeout or SERVER_CONFIG["timeout"]
    
    def get(self, endpoint, params=None):
        """Basic GET request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            response = urllib.request.urlopen(url, timeout=self.timeout)
            data = response.read().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            return None
    
    def post(self, endpoint, data=None, params=None):
        """Basic POST request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            
            post_data = json.dumps(data).encode('utf-8') if data else b''
            response = urllib.request.urlopen(req, data=post_data, timeout=self.timeout)
            return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return None
    
    def delete(self, endpoint, params=None):
        """Basic DELETE request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            req = urllib.request.Request(url)
            req.get_method = lambda: 'DELETE'
            response = urllib.request.urlopen(req, timeout=self.timeout)
            return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return None
    
    def post_binary(self, endpoint, binary_data, content_type="application/octet-stream", params=None):
        url = self.base_url + endpoint
        req = urllib.request.Request(url, data=binary_data, method="POST")
        req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                resp_data = response.read()
                try:
                    return json.loads(resp_data.decode("utf-8"))
                except Exception:
                    return None
        except Exception as e:
            print(f"[HTTPClient] post_binary error: {e}")
            return None

    def get_binary(self, endpoint, params=None):
        """GET request for binary data (file downloads)"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            response = urllib.request.urlopen(url, timeout=self.timeout)
            return response.read()  # Return raw binary data
        except Exception as e:
            return None
