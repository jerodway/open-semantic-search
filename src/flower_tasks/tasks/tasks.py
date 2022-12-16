import time

from allgetout import app
from allgetout import etl_delete

from etl import ETL
from etl_file import Connector_File
from etl_filedirectory import Connector_Filedirectory

@app.task(name='etl.delete')
def delete(uri):
    etl_delete.delete(uri=uri)

#
# Index a file
#

@app.task(name='etl.index_file')
def index_file(filename, additional_plugins=(), wait=0, commit=False, config=None):

    if wait:
        time.sleep(wait)

    etl_file = Connector_File()

    # set alternate config options (will overwrite config options from config file)
    if config:
        for option in config:
            etl_file.config[option] = config[option]

    etl_file.index_file(filename=filename,
                        additional_plugins=additional_plugins)

    if commit:
        etl_file.commit()

#
# Index file directory
#


@app.task(name='etl.index_filedirectory')
def index_filedirectory(filename, config=None):

    etl_filedirectory = Connector_Filedirectory()

    # set alternate config options (will overwrite config options from config file)
    if config:
        for option in config:
            etl_filedirectory.config[option] = config[option]

    result = etl_filedirectory.index(filename)
    etl_filedirectory.commit()

    return result


#
# Index a webpage
#
@app.task(name='etl.index_web')
def index_web(uri, wait=0, downloaded_file=False, downloaded_headers=None):
    pass


#
# Index full website
#

@app.task(name='etl.index_web_crawl')
def index_web_crawl(uri, crawler_type="PATH"):
    pass


#
# Index webpages from sitemap
#

@app.task(name='etl.index_sitemap')
def index_sitemap(uri):
    pass


#
# Index RSS Feed
#

@app.task(name='etl.index_rss')
def index_rss(uri):
    pass


@app.task(name='etl.post_solr')
def post_solr(string_to_send=None):
    pass

#
# Enrich with / run plugins
#

@app.task(name='etl.enrich')
def enrich(plugins, uri, wait=0):

    if wait:
        time.sleep(wait)

    etl = ETL()
    etl.read_configfile('/etc/opensemanticsearch/etl')
    etl.read_configfile('/etc/opensemanticsearch/enhancer-rdf')

    etl.config['plugins'] = plugins.split(',')

    filename = uri

    # if exist delete protocoll prefix file://
    if filename.startswith("file://"):
        filename = filename.replace("file://", '', 1)

    parameters = etl.config.copy()

    parameters['id'] = uri
    parameters['filename'] = filename

    parameters, data = etl.process(parameters=parameters, data={})

    return data


@app.task(name='etl.index_twitter_scraper')
def index_twitter_scraper(search=None, username=None, Profile_full=False, limit=None, Index_Linked_Webpages=False):
    pass

