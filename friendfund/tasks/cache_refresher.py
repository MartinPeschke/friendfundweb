from __future__ import with_statement
import logging, time, sys, getopt, pylibmc
from friendfund.model.globals import GetMerchantConfigProc
from friendfund.model.pool import FeaturedPool
from friendfund.tasks import get_dbm, get_cm, get_config, Usage, data_root, STATICS_SERVICE

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

CONNECTION_NAME = 'pool'
FEATURED_POOLS_CACHEKEY = "FF_FEATURED_POOLS_weafhwvgfhfr"
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
	config = get_config(configname)
	dbm = get_dbm(CONNECTION_NAME)
	cm = get_cm(CONNECTION_NAME)
	debug = config['debug'].lower() == 'true'
	log.info( 'DEBUG: %s for %s (%s)', debug, CONNECTION_NAME, config['memcached.cache.url'])
	while 1:
		merchant_config = dbm.get(GetMerchantConfigProc)
		featured_pools = []
		for p in merchant_config.featured_pools:
			 featured_pools.append(dbm.get(FeaturedPool, p_url = p.p_url))
		with cm.reserve() as mc:
			mc.set(FEATURED_POOLS_CACHEKEY, featured_pools, 864000)
		log.info("CACHE_UPDATED (<%s>)", ">, <".join(map(lambda x: x.p_url, featured_pools)))
		if len(featured_pools)<4:
			log.error("INSUFFICIENT FEATURED POOLS FOR HOMEPAGE")
		time.sleep(60)

if __name__ == "__main__":
    sys.exit(main())