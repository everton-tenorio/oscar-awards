from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import re
import json
from environs import Env

env = Env()
env.read_env()
# Conectar ao MongoDB
cliente = MongoClient(env('MONGODB_URI'))


def obter_json_imdb(ano):
    url = f'https://www.imdb.com/event/ev0000003/{ano}/1?ref_=nmawd_ev_1'
    headers = {'Accept-Language': 'pt-BR'}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    script = soup.find_all('script')[39]
    pattern = r'IMDbReactWidgets\.NomineesWidget\.push\(\[.*?({.*?})\]\);'

    # Extracting the JSON using regex
    match = re.search(pattern, str(script), re.DOTALL)
    json_out = ''
    if match:
        json_out = json_content = match.group(1)

    return json.loads(json_out)


def extrair_resultados(awards):
    resultado_dict = {}
    resultado2_dict = {}

    for i, categoria in enumerate(awards[0]['categories']):
        nome_categoria = categoria['categoryName']
        vencedor_categoria = [nom for nom in categoria['nominations'] if nom.get('isWinner')]

        perdedores_list = []
        for x in categoria['nominations']:
            if x.get('isWinner') is False:
                nome_original = x['primaryNominees'][0].get('originalName', '')
                perdedores_categoria = x['primaryNominees'][0]['name']
                if nome_original:
                    perdedores_categoria = f"{x['primaryNominees'][0]['name']}, Nome original: {x['primaryNominees'][0].get('originalName', '')}"
                perdedores_list.append(perdedores_categoria)


        if vencedor_categoria:
            if vencedor_categoria[0]['primaryNominees'][0].get('originalName', ''):
                resultado_dict[nome_categoria] = f"{vencedor_categoria[0]['primaryNominees'][0]['name']}, Nome original: {vencedor_categoria[0]['primaryNominees'][0].get('originalName', '')}"
            else:
                resultado_dict[nome_categoria] = vencedor_categoria[0]['primaryNominees'][0]['name']

        if perdedores_categoria:
            resultado2_dict[nome_categoria] = perdedores_list

    return resultado_dict, resultado2_dict


def exibir_resultados(resultado_dict, resultado2_dict):
    #print(resultado_dict)
    #print(f'## Vencedores \n{pd.DataFrame(resultado_dict).to_markdown(index=False)}')
    print('\n\n\n')
    #print(resultado2_dict)
    #print(f'## Indicados - não venceram \n{pd.DataFrame(resultado2_dict).to_markdown(index=False)}')


if __name__ == "__main__":
    anos = [1929, 1930, 1931, 1932, 1934, 1935, 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    for ano in anos:
        json_imdb = obter_json_imdb(ano)
        awards = json_imdb["nomineesWidgetModel"]["eventEditionSummary"]["awards"]
        resultado_dict, resultado2_dict = extrair_resultados(awards)
        exibir_resultados(resultado_dict, resultado2_dict)


        # Mongo

        db_name = cliente['oscar_database']
        colecao_oscar = db_name['cerimonias_oscar']
        colecao_noindicados = db_name['cerimonias_oscar_noindicados']
	
	
        # Verificar se já existe uma cerimônia com o mesmo ano
        cerimonia_existente = colecao_oscar.find_one({"ano": ano})
        cerimonia_noindicados_existente = colecao_noindicados.find_one({"ano": ano})
	
        # Se já existir, apenas atualize as categorias
        if cerimonia_existente and cerimonia_noindicados_existente:
            colecao_oscar.update_one({"ano": ano}, {"$set": {"categorias": [resultado_dict]}})
            colecao_noindicados.update_one({"ano": ano}, {"$set": {"categorias": [resultado2_dict]}})
            print(f'Cerimônia para o ano {ano} atualizada com sucesso!')
            
        else:
            documento = {
                "ano": ano,
                "categorias": [resultado_dict]
            }
            
            documento_noindicados = {
                "ano": ano,
                "categorias": [resultado2_dict]
            }
            resultado = colecao_oscar.insert_one(documento)
            colecao_noindicados.insert_one(documento_noindicados)
	
	
        # Consultar documentos na coleção
        for cerimonia in colecao_oscar.find():
            print(f'Ano: {cerimonia["ano"]}')
            for categoria in cerimonia["categorias"]:
                print(json.dumps(categoria, indent=2, ensure_ascii=False))
                #print(f'\n\n\nCategoria: {categoria["Best Picture"]}')
            print('\n')
            
        
        for resultado in colecao_noindicados.find():
         	print(f'########### Resultado dos Não indicados')
         	print(f'Ano: {resultado["ano"]}')
         	for categoria in resultado["categorias"]:
                 print(json.dumps(categoria, indent=2, ensure_ascii=False))
	
        # Listar os IDs
        #ids = [resultado['_id'] for resultado in resultados]
        #print(f'IDS{ids}')
        
        # colecao_oscar.delete_one({'_id': ObjectId('655191372d244cda57cc59f5')})


