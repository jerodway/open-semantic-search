#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path
import sys

from etl import ETL


class Connector_File(ETL):

    def __init__(self, verbose=False, quiet=True):

        ETL.__init__(self, verbose=verbose)

        self.quiet = quiet

        self.set_configdefaults()

        self.read_configfiles()

    def set_configdefaults(self):
        #
        # Standard config
        #
        # Do not edit config here!
        # Overwrite options in /etc/etl/
        # or /etc/opensemanticsearch/connector-files
        #

        ETL.set_configdefaults(self)

        self.config['force'] = False

        # filename to URI mapping
        self.config['mappings'] = {"/": "file:///"}

        self.config['facet_path_strip_prefix'] = [
            "file://",
            "http://www.", "https://www.", "http://", "https://"]

        self.config['plugins'] = [
            'enhance_mapping_id',
            'filter_blacklist',
            'filter_file_not_modified',
            'enhance_extract_text_tika_server',
            'enhance_detect_language_tika_server',
            'enhance_contenttype_group',
            'enhance_pst',
            'enhance_csv',
            'enhance_file_mtime',
            'enhance_path',
            'enhance_extract_hashtags',
            'enhance_warc',
            'enhance_zip',
            'clean_title',
            'enhance_multilingual',
        ]

        self.config['blacklist'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url"]
        self.config['blacklist_prefix'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-prefix"]
        self.config['blacklist_suffix'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-suffix"]
        self.config['blacklist_regex'] = [
            "/etc/opensemanticsearch/blacklist/blacklist-url-regex"]
        self.config['whitelist'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url"]
        self.config['whitelist_prefix'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-prefix"]
        self.config['whitelist_suffix'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-suffix"]
        self.config['whitelist_regex'] = [
            "/etc/opensemanticsearch/blacklist/whitelist-url-regex"]
        self.config['blackest_list_regex'] = [
            '/etc/opensemanticsearch/blacklist/the_blackest_of_lists-url-regex']

    def read_configfiles(self):
        #
        # include configs
        #

        # Windows style filenames
        self.read_configfile('conf\\opensemanticsearch-etl')
        self.read_configfile('conf\\opensemanticsearch-enhancer-rdf')
        self.read_configfile('conf\\opensemanticsearch-connector-files')

        # Linux style filenames
        self.read_configfile('/etc/etl/config')
        self.read_configfile('/etc/opensemanticsearch/etl')
        self.read_configfile('/etc/opensemanticsearch/etl-webadmin')
        self.read_configfile('/etc/opensemanticsearch/etl-custom')
        self.read_configfile('/etc/opensemanticsearch/enhancer-rdf')
        self.read_configfile('/etc/opensemanticsearch/facets')
        self.read_configfile('/etc/opensemanticsearch/connector-files')
        self.read_configfile('/etc/opensemanticsearch/connector-files-custom')

    # clean filename (convert filename given as URI to filesystem)
    def clean_filename(self, filename):

        # if exist delete prefix file://

        if filename.startswith("file://"):
            filename = filename.replace("file://", '', 1)

        return filename

    # index directory or file
    def index(self, filename):

        # clean filename (convert filename given as URI to filesystem)
        filename = self.clean_filename(filename)

        # if singe file start to index it
        if os.path.isfile(filename):

            self.index_file(filename=filename)

            result = True

        # if directory walkthrough
        elif os.path.isdir(filename):

            self.index_dir(rootDir=filename)

            result = True

        # else error message
        else:

            result = False

            sys.stderr.write(
                "No such file or directory: {}\n".format(filename))

        return result

    # walk through all subdirectories and call index_file for each file
    def index_dir(self, rootDir, followlinks=False):

        for dirName, subdirList, fileList in os.walk(rootDir,
                                                     followlinks=followlinks):

            if self.verbose:
                print("Scanning directory: {}".format(dirName))

            for fileName in fileList:
                if self.verbose:
                    print("Scanning file: {}".format(fileName))

                try:

                    fullname = dirName
                    if not fullname.endswith(os.path.sep):
                        fullname += os.path.sep
                    fullname += fileName

                    self.index_file(filename=fullname)

                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except BaseException as e:
                    try:
                        sys.stderr.write(
                            "Exception while processing file {}{}{} : {}\n"
                            .format(dirName, os.path.sep, fileName, e))
                    except BaseException:
                        sys.stderr.write(
                            "Exception while processing a file and exception "
                            "while printing error message (maybe problem with"
                            " encoding of filename on console or converting "
                            "the exception to string?)\n")

    # Index a file
    def index_file(self, filename, additional_plugins=()):

        # clean filename (convert filename given as URI to filesystem)
        filename = self.clean_filename(filename)

        # fresh parameters / chain for each file (so processing one file will
        # not change config/parameters for next, if directory or multiple
        # files, which would happen if given by reference)
        parameters = self.config.copy()
        if additional_plugins:
            parameters['plugins'].extend(additional_plugins)

        if self.verbose:
            parameters['verbose'] = True

        data = {}

        # add this connector name to ETL status
        data['etl_file_b'] = True

        if 'id' not in parameters:
            parameters['id'] = filename

        parameters['filename'] = filename

        parameters, data = self.process(parameters=parameters, data=data)

        return parameters, data


