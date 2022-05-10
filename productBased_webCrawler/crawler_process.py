import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
import os
import const

configure_logging()
settings = get_project_settings() # settings not required if running
runner = CrawlerRunner(settings)  # from script, defaults provided

#runner.crawl('ptt')
#runner.crawl('ucar')
runner.crawl('jorsindo')

d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run()

# after all spider finished, update the data from local to gcs
cmd_cp_data_to_gcs = f"gsutil -m rsync -r {const.LOCAL_FILE_HOME_DIR} {const.GCS_FILE_HOME_DIR}"
os.system(cmd_cp_data_to_gcs)
# delete local data after copying them onto gcs
#os.system(f'rm -r {const.LOCAL_FILE_HOME_DIR}/*')