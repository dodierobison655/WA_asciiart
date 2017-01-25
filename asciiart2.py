import webapp2
import logging
import re
import jinja2
import os
import time
from google.appengine.ext import db

## see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
    
class Art(db.Model) :
    title = db.StringProperty()
    art = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    
class MyHandler(webapp2.RequestHandler):
    def write(self, *writeArgs):    
        self.response.write(" : ".join(writeArgs))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def get(self):
        logging.info("********** MainPage GET **********")
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        python_dictionary = {}   # creating a new dictionary
        self.render("form.html", **python_dictionary)
    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        
class TestHandler(MyHandler):
    def post(self):
        logging.info("********** test GET **********")
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        title = self.request.get("title")
        art = self.request.get("art")
        e = ""
        if len(str(art))<1 or len(str(title))<1 :
            e = 'Need both a title and some artwork'
        else :
            artInst = Art()
            artInst.title = title
            artInst.art = art
            artInst.put()
            time.sleep(0.2)
        self.render("form.html", title=title, art=art, e=e, arts=arts)

class Favorite(MyHandler):
    def get(self) :
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        artInst = arts.get()
        id = artInst.key().id()   # get the id of instance
        logging.info("*** ID of this Art is "+str(id))
        title = Art.get_by_id(id).title
        art = Art.get_by_id(id).art
        self.render("favorite.html",title=title,art=art)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/testform', TestHandler),
    ('/favorite',Favorite)
], debug=True)