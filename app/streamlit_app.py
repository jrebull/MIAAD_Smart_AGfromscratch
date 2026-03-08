"""Streamlit dashboard for VRP GA experiment results — UACJ palette."""

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -- Page config --
st.set_page_config(
    page_title="VRP GA Dashboard — MIAAD UACJ",
    page_icon="🚛",
    layout="wide",
)

# -- UACJ Custom CSS --
st.markdown("""
<style>
    .stApp { background-color: #F5F7FA; }
    h1, h2, h3 { color: #003CA6; }
    .stButton > button {
        background-color: #003CA6;
        color: #FFD600;
        border: none;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] { background-color: #003CA6; color: white; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label { color: white !important; }
</style>
""", unsafe_allow_html=True)

RESULTS_DIR = Path("results")
DATA_DIR = Path("data")
FIGURES_DIR = Path("Figures")

SCENARIO_NAMES = [
    "Escenario 1 — Escalabilidad Media",
    "Escenario 2 — Alta Escalabilidad",
    "Escenario 3 — Variabilidad Económica",
    "Escenario 4 — Estrés Operativo: Penalizaciones Altas",
    "Escenario 5 — Estrés Operativo: Capacidad Ampliada",
]


def load_metrics():
    path = RESULTS_DIR / "metrics_summary.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_best_run(idx):
    path = RESULTS_DIR / f"best_run_scenario_{idx}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_instance(idx):
    path = DATA_DIR / f"instance_scenario_{idx}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


# -- Sidebar --
st.sidebar.title("🚛 VRP GA Dashboard")
st.sidebar.markdown("**MIAAD · UACJ**")
st.sidebar.markdown("Optimización Inteligente")
st.sidebar.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Resultados por Escenario",
    "📦 Comparativa Global",
    "🗺️ Visualizador de Rutas",
    "⚙️ Ejecutar Experimento",
])

# ======== TAB 1: Results per scenario ========
with tab1:
    st.header("Resultados por Escenario")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados. Ejecuta `python run_experiments.py --full` primero.")
    else:
        selected = st.selectbox("Seleccionar escenario:", SCENARIO_NAMES)
        idx = SCENARIO_NAMES.index(selected)
        m = metrics[idx]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("BKS (Mejor Fitness)", f"${m['best_fitness']:,.2f}")
        col2.metric("Promedio", f"${m['avg_best_fitness']:,.2f}")
        col3.metric("Gap", f"{m['gap_pct']:.2f}%")
        col4.metric("Tasa de Éxito", f"{m['success_rate_pct']:.1f}%")

        best_run = load_best_run(idx + 1)
        if best_run:
            st.subheader("Curva de Convergencia (Mejor Ejecución)")
            history = best_run["fitness_history"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, len(history) + 1)),
                y=history,
                mode="lines",
                line=dict(color="#003CA6", width=2),
                fill="tozeroy",
                fillcolor="rgba(0, 60, 166, 0.1)",
            ))
            fig.update_layout(
                xaxis_title="Generación",
                yaxis_title="Mejor Fitness (Z)",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

# ======== TAB 2: Global comparison ========
with tab2:
    st.header("Comparativa Global")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados.")
    else:
        # Box plot
        st.subheader("Distribución de Fitness por Escenario")
        box_data = []
        for i, m in enumerate(metrics):
            for v in m["all_best_values"]:
                box_data.append({"Escenario": f"Esc. {i+1}", "Fitness": v})
        df_box = pd.DataFrame(box_data)

        fig_box = go.Figure()
        colors = ["#003CA6", "#2C3E50", "#27AE60", "#E74C3C", "#FFD600"]
        for i, m in enumerate(metrics):
            fig_box.add_trace(go.Box(
                y=m["all_best_values"],
                name=f"Esc. {i+1}",
                marker_color=colors[i],
            ))
        fig_box.update_layout(
            yaxis_title="Mejor Fitness (Z)",
            template="plotly_white",
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Grouped bar chart
        st.subheader("BKS vs Promedio")
        labels = [f"Esc. {i+1}" for i in range(len(metrics))]
        fig_bar = go.Figure(data=[
            go.Bar(name="BKS", x=labels, y=[m["best_fitness"] for m in metrics], marker_color="#003CA6"),
            go.Bar(name="Promedio", x=labels, y=[m["avg_best_fitness"] for m in metrics], marker_color="#FFD600"),
        ])
        fig_bar.update_layout(barmode="group", yaxis_title="Fitness (Z)", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gap + Success Rate
        st.subheader("Gap (%) y Tasa de Éxito (%)")
        col1, col2 = st.columns(2)
        with col1:
            fig_gap = go.Figure(go.Bar(
                x=labels,
                y=[m["gap_pct"] for m in metrics],
                marker_color="#E74C3C",
            ))
            fig_gap.update_layout(title="Gap (%)", yaxis_title="Gap (%)", template="plotly_white")
            st.plotly_chart(fig_gap, use_container_width=True)
        with col2:
            fig_sr = go.Figure(go.Bar(
                x=labels,
                y=[m["success_rate_pct"] for m in metrics],
                marker_color="#27AE60",
            ))
            fig_sr.update_layout(title="Tasa de Éxito (%)", yaxis_title="%", template="plotly_white")
            st.plotly_chart(fig_sr, use_container_width=True)

        # Summary table
        st.subheader("Tabla Resumen")
        summary = pd.DataFrame([{
            "Escenario": f"Esc. {i+1}",
            "Clientes": m["num_clients"],
            "BKS": f"${m['best_fitness']:,.2f}",
            "Promedio": f"${m['avg_best_fitness']:,.2f}",
            "Gap (%)": f"{m['gap_pct']:.2f}%",
            "Éxito (%)": f"{m['success_rate_pct']:.1f}%",
            "Desv. Est.": f"${m['std_dev']:,.2f}",
        } for i, m in enumerate(metrics)])
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ======== TAB 3: Route visualizer ========
with tab3:
    st.header("Visualizador de Rutas")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados.")
    else:
        scenario_sel = st.selectbox("Seleccionar escenario:", SCENARIO_NAMES, key="route_sel")
        s_idx = SCENARIO_NAMES.index(scenario_sel) + 1

        best_run = load_best_run(s_idx)
        instance = load_instance(s_idx)

        if best_run and instance:
            from src.config import SCENARIOS
            from src.ga_engine import VRPInstance

            config = SCENARIOS[s_idx - 1]
            vrp = VRPInstance(instance, config)
            chromosome = best_run["best_chromosome"]
            routes = vrp.decode_chromosome(chromosome)

            fig = go.Figure()

            # Depot
            depot = instance["0"]
            fig.add_trace(go.Scatter(
                x=[depot["x"]], y=[depot["y"]],
                mode="markers+text",
                marker=dict(symbol="star", size=18, color="#E74C3C"),
                text=["Depósito"], textposition="top center",
                name="Depósito",
            ))

            # Routes
            import plotly.express as px
            route_colors = px.colors.qualitative.Set1

            for r_idx, route in enumerate(routes):
                color = route_colors[r_idx % len(route_colors)]
                xs = [depot["x"]]
                ys = [depot["y"]]
                texts = ["Depósito"]
                for cid in route:
                    xs.append(instance[cid]["x"])
                    ys.append(instance[cid]["y"])
                    texts.append(f"C{cid} (d={instance[cid]['demanda']})")
                xs.append(depot["x"])
                ys.append(depot["y"])
                texts.append("")

                fig.add_trace(go.Scatter(
                    x=xs, y=ys,
                    mode="lines+markers",
                    marker=dict(size=7, color=color),
                    line=dict(color=color, width=2),
                    name=f"Ruta {r_idx + 1} ({len(route)} clientes)",
                    text=texts,
                    hoverinfo="text",
                ))

            fig.update_layout(
                title=f"Rutas Óptimas — {scenario_sel}",
                xaxis_title="X",
                yaxis_title="Y",
                template="plotly_white",
                height=700,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.info(f"Rutas: {len(routes)} | Fitness: ${best_run['best_fitness']:,.2f}")

# ======== TAB 4: Run experiment ========
with tab4:
    st.header("Ejecutar Experimento")

    col1, col2 = st.columns(2)
    with col1:
        num_clients = st.number_input("Número de clientes", min_value=10, max_value=500, value=50)
        pop_size = st.number_input("Tamaño de población", min_value=10, max_value=500, value=100)
        generations = st.number_input("Generaciones", min_value=10, max_value=1000, value=300)
    with col2:
        mutation_rate = st.slider("Tasa de mutación", 0.0, 1.0, 0.15)
        capacity = st.number_input("Capacidad del vehículo", min_value=5, max_value=200, value=30)
        runs = st.number_input("Número de ejecuciones", min_value=1, max_value=30, value=1)

    if st.button("🚀 Ejecutar"):
        from src.config import ScenarioConfig
        from src.ga_engine import GeneticAlgorithm, VRPInstance
        from src.instance_generator import VRPInstanceGenerator

        config = ScenarioConfig(
            name="Interactive Run",
            num_clients=num_clients,
            demand_range=(5, 15),
            value_range=(50, 300),
            vehicle_capacity=capacity,
        )

        gen = VRPInstanceGenerator(num_clients=num_clients, seed=42)
        clients = gen.generate()
        instance = VRPInstance(clients, config)
        ga = GeneticAlgorithm(
            instance=instance,
            pop_size=pop_size,
            generations=generations,
            mutation_rate=mutation_rate,
        )

        progress = st.progress(0)
        chart_placeholder = st.empty()

        all_histories = []
        for r in range(runs):
            result = ga.run(seed=r)
            all_histories.append(result.fitness_history)
            progress.progress((r + 1) / runs)

        # Show convergence of last run
        fig = go.Figure()
        for i, hist in enumerate(all_histories):
            fig.add_trace(go.Scatter(
                x=list(range(1, len(hist) + 1)),
                y=hist,
                mode="lines",
                name=f"Run {i}",
                opacity=0.7,
            ))
        fig.update_layout(
            xaxis_title="Generación",
            yaxis_title="Mejor Fitness (Z)",
            template="plotly_white",
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        best_result = max(
            [ga.run(seed=r) for r in range(runs)],
            key=lambda r: r.best_fitness,
        ) if runs == 1 else type("R", (), {"best_fitness": max(h[-1] for h in all_histories)})()

        st.success(f"Mejor Fitness: ${max(h[-1] for h in all_histories):,.2f}")
