import requests

class Test:
    def http_request_1(self, url :str, method :str = 'get'):
        context = getattr(requests, method.lower())
        return context(url).text

    def http_request_2(self, url :str, method :str = 'get'):
        requests_method_list = {
            'get': requests.get,
            'post': requests.post,
            'options': requests.options,
            'put': requests.put,
            'delete': requests.delete,
            'head': requests.head,
        }
        
        if method not in requests_method_list:
            raise TypeError(f'使用了错误的请求方法：{method}')

        context = requests_method_list[method.lower()]

        return context(url).text

url = 'https://www.pixiv.net/'
res = Test().http_request_1(url, 'post')
print(res)
