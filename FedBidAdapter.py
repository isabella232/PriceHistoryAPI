import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV
import datetime
import calendar

import logging

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('/var/tmp/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

monthLookup = {v.upper(): k for k,v in enumerate(calendar.month_abbr)}
# This are magic numbers that are simply based on the FedBid files
# as Laura presented them to me.
def findMonthFromAbbrev(a):
    try:
       m = monthLookup[a]
       return m
    except Error as e:
       logger.error('Caught error '+repr(e) + a)
       return 0

    # Need to test this month lookup stuff, right now
    # it is untested.
def getDictionaryFromFedBid(raw):
    try:
        d = datetime.date(int(raw.data[4].strip(' \t\n\r')),findMonthFromAbbrev(raw.data[5]),1)
        return { \
           UNITS : replaceUndumpableData(raw.data[37]) , \
           PRICE : replaceUndumpableData(raw.data[38]), \
           AGENCY : replaceUndumpableData(raw.data[3]) , \
           VENDOR : replaceUndumpableData(raw.data[29]) , \
           PSC : replaceUndumpableData(raw.data[13]) ,  \
           DESCR : replaceUndumpableData(raw.data[24]),   \
           LONGDESCR : replaceUndumpableData(raw.data[35]) , \
    # This needs to be put in a standard format and sorted properly.
           DATE : replaceUndumpableData(d.isoformat()), \
    # here begin some less-standard fields
           AWARDIDIDV : replaceUndumpableData(raw.data[19]) \
          }
    except:
        logger.error("don't know what went wrong here")
        return {}

# I think this will be better made into a pure function and
# perhaps actually separated into particular formats (to
# allow more override flexibility, like skipping the first row.)
def loadFedBidFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
    try:
        transactions = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            logger.info('FedBid reader opened:'+filename)
            n = len(transactions)
            i = 0
            notFoundFirstRecord = True
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                if (notFoundFirstRecord):
                    result = False
                    notFoundFirstRecord = False;
                else:
                    bt = BasicTransaction(adapter,tr)
                    if (pattern):
                        result = re.search(pattern, bt.getSearchMemento())
                    else:
                        result = True
                if (result):
                     if (bt.isValidTransaction()):
                         transactions.append(bt)
                         i = i + 1
                if (i+n) > LIMIT_NUM_MATCHING_TRANSACTIONS:
                    break
        logger.error('number returned:'+str(i))
        return transactions                
    except IOError as e:
         logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
         print "I/O error({0}): {1}".format(e.errno, e.strerror)
