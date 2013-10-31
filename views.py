from pyga.requests import Tracker, Page, Session, Visitor, PageViewRequest

def track(env, start_response):
    try:
        gaid, domain, page = env['PATH_INFO'].lstrip('/').split('/', 2)
    except ValueError:
        return """
            <html><body><h1>Usage:</h1>
            <code>%(host)s/UA-123456/domain.com/path/to/page?http://domain/referral/path</code>
            <blockquote>or</blockquote>
            <code>%(host)s/UA-123456/domain.com/path/to/page?http://domain/referral/path<code>
            </body></html>
        """ % {'host': env.get('HTTP_HOST', '')}

    tracker = Tracker(gaid, domain)
    tracker.config.queue_requests = True
    visitor = Visitor()
    visitor.ip_address = env['REMOTE_ADDR']
    visitor.user_agent = env.get('HTTP_USER_AGENT', None)
    page = Page('/' + page)
    page.referrer = env.get("QUERY_STRING") or None
    request = PageViewRequest(
        config=tracker.config,
        tracker=tracker,
        visitor=visitor,
        session=Session(),
        page=page,
    )
    start_response('307 Temporary Redirect', [
        ('Location', request.build_http_request().get_full_url())
    ])
    return ""
