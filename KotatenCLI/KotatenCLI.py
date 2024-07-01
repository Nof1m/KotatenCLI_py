import httpx, os, zipfile, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

def obter_capitulos_por_idioma(manga_id, idioma):
    url = "https://api.mangadex.org/"
    endpoint = f"manga/{manga_id}/feed"

    params = {
        "translatedLanguage[]": idioma,
        "order[chapter]": "asc",
        "limit": 500
    }
    r = httpx.Client().get(f"{url}{endpoint}", params=params)

    if r.status_code == 200:
        capitulos = r.json()["data"]
        return capitulos
    else:
        print(f"Erro ao obter capítulos: {r.status_code}")
        return None
    
def download_page(session, base_url, hash_, page, capitulo_dir):
    url = f"{base_url}/data/{hash_}/{page}"
    response = session.get(url)
    if response.status_code == 200:
        file_name = os.path.basename(page)
        with open(os.path.join(capitulo_dir, file_name), mode="wb") as f:
            f.write(response.content)
    else:
        print(f"Erro ao baixar página {page}, status {response.status_code}")

def salvar_capitulo(capitulo, diretorio, formato_imagem):
    imagens_id = capitulo['id']
    imagens_url = httpx.get(f"https://api.mangadex.org/at-home/server/{imagens_id}").json()
    capitulo_number = capitulo['attributes']['chapter']

    capitulo_dir = os.path.join(diretorio, f"Capítulo {capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)

    print(f"Baixando capítulo {capitulo_number}")

    base_url = imagens_url['baseUrl']
    hash_ = imagens_url['chapter']['hash']
    pages = imagens_url['chapter']['data']

    with ThreadPoolExecutor(max_workers=5) as executor:
        session = httpx.Client()
        futures = []
        for page in pages:
            futures.append(executor.submit(download_page, session, base_url, hash_, page, capitulo_dir))
        
        for future in as_completed(futures):
            future.result()

    if formato_imagem == "cbz":
        temp_files = [os.path.join(capitulo_dir, page) for page in os.listdir(capitulo_dir)]
        criar_cbz(temp_files, capitulo_dir)
        for temp_file in temp_files:
            os.remove(temp_file)
        shutil.rmtree(capitulo_dir)

def criar_cbz(temp_files, capitulo_dir):
    with zipfile.ZipFile(f"{capitulo_dir}.cbz", 'w') as cbz_file:
        for temp_file in temp_files:
            filename = os.path.basename(temp_file)
            cbz_file.write(temp_file, arcname=filename)

    print(f"CBZ criado: {capitulo_dir}.cbz")

def main():
    pesquisa = input("Bem-vindo(a)! Digite o título do mangá que você está procurando: ")
    base_url = "https://api.mangadex.org/"

    r = httpx.Client().get(
        f"{base_url}/manga",
        params={"title": pesquisa}
    )

    if r.status_code == 200:
        mangas = r.json()["data"]

        if mangas:
            for i, manga in enumerate(mangas):
                print(f"{i} - {manga['attributes']['title']['en']}")

            while True:
                try:
                    escolha = int(input("Escolha o número do mangá que você quer baixar: "))
                    chosen_manga = mangas[escolha]
                    manga_id = chosen_manga['id']

                    idioma = input("Digite o idioma dos capítulos que você quer baixar (ex: 'en' para inglês): ")

                    capitulos = obter_capitulos_por_idioma(manga_id, idioma)

                    if capitulos:
                        diretorio = input("Digite o caminho completo do diretório onde deseja salvar os capítulos: ")
                        formato_imagem = input("Escolha o formato das imagens ('jpg' ou 'cbz'): ")

                        for capitulo in capitulos:
                            salvar_capitulo(capitulo, diretorio, formato_imagem)

                        print("Download concluído! Obrigado por usar Kotaten :D ")
                    break
                except (IndexError, ValueError):
                    print("Escolha inválida. Por favor, escolha um número válido.")
        else:
            print("Nenhum mangá encontrado com o título fornecido.")
    else:
        print(f"Erro ao fazer requisição: {r.status_code}")

if __name__ == "__main__":
    main()

print = input("Aperte Enter para fechar... ")
