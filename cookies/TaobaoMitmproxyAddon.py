import mitmproxy.http

t0 = 'Object.defineProperties(navigator,{webdriver:{get:() => false}});'
t1 = '''
        window.chrome = {
    runtime: {},
    // 
  };
  '''

t2 = '''
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
'''
t3 = '''
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5,6],
  });
'''
t4 = '''
Object.defineProperties(navigator,{
 userAgent:{
   get: () => 
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
 }
})
'''


class TaobaoMitmproxyAddon(object):
    def __init__(self):
        self.filenames = {'114.js', 'um.js', '115.js'}

    def response(self, flow: mitmproxy.http.HTTPFlow):
        for filename in self.filenames:
            if filename in flow.request.url:
                flow.response.text = t3 + t2 + t4 + t0 + flow.response.text
                print('url={0} 注入js成功'.format(flow.request.url))


addons = [
    TaobaoMitmproxyAddon()
]
