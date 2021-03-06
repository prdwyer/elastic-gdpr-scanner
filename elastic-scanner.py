#!/usr/bin/env python

###########################################################
# GDPR scanner, by Vincent Maury
# see https://github.com/blookot/elastic-gdpr-scanner
###########################################################


# This script requires Python 3!
import sys
MIN_PYTHON = (3, 0)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


import socket
import subprocess
import sys
import threading
from queue import Queue
import signal
import time
from urllib.request import Request, urlopen, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener
from urllib.error import URLError, HTTPError
import json
import re
import argparse
import ipaddress



# variables and inputs
VERBOSE = False
API_OUTPUT = False
SCAN_FIRST_INDEX_ONLY = False
SCAN_FIRST_PORT_ONLY = False
GDPR_SCAN = False               # by default, don't scan (inventory only)
THREAD_TIMEOUT = 240                 # timeout per host, in seconds
DEFAULT_TCP_SOCKET_TIMEOUT = 2              # timeout for port scan, in seconds
DEFAULT_NB_THREADS = 10             # nb of targets to scan in parallel
DEFAULT_TARGET = '127.0.0.1'
DEFAULT_PORT = '9200'
DEFAULT_USER = 'elastic'
DEFAULT_PASSWORD = 'changeme'
DEFAULT_LOG_FILE = 'es-gdpr-report.csv'
HTTP_OK = 0
HTTP_ERROR = -1
HTTP_UNAUTHORIZED = -2


# PII can include driver’s licenses, license plate numbers, VAT codes, heathcare identification numbers, and various other national ID numbers.
# main source: https://ipsec.pl/data-protection/2012/european-personal-data-regexp-patterns.html
# https://github.com/tvfischer/gdpr-data-patterns-detection which is empty...
REGEXES = [
'AIza[0-9A-Za-z-_]{35}',#'google_api'   
'6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$',#'google_captcha' : r
'ya29\.[0-9A-Za-z\-_]+',#'google_oauth'   : r
'AKIA[0-9A-Z]{16}',#'amazon_aws_access_key_id' : r
'amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',  #'amazon_mws_auth_toke' : r
's3\.amazonaws.com[/]+|[a-zA-Z0-9_-]*\.s3\.amazonaws.com',#'amazon_aws_url' : r
'EAACEdEose0cBA[0-9A-Za-z]+',#'facebook_access_token' : r
'basic\s*[a-zA-Z0-9=:_\+\/-]+',#'authorization_basic' : r
'bearer\s*[a-zA-Z0-9_\-\.=:_\+\/]+',#'authorization_bearer' : r
'api[key|\s*]+[a-zA-Z0-9_\-]+',#'authorization_api' : r
'key-[0-9a-zA-Z]{32}',#'mailgun_api_key' : r
'SK[0-9a-fA-F]{32}',#'twilio_api_key' : r
'AC[a-zA-Z0-9_\-]{32}',#'twilio_account_sid' : r
'AP[a-zA-Z0-9_\-]{32}',#'twilio_app_sid' : r
'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',# 'paypal_braintree_access_token' : r
'sq0csp-[ 0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}',#    'square_oauth_secret' : r
'sqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}',#    'square_access_token' : r
'sk_live_[0-9a-zA-Z]{24}',#    'stripe_standard_api' : r
'rk_live_[0-9a-zA-Z]{24}',#    'stripe_restricted_api' : r
'[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com*',#    'github_access_token' : r
'-----BEGIN RSA PRIVATE KEY-----',#    'rsa_private_key' : r
'-----BEGIN DSA PRIVATE KEY-----',#    'ssh_dsa_private_key' : r
'-----BEGIN EC PRIVATE KEY-----',#    'ssh_dc_private_key' : r
'-----BEGIN PGP PRIVATE KEY BLOCK-----',#    'pgp_private_block' : r
'ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$',#    'json_web_token' : r
'^[\w\.=-]+@[\w\.-]+\.[\w]{2,3}$',  #TEmail addresses       .Simpson@netwrix.com
'\b(?!000|666|9\d{2})([0-8]\d{2}|7([0-6]\d))([-]?|\s{1})(?!00)\d\d\2(?!0000)\d{4}\b', #U.S. Social Security numbers 513-84-7329
'^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$', #5MasterCard numbers 258704108753590
'\b([4]\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|[4]\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|[4]\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|[4]\d{3}\d{4}\d{4}\d{4})\b' #visa card number 4563-7568-5698-4587
'^3[47][0-9]{13}$' #American Express card numbers34583547858682157
'^((\d{5}-\d{4})|(\d{5})|([A-Z]\d[A-Z]\s\d[A-Z]\d))$'       #.S. ZIP codes97589
'[1,2][ ]?[0-9]{2}[ ]?[0,1,2,3,5][0-9][ ]?[0-9]{2}[ ]?[0-9]{3}[ ]?[0-9]{3}[ ]?[0-9]{2}',    # French social security number
'[0-9]{2}[A-Z]{2}[0-9]{5}',     # French passport number
'[0-9]{2}[0,1][0-9][0-9]{2}-[A-Z]-[0-9]{5}',    # German Personenkennziffer
# '[0-9]{3}/?[0-9]{4}/?[0-9]{4}',     # German Steuer-Identifikationsnummer
'[0-9]{2}[0-9]{2}[0,1][0-9][0-9]{2}[A-Z][0-9]{2}[0-9]',     # German Versicherungsnummer, Rentenversicherungsnummer
'[0-9,X,M,L,K,Y][0-9]{7}[A-Z]',     # Spanish Documento Nacional de Identidad
'[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-DFM]?',       # UK National Identity Number
# '[0-9]{3}[ -]?[0-9]{3}[ -]?[0-9]{4}',       # UK national health security number, but matches certain beats!
'[0-9]{2}\.?[0-9]{2}\.?[0-9]{2}-[0-9]{3}\.?[0-9]{2}',       # Belgium ID
'[A-Z]{2}?[ ]?[0-9]{2}[ ]?[0-9]{4}[ ]?[0-9]{4}[ ]?[0-9]{4}[ ]?[0-9]{4}[ ]?[0-9]{4}',        # EU IBAN

'(?:https?:)?\\/\\/angel\\.co\\/company\\/(?P<company>[A-z0-9_-]+)(?:\\/(?P<company_subpage>[A-z0-9-]+))?',
'(?:https?:)?\\/\\/angel\\.co\\/company\\/(?P<company>[A-z0-9_-]+)\\/jobs\\/(?P<job_permalink>(?P<job_id>[0-9]+)-(?P<job_slug>[A-z0-9-]+))',
'(?:https?:)?\\/\\/angel\\.co\\/(?P<type>u|p)\\/(?P<user>[A-z0-9_-]+)',
'mailto:(?P<email>[A-z0-9_.+-]+@[A-z0-9_.-]+\\.[A-z]+)',
'(?:https?:)?\\/\\/(?:www\\.)?(?:facebook|fb)\\.com\\/(?P<profile>(?![A-z]+\\.php)(?!marketplace|gaming|watch|me|messages|help|search|groups)[A-z0-9_\\-\\.]+)\\/?',
'(?:https?:)?\\/\\/(?:www\\.)facebook.com/(?:profile.php\\?id=)?(?P<id>[0-9]+)',
'(?:https?:)?\\/\\/(?:www\\.)?github\\.com\\/(?P<login>[A-z0-9_-]+)\\/(?P<repo>[A-z0-9_-]+)\\/?',
'(?:https?:)?\\/\\/(?:www\\.)?github\\.com\\/(?P<login>[A-z0-9_-]+)\\/?',
'(?:https?:)?\\/\\/plus\\.google\\.com\\/(?P<id>[0-9]{21})',
'(?:https?:)?\\/\\/plus\\.google\\.com\\/\\+(?P<username>[A-z0-9+]+)',
'(?:https?:)?\\/\\/news\\.ycombinator\\.com\\/item\\?id=(?P<item>[0-9]+)',
'(?:https?:)?\\/\\/news\\.ycombinator\\.com\\/user\\?id=(?P<user>[A-z0-9_-]+)',
'(?:https?:)?\\/\\/(?:www\\.)?(?:instagram\\.com|instagr\\.am)\\/(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\\.(?!\\.))){0,28}(?:[A-Za-z0-9_]))?)',
'(?:https?:)?\\/\\/(?:[\\w]+\\.)?linkedin\\.com\\/company\\/(?P<company_permalink>[A-z0-9-\\.]+)\\/?',
'(?:https?:)?\\/\\/(?:[\\w]+\\.)?linkedin\\.com\\/feed\\/update\\/urn:li:activity:(?P<activity_id>[0-9]+)\\/?',
'(?:https?:)?\\/\\/(?:[\\w]+\\.)?linkedin\\.com\\/in\\/(?P<permalink>[\\w\\-\\_\u00c0-\u00ff%]+)\\/?',
'(?:https?:)?\\/\\/(?:[\\w]+\\.)?linkedin\\.com\\/pub\\/(?P<permalink_pub>[A-z0-9_-]+)(?:\\/[A-z0-9]+){3}\\/?',
'(?:https?:)?\\/\\/medium\\.com\\/(?:(?:@(?P<username>[A-z0-9]+))|(?P<publication>[a-z-]+))\\/(?P<slug>[a-z0-9\\-]+)-(?P<post_id>[A-z0-9]+)(?:\\?.*)?',
'(?:https?:)?\\/\\/(?P<publication>(?!www)[a-z-]+)\\.medium\\.com\\/(?P<slug>[a-z0-9\\-]+)-(?P<post_id>[A-z0-9]+)(?:\\?.*)?',
'(?:https?:)?\\/\\/medium\\.com\\/@(?P<username>[A-z0-9]+)(?:\\?.*)?',
'(?:https?:)?\\/\\/medium\\.com\\/u\\/(?P<user_id>[A-z0-9]+)(?:\\?.*)',
'(?:tel|phone|mobile):(?P<number>\\+?[0-9. -]+)',
'(?:https?:)?\\/\\/(?:[a-z]+\\.)?reddit\\.com\\/(?:u(?:ser)?)\\/(?P<username>[A-z0-9\\-\\_]*)\\/?',
'(?:(?:callto|skype):)(?P<username>[a-z][a-z0-9\\.,\\-_]{5,31})(?:\\?(?:add|call|chat|sendfile|userinfo))?',
'(?:https?:)?\\/\\/(?:www\\.)?snapchat\\.com\\/add\\/(?P<username>[A-z0-9\\.\\_\\-]+)\\/?',
'(?:https?:)?\\/\\/(?:www\\.)?stackexchange\\.com\\/users\\/(?P<id>[0-9]+)\\/(?P<username>[A-z0-9-_.]+)\\/?',
'(?:https?:)?\\/\\/(?:(?P<community>[a-z]+(?!www))\\.)?stackexchange\\.com\\/users\\/(?P<id>[0-9]+)\\/(?P<username>[A-z0-9-_.]+)\\/?',
'(?:https?:)?\\/\\/(?:www\\.)?stackoverflow\\.com\\/questions\\/(?P<id>[0-9]+)\\/(?P<title>[A-z0-9-_.]+)\\/?',
'(?:https?:)?\\/\\/(?:www\\.)?stackoverflow\\.com\\/users\\/(?P<id>[0-9]+)\\/(?P<username>[A-z0-9-_.]+)\\/?',
'(?:https?:)?\\/\\/(?:t(?:elegram)?\\.me|telegram\\.org)\\/(?P<username>[a-z0-9\\_]{5,32})\\/?',
'(?:https?:)?\\/\\/(?:[A-z]+\\.)?twitter\\.com\\/@?(?P<username>[A-z0-9_]+)\\/status\\/(?P<tweet_id>[0-9]+)\\/?',
'(?:https?:)?\\/\\/(?:[A-z]+\\.)?twitter\\.com\\/@?(?P<username>[A-z0-9_]+)\\/?',
'(?:https?:)?\\/\\/vimeo\\.com\\/user(?P<id>[0-9]+)',
'(?:https?:)?\\/\\/(?:(?:www)?vimeo\\.com|player.vimeo.com\\/video)\\/(?P<id>[0-9]+)',
'(?:https?:)?\\/\\/(?:[A-z]+\\.)?youtube.com\\/channel\\/(?P<id>[A-z0-9-\\_]+)\\/?',
'(?:https?:)?\\/\\/(?:[A-z]+\\.)?youtube.com\\/user\\/(?P<username>[A-z0-9]+)\\/?',
'(?:https?:)?\\/\\/(?:(?:www\\.)?youtube\\.com\\/(?:watch\\?v=|embed\\/)|youtu\\.be\\/)(?P<id>[A-z0-9\\-\\_]+)',
]


# a print_lock is what is used to prevent "double" modification of shared variables.
# this is used so while one thread is using a variable, others cannot access
# it. Once done, the thread releases the print_lock.
# to use it, you want to specify a print_lock per thing you wish to print_lock.
print_lock = threading.Lock()
start_time = time.time()



# handle Ctrl-C to stop
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)



# main scanning function
def portscan(hostname):
    ip = socket.gethostbyname(hostname)
    for port in PORTS:
        if VERBOSE:
            print ("** DEBUG ** Scanning Host: {}, Port {}".format(ip,port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(float(TCP_SOCKET_TIMEOUT))
            s.connect((ip,int(port)))
            s.close()
        except socket.gaierror:
            print ('Hostname could not be resolved. Exiting')
            # pass
        except socket.error:
            print ("Host: {}, Port {}: Closed".format(ip,port))
            # pass
        else:
            if VERBOSE:
                print ("Host: {}, Port {}: Open".format(ip,port))
            # Try getting ES answer
            # first try http with no authentication
            auth = False
            proto = 'http'
            encr = False
            res = runRequest(proto,hostname,port,'',auth)
            if res['code'] == HTTP_ERROR:
                # now try with https
                proto = 'https'
                encr = True
                res = runRequest(proto,hostname,port,'',auth)
                # if we need auth, try again with auth
            if res['code'] == HTTP_UNAUTHORIZED:
                # auth in place, retry with auth
                auth = True
                res = runRequest(proto,hostname,port,'',auth)
            if res['code'] == HTTP_OK:
                esAnswer = res['content']
                if 'cluster_name' in esAnswer:
                    clusterName = esAnswer['cluster_name']
                else:
                    clusterName = "null"
                if 'name' in esAnswer:
                    name = esAnswer['name']
                else:
                    name = "null"
                if 'version' in esAnswer:
                    if 'number' in esAnswer['version']:
                        versionNumber = esAnswer['version']['number']
                    else:
                        versionNumber = 'null'
                else:
                    versionNumber = 'null'
                # then grab stats on node from /_stats/docs,store
                res = runRequest(proto,hostname,port,'/_stats/docs,store',auth)
                if res['code'] == HTTP_OK:
                    esAnswer = res['content']
                    if '_all' in esAnswer:
                        if 'total' in esAnswer['_all']:
                            totalDocs = esAnswer['_all']['total']['docs']['count']
                            totalSize = int(int(esAnswer['_all']['total']['store']['size_in_bytes'])/(1024*1024))
                        else:
                            totalDocs = 'null'
                            totalSize = 'null'
                    else:
                        totalDocs = 'null'
                        totalSize = 'null'
                    print ("Found Host: {}, Port: {}, Encrypted: {}, Authenticated: {}, Cluster name: {}, Name: {}, Version: {}, Total number of docs: {}, Total size (MB): {}".format(ip, port, encr, auth, clusterName, name, versionNumber, totalDocs, totalSize))
                    logFile.write("{},{},{},{},{},{},{},{},{}\r\n".format(ip, port, encr, auth, clusterName, name, versionNumber, totalDocs, totalSize))
                    if GDPR_SCAN:
                        # then explore indices
                        # /_cat/indices introduced in 1.3, not working on v0.90 (thus relying on node stats...)
                        if 'indices' in esAnswer:
                            for index, indexDetails in iter(esAnswer['indices'].items()):
                                if VERBOSE:
                                    print ("** Testing index {}".format(index))
                                # consider non-internal indices
                                if index[:1] != '.':
                                    # grab index stats
                                    # print (json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
                                    indexNbDocs = indexDetails['total']['docs']['count']
                                    indexSize = int(int(indexDetails['total']['store']['size_in_bytes'])/(1024*1024))
                                    # then get first doc : /[index]/_search?size=1
                                    res = runRequest(proto,hostname,port,index+"/_search?size=1",auth)
                                    if res['code'] == HTTP_OK:
                                        esDocs = res['content']
                                        # check if at least 1 document
                                        if esDocs['hits']['total'] == 0:
                                            if VERBOSE:
                                                print ("No document found in index "+index)
                                            logFile.write("{},{},{},{},{},{},{},{},{},{},{},{},N/A (no doc)\r\n".format(ip, port, encr, auth, clusterName, name, versionNumber, totalDocs, totalSize, index, indexNbDocs, indexSize))
                                        else:
                                            # get source doc
                                            try:
                                                source = esDocs['hits']['hits'][0]['_source']
                                            except:
                                                print ('Couldn\'t get document from index '+index)
                                            else:
                                                # check for compliance calling regex checker func (outputs true when regex match, ie *not* compliant)
                                                rgpdCheck = regex_checker(source)
                                                if VERBOSE:
                                                    print ('** Testing index {}, result: {}'.format(index, rgpdCheck['result']))
                                                else:
                                                    if rgpdCheck['result']:
                                                        # display uncompliant indices even if not verbose
                                                        print ("** Host: {}, Port: {}, Encrypted: {}, Authenticated: {}, Cluster name: {}, Name: {}, Version: {} - Index {} not compliant! (value '{}' matched regex '{}')".format(ip, port, encr, auth, clusterName, name, versionNumber, index, rgpdCheck['value'], rgpdCheck['regex']))
                                                # log in file anyway
                                                logFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\r\n".format(ip, port, encr, auth, clusterName, name, versionNumber, totalDocs, totalSize, index, indexNbDocs, indexSize, not(rgpdCheck['result']), rgpdCheck['value'], rgpdCheck['regex']))
                                    # scan only first index to go faster
                                    if SCAN_FIRST_INDEX_ONLY:
                                        break
                        # indices listing didn't work
                        else:
                            print ('Couldn\'t list indices')
            else:
                print ("Found Host: {}, Port {}, Encrypted: {}, Authenticated: {}".format(ip, port, encr, auth))
                logFile.write("{},{},{},{}\r\n".format(ip, port, encr, auth))
        # scan first port only
        if SCAN_FIRST_PORT_ONLY:
            break


# regex checker func (outputs true when regex match, ie outputs true when *not* compliant)
def regex_checker(jsonDoc):
    print ('Testing: '+json.dumps(jsonDoc))
    #print ('Testing: '+json.dumps(jsonDoc))
    for key, value in iter(jsonDoc.items()):
        if isinstance(value, str):
            for r in REGEXES:
                check = bool(re.search(r, value))
                if VERBOSE:
                    print ('\tCheck '+value+' against regex \''+r+'\': '+str(check))
                if check:
                    return {"result":True, "value":value, "regex":r}
        elif isinstance(value,dict):
            return regex_checker(value)
    return {"result":False, "value":"", "regex":""}



# sub function just running the GET
def runRequest(proto,host,port,query,auth):
    res = { 'code': HTTP_ERROR, 'encrypted': True, 'authenticated': True, 'content': ''}
    res['encrypted'] = (proto == 'https')
    res['authenticated'] = auth
    url = proto + '://' + host + ':' + port + '/' + query
    if VERBOSE:
        print ("Calling query {}".format(url))
    if auth:
        # create an authorization handler for basic auth on Elasticsearch
        p = HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, USER, PASSWORD)
        auth_handler = HTTPBasicAuthHandler(p)
        opener = build_opener(auth_handler)
        install_opener(opener)
    # add headers
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    try:
        # run request
        req = Request(url,headers=headers)
        r = urlopen(req)
    except HTTPError as e:
        if VERBOSE:
            print('Error HTTPError: '+str(e))
        if str(e).find('Unauthorized') > 0:
            res['code'] = HTTP_UNAUTHORIZED
        return res
    except URLError as e:
        if VERBOSE:
            print('Error URLError: '+str(e))
        return res
    except Exception as e:
        if VERBOSE:
            print('Error: '+str(e))
        return res
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        try:
            if r.code == 200:
                content = json.loads(r.read().decode('utf-8'))
                if API_OUTPUT:
                    print (json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')))
                res['code'] = HTTP_OK
                res['content'] = content
                return res
            else:
                return res
        except Exception as e:
            if VERBOSE:
                print('Error: '+str(e))
            return res
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise



# Getting arguments
parser = argparse.ArgumentParser(description='Scan Elasticsearch clusters to check for GDPR compliance.')
parser.add_argument('--target', action='store', default='', help='Hostname or IP range (CIDR format, eg 10.50.3.0/24) to scan (default: localhost)')
parser.add_argument('--port', action='store', default='', help='Port where Elasticsearch is running (default: 9200)')
parser.add_argument('--user', action='store', default='', help='Username to use to authenticate to Elasticsearch (default: elastic)')
parser.add_argument('--password', action='store', default='', help='Username to use to authenticate to Elasticsearch (default: changeme)')
parser.add_argument('--regex', action='store', default='', help='Specific regex to look for')
parser.add_argument('--nb-threads', action='store', default='', dest='nbthreads', help='Number of hosts to scan in parallel (default: 10)')
parser.add_argument('--socket-timeout', action='store', default='', dest='stimeout', help='Seconds to wait for each host/port scanned. Set it to 2 on the Internet, 0.5 in local networks (default: 2)')
parser.add_argument('--run-scan', action='store_true', default=False, dest='scan', help='Run scan for GDPR data (based on regex matching)')
parser.add_argument('--out', action='store', default='', help='Log file with verbose output (default: es-gdpr-report.csv)')
parser.add_argument('--verbose', action='store_true', default=False, help='Turn on verbose output in console')
results = parser.parse_args()
if results.target != '':
    TARGETS = results.target
else:
    TARGETS = DEFAULT_TARGET
if results.port != '':
    PORTS = [results.port]
else:
    PORTS = [DEFAULT_PORT]
if results.user != '':
    USER = results.user
else:
    USER = DEFAULT_USER
if results.password != '':
    PASSWORD = results.password
else:
    PASSWORD = DEFAULT_PASSWORD
if results.regex != '':
    list.append(REGEXES, results.regex)
if results.nbthreads != '':
    NB_THREADS = results.nbthreads
else:
    NB_THREADS = DEFAULT_NB_THREADS
if results.stimeout != '':
    TCP_SOCKET_TIMEOUT = results.stimeout
else:
    TCP_SOCKET_TIMEOUT = DEFAULT_TCP_SOCKET_TIMEOUT
GDPR_SCAN = results.scan
if results.out != '':
    LOG_FILE = results.out
else:
    LOG_FILE = DEFAULT_LOG_FILE
VERBOSE = results.verbose



# prepare log file
logFile = open(LOG_FILE,"w")
if not GDPR_SCAN:
    # simpler header when inventory only
    logFile.write("Host,Port,Encrypted,Authenticated,Cluster_name,Name,Version,Total_nb_docs,Total_size_in_MB\r\n")
else:
    logFile.write("Host,Port,Encrypted,Authenticated,Cluster_name,Name,Version,Total_nb_docs,Total_size_in_MB,Index,Index_nb_docs,Index_size_in_MB,Compliant,Value,Regex\r\n")


# The threader thread pulls a worker from the queue and processes it
def threader():
    while True:
        # gets a worker from the queue
        worker = q.get(True,THREAD_TIMEOUT)
        # Run the example job with the avail worker in queue (thread)
        try:
            portscan(worker)
        except:
            print ("Error in thread...")
        # completed with the job
        q.task_done()

# Create the queue and threader
q = Queue()

# how many threads are we going to allow for
for x in range(NB_THREADS):
     t = threading.Thread(target=threader)
     # classifying as a daemon, so they will die when the main dies
     t.daemon = True
     # begins, must come after daemon definition
     t.start()


# start workers for each address (if an IP range)
if TARGETS.find('/') > 0:
    for target in ipaddress.IPv4Network(TARGETS):
        q.put(str(target))
else:
    q.put(str(TARGETS))

# wait until the thread terminates.
q.join()


logFile.close()
print('')
print("Scan complete in {} seconds!".format(int(time.time() - start_time)))
