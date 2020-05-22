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

from lxml import etree


def generate_xml_answer(status, description=None, missing_files=None):
    nsmap = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope',
        'ead-ddb-push': 'https://ead-ddb.de/model/1.0'
    }
    result = etree.Element(
        "{%s}Envelope" % nsmap['soapenv'],
        nsmap=nsmap
    )
    result.append(
        etree.Element(
            "{%s}Header" % nsmap['soapenv'],
            nsmap=nsmap
        )
    )
    result.append(
        etree.Element(
            "{%s}Body" % nsmap['soapenv'],
            nsmap=nsmap
        )
    )
    result[1].append(
        etree.Element(
            "{%s}Status" % nsmap['ead-ddb-push'],
            nsmap=nsmap
        )
    )
    result[1][0].text = status
    if description:
        result[1].append(
            etree.Element(
                "{%s}Description" % nsmap['ead-ddb-push'],
                nsmap=nsmap
            )
        )
        result[1][1].text = description
    if missing_files:
        missing_files_xml = etree.Element(
            "{%s}MissingFiles" % nsmap['ead-ddb-push'],
            nsmap=nsmap
        )
        for missing_file in missing_files:
            missing_file_xml = etree.Element(
                "{%s}MissingFile" % nsmap['ead-ddb-push'],
                nsmap=nsmap
            )
            missing_file_xml.text = missing_file
            missing_files_xml.append(missing_file_xml)
        result[1].append(missing_files_xml)
    return result

