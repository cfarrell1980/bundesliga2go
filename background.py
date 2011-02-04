"""Helpers functions to run log-running tasks.
   These used to be part of the default web.py distribution but have since been moved
   to the experimental branch as they are unstable. You can get the source from here:
   https://github.com/webpy/webpy/raw/686aafab4c1c5d0e438b4b36fab3d14d121ef99f/experimental/background.py
   web.py is in the public domain. It was started by Aaron Swartz (webpy@aaronsw.com)

   IMPORTANT!!! backgrounding doesn't work with web.py 0.3 You need to make the changes described here
   http://www.mail-archive.com/webpy@googlegroups.com/msg03365.html
"""
from web import utils,http
from web import webapi as web
import threading

def background(func):
    """A function decorator to run a long-running function as a background thread."""
    def internal(*a, **kw):
        web.data() # cache it
        web._context = {}
        #tmpctx = web._context[threading.currentThread()]
        web._context[threading.currentThread()] = utils.storage(web.ctx.copy())
        tmpctx = web._context[threading.currentThread()]
        def newfunc():
            web._context[threading.currentThread()] = tmpctx
            func(*a, **kw)
            myctx = web._context[threading.currentThread()]
            for k in myctx.keys():
                if k not in ['status', 'headers', 'output']:
                    try: del myctx[k]
                    except KeyError: pass
        
        t = threading.Thread(target=newfunc)
        background.threaddb[id(t)] = t
        t.start()
        web.ctx.headers = []
        #return seeother(changequery(_t=id(t)))
        return web.seeother(http.changequery(_t=id(t)))
    return internal
background.threaddb = {}

def backgrounder(func):
    def internal(*a, **kw):
        i = web.input(_method='get')
        if '_t' in i:
            try:
                t = background.threaddb[int(i._t)]
            except KeyError:
                return web.notfound()
            web._context[threading.currentThread()] = web._context[t]
            return
        else:
            return func(*a, **kw)
    return internal
