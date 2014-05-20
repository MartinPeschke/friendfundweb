"""
	create_merchant -f development.ini -n "Perfect Gift" -w www.perfectgift.ie -s false --countries=DE,ES,UK
"""

from friendfund.model import common
from friendfund.model.globals import CreateMerchantProc, MerchantCountry
from friendfund.tasks import get_db_pool, get_config, Usage

log = logging.getLogger(__name__)

CONNECTION_NAME = 'ssp'
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h:n:w:s:", ["help", "file", "countries="])
        print opts
        opts = dict(opts)
        opts["-s"] = opts['-s'] == 'true'
        if '-f' not in opts:
            raise Usage("Missing Option -f")
        if opts["-s"] and not opts.get("--countries"):
            raise Usage("Missing Option --countries when specifying -s")
    except getopt.error, msg:
        raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    configname = opts['-f']
    config = get_config(configname)
    dbm = common.DBManager(get_db_pool(config, CONNECTION_NAME), None, log, None)
    debug = config['debug'].lower() == 'true'
    log.info( 'DEBUG: %s for %s', debug, CONNECTION_NAME)

    create_merchant = CreateMerchantProc(name = opts['-n'], home_page = opts['-w'], require_address = opts["-s"])
    if opts["-s"]:
        create_merchant.shippping_countries = [MerchantCountry(iso2=k) for k in opts["--countries"].replace(" ", "").upper().split(",")]
    dbm.set(create_merchant)

if __name__ == "__main__":
    sys.exit(main())