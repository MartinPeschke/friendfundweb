INPROCESS_TOKEN = 1

def set_pages_to_cache(logger, cache_pool, proto_key, dataprovider, expiretime=4200):
    with cache_pool.reserve() as mc:
        logger.info('CACHE MISS for followers')
        enum = 0
        is_final = False

        try:
            while not is_final:
                mc.set(str('%s<%s>'%(proto_key, enum)), INPROCESS_TOKEN, 30)
                dataset, is_final = dataprovider.next()
                obj = { 'payload':dataset, 'is_final' : is_final }
                mc.set(str('%s<%s>'%(proto_key, enum)), obj, expiretime)
                logger.info('MEMCACHED: just set key: is_final:%s: %s<%s>' , is_final, proto_key, enum)
                enum += 1
        except StopIteration:
            logger.error("ITERATION_TOO_FAR")
            keys = ['<%s>'%i for i in range(0, enum+1)]
            mc.delete_multi(keys, key_prefix=str(proto_key))
            raise
        except:
            keys = ['<%s>'%i for i in range(0, enum+1)]
            mc.delete_multi(keys, key_prefix=str(proto_key))
            raise
