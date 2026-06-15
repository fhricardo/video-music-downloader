import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pytubefix import YouTube
import threading
import webbrowser  # Importado no topo para boas práticas

# Configurações de tema e aparência
ctk.set_appearance_mode("System")  # Segue o tema do Windows (Light ou Dark)
ctk.set_default_color_theme("blue")  # Tema azul moderno


class VideoMusicDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO DA JANELA PRINCIPAL ---
        self.title("Video Music Downloader")
        self.geometry("550x380")
        self.resizable(False, False)

        # Suporte a ícone personalizado
        if os.path.exists("vmd-icon.ico"):
            self.iconbitmap("vmd-icon.ico")

        # --- CRIAÇÃO DO MENU SUPERIOR (Menu de Barras) ---
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Adiciona o menu "Ajuda" com a opção "Sobre"
        self.menu_ajuda = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_ajuda.add_command(
            label="Sobre o Programa", command=self.abrir_janela_sobre
        )
        self.menu_bar.add_cascade(label="Ajuda", menu=self.menu_ajuda)

        # Pasta padrão automática
        self.pasta_padrao = os.path.join(
            os.path.expanduser("~"), "Desktop", "Downloads_Midia"
        )
        if not os.path.exists(self.pasta_padrao):
            os.makedirs(self.pasta_padrao)

        # Variáveis de controle
        self.url_var = ctk.StringVar()
        self.pasta_var = ctk.StringVar(value=self.pasta_padrao)
        self.formato_var = ctk.StringVar(value="MP4 (Vídeo + Áudio)")

        self.criar_interface()

    def criar_interface(self):
        # Campo: URL do YouTube
        self.lbl_url = ctk.CTkLabel(
            self, text="URL do YouTube:", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_url.pack(anchor="w", padx=35, pady=(5, 2))

        self.entry_url = ctk.CTkEntry(
            self,
            textvariable=self.url_var,
            width=480,
            placeholder_text="Cole o link do vídeo aqui...",
        )
        self.entry_url.pack(padx=35, pady=5)

        # Campo: Pasta de Destino
        self.lbl_pasta = ctk.CTkLabel(
            self, text="Pasta de Destino:", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_pasta.pack(anchor="w", padx=35, pady=(10, 2))

        frame_pasta = ctk.CTkFrame(self, fg_color="transparent")
        frame_pasta.pack(fill="x", padx=35, pady=5)

        self.entry_pasta = ctk.CTkEntry(
            frame_pasta, textvariable=self.pasta_var, width=360
        )
        self.entry_pasta.pack(side="left", fill="x", expand=True)

        self.btn_procurar = ctk.CTkButton(
            frame_pasta, text="Procurar...", width=100, command=self.selecionar_pasta
        )
        self.btn_procurar.pack(side="right", padx=(10, 0))

        # Campo: Seleção de Formato (Menu Dropdown Custom)
        self.lbl_formato = ctk.CTkLabel(
            self, text="Formato de Saída:", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_formato.pack(anchor="w", padx=35, pady=(10, 2))

        self.combo_formato = ctk.CTkOptionMenu(
            self,
            variable=self.formato_var,
            values=["MP4 (Vídeo + Áudio)", "MP3 (Apenas Áudio)"],
            width=220,
        )
        self.combo_formato.pack(anchor="w", padx=35, pady=5)

        # Barra de Progresso Customizada
        self.progress_bar = ctk.CTkProgressBar(self, width=480)
        self.progress_bar.set(0)  # Inicia zerada
        self.progress_bar.pack(pady=(20, 5))

        # Texto de Status
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Pronto para iniciar",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="gray",
        )
        self.lbl_status.pack()

        # Frame de Botões de Ação
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=(15, 10))

        self.btn_download = ctk.CTkButton(
            frame_botoes,
            text="Download",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=140,
            command=self.baixar_midia_thread,
        )
        self.btn_download.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(
            frame_botoes,
            text="Limpar",
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            width=100,
            command=self.limpar_campos,
        )
        self.btn_limpar.pack(side="left", padx=10)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_var.set(pasta)

    def limpar_campos(self):
        self.url_var.set("")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Pronto para download")

    def atualizar_progresso(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (
            bytes_downloaded / total_size
        )  # CustomTkinter usa escala de 0.0 a 1.0

        self.progress_bar.set(percentage)
        self.lbl_status.configure(text=f"Baixando: {percentage * 100:.1f}%")
        self.update_idletasks()

    def baixar_midia_thread(self):
        thread = threading.Thread(target=self.baixar_midia)
        thread.daemon = True
        thread.start()

    def baixar_midia(self):
        url = self.url_var.get().strip()
        pasta_destino = self.pasta_var.get().strip()
        formato = self.formato_var.get()

        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube")
            return

        if not pasta_destino:
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino")
            return

        try:
            self.btn_download.configure(state="disabled")
            self.lbl_status.configure(text="Conectando ao YouTube...")
            self.progress_bar.set(0.1)

            yt = YouTube(url, on_progress_callback=self.atualizar_progresso)

            self.lbl_status.configure(text=f"Processando: {yt.title[:40]}...")
            self.progress_bar.set(0.3)

            if "MP4" in formato:
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(only_audio=True).first()

            if not stream:
                messagebox.showerror(
                    "Erro", "Não foi possível encontrar uma stream compatível"
                )
                return

            self.progress_bar.set(0.5)
            self.lbl_status.configure(text="Baixando mídia...")

            arquivo_path = stream.download(output_path=pasta_destino)
            novo_arquivo = arquivo_path

            if "MP3" in formato:
                base, ext = os.path.splitext(arquivo_path)
                novo_arquivo = base + ".mp3"
                if os.path.exists(novo_arquivo):
                    os.remove(novo_arquivo)
                os.rename(arquivo_path, novo_arquivo)

            self.progress_bar.set(1.0)
            self.lbl_status.configure(text="Download concluído!")

            messagebox.showinfo(
                "Sucesso",
                f"Download concluído com sucesso!\n\nTítulo: {yt.title}\nSalvo em: {novo_arquivo}",
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")
            self.lbl_status.configure(text="Erro no download")
        finally:
            self.btn_download.configure(state="normal")
            self.progress_bar.set(0)

    def abrir_janela_sobre(self):
        # Janela popup com CustomTkinter
        janela_sobre = ctk.CTkToplevel(self)
        janela_sobre.title("Sobre o Autor")
        janela_sobre.geometry("360x240")
        janela_sobre.resizable(False, False)
        janela_sobre.transient(self)
        janela_sobre.grab_set()

        # Força o ícone na janela Toplevel usando os dois métodos do Tkinter para não ter erro
        if os.path.exists("vmd-icon.ico"):
            try:
                janela_sobre.iconbitmap("vmd-icon.ico")
                janela_sobre.wm_iconbitmap("vmd-icon.ico")
            except Exception:
                pass  # Se o Windows travar o recurso, o programa não fecha

        lbl_app = ctk.CTkLabel(
            janela_sobre,
            text="Video Music Downloader",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        lbl_app.pack(pady=(25, 5))

        lbl_ver = ctk.CTkLabel(
            janela_sobre,
            text="Versão: 1.0.0",
            font=ctk.CTkFont(size=12, slant="italic"),
        )
        lbl_ver.pack()

        lbl_autor = ctk.CTkLabel(
            janela_sobre, text="By Flávio Ricardo", font=ctk.CTkFont(size=12)
        )
        lbl_autor.pack(pady=(15, 2))

        # Criando o link do GitHub
        lbl_git = ctk.CTkLabel(
            janela_sobre,
            text="https://github.com/fhricardo/video-music-downloader",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#12659c",
            cursor="hand2",
        )
        lbl_git.pack()

        # Vincula o clique para abrir o navegador externo
        lbl_git.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(
                "https://github.com/fhricardo/video-music-downloader"
            ),
        )

        btn_fechar = ctk.CTkButton(
            janela_sobre, text="Fechar", width=100, command=janela_sobre.destroy
        )
        btn_fechar.pack(pady=20)


if __name__ == "__main__":
    app = VideoMusicDownloader()
    app.mainloop()
