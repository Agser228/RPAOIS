import tkinter as tk
from tkinter import filedialog, messagebox
from processor import MSP430Emulator
from assembler import Assembler


class AssemblerGUI:
    def __init__(self, root, data):
        self.root = root
        self.root.title("Emulator")

        # Frame для кнопок сверху
        button_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.run_button = tk.Button(button_frame, text="Начать", command=self.run)
        self.run_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(button_frame, text=" > ", command=self.next_step)
        self.next_button.pack(side=tk.LEFT)
        self.load_button = tk.Button(button_frame, text="Загрузить", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(button_frame, text="Сохранить", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT)

        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(content_frame, width=60)
        self.text_area.grid(row=1, column=0, columnspan=2, sticky='we')

        self.reg_frame = tk.LabelFrame(content_frame, text="Регистры")
        self.reg_frame.grid(row=0, column=0, sticky='we')
        reg_row = tk.Frame(self.reg_frame)
        reg_row.pack(fill=tk.X)
        self.reg_labels = []
        for i in range(16):
            label = tk.Label(reg_row, text=f"R{i}: 0", width=6)
            label.pack(side=tk.LEFT, padx=2)
            self.reg_labels.append(label)

        self.mem_frame = tk.LabelFrame(content_frame, text="Память")
        self.mem_frame.grid(row=0, column=2, rowspan=2, sticky='ns')
        self.mem_labels = []
        for i in range(16):
            label = tk.Label(self.mem_frame, text=f"Mem[{i}]: 0", anchor='w', width=12)
            label.pack(anchor='w', pady=2)
            self.mem_labels.append(label)

        self.offset = len(data)
        self.processor = MSP430Emulator(self.offset)
        self.assembler = Assembler(self.offset)
        self.processor.memory[0:self.offset-1] = data

        self.update_register_display()
        self.update_memory_display()
        self.run_flag = 0

    def update_register_display(self):
        for i in range(16):
            value = self.processor.registers[i]
            self.reg_labels[i].config(text=f"R{i}: {value}")

    def update_memory_display(self):
        for i in range(16):
            value = self.processor.memory[i]
            self.mem_labels[i].config(text=f"M[{i}]: {value}")

    def run(self):
        code = self.text_area.get("1.0", tk.END).strip()
        if code:
            try:
                program = self.assembler.assemble(code)

                self.processor.load_program(program)

                self.highlight_line(self.processor.PC)
                self.processor.step()
                self.run_flag = 1
                print("Программа успешно запущена")

                self.update_register_display()
                self.update_memory_display()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showwarning("Внимание", "Поле ввода команд пустое!")

    def next_step(self):
        if self.run_flag == 1:
            self.highlight_line(self.processor.PC)
            try:
                self.processor.step()
                self.update_register_display()
                self.update_memory_display()
            except UserWarning as w:
                messagebox.showinfo("Инфо", str(w))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showerror("Ошибка", "Программа не запущена")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    code = file.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert(tk.END, code)
                print(f"Программа загружена из {file_path}")
            except UserWarning as w:
                messagebox.showinfo("Инфо", str(w))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt")])
        if file_path:
            try:
                code = self.text_area.get("1.0", tk.END)
                with open(file_path, "w") as file:
                    file.write(code)
                print(f"Программа сохранена в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {str(e)}")

    def highlight_line(self, line):
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        self.text_area.tag_add("highlight", f"{line - self.offset + 1}.0", f"{line - self.offset + 1}.end")
        self.text_area.tag_configure("highlight", background="grey")


if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblerGUI(root, [6, 4, 4, 4, 4, 4, 4])
    root.mainloop()
