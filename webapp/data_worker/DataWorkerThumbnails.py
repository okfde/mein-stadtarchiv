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
import subprocess
from PIL import Image, ImageFile
import shutil
from datetime import datetime
from flask import current_app
from ..models import Document, File
from minio.error import ResponseError, NoSuchKey
from ..extensions import logger, minio

Image.MAX_IMAGE_PIXELS = None


class DataWorkerThumbnails:
    def __init__(self):
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def prepare(self):
        self.statistics = {
            'wrong-mimetype': 0,
            'file-missing': 0,
            'successful': 0
        }

    def run(self, *args):
        self.prepare()
        files = File.objects(thumbnailStatus__exists=False, binary_exists=True).timeout(False).all()
        for file in files:
            self.file_thumbnails(file)

    def file_thumbnails(self, file, force_update=False):
        logger.info('worker.file', 'processing file %s' % file.id)
        document = Document.objects(files=file).first()
        if not document:
            current_app.logger.info('file %s has no document' % file.id)
            return
        if file.thumbnailGenerated and file.modified < file.thumbnailGenerated and not force_update:
            return
        file.modified = datetime.now()
        file.thumbnailGenerated = datetime.now()
        # get file
        try:
            data = minio.connection.get_object(
                current_app.config['MINIO_BUCKET'],
                "files/%s/%s" % (document.id, file.id)
            )
        except NoSuchKey:
            current_app.logger.warn('file not found: %s' % file.id)
            self.statistics['file-missing'] += 1
            file.thumbnailStatus = 'file-missing'
            file.thumbnailsGenerated = datetime.now()
            file.modified = datetime.now()
            file.save()
            return

        file_path = os.path.join(current_app.config['TEMP_THUMBNAIL_DIR'], str(file.id))

        # save file
        with open(file_path, 'wb') as file_data:
            for d in data.stream(32 * 1024):
                file_data.write(d)

        if file.mimeType not in ['application/msword', 'application/pdf', 'image/jpeg', 'image/png', 'image/tiff', 'image/bmp']:
            current_app.logger.warn('wrong mimetype: %s' % file.id)
            self.statistics['wrong-mimetype'] += 1
            file.thumbnailStatus = 'wrong-mimetype'
            file.thumbnailsGenerated = datetime.now()
            file.modified = datetime.now()
            file.save()
            os.unlink(file_path)
            return

        if file.mimeType == 'application/msword':
            file_path_old = file_path
            file_path = file_path + '-old'
            cmd = ('%s --to=PDF -o %s %s' % (current_app.config['ABIWORD_COMMAND'], file_path, file_path_old))
            self.execute(cmd)

        # create folders
        max_folder = os.path.join(current_app.config['TEMP_THUMBNAIL_DIR'], str(file.id) + '-max')
        if not os.path.exists(max_folder):
            os.makedirs(max_folder)
        out_folder = os.path.join(current_app.config['TEMP_THUMBNAIL_DIR'], str(file.id) + '-out')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        for size in current_app.config['THUMBNAIL_SIZES']:
            if not os.path.exists(os.path.join(out_folder, str(size))):
                os.makedirs(os.path.join(out_folder, str(size)))
        file.thumbnail = {}
        pages = 0

        # generate max images
        if file.mimeType in ['application/msword', 'application/pdf']:
            max_path = max_folder + os.sep + '%d.png'
            cmd = '%s -dQUIET -dSAFER -dBATCH -dNOPAUSE -sDisplayHandle=0 -sDEVICE=png16m -r100 -dTextAlphaBits=4 -sOutputFile=%s -f %s' % (
                current_app.config['GHOSTSCRIPT_COMMAND'], max_path, file_path
            )
            self.execute(cmd)
        else:
            max_path = max_folder + os.sep + '1.png'
            im = Image.open(file_path)
            if im.mode in ['YCbCr', 'RGBA']:
                try:
                    im = im.convert('RGB')
                except IOError:
                    current_app.logger.error('FATAL: File %s seems to be corrupt.' % file.id)
                    im.close()
                    return
            im.save(max_path)
            im.close()

        # generate thumbnails based on max images
        for max_file in os.listdir(max_folder):
            pages += 1
            file_path_single = os.path.join(max_folder, max_file)
            num = max_file.split('.')[0]
            im = Image.open(file_path_single)
            im = self.conditional_to_greyscale(im)
            (owidth, oheight) = im.size

            for size in current_app.config['THUMBNAIL_SIZES']:
                (width, height) = self.scale_width_height(size, owidth, oheight)
                # Two-way resizing
                resizedim = im
                if oheight > (height * 2.5):
                    # generate intermediate image with double size
                    resizedim = resizedim.resize((width * 2, height * 2), Image.NEAREST)
                resizedim = resizedim.resize((width, height), Image.ANTIALIAS)
                out_path = os.path.join(out_folder, str(size), str(num) + '.jpg')
                resizedim.save(out_path, subsampling=0, quality=80)
                # optimize image
                cmd = '%s --preserve-perms %s' % (current_app.config['JPEGOPTIM_PATH'], out_path)
                self.execute(cmd)
                # create mongodb object and append it to file
                if str(num) not in file.thumbnails:
                    file.thumbnails[str(num)] = {
                        'page': int(num),
                        'sizes': {}
                    }
                file.thumbnails[str(num)]['sizes'][str(size)] = {
                    'width': width,
                    'height': height,
                    'filesize': os.path.getsize(out_path)
                }
            im.close()
        # save all generated files in minio
        for size in current_app.config['THUMBNAIL_SIZES']:
            for out_file in os.listdir(os.path.join(out_folder, str(size))):
                try:
                    minio.connection.fput_object(
                        current_app.config['MINIO_BUCKET'],
                        "thumbnails/%s/%s/%s/%s" % (str(document.id), str(file.id), str(size), out_file),
                        os.path.join(out_folder, str(size), out_file),
                        'image/jpeg'
                    )
                except ResponseError as err:
                    current_app.logger.error(
                        'Critical error saving file from File %s from Body %s' % (file.id, document.id))
        # save in mongodb
        file.thumbnailStatus = 'successful'
        file.thumbnailsGenerated = datetime.now()
        file.modified = datetime.now()
        file.pages = pages
        file.save()
        # tidy up
        os.unlink(file_path)
        shutil.rmtree(max_folder)
        shutil.rmtree(out_folder)

    def conditional_to_greyscale(self, image):
        """
        Convert the image to greyscale if the image information
        is greyscale only
        """
        bands = image.getbands()
        if len(bands) >= 3:
            # histogram for all bands concatenated
            hist = image.histogram()
            if len(hist) >= 768:
                hist1 = hist[0:256]
                hist2 = hist[256:512]
                hist3 = hist[512:768]
                # print "length of histograms: %d %d %d" % (len(hist1), len(hist2), len(hist3))
                if hist1 == hist2 == hist3:
                    # print "All histograms are the same!"
                    return image.convert('L')
        return image

    def scale_width_height(self, height, original_width, original_height):
        if float(original_height) / float(original_width) > 1:
            factor = float(height) / float(original_height)
            width = int(round(factor * original_width))
        else:
            width = height
            factor = float(width) / float(original_width)
            height = int(round(factor * original_height))
        return (width, height)

    def execute(self, cmd):
        new_env = os.environ.copy()
        new_env['XDG_RUNTIME_DIR'] = '/tmp/'
        output, error = subprocess.Popen(
            cmd.split(' '), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=new_env).communicate()
        if error is not None and error.decode().strip() != '' and 'WARNING **: clutter failed 0, get a life.' not in error.decode():
            current_app.logger.warn("pdf output at command %s; output: %s" % (cmd, error.decode()))
        return output


def regenerate_thumbnails(file_id):
    file = File.get(file_id)
    dwt = DataWorkerThumbnails()
    dwt.prepare()
    dwt.file_thumbnails(file, True)
