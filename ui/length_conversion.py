"""
/***************************************************************************
Name                 : Length Conversion Dialog
Description          : Dialog that enables the current logged in user to
                        change the password
Date                 : 28/August/2018 
copyright            : (C) 2015 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from ui_length_conversion import Ui_LengthConversion

from stdm.ui.conversions import (
        Conversion,
        Ropani,
        Bigaha
        )

from PyQt4.QtGui import QDialog

class LengthConversion(QDialog, Ui_LengthConversion):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.convert = Conversion()

        self.conv_funcs = {
                (0,0):self.sqmtr_to_sqmtr,
                (0,1):self.sqmtr_to_sqft,
                (0,2):self.sqmtr_to_ropani,
                (0,3):self.sqmtr_to_bigaha,
                (1,0):self.sqft_to_sqmtr,
                (1,1):self.sqft_to_sqft,
                (1,2):self.sqft_to_ropani,
                (1,3):self.sqft_to_bigaha,
                (2,0):self.ropani_to_sqmtr,
                (2,1):self.ropani_to_sqft,
                (2,2):self.ropani_to_ropani,
                (2,3):self.ropani_to_bigaha,
                (3,0):self.bigaha_to_sqmtr,
                (3,1):self.bigaha_to_sqft,
                (3,2):self.bigaha_to_ropani,
                (3,3):self.bigaha_to_bigaha
                }
                
        self.initGui()            
        
    def initGui(self):
        '''
        Initialize GUI
        '''
        self.swFrom.setCurrentIndex(0)
        self.swTo.setCurrentIndex(0)

        pages = ['Square Meters', 'Square Feet', 'Ropani', 'Bigaha']
        self.cbFrom.currentIndexChanged.connect(self.change_from)
        self.cbFrom.insertItems(0, pages)
        self.cbTo.currentIndexChanged.connect(self.change_to)
        self.cbTo.insertItems(0, pages)

        self.btnClose.clicked.connect(self.close)

        self.edtSqMtr.setMaximum(999999999)
        self.edtSqMtr2.setMaximum(999999999)
        self.edtSqMtr.valueChanged.connect(self.conversion_func_router)

        self.edtSqFt.setMaximum(999999999)
        self.edtSqFt2.setMaximum(999999999)
        self.edtSqFt.valueChanged.connect(self.conversion_func_router)

        self.edtRopani.valueChanged.connect(self.conversion_func_router)
        self.edtRopani.setMaximum(999999999)
        self.edtAana.valueChanged.connect(self.conversion_func_router)
        self.edtAana.setMaximum(999999999)
        self.edtPaisa.valueChanged.connect(self.conversion_func_router)
        self.edtPaisa.setMaximum(999999999)
        self.edtDaam.valueChanged.connect(self.conversion_func_router)
        self.edtDaam.setMaximum(999999999)

        self.edtBigaha.valueChanged.connect(self.conversion_func_router)
        self.edtBigaha.setMaximum(999999999)
        self.edtKattha.valueChanged.connect(self.conversion_func_router)
        self.edtKattha.setMaximum(999999999)
        self.edtDhur.valueChanged.connect(self.conversion_func_router)
        self.edtDhur.setMaximum(999999999)
        self.edtKanuwa.valueChanged.connect(self.conversion_func_router)
        self.edtKanuwa.setMaximum(999999999)


    def change_from(self, index):
        self.swFrom.setCurrentIndex(index)

    def change_to(self, index):
        self.swTo.setCurrentIndex(index)
        self.conversion_func_router()

    def close(self):
        self.done(1)

    def conversion_func_router(self):
        self.conv_funcs[(self.cbFrom.currentIndex(), self.cbTo.currentIndex())]()

    def sqmtr_to_sqmtr(self):
        self.edtSqMtr2.setValue(self.edtSqMtr.value())

    def sqmtr_to_sqft(self):
        self.edtSqFt2.setValue(self.convert.sqmtr_to_sqft(self.edtSqMtr.value()))

    def to_ropani(self, func, value):
        ropani = func(value)
        self.edtRopani2.setValue(ropani.ropani)
        self.edtAana2.setValue(ropani.aana)
        self.edtPaisa2.setValue(ropani.paisa)
        self.edtDaam2.setValue(ropani.daam)

    def to_bigaha(self, func, value):
        big = func(value)
        self.edtBigaha2.setValue(big.bigaha)
        self.edtKattha2.setValue(big.kattha)
        self.edtDhur2.setValue(big.dhur)
        self.edtKanuwa2.setValue(big.kanuwa)

    def make_ropani(self):
        ropani = Ropani()
        ropani.ropani = self.edtRopani.value()
        ropani.aana = self.edtAana.value()
        ropani.paisa = self.edtPaisa.value()
        ropani.daam = self.edtDaam.value()
        return ropani
        
    def make_bigaha(self):
        bigaha = Bigaha()
        bigaha.bigaha = self.edtBigaha.value()
        bigaha.kattha = self.edtKattha.value()
        bigaha.dhur = self.edtDhur.value()
        bigaha.kanuwa = self.edtKanuwa.value()
        return bigaha

    def sqmtr_to_ropani(self):
        self.to_ropani(self.convert.sqmtr_to_ropani, self.edtSqMtr.value())

    def sqmtr_to_bigaha(self):
        self.to_bigaha(self.convert.sqmtr_to_bigaha, self.edtSqMtr.value())

    #  === square feet conversions ===

    def sqft_to_sqft(self):
        self.edtSqFt2.setValue(self.edtSqFt.value())

    def sqft_to_sqmtr(self):
        self.edtSqMtr2.setValue(self.convert.sqft_to_sqmtr(self.edtSqFt.value()))

    def sqft_to_ropani(self):
        self.to_ropani(self.convert.sqft_to_ropani, self.edtSqFt.value())

    def sqft_to_bigaha(self):
        self.to_bigaha(self.convert.sqft_to_bigaha, self.edtSqFt.value())

    # === ropani conversions ===

    def ropani_to_sqmtr(self):
        ropani = self.make_ropani()
        self.edtSqMtr2.setValue(self.convert.ropani_to_sqmtr(ropani))

    def ropani_to_sqft(self):
        ropani = self.make_ropani()
        self.edtSqFt2.setValue(self.convert.ropani_to_sqft(ropani))

    def ropani_to_ropani(self):
        ropani = self.make_ropani()
        self.edtRopani2.setValue(ropani.ropani)
        self.edtAana2.setValue(ropani.aana)
        self.edtPaisa2.setValue(ropani.paisa)
        self.edtDaam2.setValue(ropani.daam)

    def ropani_to_bigaha(self):
        ropani = self.make_ropani()
        sqmtr = self.convert.ropani_to_sqmtr(ropani)
        self.to_bigaha(self.convert.sqmtr_to_bigaha, sqmtr)

    # *=== bigaha conversions ===

    def bigaha_to_sqmtr(self):
        bigaha = self.make_bigaha()
        self.edtSqMtr2.setValue(self.convert.bigaha_to_sqmtr(bigaha))

    def bigaha_to_sqft(self):
        bigaha = self.make_bigaha()
        self.edtSqFt2.setValue(self.convert.bigaha_to_sqft(bigaha))

    def bigaha_to_ropani(self):
        bigaha = self.make_bigaha()
        sqmtr = self.convert.bigaha_to_sqmtr(bigaha)
        self.to_ropani(self.convert.sqmtr_to_ropani, sqmtr)

    def bigaha_to_bigaha(self):
        bigaha = self.make_bigaha()
        self.edtBigaha2.setValue(bigaha.bigaha)
        self.edtKattha2.setValue(bigaha.kattha)
        self.edtDhur2.setValue(bigaha.dhur)
        self.edtKanuwa2.setValue(bigaha.kanuwa)

    

    
        
        
        
