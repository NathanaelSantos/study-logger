import tkinter as tk
from tkinter import messagebox
import time
import csv
from datetime import datetime

ARQUIVO_CSV = "registro_estudo.csv"

class CronometroEstudo:
    def __init__(self, root):
        self.root = root
        self.root.title("Cronômetro de Estudo")

        # Definir a geometria da janela para ocupar quase toda a tela
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

        tempo_total = (time.time() - self.tempo_inicial) if self.em_execucao else self.tempo_pausado
        tempo_formatado = self.formatar_tempo(tempo_total)

        agora = datetime.now()
        data = agora.strftime("%Y-%m-%d")
        hora = agora.hour
        turno = self.definir_turno(hora)

        self.salvar_csv(data, turno, tema, tempo_formatado)
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

    def resetar(self):
        self.tempo_inicial = None
        self.tempo_pausado = 0
        self.em_execucao = False
        self.label.config(text="00:00:00")
        self.tema_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CronometroEstudo(root)
    root.mainloop()
