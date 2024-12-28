import httpx, os, zipfile, shutil
from concurrent.futures import ThreadPoolExecutor

def obter_capitulos_por_idioma(manga_id, idioma):
    url = "https://api.mangadex.org/"
    endpoint = f"manga/{manga_id}/feed"

    params = {
        "translatedLanguage[]": idioma,
        "order[chapter]": "asc",
        "limit": 500
    }
    r = httpx.get(f"{url}{endpoint}", params=params)

    if r.status_code == 200:
        capitulos = r.json()["data"]
        return capitulos
    else:
        print(f"Erro ao obter capítulos: {r.status_code}")
        return None

def download_page(session, base_url, hash_, page, capitulo_dir, max_retries=5):
    url = f"{base_url}/data/{hash_}/{page}"
    retries = 0
    while retries < max_retries:
        response = session.get(url)
        if response.status_code == 200:
            file_name = os.path.basename(page)
            with open(os.path.join(capitulo_dir, file_name), mode="wb") as f:
                f.write(response.content)
            return True
        else:
            retries += 1
            print(f"Erro ao baixar página {page}, tentativa {retries}, status {response.status_code}")
    print(f"Falha ao baixar página {page} após {max_retries} tentativas.")
    return False

def salvar_capitulo(capitulo, diretorio, formato_imagem):
    imagens_id = capitulo['id']
    imagens_url = httpx.get(f"https://api.mangadex.org/at-home/server/{imagens_id}").json()
    capitulo_number = capitulo['attributes']['chapter']
    volume = capitulo['attributes'].get('volume', 'None')

    volume_dir = os.path.join(diretorio, f"Volume {volume}")
    os.makedirs(volume_dir, exist_ok=True)
    capitulo_dir = os.path.join(volume_dir, f"Capítulo {capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)

    print(f"Baixando capítulo {capitulo_number}")

    base_url = imagens_url['baseUrl']
    hash_ = imagens_url['chapter']['hash']
    pages = imagens_url['chapter']['data']

    temp_files = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        session = httpx.Client()
        future_to_page = {
            executor.submit(download_page, session, base_url, hash_, page, capitulo_dir): page for page in pages
        }
        for future in future_to_page:
            page = future_to_page[future]
            if not future.result():
                print(f"Falha permanente no download da página {page}. Verifique a conexão ou o servidor.")

    if formato_imagem == "cbz":
        criar_cbz(capitulo_dir)
        shutil.rmtree(capitulo_dir)

def criar_cbz(capitulo_dir):
    cbz_path = f"{capitulo_dir}.cbz"
    with zipfile.ZipFile(cbz_path, 'w') as cbz_file:
        for root, _, files in os.walk(capitulo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, capitulo_dir)
                cbz_file.write(file_path, arcname)
    print(f"CBZ criado: {cbz_path}")

def main():
    pesquisa = input("Bem-vindo(a)! Digite o título do mangá que você está procurando: ")
    base_url = "https://api.mangadex.org/"

    r = httpx.get(
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

input("Aperte Enter para fechar... ")
