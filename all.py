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
'my_regex', #    'name_for_my_regex' : r
'^example\w+{10,50}'#    'example_api_key'    : r
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
Can't match these with the regular post regex as redefinitions of subgroups are not allowed in pythons regex.',
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
