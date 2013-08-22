"""
Auto-Respond to Github Issues when keyword matches are made

"""
import clihelper
import json
import logging
import requests
import urllib
import urlparse

import pprint

__version__ = '1.0.2'
LOGGER = logging.getLogger(__name__)
DESCRIPTION = 'Auto-respond to GitHub issues'


class Controller(clihelper.Controller):
    """The core application controller which is created by invoking
    clihelper.run().

   """
    @property
    def access_token(self):
        return self.application_config.get('access_token')

    @property
    def base_url_parts(self):
        return urlparse.urlparse(self.application_config.get('api_url'))

    def cleanup(self):
        """Place shutdown steps in this method."""
        del self.session

    def setup(self):
        """Place setup and initialization steps in this method."""
        self.session = requests.session()
        self.session.headers.update({'Authorization': 'token %s' %
                                                      self.access_token,
                                     'Content-Type': 'application/json'})
        self.base_url = self.base_url_parts

    def process(self):
        """This method is invoked every wake interval as specified in the
        application configuration. It is fully wrapped and you do not need to
        manage state within it.

        """
        for user in self.repos:
            for repo in self.repos[user]:
                self.process_issues(user, repo)

    def add_comment(self, user, repo, issue, value):
        LOGGER.info('Adding a comment to %s/%s issue #%s', user, repo, issue)
        response = self.session.post(self.post_comment_url(user, repo, issue),
                                     data=json.dumps({'body': value}))
        if response.status_code != 201:
            LOGGER.error('Error adding comment to %s/%s issue #%s (%s): %s',
                         user, repo, issue,
                         response.status_code, response.content)

    def add_label(self, user, repo, issue, value):
        response = self.session.post(self.add_labels_url(user, repo, issue),
                                     json.dumps([value]))
        if response.status_code != 200:
            LOGGER.error('Error adding label to %s/%s issue #%s (%s): %s',
                         user, repo, issue,
                         response.status_code, response.content)

    def process_issue(self, user, repo, issue):
        comments = list()
        match = False
        for stanza in self.repos[user][repo]:
            for string in self.repos[user][repo][stanza]['strings']:
                if (string in issue['body'].lower() or
                    string in issue['title'].lower()):
                    match = True
                    for line in self.repos[user][repo][stanza]['response']:
                        if len(self.repos[user][repo][stanza]['response']) == 1:
                            comments.append(line.strip())
                        else:
                            comments.append(" - %s" % line.strip())
        if comments:
            offset = 0
            for line in self.application_config['comments']['prefix']:
                comments.insert(offset, line.strip())
                offset += 1
            self.add_comment(user, repo, issue['number'], '\n'.join(comments))

        if match:
            if self.repos[user][repo][stanza]['action']['label']:
                for label in self.repos[user][repo][stanza]['action']['label']:
                    self.add_label(user, repo, issue['number'], label)

    def process_issues(self, user, repo):
        LOGGER.debug('URL: %s', self.issues_url(user, repo))
        response = self.session.get(self.issues_url(user, repo))
        if response.status_code != 200:
            LOGGER.error('Error getting issues for %s/%s (%s): %s',
                         user, repo, response.status_code, response.content)
            return
        for issue in response.json():
            if issue.get('comments'):
                process = True
                response = self.session.get(issue['comments_url'])
                for comment in response.json():
                    if (comment['user']['login'] in
                            self.application_config['comments']['skip_users']):
                        LOGGER.debug('Skipping issue #%s, already has comments '
                                     'from %s', issue['number'],
                                     comment['user']['login'])
                        process = False
                        break
                if not process:
                    continue
            #self.process_issue(user, repo, issue)

    @property
    def repos(self):
        return self.application_config['repositories']

    def post_comment_url(self, user, repo, issue):
        return self.url('/repos/%s/%s/issues/%s/comments' % (user, repo, issue))

    def issues_url(self, user, repo,
                   state='open', query_filter='all',
                   sort='created', direction='desc'):
        return self.url('/repos/%s/%s/issues' % (user, repo),
                            [('state', state),
                             ('filter', query_filter),
                             ('sort', sort),
                             ('direction', direction)])

    def add_labels_url(self, user, repo, issue):
        return self.url('/repos/%s/%s/issues/%s/labels' % (user, repo, issue))

    def url(self, path, query=None):
        parts = list(self.base_url_parts)
        parts[2] = path
        if query:
            parts[4] = urllib.urlencode(query)
        return urlparse.urlunparse(parts)


def main():
    clihelper.setup('github_issue_autoresponder', DESCRIPTION, __version__)
    clihelper.run(Controller)

