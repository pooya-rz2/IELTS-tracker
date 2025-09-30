import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# ===== CONFIG =====
CSV_FILE = "ielts_progress.csv"

# Listening question types (including your rename and two-facts)
LISTENING_TYPES = [
    "Multiple choice",
    "Matching (move into the gaps)",  # renamed
    "Plan/map/diagram labelling",
    "Form completion",
    "Note completion",
    "Table completion",
    "Flow-chart completion",
    "Summary completion",
    "Sentence completion",
    "Short-answer questions",
    "Two-facts"  # added
]

# Reading question types (including T/F/NG, Y/N/NG, Letterbox, two-facts)
READING_TYPES = [
    "Multiple choice",
    "T/F/NG (Identifying information)",  # number 2 renamed
    "Y/N/NG (Identifying writer’s views)",  # number 3 renamed
    "Matching information",
    "Matching headings",
    "Matching features",
    "Matching sentence endings",
    "Sentence completion",
    "Summary completion",
    "Note completion",
    "Table completion",
    "Flow-chart completion",
    "Diagram label completion",
    "Letterbox completion",  # added
    "Short-answer questions",
    "Two-facts"  # added
]

# Band score mapping (Cambridge standard)
BAND_MAP = {
    1: 1.0,
    2: 2.0, 3: 2.0,
    4: 2.5, 5: 2.5,
    6: 3.0, 7: 3.0,
    8: 3.5, 9: 3.5, 10: 3.5,
    11: 4.0, 12: 4.0,
    13: 4.5, 14: 4.5, 15: 4.5,
    16: 5.0, 17: 5.0, 18: 5.0, 19: 5.0,
    20: 5.5, 21: 5.5, 22: 5.5,
    23: 6.0, 24: 6.0, 25: 6.0, 26: 6.0,
    27: 6.5, 28: 6.5, 29: 6.5,
    30: 7.0, 31: 7.0, 32: 7.0,
    33: 7.5, 34: 7.5,
    35: 8.0, 36: 8.0,
    37: 8.5, 38: 8.5,
    39: 9.0, 40: 9.0,
}


# ===== CSV Setup =====
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "date", "time", "book", "test", "module", "part",
        "question_type", "total_questions", "correct", "minutes", "avg_time_per_q"
    ])
    df.to_csv(CSV_FILE, index=False)

# ===== Helpers =====
def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def get_band(score):
    """Convert raw correct count (int) to band score float."""
    # Clip to 40 max
    score = int(score)
    if score > 40:
        score = 40
    if score < 0:
        score = 0
    return BAND_MAP.get(score, 0.0)

def time_to_color(hour):
    """Convert hour 0-23 to a color from green (morning) to red (night)."""
    cmap = plt.cm.get_cmap('RdYlGn_r')  # reversed RdYlGn: green=0, red=23
    return cmap(hour / 23)

def book_test_order(book, test):
    """Helper to sort book-test in proper order (e.g., 15-1 before 16-4)."""
    return int(book)*10 + int(test)

# ===== GUI =====
root = tk.Tk()
root.title("IELTS Tracker")
root.geometry("520x450")

# ===== Add Exam Window =====
def add_exam():
    def on_module_change(event=None):
        mod = module_var.get()
        # Change question types dropdown
        if mod == "Listening":
            qtype_cb['values'] = LISTENING_TYPES
            part_cb['state'] = 'readonly'
            minutes_entry.config(state='disabled')
            part_var.set("1")
        else:
            qtype_cb['values'] = READING_TYPES
            part_cb['state'] = 'disabled'
            part_var.set("")
            minutes_entry.config(state='normal')

        # Reset qtype selection
        qtype_var.set("")

    def submit():
        try:
            book = int(book_var.get())
            test = int(test_var.get())
            module = module_var.get()
            part = part_var.get() if module == "Listening" else ""
            qtype = qtype_var.get()
            if not qtype:
                messagebox.showerror("Error", "Please select a question type.")
                return
            total_q = int(total_q_entry.get())
            correct = int(correct_entry.get())
            if module == "Reading":
                try:
                    minutes = float(minutes_entry.get())
                    if minutes <= 0:
                        messagebox.showerror("Error", "Minutes must be positive for Reading.")
                        return
                except ValueError:
                    # If empty or invalid input, treat as None
                    minutes = None
                avg_time = (minutes / total_q) if (minutes is not None and total_q > 0) else None
            else:
                minutes = None
                avg_time = None


            # Validate correct <= total
            if correct > total_q:
                messagebox.showerror("Error", "Correct answers cannot exceed total questions.")
                return

            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")

            df = load_data()
            new_row = {
                "date": date_str, "time": time_str, "book": book, "test": test,
                "module": module, "part": part, "question_type": qtype,
                "total_questions": total_q, "correct": correct,
                "minutes": minutes, "avg_time_per_q": avg_time
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            messagebox.showinfo("Saved", "Exam record added successfully!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    win = tk.Toplevel(root)
    win.title("Add Exam")

    tk.Label(win, text="Book").grid(row=0, column=0, sticky='w')
    book_var = tk.StringVar(value="15")
    ttk.Combobox(win, textvariable=book_var, values=[str(i) for i in range(10, 30)], state='readonly').grid(row=0, column=1)

    tk.Label(win, text="Test").grid(row=1, column=0, sticky='w')
    test_var = tk.StringVar(value="1")
    ttk.Combobox(win, textvariable=test_var, values=["1", "2", "3", "4"], state='readonly').grid(row=1, column=1)

    tk.Label(win, text="Module").grid(row=2, column=0, sticky='w')
    module_var = tk.StringVar(value="Listening")
    module_cb = ttk.Combobox(win, textvariable=module_var, values=["Listening", "Reading"], state='readonly')
    module_cb.grid(row=2, column=1)
    module_cb.bind("<<ComboboxSelected>>", on_module_change)

    tk.Label(win, text="Part (Listening only)").grid(row=3, column=0, sticky='w')
    part_var = tk.StringVar(value="1")
    part_cb = ttk.Combobox(win, textvariable=part_var, values=["1", "2", "3", "4"], state='readonly')
    part_cb.grid(row=3, column=1)

    tk.Label(win, text="Question Type").grid(row=4, column=0, sticky='w')
    qtype_var = tk.StringVar()
    qtype_cb = ttk.Combobox(win, textvariable=qtype_var, values=LISTENING_TYPES, state='readonly')
    qtype_cb.grid(row=4, column=1)

    tk.Label(win, text="Total Questions").grid(row=5, column=0, sticky='w')
    total_q_entry = tk.Entry(win)
    total_q_entry.grid(row=5, column=1)

    tk.Label(win, text="Correct Answers").grid(row=6, column=0, sticky='w')
    correct_entry = tk.Entry(win)
    correct_entry.grid(row=6, column=1)

    tk.Label(win, text="Minutes Spent (Reading only)").grid(row=7, column=0, sticky='w')
    minutes_entry = tk.Entry(win)
    minutes_entry.grid(row=7, column=1)

    on_module_change()  # initialize widgets based on default module

    tk.Button(win, text="Save", command=submit).grid(row=8, column=0, columnspan=2, pady=10)

# ===== Delete Exam =====
def delete_exam():
    def delete_selected():
        selection = listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        index_in_df = df.index[idx]
        df.drop(index_in_df, inplace=True)
        save_data(df)
        messagebox.showinfo("Deleted", "Exam deleted.")
        win.destroy()

    df = load_data()
    if df.empty:
        messagebox.showinfo("Info", "No exams to delete.")
        return

    win = tk.Toplevel(root)
    win.title("Delete Exam")
    listbox = tk.Listbox(win, width=60)
    listbox.pack(padx=10, pady=10)

    for _, row in df.iterrows():
        desc = f"{row['book']}-{row['test']} {row['module']} Part:{row['part'] if row['part'] else '-'} {row['question_type']} Correct:{row['correct']}/{row['total_questions']}"
        listbox.insert(tk.END, desc)

    tk.Button(win, text="Delete Selected", command=delete_selected).pack(pady=5)

# ===== View Stats =====
def view_stats():
    df = load_data()
    if df.empty:
        messagebox.showerror("Error", "No data available.")
        return

    def plot_overall(module):
        df_mod = df[df["module"] == module].copy()
        if df_mod.empty:
            messagebox.showerror("Error", f"No data for {module}")
            return

        # Create book_test string and sort by book_test order
        df_mod["book_test"] = df_mod["book"].astype(str) + "-" + df_mod["test"].astype(str)
        # Sum correct & total per book_test
        grouped = df_mod.groupby("book_test").agg({"correct": "sum", "total_questions": "sum"}).reset_index()

        # Calculate band scores per book_test from summed correct answers
        grouped["band_score"] = grouped["correct"].apply(get_band)

        # Sort by book-test numeric order
        grouped["sort_key"] = grouped["book_test"].apply(lambda x: book_test_order(*x.split("-")))
        grouped = grouped.sort_values("sort_key")

        # Plot
        plt.figure(figsize=(10, 5))
        hours = []
        colors = []
        for bt in grouped["book_test"]:
            # find first record time in that book-test for color (earliest time)
            times = df_mod[df_mod["book_test"] == bt]["time"].values
            if len(times) > 0:
                hour = int(times[0].split(":")[0])
            else:
                hour = 12
            hours.append(hour)
            colors.append(time_to_color(hour))

        # Line plot with dots, color by time
        x = range(len(grouped))
        y = grouped["band_score"]

        # Plot lines connecting points
        plt.plot(list(x), y.values, color="black", linewidth=1, zorder=1)
        # Scatter points
        plt.scatter(x, y, c=colors, s=30, zorder=2)

        avg = y.mean()
        plt.axhline(avg, color="gray", linestyle="dotted")

        plt.xticks(x, grouped["book_test"], rotation=45)
        plt.ylim(5, 9)
        plt.yticks(np.arange(5, 9.5, 0.5))
        plt.ylabel("Band Score")
        plt.xlabel("Book-Test")
        plt.title(f"{module} Overall Band Scores")
        plt.tight_layout()
        plt.show()

    def plot_listening_part_by_part():
        df_list = df[df["module"] == "Listening"].copy()
        if df_list.empty:
            messagebox.showerror("Error", "No Listening data.")
            return
        # Sum correct & total per book-test-part
        df_list["book_test"] = df_list["book"].astype(str) + "-" + df_list["test"].astype(str)
        grouped = df_list.groupby(["book_test", "part"]).agg({
            "correct": "sum",
            "total_questions": "sum"
        }).reset_index()

        # Calculate band per part (sum correct converted to band, assuming max 10 per part for example)
        # Since total questions vary, use percent correct scaled to 40 max, approx
        grouped["percent"] = grouped["correct"] / grouped["total_questions"]
        grouped["scaled_score"] = grouped["percent"] * 10  # scale to 10 for band mapping (approximate)
        grouped["band_score"] = grouped["scaled_score"].apply(lambda x: 5 + (4 * x / 10))  # linear 5-9 scale approx

        # Plot parts 1 to 4 lines
        plt.figure(figsize=(12, 6))
        parts = sorted(grouped["part"].unique())
        colors = ["blue", "green", "orange", "purple"]
        book_tests = sorted(grouped["book_test"].unique(), key=lambda x: book_test_order(*x.split("-")))
        x_ticks = range(len(book_tests))

        for i, p in enumerate(parts):
            data_p = grouped[grouped["part"] == p]
            # Align y data by book_test, fill missing with nan
            y_vals = []
            for bt in book_tests:
                row = data_p[data_p["book_test"] == bt]
                if len(row) == 0:
                    y_vals.append(np.nan)
                else:
                    y_vals.append(row["band_score"].values[0])
            plt.plot(x_ticks, y_vals, marker='o', label=f"Part {p}", color=colors[i])

        plt.xticks(x_ticks, book_tests, rotation=45)
        plt.ylim(5, 9)
        plt.yticks(np.arange(5, 9.5, 0.5))
        plt.ylabel("Band Score (Approximate)")
        plt.xlabel("Book-Test")
        plt.title("Listening Band Scores by Part")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def show_stats_table():
        # We create a table window showing question types stats
        df_stats = load_data()
        if df_stats.empty:
            messagebox.showerror("Error", "No data to show.")
            return

        win = tk.Toplevel(root)
        win.title("Question Types Stats")
        win.geometry("700x400")

        tree = ttk.Treeview(win, columns=("Module", "QType", "Correct", "Total", "Accuracy", "AvgTime"), show="headings")
        tree.heading("Module", text="Module")
        tree.heading("QType", text="Question Type")
        tree.heading("Correct", text="Correct")
        tree.heading("Total", text="Total")
        tree.heading("Accuracy", text="Accuracy %")
        tree.heading("AvgTime", text="Avg Time (min)")

        tree.column("Module", width=80)
        tree.column("QType", width=250)
        tree.column("Correct", width=60, anchor='center')
        tree.column("Total", width=60, anchor='center')
        tree.column("Accuracy", width=80, anchor='center')
        tree.column("AvgTime", width=90, anchor='center')

        # Calculate stats grouped by module and question_type
        for module in ["Listening", "Reading"]:
            df_mod = df_stats[df_stats["module"] == module]
            if module == "Reading":
                df_mod = df_mod[df_mod["minutes"].notna()]

            if df_mod.empty:
                continue
            # Group by question type and part for Listening, only question type for Reading
            if module == "Listening":
                group_cols = ["question_type", "part"]
            else:
                group_cols = ["question_type"]

            grouped = df_mod.groupby(group_cols).agg({
                "correct": "sum",
                "total_questions": "sum",
                "avg_time_per_q": "mean"  # will be nan for Listening
            }).reset_index()

            for _, row in grouped.iterrows():
                correct = row["correct"]
                total = row["total_questions"]
                acc = 100 * correct / total if total > 0 else 0
                avg_t = row["avg_time_per_q"] if module == "Reading" else "-"
                qtype = row["question_type"]
                part_str = f" Part {row['part']}" if module == "Listening" else ""
                # Skip if total answered = 0
                if total == 0:
                    continue
                tree.insert("", "end", values=(
                    module, qtype + part_str, int(correct), int(total), f"{acc:.1f}%", f"{avg_t:.2f}" if avg_t != "-" else "-"
                ))

        tree.pack(expand=True, fill=tk.BOTH)

    def choose_plot():
        win = tk.Toplevel(root)
        win.title("Choose Plot")
        tk.Label(win, text="Select graph to view:").pack(pady=10)
        btn1 = tk.Button(win, text="Listening Overall", command=lambda: [win.destroy(), plot_overall("Listening")])
        btn1.pack(fill=tk.X, padx=50, pady=5)
        btn2 = tk.Button(win, text="Reading Overall", command=lambda: [win.destroy(), plot_overall("Reading")])
        btn2.pack(fill=tk.X, padx=50, pady=5)
        btn3 = tk.Button(win, text="Listening by Part", command=lambda: [win.destroy(), plot_listening_part_by_part()])
        btn3.pack(fill=tk.X, padx=50, pady=5)
        btn4 = tk.Button(win, text="Show Question Types Stats", command=lambda: [win.destroy(), show_stats_table()])
        btn4.pack(fill=tk.X, padx=50, pady=5)

    choose_plot()

# ===== Main GUI Buttons =====
btn_add = tk.Button(root, text="Add Exam Record", width=20, command=add_exam)
btn_add.pack(pady=10)

btn_del = tk.Button(root, text="Delete Exam Record", width=20, command=delete_exam)
btn_del.pack(pady=10)

btn_stats = tk.Button(root, text="View Stats and Plots", width=20, command=view_stats)
btn_stats.pack(pady=10)

root.mainloop()
