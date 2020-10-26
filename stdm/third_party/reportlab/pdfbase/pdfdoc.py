#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/pdfbase/pdfdoc.py
__version__=''' $Id$ '''
__doc__="""
The module pdfdoc.py handles the 'outer structure' of PDF documents, ensuring that
all objects are properly cross-referenced and indexed to the nearest byte.  The
'inner structure' - the page descriptions - are presumed to be generated before
each page is saved.
pdfgen.py calls this and provides a 'canvas' object to handle page marking operators.
piddlePDF calls pdfgen and offers a high-level interface.

The classes within this generally mirror structures in the PDF file
and are not part of any public interface.  Instead, canvas and font
classes are made available elsewhere for users to manipulate.
"""
import string, types, binascii, codecs
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.pdfutils import LINEEND # this constant needed in both
from reportlab import rl_config
from reportlab.lib.utils import import_zlib, open_for_read, fp_str, _digester
from reportlab.pdfbase import pdfmetrics
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from sys import platform
try:
    from sys import version_info
except: # pre-2.0
    # may be inaccurate but will at least
    #work in anything which seeks to format
    # version_info into a string
    version_info = (1,5,2,'unknown',0)

if platform[:4] == 'java' and version_info[:2] == (2, 1):
    # workaround for list()-bug in Jython 2.1 (should be fixed in 2.2)
    def list(sequence):
        def f(x):
            return x
        return map(f, sequence)

def utf8str(x):
    if isinstance(x,unicode):
        return x.encode('utf8')
    else:
        return str(x)

class PDFError(Exception):
    pass

# set this flag to get more vertical whitespace (and larger files)
LongFormat = 1
##if LongFormat: (doesn't work)
##    pass
##else:
##    LINEEND = "\n" # no wasteful carriage returns!

# __InternalName__ is a special attribute that can only be set by the Document arbitrator
__InternalName__ = "__InternalName__"

# __RefOnly__ marks reference only elements that must be formatted on top level
__RefOnly__ = "__RefOnly__"

# __Comment__ provides a (one line) comment to inline with an object ref, if present
#   if it is more than one line then percentize it...
__Comment__ = "__Comment__"

# If DoComments is set then add helpful (space wasting) comment lines to PDF files
DoComments = 1
if not LongFormat:
    DoComments = 0

# name for standard font dictionary
BasicFonts = "BasicFonts"

# name for the pages object
Pages = "Pages"

### generic utilities

# for % substitutions
LINEENDDICT = {"LINEEND": LINEEND, "PERCENT": "%"}
PDF_VERSION_DEFAULT = (1, 3)
PDF_SUPPORT_VERSION = dict(     #map keyword to min version that supports it
    transparency = (1, 4),
    )

from types import InstanceType
def format(element, document, toplevel=0, InstanceType=InstanceType):
    """Indirection step for formatting.
       Ensures that document parameters alter behaviour
       of formatting for all elements.
    """
    if hasattr(element,'__PDFObject__'):
        if not toplevel and hasattr(element, __RefOnly__):
            # the object cannot be a component at non top level.
            # make a reference to it and return it's format
            return document.Reference(element).format(document)
        else:
            f = element.format(document)
            if not rl_config.invariant and DoComments and hasattr(element, __Comment__):
                f = "%s%s%s%s" % ("% ", element.__Comment__, LINEEND, f)
            return f
    elif type(element) in (float, int):
        #use a controlled number formatting routine
        #instead of str, so Jython/Python etc do not differ
        return fp_str(element)
    else:
        return str(element)

def xObjectName(externalname):
    return "FormXob.%s" % externalname

# backwards compatibility
formName = xObjectName

# no encryption
class NoEncryption:
    def encode(self, t):
        "encode a string, stream, text"
        return t
    def prepare(self, document):
        # get ready to do encryption
        pass
    def register(self, objnum, version):
        # enter a new direct object
        pass
    def info(self):
        # the representation of self in file if any (should be None or PDFDict)
        return None

class DummyDoc:
    "used to bypass encryption when required"
    __PDFObject__ = True
    encrypt = NoEncryption()

### the global document structure manager
class PDFDocument:
    __PDFObject__ = True
    # set this to define filters
    defaultStreamFilters = None
    encrypt = NoEncryption() # default no encryption
    def __init__(self,
                 dummyoutline=0,
                 compression=rl_config.pageCompression,
                 invariant=rl_config.invariant,
                 filename=None,
                 pdfVersion=PDF_VERSION_DEFAULT,
                 ):
        self._ID = None
        self.objectcounter = 0
        self.shadingCounter = 0
        self.inObject = None
        self.pageCounter = 1

        # allow None value to be passed in to mean 'give system defaults'
        if invariant is None:
            self.invariant = rl_config.invariant
        else:
            self.invariant = invariant
        self.setCompression(compression)
        self._pdfVersion = pdfVersion
        # signature for creating PDF ID
        sig = self.signature = md5()
        sig.update("a reportlab document")
        if not self.invariant:
            cat = _getTimeStamp()
        else:
            cat = 946684800.0
        sig.update(repr(cat)) # initialize with timestamp digest
        # mapping of internal identifier ("Page001") to PDF objectnumber and generation number (34, 0)
        self.idToObjectNumberAndVersion = {}
        # mapping of internal identifier ("Page001") to PDF object (PDFPage instance)
        self.idToObject = {}
        # internal id to file location
        self.idToOffset = {}
        # number to id
        self.numberToId = {}
        cat = self.Catalog = self._catalog = PDFCatalog()
        pages = self.Pages = PDFPages()
        cat.Pages = pages
        if dummyoutline:
            outlines = PDFOutlines0()
        else:
            outlines = PDFOutlines()
        self.Outlines = self.outline = outlines
        cat.Outlines = outlines
        self.info = PDFInfo()
        self.info.invariant = self.invariant
        #self.Reference(self.Catalog)
        #self.Reference(self.Info)
        self.fontMapping = {}
        #make an empty font dictionary
        DD = PDFDictionary({})
        DD.__Comment__ = "The standard fonts dictionary"
        self.Reference(DD, BasicFonts)
        self.delayedFonts = []

    def setCompression(self, onoff):
        # XXX: maybe this should also set self.defaultStreamFilters?
        self.compression = onoff

    def ensureMinPdfVersion(self, *keys):
        "Ensure that the pdf version is greater than or equal to that specified by the keys"
        for k in keys:
            self._pdfVersion = max(self._pdfVersion, PDF_SUPPORT_VERSION[k])

    def updateSignature(self, thing):
        "add information to the signature"
        if self._ID: return # but not if its used already!
        self.signature.update(utf8str(thing))

    def ID(self):
        "A unique fingerprint for the file (unless in invariant mode)"
        if self._ID:
            return self._ID
        digest = self.signature.digest()
        doc = DummyDoc()
        ID = PDFString(digest,enc='raw')
        IDs = ID.format(doc)
        self._ID = "%s %% ReportLab generated PDF document -- digest (http://www.reportlab.com) %s [%s %s] %s" % (
                LINEEND, LINEEND, IDs, IDs, LINEEND)
        return self._ID

    def SaveToFile(self, filename, canvas):
        if hasattr(getattr(filename, "write",None),'__call__'):
            myfile = 0
            f = filename
            filename = utf8str(getattr(filename,'name',''))
        else :
            myfile = 1
            filename = utf8str(filename)
            f = open(filename, "wb")
        f.write(self.GetPDFData(canvas))
        if myfile:
            f.close()
            import os
            if os.name=='mac':
                from reportlab.lib.utils import markfilename
                markfilename(filename) # do platform specific file junk
        if getattr(canvas,'_verbosity',None): print 'saved', filename

    def GetPDFData(self, canvas):
        # realize delayed fonts
        for fnt in self.delayedFonts:
            fnt.addObjects(self)
        # add info stuff to signature
        self.info.invariant = self.invariant
        self.info.digest(self.signature)
        ### later: maybe add more info to sig?
        # prepare outline
        self.Reference(self.Catalog)
        self.Reference(self.info)
        outline = self.outline
        outline.prepare(self, canvas)
        return self.format()

    def inPage(self):
        """specify the current object as a page (enables reference binding and other page features)"""
        if self.inObject is not None:
            if self.inObject=="page": return
            raise ValueError, "can't go in page already in object %s" % self.inObject
        self.inObject = "page"

    def inForm(self):
        """specify that we are in a form xobject (disable page features, etc)"""
        # don't need this check anymore since going in a form pushes old context at canvas level.
        #if self.inObject not in ["form", None]:
        #    raise ValueError, "can't go in form already in object %s" % self.inObject
        self.inObject = "form"
        # don't need to do anything else, I think...

    def getInternalFontName(self, psfontname):
        fm = self.fontMapping
        if psfontname in fm:
            return fm[psfontname]
        else:
            try:
                # does pdfmetrics know about it? if so, add
                fontObj = pdfmetrics.getFont(psfontname)
                if fontObj._dynamicFont:
                    raise PDFError("getInternalFontName(%s) called for a dynamic font" % repr(psfontname))
                fontObj.addObjects(self)
                #self.addFont(fontObj)
                return fm[psfontname]
            except KeyError:
                raise PDFError("Font %s not known!" % repr(psfontname))

    def thisPageName(self):
        return "Page"+repr(self.pageCounter)

    def thisPageRef(self):
        return PDFObjectReference(self.thisPageName())

    def addPage(self, page):
        name = self.thisPageName()
        self.Reference(page, name)
        self.Pages.addPage(page)
        self.pageCounter += 1
        self.inObject = None

    def addForm(self, name, form):
        """add a Form XObject."""
        # XXX should check that name is a legal PDF name
        if self.inObject != "form":
            self.inForm()
        self.Reference(form, xObjectName(name))
        self.inObject = None

    def annotationName(self, externalname):
        return "Annot.%s"%externalname

    def addAnnotation(self, name, annotation):
        self.Reference(annotation, self.annotationName(name))

    def refAnnotation(self, name):
        internalname = self.annotationName(name)
        return PDFObjectReference(internalname)

    def addShading(self, shading):
         name = "Sh%d" % self.shadingCounter
         self.Reference(shading, name)
         self.shadingCounter += 1
         return name

    def addColor(self,cmyk):
        sname = cmyk.spotName
        if not sname:
            if cmyk.cyan==0 and cmyk.magenta==0 and cmyk.yellow==0:
                sname = 'BLACK'
            elif cmyk.black==0 and cmyk.magenta==0 and cmyk.yellow==0:
                sname = 'CYAN'
            elif cmyk.cyan==0 and cmyk.black==0 and cmyk.yellow==0:
                sname = 'MAGENTA'
            elif cmyk.cyan==0 and cmyk.magenta==0 and cmyk.black==0:
                sname = 'YELLOW'
            if not sname:
                raise ValueError("CMYK colour %r used without a spotName" % cmyk)
            else:
                cmyk = cmyk.clone(spotName = sname)
        name = PDFName(sname)[1:]
        if name not in self.idToObject:
            sep = PDFSeparationCMYKColor(cmyk).value()  #PDFArray([/Separation /name /DeviceCMYK tint_tf])
            self.Reference(sep,name)
        return name,sname

    def setTitle(self, title):
        "embeds in PDF file"
        if title is None:
            self.info.title = '(anonymous)'
        else:
            self.info.title = title

    def setAuthor(self, author):
        "embedded in PDF file"
        #allow resetting to clear it
        if author is None:
            self.info.author = '(anonymous)'
        else:
            self.info.author = author

    def setSubject(self, subject):
        "embeds in PDF file"

        #allow resetting to clear it
        if subject is None:
            self.info.subject = '(unspecified)'
        else:
            self.info.subject = subject

    def setCreator(self, creator):
        "embeds in PDF file"

        #allow resetting to clear it
        if creator is None:
            self.info.creator = '(unspecified)'
        else:
            self.info.creator = creator

    def setKeywords(self, keywords):
        "embeds a string containing keywords in PDF file"

        #allow resetting to clear it but ensure it's a string
        if keywords is None:
            self.info.keywords = ''
        else:
            self.info.keywords = keywords

    def setDateFormatter(self, dateFormatter):
        self.info._dateFormatter = dateFormatter

    def getAvailableFonts(self):
        fontnames = self.fontMapping.keys()
        # the standard 14 are also always available! (even if not initialized yet)
        import _fontdata
        for name in _fontdata.standardFonts:
            if name not in fontnames:
                fontnames.append(name)
        fontnames.sort()
        return fontnames

    def format(self):
        # register the Catalog/INfo and then format the objects one by one until exhausted
        # (possible infinite loop if there is a bug that continually makes new objects/refs...)
        # Prepare encryption
        self.encrypt.prepare(self)
        cat = self.Catalog
        info = self.info
        self.Reference(self.Catalog)
        self.Reference(self.info)
        # register the encryption dictionary if present
        encryptref = None
        encryptinfo = self.encrypt.info()
        if encryptinfo:
            encryptref = self.Reference(encryptinfo)
        # make std fonts (this could be made optional
        counter = 0 # start at first object (object 1 after preincrement)
        ids = [] # the collection of object ids in object number order
        numbertoid = self.numberToId
        idToNV = self.idToObjectNumberAndVersion
        idToOb = self.idToObject
        idToOf = self.idToOffset
        ### note that new entries may be "appended" DURING FORMATTING
        done = None
        File = PDFFile(self._pdfVersion) # output collector
        while done is None:
            counter += 1 # do next object...
            if counter in numbertoid:
                id = numbertoid[counter]
                #printidToOb
                obj = idToOb[id]
                IO = PDFIndirectObject(id, obj)
                # register object number and version
                #encrypt.register(id,
                IOf = IO.format(self)
                # add a comment to the PDF output
                if not rl_config.invariant and DoComments:
                    try:
                        classname = obj.__class__.__name__
                    except:
                        classname = repr(obj)
                    File.add("%% %s: class %s %s" % (repr(id), classname[:50], LINEEND))
                offset = File.add(IOf)
                idToOf[id] = offset
                ids.append(id)
            else:
                done = 1
        # sanity checks (must happen AFTER formatting)
        lno = len(numbertoid)
        if counter-1!=lno:
            raise ValueError, "counter %s doesn't match number to id dictionary %s" %(counter, lno)
        # now add the xref
        xref = PDFCrossReferenceTable()
        xref.addsection(0, ids)
        xreff = xref.format(self)
        xrefoffset = File.add(xreff)
        # now add the trailer
        trailer = PDFTrailer(
            startxref = xrefoffset,
            Size = lno+1,
            Root = self.Reference(cat),
            Info = self.Reference(info),
            Encrypt = encryptref,
            ID = self.ID(),
            )
        trailerf = trailer.format(self)
        File.add(trailerf)
        # return string format for pdf file
        return File.format(self)

    def hasForm(self, name):
        """tests for existence of named form"""
        internalname = xObjectName(name)
        return internalname in self.idToObject

    def getFormBBox(self, name, boxType="MediaBox"):
        """get the declared bounding box of the form as a list.
        If you specify a different PDF box definition (e.g. the
        ArtBox) and it has one, that's what you'll get."""
        internalname = xObjectName(name)
        if internalname in self.idToObject:
            theform = self.idToObject[internalname]
            if hasattr(theform,'_extra_pageCatcher_info'):
                return theform._extra_pageCatcher_info[boxType]
            if isinstance(theform, PDFFormXObject):
                # internally defined form
                return theform.BBoxList()
            elif isinstance(theform, PDFStream):
                # externally defined form
                return list(theform.dictionary.dict[boxType].sequence)
            else:
                raise ValueError, "I don't understand the form instance %s" % repr(name)

    def getXObjectName(self, name):
        """Lets canvas find out what form is called internally.
        Never mind whether it is defined yet or not."""
        return xObjectName(name)

    def xobjDict(self, formnames):
        """construct an xobject dict (for inclusion in a resource dict, usually)
           from a list of form names (images not yet supported)"""
        D = {}
        for name in formnames:
            internalname = xObjectName(name)
            reference = PDFObjectReference(internalname)
            D[internalname] = reference
        #print "xobjDict D", D
        return PDFDictionary(D)

    def Reference(self, object, name=None, InstanceType=InstanceType):
        ### note references may "grow" during the final formatting pass: don't use d.keys()!
        # don't make references to other references, or non instances, unless they are named!
        #print"object type is ", type(object)
        iob = hasattr(object,'__PDFObject__')
        idToObject = self.idToObject
        if name is None and (not iob or object.__class__ is PDFObjectReference):
            return object
        if hasattr(object, __InternalName__):
            # already registered
            intname = object.__InternalName__
            if name is not None and name!=intname:
                raise ValueError, "attempt to reregister object %s with new name %s" % (
                    repr(intname), repr(name))
            if intname not in idToObject:
                raise ValueError, "object named but not registered"
            return PDFObjectReference(intname)
        # otherwise register the new object
        objectcounter = self.objectcounter = self.objectcounter+1
        if name is None:
            name = "R"+repr(objectcounter)
        if name in idToObject:
            other = idToObject[name]
            if other!=object:
                raise ValueError, "redefining named object: "+repr(name)
            return PDFObjectReference(name)
        if iob:
            object.__InternalName__ = name
        #print "name", name, "counter", objectcounter
        self.idToObjectNumberAndVersion[name] = (objectcounter, 0)
        self.numberToId[objectcounter] = name
        idToObject[name] = object
        return PDFObjectReference(name)

### chapter 4 Objects
PDFtrue = "true"
PDFfalse = "false"
PDFnull = "null"

class PDFText:
    __PDFObject__ = True
    def __init__(self, t):
        self.t = t
    def format(self, document):
        result = binascii.hexlify(document.encrypt.encode(self.t))
        return "<%s>" % result
    def __str__(self):
        dummydoc = DummyDoc()
        return self.format(dummydoc)

def PDFnumber(n):
    return n

import re
_re_cleanparens=re.compile('[^()]')
del re
def _isbalanced(s):
    '''tests whether a string is balanced in parens'''
    s = _re_cleanparens.sub('',s)
    n = 0
    for c in s:
        if c=='(': n+=1
        else:
            n -= 1
            if n<0: return 0
    return not n and 1 or 0

def _checkPdfdoc(utext):
    '''return true if no Pdfdoc encoding errors'''
    try:
        utext.encode('pdfdoc')
        return 1
    except UnicodeEncodeError, e:
        return 0

class PDFString:
    __PDFObject__ = True
    def __init__(self, s, escape=1, enc='auto'):
        '''s can be unicode/utf8 or a PDFString
        if escape is true then the output will be passed through escape
        if enc is raw then the string will be left alone
        if enc is auto we'll try and automatically adapt to utf_16_be if the
        effective string is not entirely in pdfdoc
        '''
        if isinstance(s,PDFString):
            self.s = s.s
            self.escape = s.escape
            self.enc = s.enc
        else:
            self.s = s
            self.escape = escape
            self.enc = enc
    def format(self, document):
        s = self.s
        enc = getattr(self,'enc','auto')
        if type(s) is str:
            if enc is 'auto':
                try:
                    u = s.decode(s.startswith(codecs.BOM_UTF16_BE) and 'utf16' or 'utf8')
                    if _checkPdfdoc(u):
                        s = u.encode('pdfdoc')
                    else:
                        s = codecs.BOM_UTF16_BE+u.encode('utf_16_be')
                except:
                    try:
                        s.decode('pdfdoc')
                    except:
                        import sys
                        print >>sys.stderr, 'Error in',repr(s)
                        raise
        elif type(s) is unicode:
            if enc is 'auto':
                if _checkPdfdoc(s):
                    s = s.encode('pdfdoc')
                else:
                    s = codecs.BOM_UTF16_BE+s.encode('utf_16_be')
            else:
                s = codecs.BOM_UTF16_BE+s.encode('utf_16_be')
        else:
            raise ValueError('PDFString argument must be str/unicode not %s' % type(s))

        escape = getattr(self,'escape',1)
        if not isinstance(document.encrypt,NoEncryption):
            s = document.encrypt.encode(s)
            escape = 1
        if escape:
            try:
                es = "(%s)" % pdfutils._escape(s)
            except:
                raise ValueError("cannot escape %s %s" % (s, repr(s)))
            if escape&2:
                es = es.replace('\\012','\n')
            if escape&4 and _isbalanced(s):
                es = es.replace('\\(','(').replace('\\)',')')
            return es
        else:
            return '(%s)' % s
    def __str__(self):
        return "(%s)" % pdfutils._escape(self.s)

def PDFName(data,lo=chr(0x21),hi=chr(0x7e)):
    # might need to change this to class for encryption
    #  NOTE: RESULT MUST ALWAYS SUPPORT MEANINGFUL COMPARISONS (EQUALITY) AND HASH
    # first convert the name
    L = list(data)
    for i,c in enumerate(L):
        if c<lo or c>hi or c in "%()<>{}[]#":
            L[i] = "#"+hex(ord(c))[2:] # forget the 0x thing...
    return "/"+(''.join(L))

class PDFDictionary:
    __PDFObject__ = True
    multiline = LongFormat
    def __init__(self, dict=None):
        """dict should be namestring to value eg "a": 122 NOT pdfname to value NOT "/a":122"""
        if dict is None:
            self.dict = {}
        else:
            self.dict = dict.copy()
    def __setitem__(self, name, value):
        self.dict[name] = value
    def __getitem__(self, a):
        return self.dict[a]
    def __contains__(self,a):
        return a in self.dict
    def Reference(self, name, document):
        self.dict[name] = document.Reference(self.dict[name])
    def format(self, document,IND=LINEEND+' '):
        dict = self.dict
        try:
            keys = dict.keys()
        except:
            print repr(dict)
            raise
        keys.sort()
        L = [(format(PDFName(k),document)+" "+format(dict[k],document)) for k in keys]
        if self.multiline:
            L = IND.join(L)
        else:
            # break up every 6 elements anyway
            t=L.insert
            for i in xrange(6, len(L), 6):
                t(i,LINEEND)
            L = " ".join(L)
        return "<< %s >>" % L

    def copy(self):
        return PDFDictionary(self.dict)

    def normalize(self):
        #normalize the names to use RL standard ie Name not /Name
        D = self.dict
        K = [k for k in D.iterkeys() if k.startswith('/')]
        for k in K:
            D[k[1:]] = D.pop(k)

class checkPDFNames:
    def __init__(self,*names):
        self.names = map(PDFName,names)
    def __call__(self,value):
        if not value.startswith('/'):
            value=PDFName(value)
        if value in self.names:
            return value

def checkPDFBoolean(value):
    if value in ('true','false'): return value

class CheckedPDFDictionary(PDFDictionary):
    validate = {}
    def __init__(self,dict=None,validate=None):
        PDFDictionary.__init__(self,dict)
        if validate: self.validate = validate

    def __setitem__(self,name,value):
        if name not in self.validate:
            raise ValueError('invalid key, %r' % name)
        cvalue = self.validate[name](value)
        if cvalue is None:
            raise ValueError('Bad value %r for key %r' % (value,name))
        PDFDictionary.__setitem__(self,name,cvalue)

class ViewerPreferencesPDFDictionary(CheckedPDFDictionary):
    validate=dict(
                HideToolbar=checkPDFBoolean,
                HideMenubar=checkPDFBoolean,
                HideWindowUI=checkPDFBoolean,
                FitWindow=checkPDFBoolean,
                CenterWindow=checkPDFBoolean,
                DisplayDocTitle=checkPDFBoolean,    #contributed by mark Erbaugh
                NonFullScreenPageMode=checkPDFNames(*'UseNone UseOutlines UseThumbs UseOC'.split()),
                Direction=checkPDFNames(*'L2R R2L'.split()),
                ViewArea=checkPDFNames(*'MediaBox CropBox BleedBox TrimBox ArtBox'.split()),
                ViewClip=checkPDFNames(*'MediaBox CropBox BleedBox TrimBox ArtBox'.split()),
                PrintArea=checkPDFNames(*'MediaBox CropBox BleedBox TrimBox ArtBox'.split()),
                PrintClip=checkPDFNames(*'MediaBox CropBox BleedBox TrimBox ArtBox'.split()),
                PrintScaling=checkPDFNames(*'None AppDefault'.split()),
                )

# stream filters are objects to support round trip and
# possibly in the future also support parameters
class PDFStreamFilterZCompress:
    pdfname = "FlateDecode"
    def encode(self, text):
        from reportlab.lib.utils import import_zlib
        zlib = import_zlib()
        if not zlib: raise ImportError, "cannot z-compress zlib unavailable"
        return zlib.compress(text)
    def decode(self, encoded):
        from reportlab.lib.utils import import_zlib
        zlib = import_zlib()
        if not zlib: raise ImportError, "cannot z-decompress zlib unavailable"
        return zlib.decompress(encoded)

# need only one of these, unless we implement parameters later
PDFZCompress = PDFStreamFilterZCompress()

class PDFStreamFilterBase85Encode:
    pdfname = "ASCII85Decode"
    def encode(self, text):
        from pdfutils import _AsciiBase85Encode, _wrap
        text = _AsciiBase85Encode(text)
        if rl_config.wrapA85:
            text = _wrap(text)
        return text
    def decode(self, text):
        from pdfutils import _AsciiBase85Decode
        return _AsciiBase85Decode(text)

# need only one of these too
PDFBase85Encode = PDFStreamFilterBase85Encode()

STREAMFMT = ("%(dictionary)s%(LINEEND)s" # dictionary
             "stream" # stream keyword
             "%(LINEEND)s" # a line end (could be just a \n)
             "%(content)s" # the content, with no lineend
             "endstream%(LINEEND)s" # the endstream keyword
             )
class PDFStream:
    '''set dictionary elements explicitly stream.dictionary[name]=value'''
    __PDFObject__ = True
    ### compression stuff not implemented yet
    __RefOnly__ = 1 # must be at top level
    def __init__(self, dictionary=None, content=None, filters=None):
        if dictionary is None:
            dictionary = PDFDictionary()
        self.dictionary = dictionary
        self.content = content
        self.filters = filters
    def format(self, document):
        dictionary = self.dictionary
        # copy it for modification
        dictionary = PDFDictionary(dictionary.dict.copy())
        content = self.content
        filters = self.filters
        if self.content is None:
            raise ValueError, "stream content not set"
        if filters is None:
            filters = document.defaultStreamFilters
        # only apply filters if they haven't been applied elsewhere
        if filters is not None and "Filter" not in dictionary.dict:
            # apply filters in reverse order listed
            rf = list(filters)
            rf.reverse()
            fnames = []
            for f in rf:
                #print "*****************content:"; print repr(content[:200])
                #print "*****************filter", f.pdfname
                content = f.encode(content)
                fnames.insert(0, PDFName(f.pdfname))
            #print "*****************finally:"; print content[:200]
            #print "****** FILTERS", fnames
            #stop
            dictionary["Filter"] = PDFArray(fnames)
        # "stream encoding is done after all filters have been applied"
        content = document.encrypt.encode(content)
        fc = format(content, document)
        #print "type(content)", type(content), len(content), type(self.dictionary)
        lc = len(content)
        #if fc!=content: burp
        # set dictionary length parameter
        dictionary["Length"] = lc
        fd = format(dictionary, document)
        sdict = LINEENDDICT.copy()
        sdict["dictionary"] = fd
        sdict["content"] = fc
        return STREAMFMT % sdict

def teststream(content=None):
    #content = "" # tests
    if content is None:
        content = teststreamcontent
    content = string.strip(content)
    content = string.replace(content, "\n", LINEEND) + LINEEND
    S = PDFStream(content = content,
                    filters=rl_config.useA85 and [PDFBase85Encode,PDFZCompress] or [PDFZCompress])
    # nothing else needed...
    S.__Comment__ = "tests stream"
    return S

teststreamcontent = """
1 0 0 1 0 0 cm BT /F9 12 Tf 14.4 TL ET
1.00 0.00 1.00 rg
n 72.00 72.00 432.00 648.00 re B*
"""
class PDFArray:
    __PDFObject__ = True
    multiline = LongFormat
    _ZLIST = list(9*' ')+[LINEEND]
    def __init__(self, sequence):
        self.sequence = list(sequence)
    def References(self, document):
        """make all objects in sequence references"""
        self.sequence = map(document.Reference, self.sequence)
    def format(self, document, IND=LINEEND+' '):
        L = [format(e, document) for e in self.sequence]
        if self.multiline:
            L = IND.join(L)
        else:
            n=len(L)
            if n>10:
                # break up every 10 elements anyway
                m,r = divmod(n,10)
                L = ''.join([l+z for l,z in zip(L,m*self._ZLIST+list(r*' '))])
                L = L.strip()
            else:
                L = ' '.join(L)
        return "[ %s ]" % L

class PDFArrayCompact(PDFArray):
    multiline=False

INDIRECTOBFMT = "%(n)s %(v)s obj%(LINEEND)s%(content)s%(CLINEEND)sendobj%(LINEEND)s"
class PDFIndirectObject:
    __PDFObject__ = True
    __RefOnly__ = 1
    def __init__(self, name, content):
        self.name = name
        self.content = content
    def format(self, document):
        name = self.name
        n, v = document.idToObjectNumberAndVersion[name]
        # set encryption parameters
        document.encrypt.register(n, v)
        fcontent = format(self.content, document, toplevel=1) # yes this is at top level
        D = LINEENDDICT.copy()
        D["n"] = n
        D["v"] = v
        D["content"] = fcontent
        D['CLINEEND'] = (LINEEND,'')[fcontent.endswith(LINEEND)]
        return INDIRECTOBFMT % D

class PDFObjectReference:
    __PDFObject__ = True
    def __init__(self, name):
        self.name = name
    def format(self, document):
        try:
            return "%s %s R" % document.idToObjectNumberAndVersion[self.name]
        except:
            raise KeyError, "forward reference to %s not resolved upon final formatting" % repr(self.name)

### chapter 5
# Following Ken Lunde's advice and the PDF spec, this includes
# some high-order bytes.  I chose the characters for Tokyo
# in Shift-JIS encoding, as these cannot be mistaken for
# any other encoding, and we'll be able to tell if something
# has run our PDF files through a dodgy Unicode conversion.
PDFHeader = (
"%%PDF-%s.%s"+LINEEND+
"%%\223\214\213\236 ReportLab Generated PDF document http://www.reportlab.com"+LINEEND)

class PDFFile:
    __PDFObject__ = True
    ### just accumulates strings: keeps track of current offset
    def __init__(self,pdfVersion=PDF_VERSION_DEFAULT):
        self.strings = []
        self.write = self.strings.append
        self.offset = 0
        self.add(PDFHeader % pdfVersion)

    def closeOrReset(self):
        pass

    def add(self, s):
        """should be constructed as late as possible, return position where placed"""
        result = self.offset
        self.offset = result+len(s)
        self.write(s)
        return result
    def format(self, document):
        strings = map(str, self.strings) # final conversion, in case of lazy objects
        return string.join(strings, "")

XREFFMT = '%0.10d %0.5d n'

class PDFCrossReferenceSubsection:
    __PDFObject__ = True
    def __init__(self, firstentrynumber, idsequence):
        self.firstentrynumber = firstentrynumber
        self.idsequence = idsequence
    def format(self, document):
        """id sequence should represent contiguous object nums else error. free numbers not supported (yet)"""
        firstentrynumber = self.firstentrynumber
        idsequence = self.idsequence
        entries = list(idsequence)
        nentries = len(idsequence)
        # special case: object number 0 is always free
        taken = {}
        if firstentrynumber==0:
            taken[0] = "standard free entry"
            nentries = nentries+1
            entries.insert(0, "0000000000 65535 f")
        idToNV = document.idToObjectNumberAndVersion
        idToOffset = document.idToOffset
        lastentrynumber = firstentrynumber+nentries-1
        for id in idsequence:
            (num, version) = idToNV[id]
            if num in taken:
                raise ValueError, "object number collision %s %s %s" % (num, repr(id), repr(taken[id]))
            if num>lastentrynumber or num<firstentrynumber:
                raise ValueError, "object number %s not in range %s..%s" % (num, firstentrynumber, lastentrynumber)
            # compute position in list
            rnum = num-firstentrynumber
            taken[num] = id
            offset = idToOffset[id]
            entries[num] = XREFFMT % (offset, version)
        # now add the initial line
        firstline = "%s %s" % (firstentrynumber, nentries)
        entries.insert(0, firstline)
        # make sure it ends with a LINEEND
        entries.append("")
        if LINEEND=="\n" or LINEEND=="\r":
            reflineend = " "+LINEEND # as per spec
        elif LINEEND=="\r\n":
            reflineend = LINEEND
        else:
            raise ValueError, "bad end of line! %s" % repr(LINEEND)
        return string.join(entries, LINEEND)

class PDFCrossReferenceTable:
    __PDFObject__ = True

    def __init__(self):
        self.sections = []
    def addsection(self, firstentry, ids):
        section = PDFCrossReferenceSubsection(firstentry, ids)
        self.sections.append(section)
    def format(self, document):
        sections = self.sections
        if not sections:
            raise ValueError, "no crossref sections"
        L = ["xref"+LINEEND]
        for s in self.sections:
            fs = format(s, document)
            L.append(fs)
        return string.join(L, "")

TRAILERFMT = ("trailer%(LINEEND)s"
              "%(dict)s%(LINEEND)s"
              "startxref%(LINEEND)s"
              "%(startxref)s%(LINEEND)s"
              "%(PERCENT)s%(PERCENT)sEOF%(LINEEND)s")

class PDFTrailer:
    __PDFObject__ = True

    def __init__(self, startxref, Size=None, Prev=None, Root=None, Info=None, ID=None, Encrypt=None):
        self.startxref = startxref
        if Size is None or Root is None:
            raise ValueError, "Size and Root keys required"
        dict = self.dict = PDFDictionary()
        for (n,v) in [("Size", Size), ("Prev", Prev), ("Root", Root),
                      ("Info", Info), ("ID", ID), ("Encrypt", Encrypt)]:
            if v is not None:
                dict[n] = v
    def format(self, document):
        fdict = format(self.dict, document)
        D = LINEENDDICT.copy()
        D["dict"] = fdict
        D["startxref"] = self.startxref
        return TRAILERFMT % D

#### XXXX skipping incremental update,
#### encryption

#### chapter 6, doc structure

class PDFCatalog:
    __PDFObject__ = True
    __Comment__ = "Document Root"
    __RefOnly__ = 1
    # to override, set as attributes
    __Defaults__ = {"Type": PDFName("Catalog"),
                "PageMode": PDFName("UseNone"),
                }
    __NoDefault__ = string.split("""
        Dests Outlines Pages Threads AcroForm Names OpenAction PageMode URI
        ViewerPreferences PageLabels PageLayout JavaScript StructTreeRoot SpiderInfo"""
                                 )
    __Refs__ = __NoDefault__ # make these all into references, if present

    def format(self, document):
        self.check_format(document)
        defaults = self.__Defaults__
        Refs = self.__Refs__
        D = {}
        for k in defaults.keys():
            default = defaults[k]
            v = None
            if hasattr(self, k) and getattr(self,k) is not None:
                v = getattr(self, k)
            elif default is not None:
                v = default
            if v is not None:
                D[k] = v
        for k in self.__NoDefault__:
            if hasattr(self, k):
                v = getattr(self,k)
                if v is not None:
                    D[k] = v
        # force objects to be references where required
        for k in Refs:
            if k in D:
                #print"k is", k, "value", D[k]
                D[k] = document.Reference(D[k])
        dict = PDFDictionary(D)
        return format(dict, document)

    def showOutline(self):
        self.setPageMode("UseOutlines")

    def showFullScreen(self):
        self.setPageMode("FullScreen")

    def setPageLayout(self,layout):
        if layout:
            self.PageLayout = PDFName(layout)

    def setPageMode(self,mode):
        if mode:
            self.PageMode = PDFName(mode)

    def check_format(self, document):
        """for use in subclasses"""
        pass

class PDFPages(PDFCatalog):
    """PAGES TREE WITH ONE INTERNAL NODE, FOR "BALANCING" CHANGE IMPLEMENTATION"""
    __Comment__ = "page tree"
    __RefOnly__ = 1
    # note: could implement page attribute inheritance...
    __Defaults__ = {"Type": PDFName("Pages"),
                    }
    __NoDefault__ = string.split("Kids Count Parent")
    __Refs__ = ["Parent"]
    def __init__(self):
        self.pages = []
    def __getitem__(self, item):
        return self.pages[item]
    def addPage(self, page):
        self.pages.append(page)
    def check_format(self, document):
        # convert all pages to page references
        pages = self.pages
        kids = PDFArray(pages)
        # make sure all pages are references
        kids.References(document)
        self.Kids = kids
        self.Count = len(pages)

class PDFPage(PDFCatalog):
    __Comment__ = "Page dictionary"
    # all PDF attributes can be set explicitly
    # if this flag is set, the "usual" behavior will be suppressed
    Override_default_compilation = 0
    __RefOnly__ = 1
    __Defaults__ = {"Type": PDFName("Page"),
                   # "Parent": PDFObjectReference(Pages),  # no! use document.Pages
                    }
    __NoDefault__ = string.split(""" Parent
        MediaBox Resources Contents CropBox Rotate Thumb Annots B Dur Hid Trans AA
        PieceInfo LastModified SeparationInfo ArtBox TrimBox BleedBox ID PZ
        Trans
    """)
    __Refs__ = string.split("""
        Contents Parent ID
    """)
    pagewidth = 595
    pageheight = 842
    stream = None
    hasImages = 0
    compression = 0
    XObjects = None
    _colorsUsed = {}
    _shadingsUsed = {}
    Trans = None
    # transitionstring?
    # xobjects?
    # annotations
    def __init__(self):
        # set all nodefaults to None
        for name in self.__NoDefault__:
            setattr(self, name, None)
    def setCompression(self, onoff):
        self.compression = onoff
    def setStream(self, code):
        if self.Override_default_compilation:
            raise ValueError, "overridden! must set stream explicitly"
        from types import ListType
        if type(code) is ListType:
            code = string.join(code, LINEEND)+LINEEND
        self.stream = code

    def setPageTransition(self, tranDict):
        self.Trans = PDFDictionary(tranDict)

    def check_format(self, document):
        # set up parameters unless usual behaviour is suppressed
        if self.Override_default_compilation:
            return
        self.MediaBox = self.MediaBox or PDFArray(self.Rotate in (90,270) and [0,0,self.pageheight,self.pagewidth] or [0, 0, self.pagewidth, self.pageheight])
        if not self.Annots:
            self.Annots = None
        else:
            #print self.Annots
            #raise ValueError, "annotations not reimplemented yet"
            if not hasattr(self.Annots,'__PDFObject__'):
                self.Annots = PDFArray(self.Annots)
        if not self.Contents:
            stream = self.stream
            if not stream:
                self.Contents = teststream()
            else:
                S = PDFStream()
                if self.compression:
                    S.filters = rl_config.useA85 and [PDFBase85Encode, PDFZCompress] or [PDFZCompress]
                S.content = stream
                S.__Comment__ = "page stream"
                self.Contents = S
        if not self.Resources:
            resources = PDFResourceDictionary()
            # fonts!
            resources.basicFonts()
            if self.hasImages:
                resources.allProcs()
            else:
                resources.basicProcs()
            if self.XObjects:
                #print "XObjects", self.XObjects.dict
                resources.XObject = self.XObjects
            if self.ExtGState:
                resources.ExtGState = self.ExtGState
            resources.setShading(self._shadingUsed)
            resources.setColorSpace(self._colorsUsed)

            self.Resources = resources
        if not self.Parent:
            pages = document.Pages
            self.Parent = document.Reference(pages)

#this code contributed by  Christian Jacobs <cljacobsen@gmail.com>
class PDFPageLabels(PDFCatalog):
    __comment__ = None
    __RefOnly__ = 0
    __Defaults__ = {}
    __NoDefault__ = ["Nums"]
    __Refs__ = []

    def __init__(self):
        self.labels = []

    def addPageLabel(self, page, label):
        """ Adds a new PDFPageLabel to this catalog.
        The 'page' argument, an integer, is the page number in the PDF document
        with which the 'label' should be associated. Page numbering in the PDF
        starts at zero! Thus, to change the label on the first page, '0' should be
        provided as an argument, and to change the 6th page, '5' should be provided
        as the argument.

        The 'label' argument should be a PDFPageLabel instance, which describes the
        format of the labels starting on page 'page' in the PDF and continuing
        until the next encounter of a PDFPageLabel.

        The order in which labels are added is not important.
        """
        self.labels.append((page, label))

    def format(self, document):
        self.labels.sort()
        labels = []
        for page, label in self.labels:
            labels.append(page)
            labels.append(label)

        self.Nums = PDFArray(labels)    #PDFArray makes a copy with list()
        return PDFCatalog.format(self, document)

class PDFPageLabel(PDFCatalog):
    __Comment__ = None
    __RefOnly__ = 0
    __Defaults__ = {}
    __NoDefault__ = "Type S P St".split()
    __convertible__ = 'ARABIC ROMAN_UPPER ROMAN_LOWER LETTERS_UPPER LETTERS_LOWER'

    ARABIC = 'D'
    ROMAN_UPPER = 'R'
    ROMAN_LOWER = 'r'
    LETTERS_UPPER = 'A'
    LETTERS_LOWER = 'a'

    def __init__(self, style=None, start=None, prefix=None):
        """
        A PDFPageLabel changes the style of page numbering as displayed in a PDF
        viewer. PDF page labels have nothing to do with 'physical' page numbers
        printed on a canvas, but instead influence the 'logical' page numbers
        displayed by PDF viewers. However, when using roman numerals (i, ii,
        iii...) or page prefixes for appendecies (A.1, A.2...) on the physical
        pages PDF page labels are necessary to change the logical page numbers
        displayed by the PDF viewer to match up with the physical numbers. A
        PDFPageLabel changes the properties of numbering at the page on which it
        appears (see the class 'PDFPageLabels' for specifying where a PDFPageLabel
        is associated) and all subsequent pages, until a new PDFPageLabel is
        encountered.

        The arguments to this initialiser determine the properties of all
        subsequent page labels. 'style' determines the numberings style, arabic,
        roman, letters; 'start' specifies the starting number; and 'prefix' any
        prefix to be applied to the page numbers. All these arguments can be left
        out or set to None.

        * style:

            - None:                       No numbering, can be used to display the prefix only.
            - PDFPageLabel.ARABIC:        Use arabic numbers: 1, 2, 3, 4...
            - PDFPageLabel.ROMAN_UPPER:   Use upper case roman numerals: I, II, III...
            - PDFPageLabel.ROMAN_LOWER:   Use lower case roman numerals: i, ii, iii...
            - PDFPageLabel.LETTERS_UPPER: Use upper case letters: A, B, C, D...
            - PDFPageLabel.LETTERS_LOWER: Use lower case letters: a, b, c, d...

        * start:

            -   An integer specifying the starting number for this PDFPageLabel. This
                can be used when numbering style changes to reset the page number back
                to one, ie from roman to arabic, or from arabic to appendecies. Can be
                any positive integer or None. I'm not sure what the effect of
                specifying None is, probably that page numbering continues with the
                current sequence, I'd have to check the spec to clarify though.

        * prefix:

            -   A string which is prefixed to the page numbers. Can be used to display
                appendecies in the format: A.1, A.2, ..., B.1, B.2, ... where a
                PDFPageLabel is used to set the properties for the first page of each
                appendix to restart the page numbering at one and set the prefix to the
                appropriate letter for current appendix. The prefix can also be used to
                display text only, if the 'style' is set to None. This can be used to
                display strings such as 'Front', 'Back', or 'Cover' for the covers on
                books.

        """
        if style:
            if style.upper() in self.__convertible__: style = getattr(self,style.upper())
            self.S = PDFName(style)
        if start: self.St = PDFnumber(start)
        if prefix: self.P = PDFString(prefix)
#ends code contributed by  Christian Jacobs <cljacobsen@gmail.com>

def testpage(document):
    P = PDFPage()
    P.Contents = teststream()
    pages = document.Pages
    P.Parent = document.Reference(pages)
    P.MediaBox = PDFArray([0, 0, 595, 841])
    resources = PDFResourceDictionary()
    resources.allProcs() # enable all procsets
    resources.basicFonts()
    P.Resources = resources
    pages.addPage(P)

#### DUMMY OUTLINES IMPLEMENTATION FOR testing
DUMMYOUTLINE = """
<<
  /Count
      0
  /Type
      /Outlines
>>"""

class PDFOutlines0:
    __PDFObject__ = True
    __Comment__ = "TEST OUTLINE!"
    text = string.replace(DUMMYOUTLINE, "\n", LINEEND)
    __RefOnly__ = 1
    def format(self, document):
        return self.text

class OutlineEntryObject:
    "an entry in an outline"
    __PDFObject__ = True
    Title = Dest = Parent = Prev = Next = First = Last = Count = None
    def format(self, document):
        D = {}
        D["Title"] = PDFString(self.Title)
        D["Parent"] = self.Parent
        D["Dest"] = self.Dest
        for n in ("Prev", "Next", "First", "Last", "Count"):
            v = getattr(self, n)
            if v is not None:
                D[n] = v
        PD = PDFDictionary(D)
        return PD.format(document)

class PDFOutlines:
    """
    takes a recursive list of outline destinations like::

        out = PDFOutline1()
        out.setNames(canvas, # requires canvas for name resolution
        "chapter1dest",
        ("chapter2dest",
        ["chapter2section1dest",
        "chapter2section2dest",
        "chapter2conclusiondest"]
        ), # end of chapter2 description
        "chapter3dest",
        ("chapter4dest", ["c4s1", "c4s2"])
        )

    Higher layers may build this structure incrementally. KISS at base level.
    """
    __PDFObject__ = True
    # first attempt, many possible features missing.
    #no init for now
    mydestinations = ready = None
    counter = 0
    currentlevel = -1 # ie, no levels yet

    def __init__(self):
        self.destinationnamestotitles = {}
        self.destinationstotitles = {}
        self.levelstack = []
        self.buildtree = []
        self.closedict = {} # dictionary of "closed" destinations in the outline

    def addOutlineEntry(self, destinationname, level=0, title=None, closed=None):
        """destinationname of None means "close the tree" """
        from types import IntType, TupleType
        if destinationname is None and level!=0:
            raise ValueError, "close tree must have level of 0"
        if type(level) is not IntType: raise ValueError, "level must be integer, got %s" % type(level)
        if level<0: raise ValueError, "negative levels not allowed"
        if title is None: title = destinationname
        currentlevel = self.currentlevel
        stack = self.levelstack
        tree = self.buildtree
        # adjust currentlevel and stack to match level
        if level>currentlevel:
            if level>currentlevel+1:
                raise ValueError, "can't jump from outline level %s to level %s, need intermediates (destinationname=%r, title=%r)" %(currentlevel, level, destinationname, title)
            level = currentlevel = currentlevel+1
            stack.append([])
        while level<currentlevel:
            # pop off levels to match
            current = stack[-1]
            del stack[-1]
            previous = stack[-1]
            lastinprevious = previous[-1]
            if type(lastinprevious) is TupleType:
                (name, sectionlist) = lastinprevious
                raise ValueError, "cannot reset existing sections: " + repr(lastinprevious)
            else:
                name = lastinprevious
                sectionlist = current
                previous[-1] = (name, sectionlist)
            #sectionlist.append(current)
            currentlevel = currentlevel-1
        if destinationname is None: return
        stack[-1].append(destinationname)
        self.destinationnamestotitles[destinationname] = title
        if closed: self.closedict[destinationname] = 1
        self.currentlevel = level

    def setDestinations(self, destinationtree):
        self.mydestinations = destinationtree

    def format(self, document):
        D = {}
        D["Type"] = PDFName("Outlines")
        c = self.count
        D["Count"] = c
        if c!=0:
            D["First"] = self.first
            D["Last"] = self.last
        PD = PDFDictionary(D)
        return PD.format(document)

    def setNames(self, canvas, *nametree):
        desttree = self.translateNames(canvas, nametree)
        self.setDestinations(desttree)

    def setNameList(self, canvas, nametree):
        "Explicit list so I don't need to do in the caller"
        desttree = self.translateNames(canvas, nametree)
        self.setDestinations(desttree)

    def translateNames(self, canvas, object):
        "recursively translate tree of names into tree of destinations"
        from types import StringType, ListType, TupleType
        Ot = type(object)
        destinationnamestotitles = self.destinationnamestotitles
        destinationstotitles = self.destinationstotitles
        closedict = self.closedict
        if Ot is StringType:
            destination = canvas._bookmarkReference(object)
            title = object
            if object in destinationnamestotitles:
                title = destinationnamestotitles[object]
            else:
                destinationnamestotitles[title] = title
            destinationstotitles[destination] = title
            if object in closedict:
                closedict[destination] = 1 # mark destination closed
            return {object: canvas._bookmarkReference(object)} # name-->ref
        if Ot is ListType or Ot is TupleType:
            L = []
            for o in object:
                L.append(self.translateNames(canvas, o))
            if Ot is TupleType:
                return tuple(L)
            return L
        # bug contributed by Benjamin Dumke <reportlab@benjamin-dumke.de>
        raise TypeError("in outline, destination name must be string: got a %s"%Ot)

    def prepare(self, document, canvas):
        """prepare all data structures required for save operation (create related objects)"""
        if self.mydestinations is None:
            if self.levelstack:
                self.addOutlineEntry(None) # close the tree
                destnames = self.levelstack[0]
                #from pprint import pprint; pprint(destnames); stop
                self.mydestinations = self.translateNames(canvas, destnames)
            else:
                self.first = self.last = None
                self.count = 0
                self.ready = 1
                return
        #self.first = document.objectReference("Outline.First")
        #self.last = document.objectReference("Outline.Last")
        # XXXX this needs to be generalized for closed entries!
        self.count = count(self.mydestinations, self.closedict)
        (self.first, self.last) = self.maketree(document, self.mydestinations, toplevel=1)
        self.ready = 1

    def maketree(self, document, destinationtree, Parent=None, toplevel=0):
        from types import ListType, TupleType, DictType
        tdestinationtree = type(destinationtree)
        if toplevel:
            levelname = "Outline"
            Parent = document.Reference(document.Outlines)
        else:
            self.count = self.count+1
            levelname = "Outline.%s" % self.count
            if Parent is None:
                raise ValueError, "non-top level outline elt parent must be specified"
        if tdestinationtree is not ListType and tdestinationtree is not TupleType:
            raise ValueError, "destinationtree must be list or tuple, got %s"
        nelts = len(destinationtree)
        lastindex = nelts-1
        lastelt = firstref = lastref = None
        destinationnamestotitles = self.destinationnamestotitles
        closedict = self.closedict
        for index in range(nelts):
            eltobj = OutlineEntryObject()
            eltobj.Parent = Parent
            eltname = "%s.%s" % (levelname, index)
            eltref = document.Reference(eltobj, eltname)
            #document.add(eltname, eltobj)
            if lastelt is not None:
                lastelt.Next = eltref
                eltobj.Prev = lastref
            if firstref is None:
                firstref = eltref
            lastref = eltref
            lastelt = eltobj # advance eltobj
            lastref = eltref
            elt = destinationtree[index]
            te = type(elt)
            if te is DictType:
                # simple leaf {name: dest}
                leafdict = elt
            elif te is TupleType:
                # leaf with subsections: ({name: ref}, subsections) XXXX should clean up (see count(...))
                try:
                    (leafdict, subsections) = elt
                except:
                    raise ValueError, "destination tree elt tuple should have two elts, got %s" % len(elt)
                eltobj.Count = count(subsections, closedict)
                (eltobj.First, eltobj.Last) = self.maketree(document, subsections, eltref)
            else:
                raise ValueError, "destination tree elt should be dict or tuple, got %s" % te
            try:
                [(Title, Dest)] = leafdict.items()
            except:
                raise ValueError, "bad outline leaf dictionary, should have one entry "+utf8str(elt)
            eltobj.Title = destinationnamestotitles[Title]
            eltobj.Dest = Dest
            if te is TupleType and Dest in closedict:
                # closed subsection, count should be negative
                eltobj.Count = -eltobj.Count
        return (firstref, lastref)

def count(tree, closedict=None):
    """utility for outline: recursively count leaves in a tuple/list tree"""
    from operator import add
    from types import TupleType, ListType
    tt = type(tree)
    if tt is TupleType:
        # leaf with subsections XXXX should clean up this structural usage
        (leafdict, subsections) = tree
        [(Title, Dest)] = leafdict.items()
        if closedict and Dest in closedict:
            return 1 # closed tree element
    if tt is TupleType or tt is ListType:
        #return reduce(add, map(count, tree))
        counts = []
        for e in tree:
            counts.append(count(e, closedict))
        return sum(counts)  #used to be: return reduce(add, counts)
    return 1

class PDFInfo:
    """PDF documents can have basic information embedded, viewable from
    File | Document Info in Acrobat Reader.  If this is wrong, you get
    Postscript errors while printing, even though it does not print."""
    __PDFObject__ = True
    producer = "ReportLab PDF Library - www.reportlab.com"
    creator = "ReportLab PDF Library - www.reportlab.com"
    title = "untitled"
    author = "anonymous"
    subject = "unspecified"
    keywords = ""
    _dateFormatter = None

    def __init__(self):
        self.invariant = rl_config.invariant

    def digest(self, md5object):
        # add self information to signature
        for x in (self.title, self.author, self.subject, self.keywords):
            md5object.update(utf8str(x))

    def format(self, document):
        D = {}
        D["Title"] = PDFString(self.title)
        D["Author"] = PDFString(self.author)
        D["CreationDate"] = PDFDate(invariant=self.invariant,dateFormatter=self._dateFormatter)
        D["Producer"] = PDFString(self.producer)
        D["Creator"] = PDFString(self.creator)
        D["Subject"] = PDFString(self.subject)
        D["Keywords"] = PDFString(self.keywords)

        PD = PDFDictionary(D)
        return PD.format(document)

    def copy(self):
        "shallow copy - useful in pagecatchering"
        thing = self.__klass__()
        for (k, v) in self.__dict__.items():
            setattr(thing, k, v)
        return thing
# skipping thumbnails, etc

class Annotation:
    """superclass for all annotations."""
    __PDFObject__ = True
    defaults = [("Type", PDFName("Annot"),)]
    required = ("Type", "Rect", "Contents", "Subtype")
    permitted = required+(
      "Border", "C", "T", "M", "F", "H", "BS", "AA", "AS", "Popup", "P", "AP")
    def cvtdict(self, d, escape=1):
        """transform dict args from python form to pdf string rep as needed"""
        Rect = d["Rect"]
        if type(Rect) is not types.StringType:
            d["Rect"] = PDFArray(Rect)
        d["Contents"] = PDFString(d["Contents"],escape)
        return d
    def AnnotationDict(self, **kw):
        if 'escape' in kw:
            escape = kw['escape']
            del kw['escape']
        else:
            escape = 1
        d = {}
        for (name,val) in self.defaults:
            d[name] = val
        d.update(kw)
        for name in self.required:
            if name not in d:
                raise ValueError, "keyword argument %s missing" % name
        d = self.cvtdict(d,escape=escape)
        permitted = self.permitted
        for name in d.keys():
            if name not in permitted:
                raise ValueError, "bad annotation dictionary name %s" % name
        return PDFDictionary(d)
    def Dict(self):
        raise ValueError, "DictString undefined for virtual superclass Annotation, must overload"
        # but usually
        #return self.AnnotationDict(self, Rect=(a,b,c,d)) or whatever
    def format(self, document):
        D = self.Dict()
        return D.format(document)

class TextAnnotation(Annotation):
    permitted = Annotation.permitted + (
        "Open", "Name")
    def __init__(self, Rect, Contents, **kw):
        self.Rect = Rect
        self.Contents = Contents
        self.otherkw = kw
    def Dict(self):
        d = {}
        d.update(self.otherkw)
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["Subtype"] = "/Text"
        return self.AnnotationDict(**d)

class FreeTextAnnotation(Annotation):
    permitted = Annotation.permitted + ("DA",)
    def __init__(self, Rect, Contents, DA, **kw):
        self.Rect = Rect
        self.Contents = Contents
        self.DA = DA
        self.otherkw = kw
    def Dict(self):
        d = {}
        d.update(self.otherkw)
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["DA"] = self.DA
        d["Subtype"] = "/FreeText"
        return self.AnnotationDict(**d)

class LinkAnnotation(Annotation):

    permitted = Annotation.permitted + (
        "Dest", "A", "PA")
    def __init__(self, Rect, Contents, Destination, Border="[0 0 1]", **kw):
        self.Border = Border
        self.Rect = Rect
        self.Contents = Contents
        self.Destination = Destination
        self.otherkw = kw

    def dummyDictString(self): # old, testing
        return """
          << /Type /Annot /Subtype /Link /Rect [71 717 190 734] /Border [16 16 1]
             /Dest [23 0 R /Fit] >>
             """

    def Dict(self):
        d = {}
        d.update(self.otherkw)
        d["Border"] = self.Border
        d["Rect"] = self.Rect
        d["Contents"] = self.Contents
        d["Subtype"] = "/Link"
        d["Dest"] = self.Destination
        return self.AnnotationDict(**d)

# skipping names tree
# skipping actions
# skipping names trees
# skipping to chapter 7

class PDFRectangle:
    __PDFObject__ = True
    def __init__(self, llx, lly, urx, ury):
        self.llx, self.lly, self.ulx, self.ury = llx, lly, urx, ury
    def format(self, document):
        A = PDFArray([self.llx, self.lly, self.ulx, self.ury])
        return format(A, document)

_NOWT=None
def _getTimeStamp():
    global _NOWT
    if not _NOWT:
        import time
        _NOWT = time.time()
    return _NOWT

class PDFDate:
    __PDFObject__ = True
    # gmt offset now suppported properly
    def __init__(self, invariant=rl_config.invariant, dateFormatter=None):
        if invariant:
            now = (2000,01,01,00,00,00,0)
            self.dhh = 0
            self.dmm = 0
        else:
            import time
            now = tuple(time.localtime(_getTimeStamp())[:6])
            from time import timezone
            self.dhh = int(timezone / (3600.0))
            self.dmm = (timezone % 3600) % 60
        self.date = now[:6]
        self.dateFormatter = dateFormatter

    def format(self, doc):
        dfmt = self.dateFormatter or (
                lambda yyyy,mm,dd,hh,m,s:
                    "D:%04d%02d%02d%02d%02d%02d%+03d'%02d'"
                        % (yyyy,mm,dd,hh,m,s,self.dhh,self.dmm))
        return format(PDFString(dfmt(*self.date)), doc)

class Destination:
    """

    not a pdfobject!  This is a placeholder that can delegates
    to a pdf object only after it has been defined by the methods
    below.

    EG a Destination can refer to Appendix A before it has been
    defined, but only if Appendix A is explicitly noted as a destination
    and resolved before the document is generated...

    For example the following sequence causes resolution before doc generation.
        d = Destination()
        d.fit() # or other format defining method call
        d.setPage(p)
        (at present setPageRef is called on generation of the page).
    """
    __PDFObject__ = True
    representation = format = page = None
    def __init__(self,name):
        self.name = name
        self.fmt = self.page = None
    def format(self, document):
        f = self.fmt
        if f is None: raise ValueError, "format not resolved %s" % self.name
        p = self.page
        if p is None: raise ValueError, "Page reference unbound %s" % self.name
        f.page = p
        return f.format(document)
    def xyz(self, left, top, zoom):  # see pdfspec mar 11 99 pp184+
        self.fmt = PDFDestinationXYZ(None, left, top, zoom)
    def fit(self):
        self.fmt = PDFDestinationFit(None)
    def fitb(self):
        self.fmt = PDFDestinationFitB(None)
    def fith(self, top):
        self.fmt = PDFDestinationFitH(None,top)
    def fitv(self, left):
        self.fmt = PDFDestinationFitV(None, left)
    def fitbh(self, top):
        self.fmt = PDFDestinationFitBH(None, top)
    def fitbv(self, left):
        self.fmt = PDFDestinationFitBV(None, left)
    def fitr(self, left, bottom, right, top):
        self.fmt = PDFDestinationFitR(None, left, bottom, right, top)
    def setPage(self, page):
        self.page = page
        #self.fmt.page = page # may not yet be defined!

class PDFDestinationXYZ:
    __PDFObject__ = True
    typename = "XYZ"
    def __init__(self, page, left, top, zoom):
        self.page = page
        self.top = top
        self.zoom = zoom
        self.left = left
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left, self.top, self.zoom ] )
        return format(A, document)

class PDFDestinationFit:
    __PDFObject__ = True
    typename = "Fit"
    def __init__(self, page):
        self.page = page
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename) ] )
        return format(A, document)

class PDFDestinationFitB(PDFDestinationFit):
    typename = "FitB"

class PDFDestinationFitH:
    __PDFObject__ = True
    typename = "FitH"
    def __init__(self, page, top):
        self.page = page; self.top=top
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.top ] )
        return format(A, document)

class PDFDestinationFitBH(PDFDestinationFitH):
    typename = "FitBH"

class PDFDestinationFitV:
    __PDFObject__ = True
    typename = "FitV"
    def __init__(self, page, left):
        self.page = page; self.left=left
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left ] )
        return format(A, document)

class PDFDestinationFitBV(PDFDestinationFitV):
    typename = "FitBV"

class PDFDestinationFitR:
    __PDFObject__ = True
    typename = "FitR"
    def __init__(self, page, left, bottom, right, top):
        self.page = page; self.left=left; self.bottom=bottom; self.right=right; self.top=top
    def format(self, document):
        pageref = document.Reference(self.page)
        A = PDFArray( [ pageref, PDFName(self.typename), self.left, self.bottom, self.right, self.top] )
        return format(A, document)

# named destinations need nothing

# skipping filespecs

class PDFResourceDictionary:
    """each element *could* be reset to a reference if desired"""
    __PDFObject__ = True
    def __init__(self):
        self.ColorSpace = {}
        self.XObject = {}
        self.ExtGState = {}
        self.Font = {}
        self.Pattern = {}
        self.ProcSet = []
        self.Properties = {}
        self.Shading = {}
        # ?by default define the basicprocs
        self.basicProcs()
    stdprocs = map(PDFName, string.split("PDF Text ImageB ImageC ImageI"))
    dict_attributes = ("ColorSpace", "XObject", "ExtGState", "Font", "Pattern", "Properties", "Shading")

    def allProcs(self):
        # define all standard procsets
        self.ProcSet = self.stdprocs

    def basicProcs(self):
        self.ProcSet = self.stdprocs[:2] # just PDF and Text

    def basicFonts(self):
        self.Font = PDFObjectReference(BasicFonts)

    def setColorSpace(self,colorsUsed):
        for c,s in colorsUsed.iteritems():
            self.ColorSpace[s] = PDFObjectReference(c)

    def setShading(self,shadingUsed):
        for c,s in shadingUsed.iteritems():
            self.Shading[s] = PDFObjectReference(c)

    def format(self, document):
        D = {}
        from types import ListType, DictType
        for dname in self.dict_attributes:
            v = getattr(self, dname)
            if type(v) is DictType:
                if v:
                    dv = PDFDictionary(v)
                    D[dname] = dv
            else:
                D[dname] = v
        v = self.ProcSet
        dname = "ProcSet"
        if type(v) is ListType:
            if v:
                dv = PDFArray(v)
                D[dname] = dv
        else:
            D[dname] = v
        DD = PDFDictionary(D)
        return format(DD, document)

##############################################################################
#
#   Font objects - the PDFDocument.addFont() method knows which of these
#   to construct when given a user-facing Font object
#
##############################################################################
class PDFType1Font:
    """no init: set attributes explicitly"""
    __PDFObject__ = True
    __RefOnly__ = 1
    # note! /Name appears to be an undocumented attribute....
    name_attributes = string.split("Type Subtype BaseFont Name")
    Type = "Font"
    Subtype = "Type1"
    # these attributes are assumed to already be of the right type
    local_attributes = string.split("FirstChar LastChar Widths Encoding ToUnicode FontDescriptor")
    def format(self, document):
        D = {}
        for name in self.name_attributes:
            if hasattr(self, name):
                value = getattr(self, name)
                D[name] = PDFName(value)
        for name in self.local_attributes:
            if hasattr(self, name):
                value = getattr(self, name)
                D[name] = value
        #print D
        PD = PDFDictionary(D)
        return PD.format(document)

## These attribute listings will be useful in future, even if we
## put them elsewhere

class PDFTrueTypeFont(PDFType1Font):
    Subtype = "TrueType"
    #local_attributes = string.split("FirstChar LastChar Widths Encoding ToUnicode FontDescriptor") #same

##class PDFMMType1Font(PDFType1Font):
##    Subtype = "MMType1"
##
##class PDFType3Font(PDFType1Font):
##    Subtype = "Type3"
##    local_attributes = string.split(
##        "FirstChar LastChar Widths CharProcs FontBBox FontMatrix Resources Encoding")
##
##class PDFType0Font(PDFType1Font):
##    Subtype = "Type0"
##    local_attributes = string.split(
##        "DescendantFonts Encoding")
##
##class PDFCIDFontType0(PDFType1Font):
##    Subtype = "CIDFontType0"
##    local_attributes = string.split(
##        "CIDSystemInfo FontDescriptor DW W DW2 W2 Registry Ordering Supplement")
##
##class PDFCIDFontType0(PDFType1Font):
##    Subtype = "CIDFontType2"
##    local_attributes = string.split(
##        "BaseFont CIDToGIDMap CIDSystemInfo FontDescriptor DW W DW2 W2")
##
##class PDFEncoding(PDFType1Font):
##    Type = "Encoding"
##    name_attributes = string.split("Type BaseEncoding")
##    # these attributes are assumed to already be of the right type
##    local_attributes = ["Differences"]
##

# UGLY ALERT - this needs turning into something O-O, it was hacked
# across from the pdfmetrics.Encoding class to avoid circularity

# skipping CMaps

class PDFFormXObject:
    # like page requires .info set by some higher level (doc)
    # XXXX any resource used in a form must be propagated up to the page that (recursively) uses
    #   the form!! (not implemented yet).
    __PDFObject__ = True
    XObjects = Annots = BBox = Matrix = Contents = stream = Resources = None
    hasImages = 1 # probably should change
    compression = 0
    def __init__(self, lowerx, lowery, upperx, uppery):
        #not done
        self.lowerx = lowerx; self.lowery=lowery; self.upperx=upperx; self.uppery=uppery

    def setStreamList(self, data):
        if type(data) is types.ListType:
            data = string.join(data, LINEEND)
        self.stream = data

    def BBoxList(self):
        "get the declared bounding box for the form as a list"
        if self.BBox:
            return list(self.BBox.sequence)
        else:
            return [self.lowerx, self.lowery, self.upperx, self.uppery]

    def format(self, document):
        self.BBox = self.BBox or PDFArray([self.lowerx, self.lowery, self.upperx, self.uppery])
        self.Matrix = self.Matrix or PDFArray([1, 0, 0, 1, 0, 0])
        if not self.Annots:
            self.Annots = None
        else:
            #these must be transferred to the page when the form is used
            raise ValueError("annotations don't work in PDFFormXObjects yet")
        if not self.Contents:
            stream = self.stream
            if not stream:
                self.Contents = teststream()
            else:
                S = PDFStream()
                S.content = stream
                # need to add filter stuff (?)
                S.__Comment__ = "xobject form stream"
                self.Contents = S
        if not self.Resources:
            resources = PDFResourceDictionary()
            # fonts!
            resources.basicFonts()
            if self.hasImages:
                resources.allProcs()
            else:
                resources.basicProcs()
            if self.XObjects:
                #print "XObjects", self.XObjects.dict
                resources.XObject = self.XObjects
            self.Resources=resources
        if self.compression:
            self.Contents.filters = rl_config.useA85 and [PDFBase85Encode, PDFZCompress] or [PDFZCompress]
        sdict = self.Contents.dictionary
        sdict["Type"] = PDFName("XObject")
        sdict["Subtype"] = PDFName("Form")
        sdict["FormType"] = 1
        sdict["BBox"] = self.BBox
        sdict["Matrix"] = self.Matrix
        sdict["Resources"] = self.Resources
        return self.Contents.format(document)

class PDFPostScriptXObject:
    "For embedding PD (e.g. tray commands) in PDF"
    __PDFObject__ = True
    def __init__(self, content=None):
        self.content = content

    def format(self, document):
        S = PDFStream()
        S.content = self.content
        S.__Comment__ = "xobject postscript stream"
        sdict = S.dictionary
        sdict["Type"] = PDFName("XObject")
        sdict["Subtype"] = PDFName("PS")
        return S.format(document)

_mode2CS={'RGB':'DeviceRGB', 'L':'DeviceGray', 'CMYK':'DeviceCMYK'}
class PDFImageXObject:
    # first attempts at a hard-coded one
    # in the file, Image XObjects are stream objects.  We already
    # have a PDFStream object with 3 attributes:  dictionary, content
    # and filters.  So the job of this thing is to construct the
    # right PDFStream instance and ask it to format itself.
    __PDFObject__ = True
    def __init__(self, name, source=None, mask=None):
        self.name = name
        self.width = 24
        self.height = 23
        self.bitsPerComponent = 1
        self.colorSpace = 'DeviceGray'
        self._filters = rl_config.useA85 and ('ASCII85Decode',) or ()
        self.streamContent = """
            003B00 002700 002480 0E4940 114920 14B220 3CB650
            75FE88 17FF8C 175F14 1C07E2 3803C4 703182 F8EDFC
            B2BBC2 BB6F84 31BFC2 18EA3C 0E3E00 07FC00 03F800
            1E1800 1FF800>
            """
        self.mask = mask

        if source is None:
            pass # use the canned one.
        elif hasattr(source,'jpeg_fh'):
            self.loadImageFromSRC(source)   #it is already a PIL Image
        else:
            # it is a filename
            import os
            ext = string.lower(os.path.splitext(source)[1])
            src = open_for_read(source)
            if not(ext in ('.jpg', '.jpeg') and self.loadImageFromJPEG(src)):
                if rl_config.useA85:
                    self.loadImageFromA85(src)
                else:
                    self.loadImageFromRaw(src)

    def loadImageFromA85(self,source):
        IMG=[]
        imagedata = map(string.strip,pdfutils.makeA85Image(source,IMG=IMG))
        words = string.split(imagedata[1])
        self.width, self.height = map(string.atoi,(words[1],words[3]))
        self.colorSpace = {'/RGB':'DeviceRGB', '/G':'DeviceGray', '/CMYK':'DeviceCMYK'}[words[7]]
        self.bitsPerComponent = 8
        self._filters = 'ASCII85Decode','FlateDecode' #'A85','Fl'
        if IMG: self._checkTransparency(IMG[0])
        elif self.mask=='auto': self.mask = None
        self.streamContent = string.join(imagedata[3:-1],'')

    def loadImageFromJPEG(self,imageFile):
        try:
            try:
                info = pdfutils.readJPEGInfo(imageFile)
            finally:
                imageFile.seek(0) #reset file pointer
        except:
            return False
        self.width, self.height = info[0], info[1]
        self.bitsPerComponent = 8
        if info[2] == 1:
            self.colorSpace = 'DeviceGray'
        elif info[2] == 3:
            self.colorSpace = 'DeviceRGB'
        else: #maybe should generate an error, is this right for CMYK?
            self.colorSpace = 'DeviceCMYK'
            self._dotrans = 1
        self.streamContent = imageFile.read()
        if rl_config.useA85:
            self.streamContent = pdfutils._AsciiBase85Encode(self.streamContent)
            self._filters = 'ASCII85Decode','DCTDecode' #'A85','DCT'
        else:
            self._filters = 'DCTDecode', #'DCT'
        self.mask = None
        return True

    def loadImageFromRaw(self,source):
        IMG=[]
        imagedata = pdfutils.makeRawImage(source,IMG=IMG)
        words = string.split(imagedata[1])
        self.width, self.height = map(string.atoi,(words[1],words[3]))
        self.colorSpace = {'/RGB':'DeviceRGB', '/G':'DeviceGray', '/CMYK':'DeviceCMYK'}[words[7]]
        self.bitsPerComponent = 8
        self._filters = 'FlateDecode', #'Fl'
        if IMG: self._checkTransparency(IMG[0])
        elif self.mask=='auto': self.mask = None
        self.streamContent = string.join(imagedata[3:-1],'')

    def _checkTransparency(self,im):
        if self.mask=='auto':
            if im._dataA:
                self.mask = None
                self._smask = PDFImageXObject(_digester(im._dataA.getRGBData()),im._dataA,mask=None)
                self._smask._decode = [0,1]
            else:
                tc = im.getTransparent()
                if tc:
                    self.mask = (tc[0], tc[0], tc[1], tc[1], tc[2], tc[2])
                else:
                    self.mask = None
        elif hasattr(self.mask,'rgb'):
            _ = self.mask.rgb()
            self.mask = _[0],_[0],_[1],_[1],_[2],_[2]

    def loadImageFromSRC(self, im):
        "Extracts the stream, width and height"
        fp = im.jpeg_fh()
        if fp:
            self.loadImageFromJPEG(fp)
        else:
            zlib = import_zlib()
            if not zlib: return
            self.width, self.height = im.getSize()
            raw = im.getRGBData()
            #assert len(raw) == self.width*self.height, "Wrong amount of data for image expected %sx%s=%s got %s" % (self.width,self.height,self.width*self.height,len(raw))
            self.streamContent = zlib.compress(raw)
            if rl_config.useA85:
                self.streamContent = pdfutils._AsciiBase85Encode(self.streamContent)
                self._filters = 'ASCII85Decode','FlateDecode' #'A85','Fl'
            else:
                self._filters = 'FlateDecode', #'Fl'
            self.colorSpace= _mode2CS[im.mode]
            self.bitsPerComponent = 8
            self._checkTransparency(im)

    def format(self, document):
        S = PDFStream(content = self.streamContent)
        dict = S.dictionary
        dict["Type"] = PDFName("XObject")
        dict["Subtype"] = PDFName("Image")
        dict["Width"] = self.width
        dict["Height"] = self.height
        dict["BitsPerComponent"] = self.bitsPerComponent
        dict["ColorSpace"] = PDFName(self.colorSpace)
        if self.colorSpace=='DeviceCMYK' and getattr(self,'_dotrans',0):
            dict["Decode"] = PDFArray([1,0,1,0,1,0,1,0])
        elif getattr(self,'_decode',None):
            dict["Decode"] = PDFArray(self._decode)
        dict["Filter"] = PDFArray(map(PDFName,self._filters))
        dict["Length"] = len(self.streamContent)
        if self.mask: dict["Mask"] = PDFArray(self.mask)
        if getattr(self,'smask',None): dict["SMask"] = self.smask
        return S.format(document)

class PDFSeparationCMYKColor:
    def __init__(self, cmyk):
        from reportlab.lib.colors import CMYKColor
        if not isinstance(cmyk,CMYKColor):
            raise ValueError('%s needs a CMYKColor argument' % self.__class__.__name__)
        elif not cmyk.spotName:
            raise ValueError('%s needs a CMYKColor argument with a spotName' % self.__class__.__name__)
        self.cmyk = cmyk

    def _makeFuncPS(self):
        '''create the postscript code for the tint transfer function
        effectively this is tint*c, tint*y, ... tint*k'''
        R = [].append
        for i,v in enumerate(self.cmyk.cmyk()):
            v=float(v)
            if i==3:
                if v==0.0:
                    R('pop')
                    R('0.0')
                else:
                    R(str(v))
                    R('mul')
            else:
                if v==0:
                    R('0.0')
                else:
                    R('dup')
                    R(str(v))
                    R('mul')
                R('exch')
        return '{%s}' % (' '.join(R.__self__))

    def value(self):
        return PDFArrayCompact((
                    PDFName('Separation'),
                    PDFName(self.cmyk.spotName),
                    PDFName('DeviceCMYK'),
                    PDFStream(
                        dictionary=PDFDictionary(dict(
                            FunctionType=4,
                            Domain=PDFArrayCompact((0,1)),
                            Range=PDFArrayCompact((0,1,0,1,0,1,0,1))
                            )),
                        content=self._makeFuncPS(),
                        filters=None,#[PDFBase85Encode, PDFZCompress],
                        )
                    ))

class PDFFunction:
    """superclass for all function types."""
    __PDFObject__ = True
    defaults = []
    required = ("FunctionType", "Domain")
    permitted = required+("Range",)
    def FunctionDict(self, **kw):
        d = {}
        for (name,val) in self.defaults:
            d[name] = val
        d.update(kw)
        for name in self.required:
            if name not in d:
                raise ValueError, "keyword argument %s missing" % name
        permitted = self.permitted
        for name in d.keys():
            if name not in permitted:
                raise ValueError, "bad annotation dictionary name %s" % name
        return PDFDictionary(d)

    def Dict(self, document):
        raise ValueError, "Dict undefined for virtual superclass PDFShading, must overload"
        # but usually
        #return self.FunctionDict(self, ...)

    def format(self, document):
        D = self.Dict(document)
        return D.format(document)

class PDFExponentialFunction(PDFFunction):
    defaults = PDFFunction.defaults + [("Domain", PDFArrayCompact((0.0, 1.0)))]
    required = PDFFunction.required + ("N",)
    permitted = PDFFunction.permitted + ("C0", "C1", "N")
    def __init__(self, C0, C1, N, **kw):
        self.C0 = C0
        self.C1 = C1
        self.N = N
        self.otherkw = kw
    def Dict(self, document):
        d = {}
        d.update(self.otherkw)
        d["FunctionType"] = 2
        d["C0"] = PDFArrayCompact(self.C0)
        d["C1"] = PDFArrayCompact(self.C1)
        d["N"] = self.N
        return self.FunctionDict(**d)

class PDFStitchingFunction(PDFFunction):
    required = PDFFunction.required + ("Functions", "Bounds", "Encode")
    permitted = PDFFunction.permitted + ("Functions", "Bounds", "Encode")
    def __init__(self, Functions, Bounds, Encode, **kw):
        self.Functions = Functions
        self.Bounds = Bounds
        self.Encode = Encode
        self.otherkw = kw
    def Dict(self, document):
        d = {}
        d.update(self.otherkw)
        d["FunctionType"] = 3
        d["Functions"] = PDFArray([document.Reference(x) for x in self.Functions])
        d["Bounds"] = PDFArray(self.Bounds)
        d["Encode"] = PDFArray(self.Encode)
        return self.FunctionDict(**d)

class PDFShading:
    """superclass for all shading types."""
    __PDFObject__ = True
    required = ("ShadingType", "ColorSpace")
    permitted = required+("Background", "BBox", "AntiAlias")
    def ShadingDict(self, **kw):
        d = {}
        d.update(kw)
        for name in self.required:
            if name not in d:
                raise ValueError, "keyword argument %s missing" % name
        permitted = self.permitted
        for name in d.keys():
            if name not in permitted:
                raise ValueError, "bad annotation dictionary name %s" % name
        return PDFDictionary(d)

    def Dict(self, document):
        raise ValueError, "Dict undefined for virtual superclass PDFShading, must overload"
        # but usually
        #return self.ShadingDict(self, ...)

    def format(self, document):
        D = self.Dict(document)
        return D.format(document)

class PDFFunctionShading(PDFShading):
    required = PDFShading.required + ("Function",)
    permitted = PDFShading.permitted + ("Domain", "Matrix", "Function")
    def __init__(self, Function, ColorSpace, **kw):
        self.Function = Function
        self.ColorSpace = ColorSpace
        self.otherkw = kw
    def Dict(self, document):
        d = {}
        d.update(self.otherkw)
        d["ShadingType"] = 1
        d["ColorSpace"] = PDFName(self.ColorSpace)
        d["Function"] = document.Reference(self.Function)
        return self.ShadingDict(**d)

class PDFAxialShading(PDFShading):
    required = PDFShading.required + ("Coords", "Function")
    permitted = PDFShading.permitted + (
            "Coords", "Domain", "Function", "Extend")
    def __init__(self, x0, y0, x1, y1, Function, ColorSpace, **kw):
        self.Coords = (x0, y0, x1, y1)
        self.Function = Function
        self.ColorSpace = ColorSpace
        self.otherkw = kw
    def Dict(self, document):
        d = {}
        d.update(self.otherkw)
        d["ShadingType"] = 2
        d["ColorSpace"] = PDFName(self.ColorSpace)
        d["Coords"] = PDFArrayCompact(self.Coords)
        d["Function"] = document.Reference(self.Function)
        return self.ShadingDict(**d)

class PDFRadialShading(PDFShading):
    required = PDFShading.required + ("Coords", "Function")
    permitted = PDFShading.permitted + (
            "Coords", "Domain", "Function", "Extend")
    def __init__(self, x0, y0, r0, x1, y1, r1, Function, ColorSpace, **kw):
        self.Coords = (x0, y0, r0, x1, y1, r1)
        self.Function = Function
        self.ColorSpace = ColorSpace
        self.otherkw = kw
    def Dict(self, document):
        d = {}
        d.update(self.otherkw)
        d["ShadingType"] = 3
        d["ColorSpace"] = PDFName(self.ColorSpace)
        d["Coords"] = PDFArrayCompact(self.Coords)
        d["Function"] = document.Reference(self.Function)
        return self.ShadingDict(**d)

if __name__=="__main__":
    print "There is no script interpretation for pdfdoc."
