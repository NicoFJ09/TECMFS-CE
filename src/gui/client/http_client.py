"""
Cliente HTTP modular para TECMFS-CE
Responsabilidades separadas por módulo
"""
import urllib.request
import urllib.parse
import json
from PyQt5.QtCore import QObject, pyqtSignal
from config import SERVER_CONFIG


class HTTPClient:
    """Cliente HTTP básico sin lógica de negocio"""
    
    def __init__(self, base_url, timeout=None):
        self.base_url = base_url
        # Usar timeout de config si no se especifica
        self.timeout = timeout or SERVER_CONFIG["timeout"]
    
    def get(self, endpoint, params=None):
        """GET request básico"""
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
        """POST request básico"""
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
        """DELETE request básico"""
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
