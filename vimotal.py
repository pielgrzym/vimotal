# -*- coding: utf-8 -*-
import os
import urllib, urllib2
import ConfigParser
import cPickle as pickle
from xml.dom import minidom

ITERATION_GROUPS = (
        'current_backlog',
        'backlog',
        'done',
        'current',
        )

class Pivotal(object):
    def __init__(self):
        home = os.getenv("HOME")
        self.settings = ConfigParser.ConfigParser()
        self.settings.read(os.path.join(home, '.vimotal'))
        user = self.settings.get('auth', 'user')
        password = self.settings.get('auth', 'password')
        self.token = self.getToken(user, password)
        try:
            self.projects = self.readCache()
        except (IOError, EOFError):
            self.fetchProjects()

    def fetchProjects(self):
        config_sections = self.settings.sections()
        project_names = filter(lambda x: x.startswith('project_'), config_sections)
        r = {}
        for project_name in project_names:
            pid = self.settings.get(project_name, 'id')
            project_name = project_name.replace('project_','')
            project = PivotalProject(self, pid, project_name)
            r[project_name] = project
        self.writeCache(r)
        self.projects = r

    def readCache(self):
        c = None
        cachefile = self.settings.get('main', 'cachefile')
        home = os.getenv("HOME")
        with open(os.path.join(home,cachefile), 'rb') as cache:
            c = pickle.load(cache)
        return c

    def writeCache(self, data):
        cachefile = self.settings.get('main', 'cachefile')
        home = os.getenv("HOME")
        with open(os.path.join(home,cachefile), 'wb') as cache:
            pickle.dump(data, cache)

    def getToken(self, username, password):
        authurl = "https://www.pivotaltracker.com/services/v3/tokens/active"
        values = {
                'username': username,
                'password': password,
                }
        data = urllib.urlencode(values)
        request = urllib2.Request(authurl, data)
        response = urllib2.urlopen(request)
        dom = minidom.parseString(response.read())
        token = dom.getElementsByTagName('guid')[0]
        return token.firstChild.data

class PivotalProject(object):
    def __init__(self, pivotal, pid, name, groups=None):
        self.pivotal = pivotal
        self.pid = int(pid)
        self.name = name
        if groups is None:
            self.fetchGroups('current', 'backlog')
        else:
            self.fetchGroups(*groups)

    def __unicode__(self):
        return '%s [#%d]' % (self.name, self.pid)

    def fetchAllIterations(self):
        url = 'https://www.pivotaltracker.com/services/v3/projects/%d/iterations' % self.pid
        req = urllib2.Request(url, None, {'X-TrackerToken': self.pivotal.token})
        response = urllib2.urlopen(req)
        self.iterations = self.__parseIterationsXML(response.read())

    def fetchGroups(self, *args):
        for name in args:
            self.fetchIterationGroup(name)

    def fetchIterationGroup(self, name):
        if name not in ITERATION_GROUPS:
            raise AttributeError("No souch iteration group %s" % name)
        url = 'https://www.pivotaltracker.com/services/v3/projects/%d/iterations/%s' % (self.pid, name)
        req = urllib2.Request(url, None, {'X-TrackerToken': self.pivotal.token})
        response = urllib2.urlopen(req)
        setattr(self, name, self.__parseIterationsXML(response.read()))

    def __parseIterationsXML(self, xml):
        dom = minidom.parseString(xml)
        iterations = []
        for i in dom.getElementsByTagName('iteration'):
            iterations.append(PivotalIteration(i))
        return iterations

    def printIterations(self, group=None):
        if group not in ITERATION_GROUPS:
            raise AttributeError("No souch iteration group %s" % name)
        if not group:
            self.fetchIterationGroup(group)
        if group == 'current':
            current = u"Current"
        else:
            current = False
        group = getattr(self, group, None)
        result = ""
        for iteration in group:
            result += u"◆%d | %s - %s ---------------------- %% %g\n" % (
                    int(iteration.id),
                    iteration.get_date('start').strftime("%d.%m"),
                    current or iteration.get_date('finish').strftime("%d.%m"),
                    float(iteration.team_strength),
                    )
            for story in iteration.stories:
                result += u"    ▶ %d %s %s\n" % (
                            int(story.id),
                            story.get_type(),
                            story.name,
                        )
        return result


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

    def get_date(self, dname):
        if dname not in ['start', 'finish']:
            raise AttributeError("No souch date: %s" % dname)
        date = getattr(self, dname, None)
        from datetime import datetime
        try:
            return datetime.strptime(date[:19], "%Y/%m/%d %H:%M:%S")
        except:
            return "---"

    def __unicode__(self):
        return self.id

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

    def get_type(self):
        story_type = self.story_type
        if story_type == 'feature':
            return u"★ "
        elif story_type == 'bug':
            return u"✗ "
        elif story_type == 'chore':
            return u"◎ "
        else:
            return u"-"
