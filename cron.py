import tkinter as tk
from tkinter import messagebox, ttk
import time
import csv
from datetime import datetime
import os
import shutil

ARQUIVO_CSV = "registro_estudo.csv"
PASTA_BACKUP = "backups"

class CronometroEstudo:
    def __init__(self, root):
        self.root = root
        self.root.title("Cronômetro de Estudo")

        # Barra de Menu
        menu_bar = tk.Menu(self.root)
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="Visualizar Registros", command=self.visualizar_registros)
        arquivo_menu.add_command(label="Exportar CSV", command=self.exportar_csv)
        arquivo_menu.add_command(label="Restaurar Último Backup", command=self.restaurar_backup)
        menu_bar.add_cascade(label="Menu", menu=arquivo_menu)
        self.root.config(menu=menu_bar)

        # Tela cheia
        largura = self.root.winfo_screenwidth()
        altura = self.root.winfo_screenheight()
        self.root.geometry(f"{largura}x{altura}")

        # Estado
        self.tempo_inicial = None
        self.tempo_pausado = 0
        self.em_execucao = False

        # Tema
        self.tema_label = tk.Label(root, text="Tema do estudo:", font=("Helvetica", 14))
        self.tema_label.pack(pady=20)
        self.tema_entry = tk.Entry(root, width=50, font=("Helvetica", 14))
        self.tema_entry.pack(pady=10)

        # Timer
        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 40))
        self.label.pack(pady=30)

        # Botões
        self.botao_iniciar = tk.Button(root, text="Iniciar", width=20, font=("Helvetica", 14), command=self.iniciar)
        self.botao_iniciar.pack(pady=10)

        self.botao_pausar = tk.Button(root, text="Pausar", width=20, font=("Helvetica", 14), command=self.pausar)
        self.botao_pausar.pack(pady=10)

        self.botao_finalizar = tk.Button(root, text="Finalizar", width=20, font=("Helvetica", 14), command=self.finalizar)
        self.botao_finalizar.pack(pady=10)

        self.atualizar_cronometro()
        self.verificar_arquivo_csv()

    def iniciar(self):
        if not self.em_execucao:
            self.tempo_inicial = time.time() - self.tempo_pausado
            self.em_execucao = True

    def pausar(self):
        if self.em_execucao:
            self.tempo_pausado = time.time() - self.tempo_inicial
            self.em_execucao = False

    def finalizar(self):
        tema = self.tema_entry.get().strip()
        if not tema:
            messagebox.showwarning("Aviso", "Digite o tema do estudo.")
            return

        if self.tempo_inicial is None:
            return

        tempo_total = time.time() - self.tempo_inicial if self.em_execucao else self.tempo_pausado
        tempo_formatado = self.formatar_tempo(tempo_total)

        agora = datetime.now()
        data = agora.strftime("%Y-%m-%d")
        hora = agora.hour
        turno = self.definir_turno(hora)

        self.salvar_csv(data, turno, tema, tempo_formatado)

        self.em_execucao = False
        self.tempo_pausado = 0

        messagebox.showinfo("Finalizado", f"Tempo registrado: {tempo_formatado}")
        self.resetar()

    def atualizar_cronometro(self):
        if self.em_execucao:
            tempo_atual = time.time() - self.tempo_inicial
        else:
            tempo_atual = self.tempo_pausado

        self.label.config(text=self.formatar_tempo(tempo_atual))
        self.root.after(500, self.atualizar_cronometro)

    def formatar_tempo(self, segundos):
        h = int(segundos // 3600)
        m = int((segundos % 3600) // 60)
        s = int(segundos % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def definir_turno(self, hora):
        if 6 <= hora < 12:
            return "Manhã"
        elif 12 <= hora < 18:
            return "Tarde"
        else:
            return "Noite"

    def salvar_csv(self, data, turno, tema, tempo):
        with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            if arquivo.tell() == 0:
                escritor.writerow(["Data", "Turno", "Tema", "Tempo Estudado"])
            escritor.writerow([data, turno, tema, tempo])

        self.criar_backup()

    def criar_backup(self):
        if not os.path.exists(PASTA_BACKUP):
            os.makedirs(PASTA_BACKUP)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nome_backup = f"{PASTA_BACKUP}/registro_estudo_backup_{timestamp}.csv"
        shutil.copy(ARQUIVO_CSV, nome_backup)

    def exportar_csv(self):
        try:
            destino = "registro_estudo_exportado.csv"
            shutil.copy(ARQUIVO_CSV, destino)
            messagebox.showinfo("Exportado", f"Arquivo exportado como: {destino}")
        except FileNotFoundError:
            messagebox.showwarning("Aviso", "Nenhum registro encontrado para exportar.")

    def restaurar_backup(self):
        if not os.path.exists(PASTA_BACKUP):
            messagebox.showwarning("Aviso", "Nenhum backup disponível.")
            return

        arquivos = sorted(os.listdir(PASTA_BACKUP), reverse=True)
        if not arquivos:
            messagebox.showwarning("Aviso", "Nenhum backup encontrado.")
            return

        ultimo_backup = os.path.join(PASTA_BACKUP, arquivos[0])
        shutil.copy(ultimo_backup, ARQUIVO_CSV)
        messagebox.showinfo("Restaurado", f"Backup restaurado: {ultimo_backup}")

    def resetar(self):
        self.tempo_inicial = None
        self.tempo_pausado = 0
        self.em_execucao = False
        self.label.config(text="00:00:00")
        self.tema_entry.delete(0, tk.END)

    def visualizar_registros(self):
        try:
            with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo:
                leitor = csv.reader(arquivo)
                linhas = list(leitor)
        except FileNotFoundError:
            messagebox.showinfo("Visualizar Registros", "Nenhum registro encontrado.")
            return

        if not linhas:
            messagebox.showinfo("Visualizar Registros", "Nenhum dado disponível.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Registros de Estudo")
        janela.geometry("900x600")

        colunas = linhas[0]
        dados = linhas[1:]

        tree = ttk.Treeview(janela, columns=colunas, show="headings")
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor="center")

        for linha in dados:
            tree.insert("", tk.END, values=linha)

        tree.pack(expand=True, fill="both")

        scroll_y = ttk.Scrollbar(janela, orient="vertical", command=tree.yview)
        scroll_y.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(janela, orient="horizontal", command=tree.xview)
        scroll_x.pack(side="bottom", fill="x")
        tree.configure(xscrollcommand=scroll_x.set)

    def verificar_arquivo_csv(self):
        if not os.path.exists(ARQUIVO_CSV):
            if os.path.exists(PASTA_BACKUP):
                backups = sorted(os.listdir(PASTA_BACKUP), reverse=True)
                if backups:
                    restaurar = messagebox.askyesno("Arquivo ausente", "Arquivo principal ausente. Deseja restaurar o último backup?")
                    if restaurar:
                        caminho = os.path.join(PASTA_BACKUP, backups[0])
                        shutil.copy(caminho, ARQUIVO_CSV)
                        messagebox.showinfo("Restaurado", f"Backup restaurado: {caminho}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CronometroEstudo(root)
    root.mainloop()
