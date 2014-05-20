from __future__ import with_statement
import logging
from logging.config import fileConfig
import time
import sys
import getopt

from friendfund.model.globals import GetMerchantConfigProc
from friendfund.model.pool import FeaturedPool
from friendfund.tasks import get_dbm, get_cm, get_config, Usage


CONNECTION_NAME = 'pool'
FEATURED_POOLS_CACHEKEY = "FF_FEATURED_POOLS_weafhwvgfhfr"
MERCHANTS_CACHEKEY = "FF_MERCHANTS_weafhwvgfhfr"
MERCHANTS_POOLS_CACHEKEY = "FF_MERCHANTS_FEATURED_POOLS"
HOMEPAGE_STATS_CACHEKEY = "FF_HOMEPAGE_STATS_weafhwvgfhfr"

def get_mfp_key(key):
    return "%s|%s" % (MERCHANTS_POOLS_CACHEKEY, key)

def get_key_from_mfp_key(key):
    return key.split("|")[1]


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h", ["help", "file"])
        opts = dict(opts)
        if '-f' not in opts:
            raise Usage("Missing Option -f")
    except getopt.error, msg:
        raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    configname = opts['-f']

    fileConfig(configname)
    log = logging.getLogger(__name__)

    config = get_config(configname)
    dbm = get_dbm(CONNECTION_NAME)
    cm = get_cm(CONNECTION_NAME)
    debug = config['debug'].lower() == 'true'
    log.info( 'DEBUG: %s for %s (%s)', debug, CONNECTION_NAME, config['memcached.cache.url'])
    cache_set_values = {}
    while 1:
        merchant_config = dbm.get(GetMerchantConfigProc)
        featured_pools = []
        ###get homepage featured pools
        for p in merchant_config.featured_pools:
            featured_pools.append(dbm.get(FeaturedPool, p_url = p.p_url))
        ###get merchant home iframe featured pools
        cache_set_values = {FEATURED_POOLS_CACHEKEY: featured_pools,
                            MERCHANTS_CACHEKEY:merchant_config.merchants,
                            HOMEPAGE_STATS_CACHEKEY:merchant_config.stats}

        mfpools = {}
        for key, merchant in merchant_config.key_map.iteritems():
            if merchant.featured_pools:
                mfp = []
                for p in merchant.featured_pools:
                    mfp.append(dbm.get(FeaturedPool, p_url = p.p_url))
                cache_key = get_mfp_key(key)
                mfpools[cache_key] = mfp
        cache_set_values.update(mfpools)

        with cm.reserve() as mc:
            mc.set_multi(cache_set_values, 864000)

        log.info("CACHE_UPDATED (<%s>) (%s)", ">, <".join(map(lambda x: x.p_url, featured_pools)),
                 ", ".join(["%s:%s"%(get_key_from_mfp_key(key), len(items)) for key, items in mfpools.iteritems()]))
        if len(featured_pools)<4:
            log.error("INSUFFICIENT FEATURED POOLS FOR HOMEPAGE")
        time.sleep(60)

if __name__ == "__main__":
    sys.exit(main())