import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pytubefix import YouTube
from pytubefix.exceptions import (
    BotDetection,
    LiveStreamEnded,
    LiveStreamError,
    VideoUnavailable,
    AgeRestrictedError,
    RegexMatchError,
)
import threading
import webbrowser  # Importado no topo para boas práticas

# Configurações de tema e aparência
ctk.set_appearance_mode("System")  # Segue o tema do Windows (Light ou Dark)
ctk.set_default_color_theme("blue")  # Tema azul moderno

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def obter_caminho_recurso(nome_arquivo):
    """Retorna o caminho absoluto de um recurso, compatível com PyInstaller e execução direta."""
    if hasattr(sys, "_MEIPASS"):
        caminho_meipass = os.path.join(sys._MEIPASS, nome_arquivo)
        if os.path.exists(caminho_meipass):
            return caminho_meipass
    caminho_local = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(caminho_local):
        return caminho_local
    if os.path.exists(nome_arquivo):
        return nome_arquivo
    return None


class VideoMusicDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CARREGAR CONFIGURAÇÕES PERSISTENTES (PO TOKEN) ---
        self.config_data = self.carregar_config()
        self.usar_po_token_manual = self.config_data.get("use_manual_po_token", False)
        self.manual_po_token = self.config_data.get("po_token", "")
        self.manual_visitor_data = self.config_data.get("visitor_data", "")

        # --- CONFIGURAÇÃO DA JANELA PRINCIPAL ---
        self.title("Video Music Downloader")
        self.geometry("550x380")
        self.resizable(False, False)

        # Suporte a ícone personalizado
        icone = obter_caminho_recurso("vmd-icon.ico")
        if icone:
            try:
                self.iconbitmap(icone)
            except Exception:
                pass

        # --- CRIAÇÃO DO MENU SUPERIOR (Menu de Barras) ---
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Adiciona o menu "Configurações"
        self.menu_config = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_config.add_command(
            label="Configurar PO Token (YouTube)...", command=self.abrir_janela_potoken
        )
        self.menu_bar.add_cascade(label="Configurações", menu=self.menu_config)

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

    def carregar_config(self):
        """Carrega as configurações salvas de token e preferências."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"use_manual_po_token": False, "po_token": "", "visitor_data": ""}

    def salvar_config(self):
        """Salva as configurações de token no arquivo JSON local."""
        try:
            dados = {
                "use_manual_po_token": self.usar_po_token_manual,
                "po_token": self.manual_po_token,
                "visitor_data": self.manual_visitor_data,
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4)
        except Exception:
            pass

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
            self.lbl_status.configure(text="Conectando ao YouTube com PO Token...")
            self.progress_bar.set(0.1)

            # Instanciação do YouTube com PO Token:
            # 1. Modo Manual: Caso o usuário tenha configurado PO Token e Visitor Data personalizados.
            # 2. Modo Automático (Padrão): Utiliza client='WEB', onde o pytubefix gera automaticamente
            #    o PO Token (Proof of Origin) via BotGuard / Node.js, contornando bloqueios de bot.
            if self.usar_po_token_manual and self.manual_po_token:
                vis_data = self.manual_visitor_data
                po_tok = self.manual_po_token
                yt = YouTube(
                    url,
                    client="WEB",
                    use_po_token=True,
                    po_token_verifier=lambda: (vis_data, po_tok),
                    on_progress_callback=self.atualizar_progresso,
                )
            else:
                yt = YouTube(
                    url,
                    client="WEB",
                    on_progress_callback=self.atualizar_progresso,
                )

            self.lbl_status.configure(text=f"Processando: {yt.title[:40]}...")
            self.progress_bar.set(0.3)

            if "MP4" in formato:
                stream = yt.streams.get_highest_resolution()
                # Fallbacks caso get_highest_resolution não encontre direto
                if not stream:
                    stream = (
                        yt.streams.filter(progressive=True, file_extension="mp4")
                        .order_by("resolution")
                        .desc()
                        .first()
                    )
                if not stream:
                    stream = (
                        yt.streams.filter(progressive=True)
                        .order_by("resolution")
                        .desc()
                        .first()
                    )
            else:
                # Seleciona o áudio de maior taxa de bits (abr)
                stream = (
                    yt.streams.filter(only_audio=True)
                    .order_by("abr")
                    .desc()
                    .first()
                )
                if not stream:
                    stream = yt.streams.filter(only_audio=True).first()

            if not stream:
                messagebox.showerror(
                    "Erro", "Não foi possível encontrar uma stream compatível para download."
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

        except BotDetection as e:
            self.lbl_status.configure(text="Erro: Detecção de bot")
            messagebox.showerror(
                "Detecção de Robô (YouTube)",
                "O YouTube detectou a requisição como bot.\n\n"
                "Para solucionar:\n"
                "1. Aguarde alguns instantes e tente novamente.\n"
                "2. Vá ao menu 'Configurações > Configurar PO Token' e informe um PO Token obtido no seu navegador.",
            )
        except LiveStreamEnded:
            self.lbl_status.configure(text="Transmissão ao vivo encerrada")
            messagebox.showwarning(
                "Transmissão Encerrada",
                "Esta transmissão ao vivo foi encerrada recentemente e ainda está sendo processada pelo YouTube.\n\n"
                "Aguarde o término do processamento para que os arquivos de mídia fiquem disponíveis para download.",
            )
        except LiveStreamError:
            self.lbl_status.configure(text="Transmissão ao vivo ativa")
            messagebox.showwarning(
                "Transmissão ao Vivo",
                "Transmissões ao vivo em andamento não podem ser baixadas diretamente.\n"
                "Aguarde a transmissão ser finalizada.",
            )
        except VideoUnavailable:
            self.lbl_status.configure(text="Vídeo indisponível")
            messagebox.showerror(
                "Vídeo Indisponível",
                "Este vídeo não está disponível (pode ser privado, removido ou bloqueado por direitos autorais).",
            )
        except AgeRestrictedError:
            self.lbl_status.configure(text="Restrição de idade")
            messagebox.showerror(
                "Restrição de Idade",
                "Este vídeo possui restrição de idade e não permite download anônimo.",
            )
        except RegexMatchError:
            self.lbl_status.configure(text="Erro de decodificação")
            messagebox.showerror(
                "Erro de Decodificação",
                "O YouTube alterou seu código JavaScript interno e a biblioteca precisa ser atualizada.\n"
                "Execute: pip install --upgrade pytubefix",
            )
        except Exception as e:
            self.lbl_status.configure(text="Erro no download")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")
        finally:
            self.btn_download.configure(state="normal")
            self.progress_bar.set(0)

    def abrir_janela_potoken(self):
        """Janela modal para configuração de PO Token (Proof of Origin)."""
        janela_po = ctk.CTkToplevel(self)
        janela_po.title("Configurações do PO Token")
        janela_po.geometry("520x430")
        janela_po.resizable(False, False)
        janela_po.transient(self)
        janela_po.grab_set()

        icone = obter_caminho_recurso("vmd-icon.ico")
        if icone:
            try:
                janela_po.iconbitmap(icone)
                janela_po.wm_iconbitmap(icone)
            except Exception:
                pass

        lbl_titulo = ctk.CTkLabel(
            janela_po,
            text="Autenticação e PO Token (Proof of Origin)",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        lbl_titulo.pack(pady=(15, 5))

        lbl_desc = ctk.CTkLabel(
            janela_po,
            text=(
                "O YouTube exige o Proof of Origin Token para validar requisições.\n"
                "Por padrão, o VMD gera o token automaticamente via BotGuard (Node.js).\n"
                "Se preferir usar valores manuais obtidos no navegador, preencha abaixo:"
            ),
            font=ctk.CTkFont(size=11),
            justify="center",
            text_color="gray",
        )
        lbl_desc.pack(padx=20, pady=(0, 10))

        # Variáveis locais
        usar_manual_var = ctk.BooleanVar(value=self.usar_po_token_manual)
        token_var = ctk.StringVar(value=self.manual_po_token)
        visitor_var = ctk.StringVar(value=self.manual_visitor_data)

        def alternar_campos():
            estado = "normal" if usar_manual_var.get() else "disabled"
            entry_token.configure(state=estado)
            entry_visitor.configure(state=estado)

        chk_manual = ctk.CTkCheckBox(
            janela_po,
            text="Usar PO Token manual (substituir o automático)",
            variable=usar_manual_var,
            command=alternar_campos,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        chk_manual.pack(anchor="w", padx=30, pady=(5, 10))

        # Campo: PO Token
        lbl_tok = ctk.CTkLabel(
            janela_po, text="PO Token (serviceIntegrityDimensions.poToken):", font=ctk.CTkFont(size=12)
        )
        lbl_tok.pack(anchor="w", padx=30, pady=(2, 2))

        entry_token = ctk.CTkEntry(
            janela_po,
            textvariable=token_var,
            width=460,
            placeholder_text="Cole o PO Token aqui...",
        )
        entry_token.pack(padx=30, pady=2)

        # Campo: Visitor Data
        lbl_vis = ctk.CTkLabel(
            janela_po,
            text="Visitor Data (context.client.visitorData):",
            font=ctk.CTkFont(size=12),
        )
        lbl_vis.pack(anchor="w", padx=30, pady=(8, 2))

        entry_visitor = ctk.CTkEntry(
            janela_po,
            textvariable=visitor_var,
            width=460,
            placeholder_text="Cole o visitorData aqui...",
        )
        entry_visitor.pack(padx=30, pady=2)

        alternar_campos()

        # Link documentação
        lbl_doc = ctk.CTkLabel(
            janela_po,
            text="📖 Como obter o PO Token no navegador (Documentação Pytubefix)",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#12659c",
            cursor="hand2",
        )
        lbl_doc.pack(pady=(12, 10))
        lbl_doc.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(
                "https://pytubefix.readthedocs.io/en/latest/user/po_token.html"
            ),
        )

        def salvar():
            self.usar_po_token_manual = usar_manual_var.get()
            self.manual_po_token = token_var.get().strip()
            self.manual_visitor_data = visitor_var.get().strip()
            self.salvar_config()
            messagebox.showinfo(
                "Configurações", "Configurações de PO Token salvas com sucesso!"
            )
            janela_po.destroy()

        frame_botoes = ctk.CTkFrame(janela_po, fg_color="transparent")
        frame_botoes.pack(pady=(5, 15))

        btn_salvar = ctk.CTkButton(
            frame_botoes, text="Salvar", width=120, command=salvar
        )
        btn_salvar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            width=100,
            command=janela_po.destroy,
        )
        btn_cancelar.pack(side="left", padx=10)

    def abrir_janela_sobre(self):
        # Janela popup com CustomTkinter
        janela_sobre = ctk.CTkToplevel(self)
        janela_sobre.title("Sobre o Autor")
        janela_sobre.geometry("360x240")
        janela_sobre.resizable(False, False)
        janela_sobre.transient(self)
        janela_sobre.grab_set()

        # Força o ícone na janela Toplevel usando os dois métodos do Tkinter para não ter erro
        icone = obter_caminho_recurso("vmd-icon.ico")
        if icone:
            try:
                janela_sobre.iconbitmap(icone)
                janela_sobre.wm_iconbitmap(icone)
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
            text="Versão: 1.1.0",
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
