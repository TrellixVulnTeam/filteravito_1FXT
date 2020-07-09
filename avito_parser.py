import random
import datetime
import re

from selenium.common.exceptions import WebDriverException
import userAgenetRotator
from avito_filter_page import AvitoFilterPage
from crawler_data import CrawlerData
from geolocation_data import geolocation_map
from image_download_manager import DownloadManager
from realty_appartment_page import RealtyApartmentPage
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import logging

# log settings
now = datetime.datetime.now()
logname = str(now.strftime('%Y-%m-%dT%H-%M-%S')) + " parser.log"
logging.basicConfig(level=logging.INFO, filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')


class AvitoParser:
    driver = None
    download_manager = None

    def __init__(self, queue):
        self.setup_driver()

    # generate a random UA
    def setup_driver(self):
        useragent = random.choice(userAgenetRotator.USER_AGENTS_LIST)
        logging.info(useragent)
        # proxy set manually by firefox in a profile folders
        # load the profile with a set proxy
        profile = webdriver.FirefoxProfile("/home/ilya/.mozilla/firefox/vfwzppqq.avitoproxy")
        # no images
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        # set fake UA
        profile.set_preference("general.useragent.override", useragent)
        options = Options()
        options.headless = True
        driver = Firefox(options=options, firefox_profile=profile)
        driver.set_page_load_timeout(CrawlerData.IMPLICIT_TIMEOUT_INT_SECONDS)
        self.driver = driver

    # parses the given location into realty_page objects
    # feeds up the image downloader with realty page images

    def parse_location(self, location):
        filter_page = AvitoFilterPage(self.driver, geolocation_map["Боровск"])
        filter_page.parse_filter_page()
        # some advertisments found
        if len(filter_page.daily_hrefs) > 0:
            # set up the downloader
            self.download_manager = DownloadManager(thread_count=4)
            self.download_manager.begin_downloads()
            # go through each page sequentially
            for realty_link in filter_page.daily_hrefs:
                realty_page = RealtyApartmentPage(self.driver, realty_link)
                realty_page.parse_realty_apprment_page()
                # extract advertisment number
                # Объявление: №507307470, Сегодня, 14:04
                # make up a tuple of (507307470, {links})
                # queue it up in the image downloader
                adv = (re.search('\d{9}', realty_page.timestamp), realty_page.realty_images)
                self.download_manager.queue_image_links(adv)
        else:
            logging.info("No links parsed")

    # feed the parses with certain algoritms
    def run_parser_task(self, tasks):

        for keys, locs in tasks.items():
            print(keys)
            logging.info(keys)
            print(*locs)
            for l in locs:
                try:
                    d = self.setup_driver()
                    print(l)
                    logging.info(l)
                    self.parse_location(d, l)
                except ValueError:
                    logging.error("Avito wrapper object is broken.", exc_info=True)
                except WebDriverException:
                    logging.error("Web driver crashed.", exc_info=True)
                except Exception:
                    logging.error("Parser crashed.", exc_info=True)
                finally:
                    # gracefully waiting for picture download  to complete
                    self.download_manager.endup_downloads()
                    # gracefully closing the driver
                    logging.info("Closing all active windows. Disposing the driver")
                    d.close()
                    d.quit()
                    logging.info("Parsing completed")
