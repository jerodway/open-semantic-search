#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib

from etl import ETL
import enhance_mapping_id

class Delete(ETL):
    def __init__(self, verbose=False, quiet=True):

        ETL.__init__(self, verbose=verbose)

        self.quiet = quiet

        self.set_configdefaults()

        self.read_configfiles()

        # read on what DB or search server software our index is
        export = self.config['export']

        # call delete function of the configured exporter
        # module = importlib.import_module(export)
        # objectreference = getattr(module, export)
        # self.connector = objectreference()

    def set_configdefaults(self):
        #
        # Standard config
        #
        # Do not edit config here! Overwrite options in /etc/etl/ or /etc/opensemanticsearch/connector-files
        #

        ETL.set_configdefaults(self)

        self.config['force'] = False

    def read_configfiles(self):
        #
        # include configs
        #

        # Windows style filenames
        self.read_configfile('conf\\opensemanticsearch-etl')
        self.read_configfile('conf\\opensemanticsearch-connector-files')

        # Linux style filenames
        self.read_configfile('/etc/opensemanticsearch/etl')
        self.read_configfile('/etc/opensemanticsearch/connector-files')

    def delete(self, uri):

        if 'mappings' in self.config:
            uri = enhance_mapping_id.mapping(value=uri, mappings=self.config['mappings'])
        
        if self.verbose:
            print("Deleting from index {}".format(uri))

        self.connector.delete(parameters=self.config, docid=uri)

    def empty(self):

        if self.verbose:
            print("Deleting all documents from index")

        self.connector.delete(parameters=self.config, query="*:*")