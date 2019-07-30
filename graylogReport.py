#!/usr/bin/python3

from reportsLib import *
from docopt import docopt

TokenManagement = {
        'create': createToken,
        'delete': deleteToken,
        'remove': deleteToken,
        'update': updateTokens,
        'list': listTokens
        }

Report = {
        'absolute': absoluteReport,
        'relative': relativeReport,
        }

Mail = {
        'send': sendReport
        }

Search = {
        'get': getSearches
        }

def main(): 
    usage= """ Usage:
        graylogReport token create <tokenName> <user> <password> <server> [--port=<port>]
        graylogReport token delete <user> <password> <tokenValue> <server> [--port=<port>]
        graylogReport token list
        graylogReport token update <user> <password> <server> [--port=<port>]
        graylogReport token -h | --help
        graylogReport search get [--searchName=<searchName>] <tokenValue> <server> [--port=<port>]
        graylogReport report (absolute <startUTC> <endUTC> | relative <rel>) <tokenValue> <searchQuery> <fields> <server> [--filename=<filename>]
        graylogReport mail send <sender> <toaddr>  --subject=<subject> <filename> <mailserver>

    Options:
        -h --help                   Show this screen.
        <tokenName>                 Name for creating a token.
        <tokenValue>                Token value for Graylog API.
        <user>                      Graylog user.
        <password>                  Graylog password.
        <server>                    Graylog hostname or IP.
        --port=<port>               Graylog web api interface port. [default: 9000] 
        --searchName=<searchName>   Saved search name.
        <searchQuery>               Query for Graylog search (Lucene syntax).
        <startUTC>                  Timestamp YYYY-MM-dd HH:mm:ss.
        <endUTC>                    Timestamp YYYY-MM-dd HH:mm:ss.
        <rel>                       Relative time in seconds. 
        <fields>                    Fields from logs to export.
        <sender>                    Email sender.
        <toaddr>                    Email recipient.
        --subject=<subject>         Optional subject for email.
        <mailServer>                SMTP mail server to use.
   """     

    arguments = docopt(usage, version=None)

    # Token management
    if arguments['token']:
        # Remove token element since it's True
        del arguments['token']

        # Get key for True value, supposed to be a method
        aux = [ x for x in arguments if arguments[x] == True ]

        # Assign method to variable
        uep = TokenManagement[aux[0]]

        # Call method with arguments
        uep(arguments)

    # Searches 
    elif arguments['search']:
        # Remove search element since it's True
        del arguments['search']

        # Get key for True value, supposed to be a method
        aux = [ x for x in arguments if arguments[x] == True ]

        # Assign method to variable
        uep = Search[aux[0]]

        # Call method with arguments
        uep(arguments)

    # Reports
    elif arguments['report']:
        # Remove search element since it's True
        del arguments['report']

        # Get key for True value, supposed to be a method
        aux = [ x for x in arguments if arguments[x] == True ]

        # Assign method to variable
        uep = Report[aux[0]]

        # Call method with arguments
        uep(arguments)

    # Mail
    elif arguments['mail']:
        # Remove search element since it's True
        del arguments['mail']

        # Get key for True value, supposed to be a method
        aux = [ x for x in arguments if arguments[x] == True ]

        # Assign method to variable
        uep = Mail[aux[0]]

        # Call method with arguments
        uep(arguments)

if __name__ == '__main__':
	main()
