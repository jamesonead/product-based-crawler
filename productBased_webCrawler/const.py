MYSQL_HOST = '35.206.211.214'
#MYSQL_HOST = '10.240.0.48'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'product-based'
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = 'bdcd77202880'
#MYSQL_TABLE = 'crawled_urls'
MYSQL_TABLE = 'crawled_urls_v1'


GCS_BUCKET = 'onedata-prod'
GCS_FILE_HOME_DIR = f'gs://{GCS_BUCKET}/product-based/articles'

LOCAL_FILE_HOME_DIR = './articles'