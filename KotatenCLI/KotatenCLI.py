import httpx, os
from time import sleep

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

def salvar_capitulo(capitulo, diretorio):
    imagens_id = capitulo['id']

    imagens_url = httpx.Client().get(f"https://api.mangadex.org/at-home/server/{imagens_id}")
    imagens_url = imagens_url.json()

    capitulo_number = capitulo['attributes']['chapter']

    capitulo_dir = os.path.join(diretorio, f"Capítulo {capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)


    print(f"Baixando capitulo {capitulo_number}")
    for page in imagens_url["chapter"]["data"]:
      
        r = httpx.Client().get(f"{imagens_url['baseUrl']}/data/{imagens_url['chapter']['hash']}/{page}")

        with open(f"{capitulo_dir}/{page}", mode="wb") as f:
            f.write(r.content)

def main():
    pesquisa = input("Bem-vindo(a)! digite o título do mangá que você está procurando: ")
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
                    escolha = int(input("Escolha o número do mangá que você que deseja: "))
                    chosen_manga = mangas[escolha]
                    manga_id = chosen_manga['id']
                    
                    idioma = input("Digite o idioma dos capítulos que você quer baixar (ex: 'en' para inglês): ")
                    
                    capitulos = obter_capitulos_por_idioma(manga_id, idioma)
                    
                    if capitulos:
                        diretorio = input("Digite o caminho completo do diretório onde deseja salvar os capítulos: ")  

                        for capitulo in capitulos:
                            salvar_capitulo(capitulo, diretorio)
                        
                        print("Download concluído!, Obrigado por usar Kotaten :D ")
                    break
                except (IndexError, ValueError):
                    print("Escolha inválida. Por favor, escolha um número válido.")
        else:
            print("Nenhum mangá encontrado com o título fornecido.")
    else:
        print(f"Erro ao fazer requisição: {r.status_code}")

if __name__ == "__main__":
    main()

sleep(10)