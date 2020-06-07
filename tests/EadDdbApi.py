# encoding: utf-8

"""
Copyright (c) 2017, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import hashlib
import unittest
import requests
from lxml import etree
from webapp.config import Config


class EadDdbApi(unittest.TestCase):

    def setUp(self):
        self.auth = 'UNITTEST'
        self.asset_xml_filename = 'ead-ddb-test.xml'
        self.asset_image_filenames = []
        self.config = Config()
        self.unittest_path = os.path.join(self.config.PROJECT_ROOT, os.pardir, 'tests')
        self.xml_path = os.path.join(self.unittest_path, 'data', self.asset_xml_filename)
        self.image_path = os.path.join(self.unittest_path, 'data', 'images')
        self.asset_base_url = 'https://mein-stadtarchiv.de/static/unittest/'
        #self.download_data()

    def download_data(self):
        r = requests.get('%s/%s' % (self.asset_base_url, self.asset_xml_filename))
        with open(self.xml_path, 'wb') as xml_file:
            xml_file.write(r.content)
        for image in self.asset_image_filenames:
            r = requests.get('%s/images/%s' % (self.asset_base_url, image))
            with open(os.path.join(self.image_path, image), 'wb') as image_file:
                image_file.write(r.content)

    def test_api(self):
        valid_formats = {
            'tif': ['tif', 'image/tiff'],
            'tiff': ['tif', 'image/tiff'],
            'jpg': ['jpg', 'image/jpeg'],
            'jpeg': ['jpg', 'image/jpeg'],
            'png': ['png', 'image/png'],
            'pdf': ['pdf', 'application/pdf'],
            'bmp': ['bmp', 'image/bmp']
        }

        ### xml handling ###
        with open(self.xml_path, 'r') as xml_file:
            xml_data = bytes(xml_file.read().replace("\n", ""), 'utf8')

        headers = {'Content-Type': 'text/xml'}
        document_params = {'auth': self.auth, 'force-reupload': '1'}
        document_url = '%s/api/ead-ddb/push-data' % self.config.PROJECT_URL
        print('upload xml file')
        r = requests.post(document_url, headers=headers, data=xml_data, params=document_params)
        assert r.status_code == 200

        result_xml = etree.fromstring(r.text)
        result = result_xml.xpath('.//ead-ddb-push:Description', namespaces=result_xml.nsmap)
        assert len(result)

        missing_files = []
        missing_files_xml = result_xml.xpath('.//ead-ddb-push:MissingFile', namespaces=result_xml.nsmap)
        for missing_file_xml in missing_files_xml:
            missing_files.append(missing_file_xml.text)

        images = {}
        for dir, dirs, files in os.walk(self.image_path):
            for file in files:
                if file in images:
                    images[file].append(os.path.abspath(dir))
                else:
                    images[file] = [os.path.abspath(dir)]

        xml_data = etree.parse(self.xml_path).getroot()
        file_params = {'auth': self.auth}
        file_url = '%s/api/ead-ddb/push-file' % self.config.PROJECT_URL

        namespaces = xml_data.nsmap
        namespaces['ns'] = namespaces[None]
        del namespaces[None]

        file_already_uploaded = 0
        file_missing = 0
        file_uploaded = 0
        file_upload_error = 0
        double_image_count = 0

        documents_xml = xml_data.xpath('.//ns:archdesc[@level="collection"]/ns:dsc//ns:c[@level="file"]', namespaces=namespaces)
        for document_xml in documents_xml:
            document_uid = document_xml.get('id')
            files_xml = document_xml.xpath('.//ns:daogrp/ns:daodesc/ns:list/ns:item', namespaces=namespaces)
            for file_xml in files_xml:
                xml_file_name = file_xml.xpath('.//ns:name', namespaces=namespaces)
                assert len(xml_file_name)

                xml_file_name = xml_file_name[0].text
                assert xml_file_name

                if document_uid + '-' + xml_file_name not in missing_files:
                    file_already_uploaded += 1
                    continue

                document_file_name = None
                document_file_ending = None
                document_file_path = None

                # get best image
                double_image = False
                for image in images.keys():
                    ending = image.split('.')[-1]
                    if xml_file_name == image[0:-1 * (len(ending) + 1)] and ending.lower() in valid_formats.keys():
                        if len(images[image]) > 1:
                            double_image = True
                        if not document_file_name and not document_file_ending:
                            document_file_name = image
                            document_file_path = images[image][0]
                            document_file_ending = valid_formats[ending.lower()][0]
                        elif valid_formats[ending.lower()][0] in ['tif', 'tiff']:
                            document_file_name = image
                            document_file_path = images[image][0]
                            document_file_ending = valid_formats[ending.lower()][0]

                if double_image:
                    double_image_count += 1
                    continue
                if not document_file_name or not document_file_name:
                    file_missing += 1
                    continue

                sha1 = hashlib.sha1()
                document_file_path_full = os.path.join(document_file_path, document_file_name)
                with open(document_file_path_full, 'rb') as f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        sha1.update(data)

                upload_data = {
                    'document_uid': document_uid,
                    'name': xml_file_name,
                    'fileName': document_file_name,
                    'mimeType': valid_formats[document_file_ending][1],
                    'sha1Checksum': sha1.hexdigest(),
                    'size': os.path.getsize(document_file_path_full)
                }
                print('upload image %s' % document_file_name)
                with open(document_file_path_full, 'rb') as image_file:
                    upload_files = {
                        'file': image_file
                    }
                    r = requests.post(file_url, data=upload_data, files=upload_files, params=file_params)
                result_xml = etree.fromstring(r.text)
                result = result_xml.xpath('.//ead-ddb-push:Description', namespaces=result_xml.nsmap)
                assert len(result)
                if result[0].text == 'file saved':
                    file_uploaded += 1
                else:
                    file_upload_error += 1
