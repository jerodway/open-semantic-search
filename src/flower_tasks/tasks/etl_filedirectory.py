#!/usr/bin/python3
# -*- coding: utf-8 -*-

from etl_file import Connector_File

#
# Parallel processing of files by adding each file to celery tasks
#


class Connector_Filedirectory(Connector_File):

    def __init__(self, verbose=False, quiet=False):

        Connector_File.__init__(self, verbose=verbose)

        self.quiet = quiet

        # apply filters before adding to queue, so filtered or yet indexed files not added to queue
        # adding to queue by plugin export_queue_files

        # exporter to index filenames before text extraction and other later tasks
        # will run before adding tasks to queue by export_queue_files
        # so reseted plugin status will be in index before started ETL tasks apply not modified filter
        export_to_index = self.config['export']

        self.config['plugins'] = [
            'enhance_mapping_id',
            'filter_blacklist',
            'filter_file_not_modified',
            'enhance_file_mtime',
            'enhance_path',
            'enhance_entity_linking',
            'enhance_multilingual',
            export_to_index,
            'export_queue_files',
        ]


