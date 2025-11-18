day5 Python中使用requests调用HTTP接口详解


## 一、基础使用、
---
### 安装requests
    
        pip install requests

### 基本HTTP方法

       import requests
       //GET请求
       response = requests.get('https://api.example.com/users')
       print(response.status_code)  // 状态码
       print(response.json())       // JSON响应
       print(response.text)         // 文本响应

       // POST请求
       data = {'username': 'admin', 'password': '123456'}
       response = requests.post('https://api.example.com/login', json=data)
    
       // 带参数的GET请求
       params = {'page': 1, 'size': 10}
       response = requests.get('https://api.example.com/users', params=params)
    
       // PUT请求
       update_data = {'name': 'John', 'age': 30}
       response = requests.put('https://api.example.com/users/1', json=update_data)
    
       // DELETE请求
       response = requests.delete('https://api.example.com/users/1')
    
       // PATCH请求
       patch_data = {'status': 'active'}
       response = requests.patch('https://api.example.com/users/1', json=patch_data)
---
### 请求头和认证

       
        // 自定义请求头
        headers = {
           'User-Agent': 'Mozilla/5.0',
           'Authorization': 'Bearer your_token_here',
           'Content-Type': 'application/json'
        }
        response = requests.get('https://api.example.com/data', headers=headers)
        
        // Basic认证
        from requests.auth import HTTPBasicAuth
        response = requests.get('https://api.example.com/data', 
                               auth=HTTPBasicAuth('username', 'password'))
        
        // 或者简写
        response = requests.get('https://api.example.com/data', 
                               auth=('username', 'password'))
---
### 超时和异常处理
    

    try:
        response = requests.get('https://api.example.com/data', timeout=5)
        response.raise_for_status()  // 如果状态码不是200，抛出异常
        data = response.json()
    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.ConnectionError:
        print("连接错误")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

---
## 二、进阶使用
### 会话管理（Session）


    // 使用Session可以保持cookie和连接复用
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer token'})
    // 登录
    login_data = {'username': 'admin', 'password': '123456'}
    session.post('https://api.example.com/login', json=login_data)
    // 后续请求会自动携带cookie和默认headers
    response = session.get('https://api.example.com/user/profile')
    // 关闭session
    session.close()

---
### 文件上传
    

    // 上传单个文件
    files = {'file': open('report.pdf', 'rb')}
    response = requests.post('https://api.example.com/upload', files=files)
    
    // 上传多个文件
    files = {
        'file1': open('image1.jpg', 'rb'),
        'file2': open('image2.jpg', 'rb')
    }
    response = requests.post('https://api.example.com/upload', files=files)
    
    // 带额外数据
    files = {'file': open('report.pdf', 'rb')}
    data = {'description': '月度报告'}
    response = requests.post('https://api.example.com/upload', 
                            files=files, data=data)
---
### 文件下载
    
        // 下载文件
        response = requests.get('https://example.com/large-file.zip', stream=True)
        with open('downloaded_file.zip', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
---
## 三、工具类封装

---
### 基础封装版本

    import requests
    import json
    from typing import Optional, Dict, Any
    from requests.exceptions import RequestException
    
    class HTTPClient:
        """HTTP客户端工具类"""
    
    def __init__(self, base_url: str = '', timeout: int = 30):
        """
        初始化HTTP客户端
        :param base_url: 基础URL
        :param timeout: 超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Python-HTTPClient/1.0'
        }
        self.session.headers.update(self.default_headers)
    
    def set_header(self, key: str, value: str):
        """设置默认请求头"""
        self.session.headers[key] = value
    
    def set_auth_token(self, token: str, token_type: str = 'Bearer'):
        """设置认证Token"""
        self.session.headers['Authorization'] = f'{token_type} {token}'
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        if endpoint.startswith('http'):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理响应"""
        try:
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'headers': dict(response.headers)
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': str(e),
                'data': response.text
            }
        except json.JSONDecodeError:
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.text,
                'headers': dict(response.headers)
            }
    
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        try:
            url = self._build_url(endpoint)
            response = self.session.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=self.timeout
            )
            return self._handle_response(response)
        except RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             json_data: Optional[Dict] = None, 
             headers: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        try:
            url = self._build_url(endpoint)
            response = self.session.post(
                url, 
                data=data,
                json=json_data,
                headers=headers, 
                timeout=self.timeout
            )
            return self._handle_response(response)
        except RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def put(self, endpoint: str, data: Optional[Dict] = None,
            json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        try:
            url = self._build_url(endpoint)
            response = self.session.put(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def delete(self, endpoint: str, params: Optional[Dict] = None,
               headers: Optional[Dict] = None) -> Dict[str, Any]:
        """DELETE请求"""
        try:
            url = self._build_url(endpoint)
            response = self.session.delete(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def upload_file(self, endpoint: str, file_path: str, 
                    file_key: str = 'file',
                    extra_data: Optional[Dict] = None) -> Dict[str, Any]:
        """上传文件"""
        try:
            url = self._build_url(endpoint)
            with open(file_path, 'rb') as f:
                files = {file_key: f}
                response = self.session.post(
                    url,
                    files=files,
                    data=extra_data,
                    timeout=self.timeout
                )
            return self._handle_response(response)
        except RequestException as e:
            return {'success': False, 'error': str(e)}
        except IOError as e:
            return {'success': False, 'error': f'文件错误: {str(e)}'}
    
    def close(self):
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        """支持with语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动关闭"""
        self.close()

---
### 使用示例

    // 基本使用
    client = HTTPClient(base_url='https://api.example.com')
    client.set_auth_token('your_token_here')
    
    // GET请求
    result = client.get('/users', params={'page': 1, 'size': 10})
    if result['success']:
        print(result['data'])
    else:
        print(f"错误: {result['error']}")
    
    // POST请求
    user_data = {'name': 'John', 'email': 'john@example.com'}
    result = client.post('/users', json_data=user_data)
    
    // 使用with语句自动管理资源
    with HTTPClient(base_url='https://api.example.com') as client:
        client.set_auth_token('token')
        result = client.get('/users')
        print(result)
    
    3. 增强版封装（带日志和重试）
        import requests
        import logging
        import time
        from typing import Optional, Dict, Any, Callable
        from functools import wraps
    
    // 配置日志
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    
    def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
        """重试装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except requests.exceptions.RequestException as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)  // 指数退避
                            logger.warning(f"请求失败，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                logger.error(f"请求失败，已达最大重试次数: {last_exception}")
                raise last_exception
            return wrapper
        return decorator
    
    class AdvancedHTTPClient:
    """增强版HTTP客户端"""
    
    def __init__(self, base_url: str = '', timeout: int = 30, 
                 max_retries: int = 3, enable_logging: bool = True):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_logging = enable_logging
        self.session = requests.Session()
        
        // 配置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=requests.adapters.Retry(
                total=max_retries,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def _log_request(self, method: str, url: str, **kwargs):
        """记录请求日志"""
        if self.enable_logging:
            logger.info(f"[{method}] {url}")
            if 'params' in kwargs and kwargs['params']:
                logger.debug(f"参数: {kwargs['params']}")
            if 'json' in kwargs and kwargs['json']:
                logger.debug(f"数据: {kwargs['json']}")
    
    def _log_response(self, response: requests.Response):
        """记录响应日志"""
        if self.enable_logging:
            logger.info(f"响应状态: {response.status_code}")
            logger.debug(f"响应时间: {response.elapsed.total_seconds()}秒")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """通用请求方法"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if not endpoint.startswith('http') else endpoint
        
        self._log_request(method, url, **kwargs)
        
        response = self.session.request(
            method=method,
            url=url,
            timeout=kwargs.pop('timeout', self.timeout),
            **kwargs
        )
        
        self._log_response(response)
        
        return {
            'success': response.ok,
            'status_code': response.status_code,
            'data': response.json() if response.content and 'application/json' in response.headers.get('Content-Type', '') else response.text,
            'headers': dict(response.headers),
            'elapsed': response.elapsed.total_seconds()
        }
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('DELETE', endpoint, **kwargs)

--- 

//使用示例
    
    // 创建客户端实例
        client = AdvancedHTTPClient(
            base_url='https://api.example.com',
            timeout=30,
            max_retries=3,
            enable_logging=True
        )
    
    // 设置认证
        client.session.headers.update({
            'Authorization': 'Bearer your_token',
            'Content-Type': 'application/json'
        })
    
    // 发送请求
        try:
            result = client.get('/users', params={'page': 1})
            if result['success']:
                print(f"数据: {result['data']}")
                print(f"响应时间: {result['elapsed']}秒")
        except Exception as e:
            print(f"请求失败: {e}")

四、最佳实践

    使用Session进行连接复用，提高性能
    
    设置合理的超时时间，避免长时间等待
    
    统一的异常处理，提高代码健壮性
    
    日志记录，便于调试和监控
    
    重试机制，应对网络不稳定
    
    环境变量管理敏感信息，如API密钥
    
    使用类型注解，提高代码可读性