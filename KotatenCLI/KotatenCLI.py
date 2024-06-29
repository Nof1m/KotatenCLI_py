import httpx, os, zipfile, tempfile, shutil


def obter_capitulos_por_idioma(manga_id, idioma):
    url =  "https://api.mangadex.org/"
    endpoint = f"manga/{manga_id}/feed"

    params = {
        "translatedLanguage[]": idioma
    }
    r = httpx.Client().get(f"{url}{endpoint}", params=params)

    if r.status_code == 200:
        capitulos = r.json()["data"]
        return capitulos
    else:
        print(f"Erro ao obter capítulos: {r.status_code}")
        return None

def salvar_capitulo(capitulo, diretorio, formato_imagem):
    imagens_id = capitulo['id']
    imagens_url = httpx.Client().get(f"https://api.mangadex.org/at-home/server/{imagens_id}").json()
    capitulo_number = capitulo['attributes']['chapter']

    capitulo_dir = os.path.join(diretorio, f"Capítulo {capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)

    temp_files = []

    print(f"Baixando capítulo {capitulo_number}")
    for page in imagens_url["chapter"]["data"]:
        r = httpx.Client().get(f"{imagens_url['baseUrl']}/data/{imagens_url['chapter']['hash']}/{page}")

        if formato_imagem == "cbz":
            temp_file = os.path.join(tempfile.gettempdir(), page)
            temp_files.append(temp_file)
            with open(temp_file, mode="wb") as f:
                f.write(r.content)
        else:  
            with open(f"{capitulo_dir}/{page}.{formato_imagem}", mode="wb") as f:
                f.write(r.content)

    if formato_imagem == "cbz":
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
                        formato_imagem = input("Escolha o formato das imagens ('png/jpg' ou 'cbz'): ")

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
