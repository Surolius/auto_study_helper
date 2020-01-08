'''
1. Load all PDF
1.1 Create Titles
1.2 Rework Titles
2. Split slides
3. Randomizw order of slides
4. Merge to one pdf
'''
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import random
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
import pandas as pd
import numpy as np

def merge_pdfs(paths, output,folder):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(os.path.join(folder,path),strict = False)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)

# def auto_create_titles(path):
#     # TODO: implement auto version


def get_page_size(path):
    pdf_reader = PdfFileReader(path)
    height = pdf_reader.getPage(0).mediaBox.upperRight[1]
    width = pdf_reader.getPage(0).mediaBox.lowerRight[0]
    # print((height,width))
    return height, width


def create_titles(name,header):
    height, width = get_page_size('format.pdf')
    registerFont(TTFont('Arial', 'ARIAL.ttf'))
    c = canvas.Canvas(os.path.join('headers',name +".pdf"),pagesize=(width,height))
    c.setFont("Arial", 30)
    c.drawCentredString(width/2, height/2, header)
    c.save()


def filter_pages(path,filter_definition,filter_wrong):
    df = pd.read_excel(path)
    df = df.values
    index = 0
    if filter_definition == 1 and filter_wrong == 0:
        index = np.where(df[:,3] == 1)
    elif filter_definition  == 0 and filter_wrong == 1:
        index = np.where(df[:,4] == 1)
    elif filter_definition  == 1 and filter_wrong !=0:
        index = np.where((df[:,3] ==1 ) & (df[:,4] >= filter_wrong))
    elif filter_definition  == 0 and filter_wrong == 0:
        index = np.where(df != 'test')
    return index[0]


def merge_total(path, path_headers,output,randomize,index):
    pdf = PdfFileReader(path)
    headers = PdfFileReader(path_headers)
    pdf_writer = PdfFileWriter()
    number_of_pages = headers.getNumPages()
    pages_list = list(range(number_of_pages))
    if len(index) != 0:
        pages_list = index
    print(pages_list)
    if randomize == 1:
        random.shuffle(pages_list)
    # print(pages_list)
    for page in pages_list:
        pdf_writer.addPage(headers.getPage(page))
        pdf_writer.addPage(pdf.getPage(page))
    with open(output, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

def create_pdfs_with_titles(path):
    df = pd.read_excel(path)
    headers = df['headers'].tolist()
    name = 0
    for header in headers:
        print(header)
        create_titles(str(name),str(header))
        name+=1

def files_in_folder(folder):
    paths = os.listdir(folder)
    paths_filtered = [file for file in paths if file[-4:] == '.pdf' ]
    paths_filtered.sort()
    print(paths_filtered)
    return paths_filtered
def sort_numerical_files(folder):
    paths = os.listdir(folder)
    paths_filtered = [file for file in paths if file[-4:] == '.pdf']
    numbers = [int(file[:-4])for file in paths_filtered]
    numbers.sort()
    print(numbers)
    path_sorted = [str(num) +'.pdf' for num in numbers]
    return path_sorted

if __name__ == '__main__':
    paths_filtered = files_in_folder("study_pdfs")
    create_pdfs_with_titles('headers.xlsx')
    headers = sort_numerical_files('headers')
    merge_pdfs(headers,'headers.pdf','headers')
    merge_pdfs(paths_filtered,'subjects.pdf',"study_pdfs")
    index = []
    index = filter_pages(path = 'headers.xlsx',filter_definition=1,filter_wrong=3)
    merge_total('subjects.pdf','headers.pdf','cards.pdf',1,index)