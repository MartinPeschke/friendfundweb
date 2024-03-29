import types
import collections
from xml.sax.saxutils import quoteattr, escape
from datetime import datetime, date
import logging
from collections import OrderedDict

from friendfund.lib import tools as t


log = logging.getLogger(__name__)

#############################################################################################
##################### Database Types and Objects ############################################
#############################################################################################

class TypeNotSupportedException(Exception):
    pass


class RequiredAttributeMissing(Exception):
    pass


class DBMapping(object):
    pass


class GenericAttrib(DBMapping):
    def __init__(self, cls, pykey, dbkey, persistable = True, required = False, enumeration = None, default = None):
        self.dbkey = dbkey
        self.pykey = pykey
        self.cls = cls
        self.persistable = persistable
        self.required = required
        self.enumeration = enumeration
        self.default = default

    def toDB(self, val):
        if val is None:
            if self.default is None:
                return ''
            else:
                val = self.default

        if self.enumeration and (not val in self.enumeration):
            raise ValueError("UNEXPECTED VALUE in ENUM: %s (not in %s)" % (val, self.cls))
        elif self.cls == bool:
            result = (self.dbkey, '"%s"' % int(bool(val)))
        elif issubclass(self.cls, date):
            if isinstance(val, date):
                result = (self.dbkey, quoteattr(val.strftime('%Y-%m-%d')))
            else:
                result = (self.dbkey, quoteattr(unicode(val)))
        else:
            result = (self.dbkey, quoteattr(unicode(val)))
        return '%s=%s' % result

    def fromDB(self, val):
        if val is None:
            if self.required:
                raise RequiredAttributeMissing("MISSING: %s(%s)" % ( self.pykey, self.dbkey ))
            elif self.default is None:
                return None
            else:
                return self.default

        if self.cls == bool:
            return val and bool(int(val))
        elif isinstance(self.cls, set):
            if not val in self.cls:
                raise ValueError("UNEXPECTED VALUE in ENUM: %s (not in %s)" % (val, self.cls))
            else:
                return self.cls(val)
        elif issubclass(self.cls, date):
            try:
                return datetime.strptime(val.rsplit('.',1)[0], '%Y-%m-%dT%H:%M:%S')
            except ValueError, e:
                return datetime.strptime(val.split('T')[0], '%Y-%m-%d')
        else:
            if self.enumeration and (not self.cls(val) in self.enumeration):
                raise ValueError("UNEXPECTED VALUE in ENUM: %s (not in %s)" % (val, self.enumeration))
            return self.cls(val)

    def __repr__(self):
        return '<%s: %s,%s>' % (self.__class__.__name__, self.pykey,self.dbkey)

class GenericElement(DBMapping):
    def __init__(self, cls, pykey, dbkey, persistable = True, required = False, default = None):
        self.dbkey = dbkey
        self.pykey = pykey
        self.cls = cls
        self.persistable = persistable
        self.required = required
        self.default = default

    def toDB(self, val):
        if val is None:
            if self.default is None:
                return ''
            else:
                val = self.default

        if self.cls == bool:
            result = (self.dbkey, int(bool(val)), self.dbkey)
        elif issubclass(self.cls, date):
            if isinstance(val, datetime):
                result = (self.dbkey, escape(val.strftime('%Y-%m-%d')), self.dbkey)
            else:
                result = (self.dbkey, escape(unicode(val)), self.dbkey)
        else:
            result = (self.dbkey, escape(unicode(val)), self.dbkey)
        return '<%s>%s</%s>' % result

    def fromDB(self, val):
        if val is None or val.text is None:
            if self.required:
                raise RequiredAttributeMissing("MISSING: %s(%s)" % ( self.pykey, self.dbkey ))
            elif self.default is None:
                return None
            else:
                return self.default

        if self.cls == bool:
            return val and bool(int(val.text))
        elif issubclass(self.cls, date):
            return datetime.strptime(val.text, '%Y-%m-%d')
        else:
            return self.cls(val.text)
    def __repr__(self):
        return '<%s: %s,%s>' % (self.__class__.__name__, self.pykey,self.dbkey)


class DBCDATA(DBMapping):
    def __init__(self, pykey, dbkey, persistable = True, required = False):
        self.dbkey = dbkey
        self.pykey = pykey
        self.cls = unicode
        self.persistable = persistable
        self.required = required

    @classmethod
    def _get_template(cls, **kwargs):
        # TODO: what is this? how is this possibly working?
        _get_root = _set_root

    def toDB(self, val):
        return '<![CDATA[%s]]>' % val

    @classmethod
    def fromDB(cls, xml):
        return None


class DBMappedObject(DBMapping):
    _cachable = True
    _expiretime = 1
    _unique_keys = []
    _no_params = False
    _get_root = _set_root = None

    def __init__(self, **kwargs):
        for elem in self._keys:
            if getattr(elem, "is_list", False):
                setattr(self, elem.pykey, kwargs.get(elem.pykey, []))
            elif getattr(elem, "is_dict", False):
                setattr(self, elem.pykey, kwargs.get(elem.pykey, {}))
            else:
                setattr(self, elem.pykey, kwargs.get(elem.pykey, None))

    def __unicode__(self):
        return '<%r: %r>' % (self.__class__.__name__, ','.join(['%s:%s'%(k.pykey,getattr(self, k.pykey)) for k in self._keys[:3]]))

    def __repr__(self):
        return '<%r: %r>' % (self.__class__.__name__, ','.join(['%s:%s'%(k,getattr(self, k)) for k in self._unique_keys[:3]]))

    def to_map(self, flat = True):
        return dict([(k.pykey,getattr(self, k.pykey)) for k in self._keys if not flat or flat and isinstance(k, (GenericAttrib, GenericElement))])

    def from_map(self, map, override = False):
        keyMap = dict([(k.pykey,k) for k in self._keys])
        for k,v in map.iteritems():
            if k in keyMap:
                if issubclass(keyMap[k].cls, DBMappedObject):
                    obj = getattr(self, k) or keyMap[k].cls()
                    obj = obj.from_map(v, override)
                    setattr(self, k, obj)
                else:
                    if not override:
                        v = getattr(self, k) or v
                    setattr(self, k, v)
        return self

    def to_minimal_repr(self):
        return t.encode_minimal_repr(self.to_map())

    @classmethod
    def from_minimal_repr(cls, value):
        return cls(**t.decode_minimal_repr(value))

    def update(self, obj):
        for elem in self._keys:
            if getattr(obj, elem.pykey, None):
                setattr(self, elem.pykey, getattr(obj, elem.pykey))


#############################################################################################
##################### Manager and Mapper Objects#############################################
#############################################################################################

class DBMapper(object):
    def __init__(self, cls, pykey, dbkey, persistable = True, is_list = False, is_dict = False, dict_key = None):
        self.dbkey = dbkey
        self.pykey = pykey
        self.cls = cls
        self.persistable = persistable
        self.is_list = is_list
        self.is_dict = is_dict
        self.dict_key = dict_key

        if self.is_dict and not self.dict_key:
            raise TypeError("DBMapper missing dict_key-extractor function parameter")

    @classmethod
    def toDB(cls, obj):
        attribs = collections.deque()
        children = collections.deque()
        if not hasattr(obj, "_keys"):
            xml = None
        else:
            for k in obj._keys:
                value = getattr(obj, k.pykey, None)
                if k.persistable:
                    if isinstance(k, GenericAttrib):
                        attribs.append(k.toDB(value))
                    elif (isinstance(k, GenericElement) or isinstance(k, DBCDATA)):
                        children.append(k.toDB(value))
                    elif isinstance(value, (types.ListType, collections.deque, types.GeneratorType)):
                        children.extend(map(lambda x: k.toDB(x), filter(lambda x: isinstance(x,DBMappedObject), value)))
                    elif isinstance(value, (types.DictType, OrderedDict)):
                        children.extend(map(lambda x: k.toDB(value[x]), filter(lambda x: isinstance(value[x],DBMappedObject), value)))
                    elif isinstance(k, DBMapper):
                        children.append(k.toDB(value))
                    else:
                        raise TypeNotSupportedException("Type %s not supported" % type(k))

            attribs = filter(bool, attribs)
            children = filter(bool, children)
            if len(children):
                xml = "<%s %s>%s</%s>" % (obj._set_root \
                                              ,' '.join(filter(bool, attribs)) \
                                              ,''.join(filter(None, children)) \
                                              ,obj._set_root)
            elif len(attribs):
                xml = "<%s %s />" % (obj._set_root,   ' '.join(attribs))
            else:
                xml = None
        return xml

    @classmethod
    def _get_template(thiscls, cls, **kwargs):
        attribs = []
        for k in cls._keys:
            if k.pykey in kwargs:
                value = kwargs.get(k.pykey, None)
                if value is not None:
                    attribs.append(k.toDB(value))
        return "<%s %s />" % (cls._set_root,' '.join(attribs))

    @classmethod
    def fromDB(thiscls, cls, xml, statics_service):
        if xml is None:
            return None
        if not( cls._get_root is None or xml.tag == cls._get_root ):
            raise Exception('Unexpected tag, found: %s, expected: %s' %(xml.tag, cls._get_root))
        vals = {}
        for k in cls._keys:
            if k.dbkey:
                if isinstance(k, DBMapper):
                    if k.is_list:
                        val = xml.findall(k.dbkey)
                        vals[k.pykey] = [k.fromDB(k.cls, v, statics_service) for v in val]
                    elif k.is_dict:
                        tmpdict = {}
                        val = xml.findall(k.dbkey)
                        for v in val:
                            obj = k.fromDB(k.cls, v, statics_service)
                            tmpdict[k.dict_key(obj)] = obj
                        vals[k.pykey] = tmpdict
                    else:
                        val = xml.find(k.dbkey)
                        vals[k.pykey] = k.fromDB(k.cls, val, statics_service)
                elif isinstance(k, GenericElement):
                    val = xml.find(k.dbkey)
                    vals[k.pykey] = k.fromDB(val)
                elif isinstance(k, DBMapping):
                    val = xml.get(k.dbkey)
                    vals[k.pykey] = k.fromDB(val)
                else:
                    raise TypeNotSupportedException("Type %s not supported" % type(k))
        obj = cls(**vals)
        obj._statics = statics_service
        if hasattr(obj, 'fromDB'): obj.fromDB(xml)
        return obj
