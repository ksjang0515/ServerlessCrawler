PROXY = "http://user-ksjang0515:jks020515@kr.smartproxy.com:10000"
URL = "https://pcmap-api.place.naver.com/place/graphql"

KEYWORD = "음식점"

MINIMUM_DISTANCE = 0.0005
# ROOT_BOUNDS = "126.5000000;35.0000000;129.4000000;38.0000000"
ROOT_BOUNDS = "126.8124125;37.4527307;127.1700164;37.6881443"

# S3
S3_BUCKET_NAME = "fast-coord-gql-crawler"
S3_KEYWORDS_PATH = "Keywords"
S3_CHILDNODES_PATH = "ChildNodes"

# Lambda
CHECKER_INITIATOR_FN_NAME = "CheckerInitiatorFn"
CHECKER_FN_NAME = "CheckerFn"

# Timestream
TIMESTREAM_DB_NAME = "TimestreamTest"
TIMESTREAM_TABLE_NAME = "TestTable"
TIMESTREAM_REGION = "ap-northeast-1"