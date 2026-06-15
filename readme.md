# 🎬 Video Music Downloader (VMD)

![Preview do App](img/preview.png)

---

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange.svg)
![Pytubefix](https://img.shields.io/badge/Engine-Pytubefix-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

O **Video Music Downloader** é uma aplicação desktop moderna e intuitiva desenvolvida em Python para o sistema operacional Windows. O objetivo principal do projeto é permitir o download rápido de vídeos (MP4) e áudios (MP3) do YouTube diretamente para o computador, sem a necessidade de instalar dependências complexas como o FFmpeg de forma manual.

---

## ✨ Funcionalidades

* **Download Híbrido:** Escolha entre baixar o vídeo completo em alta resolução (`.mp4`) ou apenas a faixa de áudio (`.mp3`).
* **Interface Moderna:** Desenvolvida com `CustomTkinter`, oferecendo suporte nativo ao Modo Escuro/Claro (Dark/Light Mode) baseado nas configurações do seu Windows.
* **Conversão Inteligente:** Extrai e renomeia o fluxo de áudio nativo sem engasgar e sem travar a interface.
* **Download em Segundo Plano (Threading):** A barra de progresso e a interface gráfica continuam fluidas e responsivas enquanto o download acontece em paralelo.
* **Diretório Inteligente:** Cria automaticamente uma pasta dedicada na sua Área de Trabalho (`Desktop/Downloads_Midia`) caso nenhuma pasta seja selecionada.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes bibliotecas do ecossistema Python:

* **[CustomTkinter](https://github.com/TomsOpts/CustomTkinter):** Evolução da biblioteca nativa Tkinter, utilizada para criar o design moderno e arredondado dos componentes visuais.
* **[Pytubefix](https://github.com/JuanBindez/pytubefix):** Biblioteca robusta e atualizada para interagir com a API do YouTube, substituindo com sucesso o antigo `pytube`.
* **Threading (Nativa):** Módulo utilizado para assincronismo, evitando o congelamento da janela durante o download de arquivos pesados.
* **Webbrowser (Nativa):** Utilizada para injetar o comportamento de link clicável que redireciona o usuário para o repositório do GitHub.

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o **Python 3.10 ou superior** instalado em sua máquina.

### Passo a Passo

1.  **Clonar o Repositório:**
    ```bash
    git clone [https://github.com/fhricardo/video-music-downloader.git](https://github.com/fhricardo/video-music-downloader.git)
    cd video-music-downloader
    ```

2.  **Criar e Ativar o Ambiente Virtual:**
    ```bash
    python -m venv .venv
    # No Windows (Prompt de Comando):
    .venv\Scripts\activate
    ```

3.  **Instalar as Dependências:**
    ```bash
    pip install customtkinter pytubefix
    ```

4.  **Iniciar a Aplicação:**
    ```bash
    python app.py
    ```

---

## 📦 Compilação para Executável (.exe)

Caso queira gerar um arquivo executável para rodar no Windows de forma portátil (sem precisar do terminal ou do Python instalado), você pode compilar o projeto utilizando o **PyInstaller**.

1. Instale o PyInstaller no seu ambiente virtual:
```bash
   pip install pyinstaller
```

2. Execute o comando de compilação apontando para o seu script e o seu ícone (`vmd-icon.ico`):
```bash
pyinstaller --noconsole --onefile --name="Video Music Downloader" --icon="vmd-icon.ico" app.py

```

3. Após o término do processo, a pasta **`dist/`** será criada e dentro dela estará o seu executável pronto para uso ou distribuição.

---

## 👨‍💻 Autor

Desenvolvido com 💻 por **Flávio Ricardo**.

* **GitHub:** [@fhricardo](https://github.com/fhricardo)
* **Projeto Original:** [Video Music Downloader](https://github.com/fhricardo/video-music-downloader)

---

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para obter mais detalhes.