import requests
import bs4
from urllib.parse import urljoin
import string
import random
import os

url_ribuni = 'http://ribuni.uni.edu.ni/view/divisions/sch=5Fche/'

directorio_base = os.path.join(os.getcwd(), 'docs')

# Contiene los años que servirán como directorios para guardar los documentos.
only_anios: list[str] = []

# Obtiene en texto plano todo el contenido HTML del enlace establecido.
def get_soup(url: str) -> bs4.BeautifulSoup | None:
    response = requests.get(url)
    soup = None

    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'lxml')

    return soup

# Obtiene el enlace completo para poder navegar.
def complete_url(url: str) -> str:
    return urljoin(url_ribuni, url)

# Obtiene una lista que contiene los links de los años para navegar posteriormente.
def get_links_anios(soup: bs4.BeautifulSoup) -> list:
    li_tags = soup.find_all('li')
    url_list = []
    
    for item in li_tags:
        a_tag = item.find('a')

        if type(a_tag) == type(None):
            continue

        link_anio: str = a_tag.get('href')
        is_anio: bool = link_anio.startswith('2')

        if not is_anio:
            continue

        only_anios.append(link_anio.split('.')[0])

        # Dado que link_anio sólo contiene la última parte de la URL, se debe completar.
        url_list.append(complete_url(link_anio))
    
    return url_list

# Obtiene los enlaces para cada documento que se subió en determinado año
def get_links_documents(soup: bs4.BeautifulSoup):
    p_tags = soup.find_all('p')
    links_documents = []

    for item in p_tags:
        a_tag = item.find('a')

        if type(a_tag) == type(None):
            continue

        link_document: str = a_tag.get('href')
        links_documents.append(link_document)

    return links_documents

# Obtiene el link para descargar el PDF
def get_link_pdf(soup: bs4.BeautifulSoup) -> str | None:
    td_tags = soup.find_all('td')

    for item in td_tags:
        a_tag = item.find('a')

        if type(a_tag) == type(None):
            continue

        link_pdf: str = a_tag.get('href')
        is_pdf: bool = link_pdf.endswith('.pdf') or link_pdf.endswith('.PDF')

        if is_pdf:
            return link_pdf

# Descarga el PDF en caso de que lo haya encontrado.        
def save_in_disk(url: str, anio: str | int):
    if type(url) == type(None):
        print(f'No se encontró una url válida para un PDF del año: {anio}')
        return
    
    response = requests.get(url)
    
    random_name = generate_random_name()

    ruta = os.path.join(directorio_base, anio)

    # Verificar si el directorio existe
    if not os.path.exists(ruta):
        # Si no existe, crearlo
        os.makedirs(ruta)

    doc_uri = os.path.join(ruta, f'{random_name}.pdf')
    
    with open(doc_uri, 'wb') as file:
        file.write(response.content)
        print(f'Se guardó existosamente el documento para el año: {anio}')
        
# Para evitar el reemplazo de los ficheros, se generará un nombre aleatorio de caracteres.
def generate_random_name(length = 10):
    caracteres = string.ascii_letters + string.digits
    random_name = ''.join(random.choice(caracteres) for _ in range(length))
    return random_name

if __name__ == '__main__':
    soup = get_soup(url_ribuni)
    links_anios = get_links_anios(soup)

    position = 0
    
    if position > len(only_anios) - 1:
        print(f'Aún no existe la posición {position} en el arreglo: {only_anios}')
        exit()

    for anio in links_anios:
        document_soup = get_soup(anio)
        links_documents = get_links_documents(document_soup)

        for document in links_documents:
            pdf_soup = get_soup(document)
            pdf_link = get_link_pdf(pdf_soup)
            save_in_disk(pdf_link, only_anios[position])

        position = position + 1