Github Issue Auto-Responder
===========================
Polls GitHub project issues on a regular interval to look for issues *without comments*
and tries to identify a proper response for the ticket, adding a comment and/or a
label if so.

Requirements
------------
Python 2.6, 2.7

Installation Instructions
-------------------------
1. Install via pip:

    pip install github-issue-autoresponder

2. Create a Personal API Token on GitHub: https://github.com/blog/1509-personal-api-tokens
3. Copy `/usr/share/github_issue_autoresponder/etc/github_issue_autoresponder.yml` to `/etc`
4. Edit `/etc/github_issue_autoresponder.yml `

Optional (RHEL distros):

    cp /usr/share/github_issue_autoresponder/etc/github_issue_autoresponder.initd /etc/init.d/github_issue_autoresponder
    chmod u+x /etc/init.d/github_issue_autoresponder
    chkconfig github_issue_autoresponder on

Running
-------

    github_issue_autoresponder -c path/to/configuration [-f]

Configuration
-------------
The configuration file uses *YAML* syntax for its markup and **whitespace/indentation is important**. For more information on *YAML*, please visit http://yaml.org. A good resource for configuration lint checking is http://yamllint.com.

The configuration is set per user/org and repository and may have multiple rules. Each rule has multiple sections: strings, response and action.

 - *strings* should be entered all lowercase* and match the lowercase title and body of an issue. If a string is matched, any values in the response section will be added as a comment any labels in action > label will be added.

 - *response* is a list of strings to add to the comment. If there is more than one item in the list, they will be added as a list, if there is only one, it will just be the string.

 - *action* currently only supports labels but may do more in the future. If any of the strings are matched, labels in the labels sub tree will be added. Labels should be entered as a list.

 To change how often the application will poll, edit the Application > wake_interval value in seconds. 

Example
-------
The following configuration would scan issues at https://github.com/you/repo_name running two rules:

 - rule_one scans for "string value 1" and "string value 2" and if found in the title or body of the issue, it will add two bullets from the response stanza of the config and it will add a "pending review" label.
 - rule two scans for "foo" in the title or body and adds the comment "This issue matched on foo" 


    %YAML 1.2
    ---
    Application:
      api_url: https://api.github.com
      wake_interval: 300
      access_token: PUT-A-PERSONAL-ACCESS-TOKEN-HERE
      comment_prefix:
        - "*This is an automated response to your ticket.*"
      repositories:
        you:
          repo_name:
            rule_one:
              strings:
                - string value 1
                - string value 2
              response:
                - This issue was matched on "string value 1" or "string value 2" in the issue title or body.
                - You can have multiple items to note in the comment response
              action:
                label:
                  - pending review
            rule_two:
              strings:
                - foo
              response:
                - This issue matched on "foo"

    Daemon:
        user: github_issue_autoresponder
        group: daemon
        pidfile: /var/run/github_issue_autoresponder.pid

    Logging:
      loggers:
        github_issue_autoresponder:
          handlers: [console]
          level: DEBUG
          propagate: true
