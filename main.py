import webapp2,os,jinja2
from google.appengine.ext import db
from django.utils.baseconv import base62

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class UrlEntry(db.Model):
    url = db.StringProperty(required=True)
    hash = db.StringProperty()
    date = db.DateProperty(auto_now_add=True)
    hitcount = db.IntegerProperty()
        
        
class MainPage(webapp2.RequestHandler):
    def get(self):
        errmsg = self.request.get('errmsg',None)
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render({'errmsg':errmsg}))
        
    def post(self):
        url = self.request.get('url')
        if url.lower().startswith("http"):
            #check if duplicate
            urlEntry = UrlEntry.gql("WHERE url = :1", url).get()
            if not urlEntry:
                urlEntry = UrlEntry(url=url)
                urlEntry.hash = base62.encode(urlEntry.put().id())
                urlEntry.hitcount = 0
                urlEntry.put()
            template = jinja_environment.get_template('success.html')
            self.response.write(template.render({'original':urlEntry.url, 'shortened': self.request.url + urlEntry.hash}))
        else:
            self.redirect("/?errmsg=Invalid Url.")
            
class RedirectHandler(webapp2.RequestHandler):
    
    def get(self,shorty_hash):
        urlEntry = UrlEntry.get_by_id(int(base62.decode(str(shorty_hash))))
        if not urlEntry :
            self.redirect("/?errmsg=Looks like you found a Broken Url.")
        else:
            urlEntry.hitcount += 1
            urlEntry.put()
            self.redirect(str(urlEntry.url))
        
app = webapp2.WSGIApplication(
                              [('/', MainPage), ('/(.+)',RedirectHandler)], debug=True)