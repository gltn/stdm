import os
from typing import List
from qgis.core import (
    QgsPrintLayout,
    QgsProject,
    QgsReadWriteContext
   )
from PyQt5.QtXml import QDomDocument

from PyQt5.QtCore import (
    QFile,
    QIODevice
)

TMPL_DIR = "D:/Home/Lab/Python/tempconvert/templates/"

class TemplateConverter:
    def __init__(self, templates: List[str]):
        self.templates = templates
        self.dom_documents = self.make_dom_documents(self.templates)
        self.dom_docs_v2 = self.find_dom_docs_v2(self.dom_documents)
        
    def print_elements(self):
        print('print_elements...')
        doc_elem = self.dom_docs_v2[0].documentElement()
        node = doc_elem.firstChild()
        while not node.isNull():
            dom_elem = node.toElement()
            print('Dom Elem: ',dom_elem)
            if not dom_elem.isNull():
                print(dom_elem.tagName())
            node = node.nextSibling()
                
    def make_dom_documents(self, templates: List[str]) -> List[QDomDocument]:
        print('make_dom_document ...')
        dom_docs = []  #type: List[QDomDocument]
        for template in templates:
            dom_doc = self.file_to_dom_document(TMPL_DIR+template)
            if dom_doc:
                dom_docs.append(dom_doc)
        return dom_docs

    def file_to_dom_document(self, filename: str) -> QDomDocument:
        print('file_to_dom_document ...', filename)
        xmlfile = QFile(filename)
        if not xmlfile.open(QIODevice.ReadOnly):
            return None

        dom_doc = QDomDocument()
        dom_doc.setContent(xmlfile)
        return dom_doc

    def find_dom_docs_v2(self, dom_docs: List[QDomDocument]) -> List[QDomDocument]:
        print('filter_dom_docs_v2 ...')
        dom_docs_v2 = [] # type: List[QDomDocument]
        for dom_doc in dom_docs:
            dom_list = dom_doc.elementsByTagName('Composer')
            print(dom_list.count())
            if dom_list.count() > 0:
                dom_docs_v2.append(dom_doc)
            else:
                print('Empty dom list')
        return dom_docs_v2

def get_templates(tmpl_folder: str) -> List[str]:
    print("Read templates in folder......")
    files = os.listdir(tmpl_folder)
    templates = []
    for file in files:
        if file.endswith('.sdt'):
            templates.append(file)
    return templates

def run_script():
    templates = get_templates(TMPL_DIR)
    tmp_conv = TemplateConverter(templates)
    qgs_layout = QgsPrintLayout(QgsProject())
    context = QgsReadWriteContext()
    #tmp_conv.print_elements()
    dd = tmp_conv.dom_docs_v2[0]
    print(dd)
    items = qgs_layout.loadFromTemplate(dd, context)
    if items:
        print('Items found!')
    #print(tmp_conv.dom_docs_v2)


if __name__ == "__main__":
    templates = get_templates('templates')
    tmp_conv = TemplateConverter(templates)
    qgs_layout = QgsPrintLayout()
    items = qgs_layout.loadFromTemplate(tmp_conv.dom_doc_v2[0])
    print(items)
    print(tmp_conv.dom_docs_v2)


