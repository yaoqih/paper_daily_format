import fitz
import os
from pdf2image import convert_from_bytes
import shutil
from tqdm import tqdm
pdf_save_path='./paper_download/'
labeled_save_path='./paper_labeled/'
images_data=save_path='./images_data/'
def pdf2image3(pdf_path):
    #使用pdf2image将pdf转化为图片
    images = convert_from_bytes(open(pdf_save_path+pdf_path, 'rb').read())
    pic_save_path=pdf_save_path+pdf_path.replace('.pdf','')+'/'
    if not os.path.exists(pic_save_path):
        os.mkdir(pic_save_path)
    for image in images:
        if not os.path.exists(pic_save_path + f'img_{images.index(image)}.png'):
            image.save(pic_save_path + f'img_{images.index(image)}.png', 'PNG')

def extract_images_from_pdf(pdf_path):
    #传统方法将pdf中的图片导出来
    pdf_document = fitz.open(pdf_save_path+pdf_path)
    pic_save_path=pdf_save_path+pdf_path.replace('.pdf','')+'/'
    if not os.path.exists(pic_save_path):
        os.mkdir(pic_save_path)
    for current_page in range(len(pdf_document)):
        for image in pdf_document.get_page_images(current_page):
            xref = image[0]
            pix = fitz.Pixmap(pdf_document, xref)
            if pix.n < 5:        # this is GRAY or RGB
                pix.save(pic_save_path+"page%s-%s.png" % (current_page, xref))
            else:                # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save(pic_save_path+"page%s-%s.png" % (current_page, xref))
                pix1 = None
            pix = None
    pdf_document.close()
def extract_from_download(save_path='./images_data/'):
    #从标注好的文件夹中把图片和标注导出来
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    index_count=0
    for path in os.listdir(labeled_save_path):
        path=labeled_save_path+path
        if os.path.isdir(path):
            path+='/'
            for file in os.listdir(path):
                if file.endswith('.png'):
                    shutil.copy(path+file,save_path+f'img_{index_count}.png')
                    if os.path.exists(path+file.replace('.png','.json')):
                        shutil.copy(path+file.replace('.png','.json'),save_path+f'img_{index_count}.json')
                    index_count+=1
def extract_img(save_path='./labels/'):
    #将一个文件夹中的图片导出来
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    for img in os.listdir(images_data):
        if img.endswith('.png'):
            shutil.copy(images_data+img,save_path+img)
# pdf_list=tqdm(os.listdir(pdf_save_path))
# for pdf in pdf_list:
#     if pdf.endswith('.pdf'):
#         pdf2image3(pdf)
extract_from_download()
extract_img()