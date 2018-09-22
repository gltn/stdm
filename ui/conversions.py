# class conversions
from collections import OrderedDict
import math

#import sys
#sys.path.append('..')

from stdm.utils.conversion_tables import (
        ropani_conv_table,
        bigaha_conv_table,
        ropani_sqft_table,
        bigaha_sqft_table
        )

class Ropani(object):
    def __init__(self):
        self.ropani = 0.0
        self.aana = 0.0
        self.paisa = 0.0
        self.daam = 0.0
    def __str__(self):
        return 'Ropani(Ropani:'+str(self.ropani)+';Aana:'+str(self.aana)+';Paisa:'+str(self.paisa)+';Daam:'+str(self.daam)+')'

class Bigaha(object):
    def __init__(self):
        self.bigaha = 0.0
        self.kattha = 0.0
        self.dhur = 0.0
        self.kanuwa = 0.0
    def __str__(self):
        return 'Bigaha(Bigaha:'+str(self.bigaha)+';Kattha:'+str(self.kattha)+';Dhur:'+str(self.dhur)+';Kanuwa:'+str(self.kanuwa)+')'

class Conversion(object):
    registered_conversion = OrderedDict()
    MTR_TO_SQFEET = 10.7639
    SQFEET_TO_SQMTR = 0.092903

    def __init__(self):
        self.results = OrderedDict()

    @classmethod
    def register(cls):
        Conversion.registered_conversion[cls.CONVERT_INFO] = cls

    def to_ropani(self, value, conv_table):
        self.results.clear()
        self._intl_to_local(value, 0, conv_table, self.results) 
        rop = Ropani()
        rop.ropani = self.results['ropani']
        rop.aana = self.results['aana']
        rop.paisa = self.results['paisa']
        rop.daam = self.results['daam']
        return rop

    def to_bigaha(self, value, conv_table):
        self.results.clear()
        self._intl_to_local(value, 0, conv_table, self.results) 
        big = Bigaha()
        big.bigaha = self.results['bigaha']
        big.kattha = self.results['kattha']
        big.dhur = self.results['dhur']
        big.kanuwa = self.results['kanuwa'] 
        return big

    def ropani_to_local(self, ropani, conv_table):
        results = 0.0
        results = conv_table[0][1] * ropani.ropani + \
                  conv_table[1][1] * ropani.aana + \
                  conv_table[2][1] * ropani.paisa + \
                  conv_table[3][1] * ropani.daam
        return results

    def bigaha_to_local(self, bigaha, conv_table):
        results = 0.0
        results = conv_table[0][1] * bigaha.bigaha + \
                  conv_table[1][1] * bigaha.kattha + \
                  conv_table[2][1] * bigaha.dhur + \
                  conv_table[3][1] * bigaha.kanuwa
        return results

    def _intl_to_local(self, sqmtr, index, conv_table, results):
        """
        """
        if index == len(conv_table):return results

        k = conv_table[index][0]
        v = conv_table[index][1]

        index += 1
        ans = 0
        remain = sqmtr

        if sqmtr > v:
            ans = math.floor(sqmtr/v)
            remain = sqmtr - (ans * v)

        results[k] = ans
        self._intl_to_local(round(remain, 2), index, conv_table, results)

    def sqmtr_to_sqft(self, sqmtr):
        """
        square meter to square feet conversion function
        :param sqmtr: decimal
        :rtype: decimal
        """
        return sqmtr * Conversion.MTR_TO_SQFEET

    def sqmtr_to_ropani(self, sqmtr):
        """
        square meter to ropani conversion function
        :param sqmtr: decimal
        :rtype: Ropani
        """
        ropani = self.to_ropani(sqmtr, ropani_conv_table)
        return ropani

    def sqmtr_to_bigaha(self, sqmtr):
        big = self.to_bigaha(sqmtr, bigaha_conv_table)
        return big

    def sqft_to_sqmtr(self, sqft):
        return sqft * Conversion.SQFEET_TO_SQMTR

    def sqft_to_ropani(self, sqft):
        ropani = self.to_ropani(sqft, ropani_sqft_table)
        return ropani

    def sqft_to_bigaha(self, sqft):
        big = self.to_bigaha(sqft, bigaha_sqft_table)
        return big

    def ropani_to_sqmtr(self, ropani):
        sqmtr = self.ropani_to_local(ropani, ropani_conv_table)
        return sqmtr

    def ropani_to_sqft(self, ropani):
        sqft = self.ropani_to_local(ropani, ropani_sqft_table)
        return sqft

    def bigaha_to_sqmtr(self, bigaha):
        sqmtr = self.bigaha_to_local(bigaha, bigaha_conv_table)
        return sqmtr

    def bigaha_to_sqft(self, bigaha):
        sqft = self.bigaha_to_local(bigaha, bigaha_sqft_table)
        return sqft
