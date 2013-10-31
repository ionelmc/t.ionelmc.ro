from time import time
from uuid import uuid4
from urllib import urlencode
from Cookie import SimpleCookie
from werkzeug.urls import url_decode
#from werkzeug.debug import DebuggedApplication

def track(env, start_response):
    try:
        gaid, domain = env['PATH_INFO'].lstrip('/').split('/', 1)
        if '/' in domain:
            raise ValueError
    except ValueError:
        return """
            <html><body><h1>Usage:</h1>
            <code>%(host)s/UA-123456/domain.com?dp=<b>/path/to/page</b>&t=pageview&</code>

            </body></html>
        """ % {'host': env.get('HTTP_HOST', '')}

    cookies = SimpleCookie()
    if 'HTTP_COOKIE' in env:
        cookies.load(env['HTTP_COOKIE'])

    cookies['cid'] = cid = 'cid' in cookies and cookies['cid'].value or str(uuid4())
    cookies['cid']['path'] = '/%s/%s' % (gaid, domain)
    cookies['cid']['max-age'] = 31536000

    data = dict(
        v=1,
        tid=gaid,
        cid=cid,
        dh=domain,
        dr=env.get("HTTP_REFERER", ''),
        z=str(time()),
    )
    data.update(url_decode(env["QUERY_STRING"]).items())


    location = "//www.google-analytics.com/collect?" + urlencode(data)
    #start_response('200', [
    #    ('Set-Cookie', cookies['cid'].OutputString()),
    #])
    #return '<a href="%s?%s">x</a><code>%r</code><br><iframe src="%s"/>' % (
    #    env['PATH_INFO'], env["QUERY_STRING"],
    #    location, location
    #)

    start_response('307 Temporary Redirect', [
        ('Set-Cookie', cookies['cid'].OutputString()),
        ('Location', location)
    ])
    return ""
