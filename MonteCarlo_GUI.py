import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as mtick
import numpy as np
from matplotlib.lines import Line2D
import mplcursors

from Simulation_Core import run_simulation

# Mapping dropdown display names → internal simulation type
SIM_TYPE_MAP = {
    "Retirement": "retirement",
    "Single Stock": "single_stock",
    "Multi-Asset": "multi_asset"
}

def update_inputs(*args):
    sim_type_display = sim_type_var.get()
    sim_type = SIM_TYPE_MAP[sim_type_display]

    # Hide all optional fields first
    for widget in [assets_label, assets_entry, correlation_label, correlation_entry, contribution_label, contribution_entry]:
        widget.pack_forget()

    # Show relevant fields and set defaults
    if sim_type == "multi_asset":
        assets_label.pack(anchor='w', padx=5, pady=2)
        assets_entry.pack(fill='x', padx=5, pady=2)
        assets_entry.delete(0, tk.END)
        assets_entry.insert(0, "12")

        correlation_label.pack(anchor='w', padx=5, pady=2)
        correlation_entry.pack(fill='x', padx=5, pady=2)
        correlation_entry.delete(0, tk.END)
        correlation_entry.insert(0, "0.5")

    elif sim_type == "retirement":
        contribution_label.pack(anchor='w', padx=5, pady=2)
        contribution_entry.pack(fill='x', padx=5, pady=2)
        contribution_entry.delete(0, tk.END)
        contribution_entry.insert(0, "20000")

def on_run_simulation():
    try:
        sim_type_display = sim_type_var.get()
        sim_type = SIM_TYPE_MAP[sim_type_display]

        def parse_entry(entry_widget, type_func=float, field_name="Field"):
            raw_value = entry_widget.get().replace(',', '').strip()
            if raw_value == "":
                raise ValueError(f"{field_name} cannot be empty.")
            try:
                return type_func(raw_value)
            except ValueError:
                raise ValueError(f"{field_name} must be a valid number.")

        # Parse common inputs
        inv = parse_entry(initial_investment_entry, float, "Initial Investment")
        ret = parse_entry(mean_return_entry, float, "Mean Return")
        vol = parse_entry(volatility_entry, float, "Volatility")
        yrs = parse_entry(years_entry, int, "Years")
        sims = parse_entry(simulations_entry, int, "Simulations")

        # Optional inputs
        assets = 0
        corr = 0
        contrib = 0

        if sim_type == "multi_asset":
            assets = parse_entry(assets_entry, int, "Assets")
            corr = parse_entry(correlation_entry, float, "Correlation")
        elif sim_type == "retirement":
            contrib = parse_entry(contribution_entry, float, "Contribution")

        # Run simulation
        raw_portfolio = run_simulation(sim_type, inv, ret, vol, yrs, sims, assets, corr, contrib)
        years = yrs

        # Trim 5 highest and lowest paths only if enough simulations
        if sims > 10:
            final_values = raw_portfolio[:, -1]
            sorted_indices = np.argsort(final_values)
            trimmed_portfolio = raw_portfolio[sorted_indices[5:-5]]
        else:
            trimmed_portfolio = raw_portfolio

        avg_path = trimmed_portfolio.mean(axis=0)
        p5 = np.percentile(trimmed_portfolio, 5, axis=0)
        p95 = np.percentile(trimmed_portfolio, 95, axis=0)
        x = np.arange(years + 1)

        # Clear previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(14, 7), dpi=100)
        ax1 = fig.add_subplot(111)

        # Plot faint simulated paths
        sim_lines = []
        for sim_path in trimmed_portfolio:
            line, = ax1.plot(x, sim_path, color='blue', alpha=0.1, label='_nolegend_')
            sim_lines.append(line)

        # Average path
        avg_line, = ax1.plot(x, avg_path, color='red', linewidth=2, label='Average Path')

        # 5th–95th percentile band
        band = ax1.fill_between(x, p5, p95, color='gray', alpha=0.2, label='5th-95th Percentile')

        # Y-axis formatting
        y_min = 0
        y_max = max(trimmed_portfolio.max(), inv * 10 + 1)
        tick_step = max(1, (y_max - y_min) // 10)
        ax1.set_ylim(y_min, y_max)
        ax1.set_yticks(np.arange(y_min, y_max + tick_step, tick_step))
        ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

        ax2 = ax1.twinx()
        ax2.set_ylim(ax1.get_ylim())
        ax2.set_yticks(ax1.get_yticks())
        ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

        ax1.set_xlabel("Year")
        ax1.set_ylabel("Portfolio Value ($)")
        ax1.set_title(f"{sim_type_display} Simulation: {years}-Year Portfolio")
        ax1.set_xticks(x)
        ax1.grid(True)

        # Dark-blue legend line for simulated paths
        legend_sim_line = Line2D([0], [0], color='#0033cc', lw=2, label='Simulated Paths')
        ax1.legend(handles=[legend_sim_line, avg_line, band], loc="upper left")

        # Hover tooltips
        all_lines = sim_lines + [avg_line]
        cursor = mplcursors.cursor(all_lines, hover=True)

        @cursor.connect("add")
        def on_hover(sel):
            x_val = int(sel.target[0])
            y_val = sel.target[1]
            sel.annotation.set_text(f"Year: {x_val}\nValue: ${y_val:,.0f}")
            sel.annotation.get_bbox_patch().set(fc="#f0f0f0", ec="#555555", alpha=0.9)
            sel.annotation.set_color("#000000")

        # --- Portfolio depletion check for negative contributions in retirement ---
        if sim_type == "retirement" and contrib < 0:
            ran_out = (raw_portfolio <= 0).any(axis=1)
            probability_run_out = ran_out.mean() * 100

            first_zero_year = np.where(raw_portfolio <= 0, np.arange(yrs+1), np.inf)
            depleted_years = first_zero_year.min(axis=1)
            
            # User-friendly average year of depletion
            if np.all(depleted_years == np.inf):
                avg_depletion_year_str = "Never"
            else:
                avg_depletion_year = np.mean(depleted_years[depleted_years < np.inf])
                avg_depletion_year_str = f"{avg_depletion_year:.1f}"

            depletion_label.config(
                text=f"Probability of running out of money: {probability_run_out:.1f}% | "
                     f"Average year of depletion: {avg_depletion_year_str}"
            )

            # Add red line at $0
            ax1.axhline(0, color='red', linestyle='--', linewidth=1)
        else:
            depletion_label.config(text="")

        # Draw canvas
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    except ValueError as ve:
        messagebox.showerror("Invalid Input", str(ve))
    except Exception as e:
        messagebox.showerror("An Error Occurred", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Monte Carlo Portfolio Simulator")

    input_frame = tk.Frame(root, padx=10, pady=10)
    input_frame.pack(side=tk.LEFT, fill=tk.Y)

    sim_type_var = tk.StringVar(root)
    sim_type_var.set("Retirement")
    sim_type_var.trace("w", update_inputs)

    tk.Label(input_frame, text="Simulation Type:").pack()
    sim_type_menu = tk.OptionMenu(input_frame, sim_type_var, "Retirement", "Single Stock", "Multi-Asset")
    sim_type_menu.pack()

    # Common inputs
    tk.Label(input_frame, text="Initial Investment:").pack()
    initial_investment_entry = tk.Entry(input_frame)
    initial_investment_entry.insert(0, "90000")
    initial_investment_entry.pack()

    tk.Label(input_frame, text="Mean Return:").pack()
    mean_return_entry = tk.Entry(input_frame)
    mean_return_entry.insert(0, "0.08")
    mean_return_entry.pack()

    tk.Label(input_frame, text="Volatility:").pack()
    volatility_entry = tk.Entry(input_frame)
    volatility_entry.insert(0, "0.1")
    volatility_entry.pack()

    tk.Label(input_frame, text="Years:").pack()
    years_entry = tk.Entry(input_frame)
    years_entry.insert(0, "30")
    years_entry.pack()

    tk.Label(input_frame, text="Simulations:").pack()
    simulations_entry = tk.Entry(input_frame)
    simulations_entry.insert(0, "300")
    simulations_entry.pack()

    # Multi-Asset and Retirement optional inputs
    assets_label = tk.Label(input_frame, text="Assets:")
    assets_entry = tk.Entry(input_frame)

    correlation_label = tk.Label(input_frame, text="Correlation:")
    correlation_entry = tk.Entry(input_frame)

    contribution_label = tk.Label(input_frame, text="Contribution:")
    contribution_entry = tk.Entry(input_frame)

    run_button = tk.Button(input_frame, text="Run Simulation", command=on_run_simulation)
    run_button.pack(side='bottom', pady=10)

    # --- Container for plot and depletion label ---
    plot_container = tk.Frame(root)
    plot_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    plot_frame = tk.Frame(plot_container)
    plot_frame.pack(fill=tk.BOTH, expand=True)

    # Depletion label directly under the plot
    depletion_label = tk.Label(plot_container, text="", font=("Arial", 12), fg="red")
    depletion_label.pack(fill=tk.X, pady=5)

    update_inputs()
    root.mainloop()
