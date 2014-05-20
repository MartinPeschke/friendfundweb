import logging
import os
import subprocess
import fnmatch
from collections import deque

from friendfund.model.async.ecard_render import GetPoolECardsProc
from friendfund.services import static_service as statics
from friendfund.tasks import config, get_dbm, upload_pimg_folder, IMAGEMAGICKROOT
from friendfund.tasks.celerytasks import app
from friendfund.tasks.celerytasks.photo_renderer import retrieve_tmp_image


log = logging.getLogger()

BACKGROUND_FORMAT = (960,540)
SINGLE_ENTRY = (320,180)
SINGLE_ENTRY_PIC = (150,150)
SINGLE_ENTRY_MESSAGE = (150,150)

CONNECTION_NAME = 'async'

STATIC_SERVICE = statics.StaticService(config['static.servers'],config['static.servers'])

"""
	echo "123xyzHere I use caption to wordwrap and then some with this text for oodles.\nTwo separate lines. and more text and more text. and more text and more text. and more text and more text. and more text and more text. and more text and more text. and more text and more text. and more text and more text" |\
	convert -size 230x150 -fill black -font Helvetica -pointsize 14 -gravity West caption:@- png:- |\
	convert - -background white -gravity West -extent 250x150  - | \
	convert \( db.jpg -resize 100x100^ -gravity Center -extent 120x120 \) - -gravity center +append - |\
	convert - -background white -gravity Center -extent 370x160  mlineexample1_0.jpg
"""


def render_tile(tempfname, user_name, message):
    p1 = subprocess.Popen( ['/bin/echo', message.replace('"', '\"')], stdout=subprocess.PIPE )
    p2 = subprocess.Popen( [os.path.join(IMAGEMAGICKROOT, 'convert'), '-size', '230x150', '-fill', 'black', '-font', 'Helvetica', '-pointsize', '14', '-gravity', 'West', 'caption:@-','png:-'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen( [os.path.join(IMAGEMAGICKROOT, 'convert'), '-', '-background', 'white', '-gravity', 'West', '-extent', '250x150', '-'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen( [os.path.join(IMAGEMAGICKROOT, 'convert'), '(', tempfname, '-resize', '100x100^', '-gravity', 'Center', '-extent', '120x120', ')', '-', '-gravity', 'center', '+append', '-'], stdin=p3.stdout, stdout=subprocess.PIPE)
    p5 = subprocess.Popen( [os.path.join(IMAGEMAGICKROOT, 'convert'), '-', '-background', 'white', '-gravity', 'Center', '-extent', '370x160', tempfname], stdin=p4.stdout, stdout=subprocess.PIPE)
    return tempfname

@app.task
def remote_ecard_render(pool_url):
    dbm = get_dbm(CONNECTION_NAME)
    ecardresult = dbm.get(GetPoolECardsProc, p_url = pool_url)
    for ecard in ecardresult.ecards:
        partial_montages = deque()
        for user in ecard.users:
            picture_url = STATIC_SERVICE.get_user_picture(user.profile_picture_url, "MYPOOLS")
            log.info(picture_url)
            tmpfname = retrieve_tmp_image(picture_url)
            log.info(tmpfname)
            partial_montages.append( render_tile(tmpfname, user.u_name or '', user.message or 'hahahahaha no message') )


        final_collage_name =  statics.tokenize_url(pool_url)
        newurl = final_collage_name
        basepath,fname = os.path.split(final_collage_name)
        newfpath = os.path.join(upload_pimg_folder, basepath)
        newfname = os.extsep.join([('%s_%s' % (fname, 'ECARD')), 'png'])
        final_collage_fullname = os.path.join(newfpath, newfname)

        #montage mlineexample*.jpg -geometry 320x180 -tile 3x3 output.jpg
        montage_command = [os.path.join(IMAGEMAGICKROOT, 'montage')] + [f for f in partial_montages] + ['-geometry','320x160+1+1','-tile', '3x4', final_collage_fullname]
        p = subprocess.Popen( montage_command )
        p.communicate()
        # for f in partial_montages:
        # try:
        # os.unlink(f)
        # log.info("removed %s" % f)
        # except Exception, e:
        # log.error("could not unlink %s" % e)
        for fname in sorted(fnmatch.filter(os.listdir(newfpath), '%s*.png' % ('%s_%s' % (fname, 'ECARD')))):
            log.info(os.path.join(newfpath, fname))
    return 'ack'