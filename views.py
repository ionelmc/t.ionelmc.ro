import logging
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
        start_response('400', [])
        return """
<html><body>
    <h1>Usage:</h1>
    <code>%(host)s/UA-123456/domain.com?dp=<b>/path/to/page</b>&t=pageview<i>&args</i></code>
    <blockquote><dl>
        <dt><strong>UA-123456</strong></dt>
        <dd>This is the Tracking ID</dd>

        <dt><strong>domain.com</strong></dt>
        <dd>This is the domain that you see in your <a
            href="https://support.google.com/analytics/answer/2790010?hl=en-GB">
            Universal Analytics</a> javascript tracking code.</dd>

        <dt><strong>t</strong></dt>
        <dd>Type of event.</dd>

        <dt><strong>dp</strong></dt>
        <dd>Page url that should show as viewed. You want this to be the page
            path that the feed item points to. In other words, the URL without
            the protocol and domain. <strong>Don't forget to quote it !</strong>
            </dd>

        <dt><strong>dr</strong></dt>
        <dd>You can specify a different referral URL here. If you don't specify
            this then the <code>Referer</code> header is used. Set
            <code>dr</code> to empty value if you don't want this. <strong>Don't
            forget to quote it !</strong> </dd>

        <dt><strong>referer</strong></dt>
        <dd>Specify this to override the value from the <code>Referer</code>
            header is used. Has no effect if <strong><code>dr</code></strong> is
            set. <strong>Don't forget to quote it !</strong> </dd>

        <dt><strong><em>args</em></strong></dt>
        <dd>Any <a
            href="https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters">
            measurement protocol</a> parameters.</dd>

    </blockquote>
</body></html>
        """ % {'host': env.get('HTTP_HOST', '')}

    cookies = SimpleCookie()
    if 'HTTP_COOKIE' in env:
        cookies.load(env['HTTP_COOKIE'])

    cid = 'cid' in cookies and cookies['cid'].value or str(uuid4())
    cookies['cid'] = cid
    cookies['cid']['path'] = '/%s/%s' % (gaid, domain)
    cookies['cid']['max-age'] = 62899200
    parameters = url_decode(env["QUERY_STRING"])
    referer = parameters.pop('referer', None)
    data = dict(
        v=1,
        tid=gaid,
        cid=cid,
        dh=domain,
        dr=env.get("HTTP_REFERER", '') if referer is None else referer,
        z=str(time()),
    )
    data.update(parameters.items())

    logging.info("Redirect data: %r", data)
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

def warmup(env, start_response):
    start_response('200', [])
    return ""
