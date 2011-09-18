import urllib, urllib2
import ConfigParser
from xml.dom import minidom

class Pivotal(object):
    def __init__(self):
        import os
        home = os.getenv("HOME")
        self.settings = ConfigParser.ConfigParser()
        self.settings.read(os.path.join(home, '.vimotal'))
        user = self.settings.get('auth', 'user')
        password = self.settings.get('auth', 'password')
        self.token = self.getToken(user, password)
        self.projects = self.populateProjects()

    def populateProjects(self):
        config_sections = self.settings.sections()
        project_names = filter(lambda x: x.startswith('project_'), config_sections)
        r = {}
        for project_name in project_names:
            pid = self.settings.get(project_name, 'id')
            project = PivotalProject(self, pid, project_name)
            r[project_name] = project
        return r

    def getToken(self, username, password):
        authurl = "https://www.pivotaltracker.com/services/v3/tokens/active"
        values = {
                'username': username,
                'password': password,
                }
        data = urllib.urlencode(values)
        request = urllib2.Request(authurl, data)
        response = urllib2.urlopen(request)
        response_dom = minidom.parseString(response.read())
        token = response_dom.getElementsByTagName('guid')[0]
        return token.firstChild.data

class PivotalProject(object):
    def __init__(self, pivotal, pid, name):
        self.pivotal = pivotal
        self.pid = int(pid)
        self.name = name
        self.fetchIterations()

    def __unicode__(self):
        return '%s [#%d]' % (self.name, self.pid)

    def fetchIterations(self):
        url = 'https://www.pivotaltracker.com/services/v3/projects/%d/iterations' % self.pid
        req = urllib2.Request(url, None, {'X-TrackerToken': self.pivotal.token})
        response = urllib2.urlopen(req)
        self.iterations = self.__parseIterationsXML(response.read())

    def __parseIterationsXML(self, xml):
        dom = minidom.parseString(xml)
        iterations = []
        for i in dom.getElementsByTagName('iteration'):
            iterations.append(PivotalIteration(i))
        return iterations

class PivotalIteration(object):
    def __init__(self, data):
        field_list = ['id', 'number', 'start', 'finish', 'team_strength']
        for field in field_list:
            try:
                setattr(self,
                        field,
                        data.getElementsByTagName(field)[0].firstChild.data)
            except (IndexError, AttributeError):
                setattr(self, field, None)
        self.stories = [ PivotalStory(s) for s in data.getElementsByTagName('story') ]

    def __unicode__(self):
        return '[#%d] - %d' % int(self.id, self.team_strength)

class PivotalStory(object):
    def __init__(self, data):
        field_list = [
                'id',
                'project_id',
                'story_type',
                'url',
                'estimate',
                'current_state',
                'description',
                'name',
                'requested_by',
                'owned_by',
                'created_at',
                'accepted_at',
                ]
        for field in field_list:
            try:
                setattr(self,
                        field,
                        data.getElementsByTagName(field)[0].firstChild.data)
            except (IndexError, AttributeError):
                setattr(self, field, None)

    def __unicode__(self):
        return '[#%d] %s' % int(self.id, self.name)
