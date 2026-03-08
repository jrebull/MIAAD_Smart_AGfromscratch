"""Streamlit dashboard for VRP GA experiment results — UACJ palette."""

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# -- Resolve project root so src/ imports work regardless of CWD --
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -- Page config --
st.set_page_config(
    page_title="VRP GA Dashboard — MIAAD UACJ",
    page_icon="https://img.icons8.com/fluency/48/truck.png",
    layout="wide",
)

# -- UACJ Custom CSS --
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F5F7FA; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #003CA6; }
    .stButton > button {
        background-color: #003CA6;
        color: #FFD600;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #002a7a; }
    [data-testid="stSidebar"] { background-color: #003CA6; color: white; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p { color: white !important; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #003CA6;
    }
    .metric-card h4 { margin: 0 0 0.3rem 0; font-size: 0.85rem; color: #555; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; color: #003CA6; }
</style>
""", unsafe_allow_html=True)

RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"

SCENARIO_NAMES = [
    "Escenario 1 — Escalabilidad Media",
    "Escenario 2 — Alta Escalabilidad",
    "Escenario 3 — Variabilidad Económica",
    "Escenario 4 — Estrés Operativo: Penalizaciones Altas",
    "Escenario 5 — Estrés Operativo: Capacidad Ampliada",
]

# -- SVG icon helper --
ICONS = {
    "chart":  '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003CA6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "box":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003CA6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
    "map":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003CA6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>',
    "gear":   '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#003CA6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "truck":  '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
}


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


def decode_chromosome_pure(chromosome, clients, capacity):
    """Decode chromosome without importing src — pure Python."""
    routes, current_route, current_load = [], [], 0
    for client_id in chromosome:
        demand = clients[client_id]["demanda"]
        if current_load + demand > capacity:
            routes.append(current_route)
            current_route = [client_id]
            current_load = demand
        else:
            current_route.append(client_id)
            current_load += demand
    if current_route:
        routes.append(current_route)
    return routes


CAPACITIES = [30, 30, 30, 20, 50]


def metric_card(label, value, color="#003CA6"):
    """Render a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <h4>{label}</h4>
        <div class="value" style="color: {color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# -- Sidebar --
st.sidebar.markdown(f'{ICONS["truck"]} **VRP GA Dashboard**', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**MIAAD &middot; UACJ**", unsafe_allow_html=True)
st.sidebar.markdown("Optimizacion Inteligente")
st.sidebar.markdown("Mtro. Raul Gibran Porras Alaniz")
st.sidebar.markdown("---")
st.sidebar.markdown("Javier Augusto Rebull Saucedo")
st.sidebar.markdown("Matricula: 263483")

tab1, tab2, tab3, tab4 = st.tabs([
    "Resultados por Escenario",
    "Comparativa Global",
    "Visualizador de Rutas",
    "Ejecutar Experimento",
])

# ======== TAB 1: Results per scenario ========
with tab1:
    st.markdown(f'{ICONS["chart"]} **Resultados por Escenario**', unsafe_allow_html=True)
    st.markdown("---")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados. Ejecuta `python run_experiments.py --full` primero.")
    else:
        selected = st.selectbox("Seleccionar escenario:", SCENARIO_NAMES)
        idx = SCENARIO_NAMES.index(selected)
        m = metrics[idx]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("BKS (Mejor Fitness)", f"${m['best_fitness']:,.2f}")
        with col2:
            metric_card("Promedio", f"${m['avg_best_fitness']:,.2f}")
        with col3:
            metric_card("Gap", f"{m['gap_pct']:.2f}%", color="#E74C3C")
        with col4:
            metric_card("Tasa de Exito", f"{m['success_rate_pct']:.1f}%", color="#27AE60")

        st.markdown("<br>", unsafe_allow_html=True)

        best_run = load_best_run(idx + 1)
        if best_run:
            st.markdown("**Curva de Convergencia (Mejor Ejecucion)**")
            history = best_run["fitness_history"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, len(history) + 1)),
                y=history,
                mode="lines",
                line=dict(color="#003CA6", width=2.5),
                fill="tozeroy",
                fillcolor="rgba(0, 60, 166, 0.08)",
                name="Mejor Fitness",
            ))
            fig.update_layout(
                xaxis_title="Generacion",
                yaxis_title="Mejor Fitness (Z)",
                template="plotly_white",
                margin=dict(t=20),
            )
            st.plotly_chart(fig, use_container_width=True)

# ======== TAB 2: Global comparison ========
with tab2:
    st.markdown(f'{ICONS["box"]} **Comparativa Global**', unsafe_allow_html=True)
    st.markdown("---")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados.")
    else:
        st.markdown("**Distribucion de Fitness por Escenario**")
        fig_box = go.Figure()
        colors = ["#003CA6", "#2C3E50", "#27AE60", "#E74C3C", "#FFD600"]
        for i, m in enumerate(metrics):
            fig_box.add_trace(go.Box(
                y=m["all_best_values"],
                name=f"Esc. {i+1}",
                marker_color=colors[i],
                line_color=colors[i],
            ))
        fig_box.update_layout(
            yaxis_title="Mejor Fitness (Z)",
            template="plotly_white",
            margin=dict(t=20),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("**BKS vs Promedio**")
        labels = [f"Esc. {i+1}" for i in range(len(metrics))]
        fig_bar = go.Figure(data=[
            go.Bar(name="BKS", x=labels, y=[m["best_fitness"] for m in metrics], marker_color="#003CA6"),
            go.Bar(name="Promedio", x=labels, y=[m["avg_best_fitness"] for m in metrics], marker_color="#FFD600", marker_line_color="#2C3E50", marker_line_width=1),
        ])
        fig_bar.update_layout(barmode="group", yaxis_title="Fitness (Z)", template="plotly_white", margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("**Gap (%) y Tasa de Exito (%)**")
        col1, col2 = st.columns(2)
        with col1:
            fig_gap = go.Figure(go.Bar(
                x=labels,
                y=[m["gap_pct"] for m in metrics],
                marker_color="#E74C3C",
                marker_line_color="#c0392b",
                marker_line_width=1,
            ))
            fig_gap.update_layout(yaxis_title="Gap (%)", template="plotly_white", margin=dict(t=20))
            st.plotly_chart(fig_gap, use_container_width=True)
        with col2:
            fig_sr = go.Figure(go.Bar(
                x=labels,
                y=[m["success_rate_pct"] for m in metrics],
                marker_color="#27AE60",
                marker_line_color="#1e8449",
                marker_line_width=1,
            ))
            fig_sr.update_layout(yaxis_title="Tasa de Exito (%)", template="plotly_white", margin=dict(t=20))
            st.plotly_chart(fig_sr, use_container_width=True)

        st.markdown("**Tabla Resumen**")
        summary = pd.DataFrame([{
            "Escenario": f"Esc. {i+1}",
            "Clientes": m["num_clients"],
            "BKS": f"${m['best_fitness']:,.2f}",
            "Promedio": f"${m['avg_best_fitness']:,.2f}",
            "Gap (%)": f"{m['gap_pct']:.2f}%",
            "Exito (%)": f"{m['success_rate_pct']:.1f}%",
            "Desv. Est.": f"${m['std_dev']:,.2f}",
        } for i, m in enumerate(metrics)])
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ======== TAB 3: Route visualizer ========
with tab3:
    st.markdown(f'{ICONS["map"]} **Visualizador de Rutas**', unsafe_allow_html=True)
    st.markdown("---")
    metrics = load_metrics()
    if metrics is None:
        st.warning("No se encontraron resultados.")
    else:
        scenario_sel = st.selectbox("Seleccionar escenario:", SCENARIO_NAMES, key="route_sel")
        s_idx = SCENARIO_NAMES.index(scenario_sel) + 1

        best_run = load_best_run(s_idx)
        instance = load_instance(s_idx)

        if best_run and instance:
            capacity = CAPACITIES[s_idx - 1]
            chromosome = best_run["best_chromosome"]
            routes = decode_chromosome_pure(chromosome, instance, capacity)

            fig = go.Figure()

            depot = instance["0"]
            fig.add_trace(go.Scatter(
                x=[depot["x"]], y=[depot["y"]],
                mode="markers+text",
                marker=dict(symbol="star", size=18, color="#E74C3C"),
                text=["Deposito"], textposition="top center",
                name="Deposito",
                showlegend=True,
            ))

            route_colors = px.colors.qualitative.Set1

            for r_idx, route in enumerate(routes):
                color = route_colors[r_idx % len(route_colors)]
                xs = [depot["x"]]
                ys = [depot["y"]]
                texts = ["Deposito"]
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
                    marker=dict(size=6, color=color),
                    line=dict(color=color, width=2),
                    name=f"Ruta {r_idx + 1} ({len(route)} cl.)",
                    text=texts,
                    hoverinfo="text",
                ))

            fig.update_layout(
                xaxis_title="Coordenada X",
                yaxis_title="Coordenada Y",
                template="plotly_white",
                height=700,
                margin=dict(t=30),
            )
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card("Rutas", str(len(routes)))
            with col2:
                metric_card("Fitness", f"${best_run['best_fitness']:,.2f}")
            with col3:
                metric_card("Clientes", str(len(chromosome)))

# ======== TAB 4: Run experiment ========
with tab4:
    st.markdown(f'{ICONS["gear"]} **Ejecutar Experimento**', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        num_clients = st.number_input("Numero de clientes", min_value=10, max_value=500, value=50)
        pop_size = st.number_input("Tamano de poblacion", min_value=10, max_value=500, value=100)
        generations = st.number_input("Generaciones", min_value=10, max_value=1000, value=300)
    with col2:
        mutation_rate = st.slider("Tasa de mutacion", 0.0, 1.0, 0.15)
        capacity = st.number_input("Capacidad del vehiculo", min_value=5, max_value=200, value=30)
        runs = st.number_input("Numero de ejecuciones", min_value=1, max_value=30, value=1)

    if st.button("Ejecutar Algoritmo Genetico"):
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
        vrp_instance = VRPInstance(clients, config)
        ga = GeneticAlgorithm(
            instance=vrp_instance,
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

        fig = go.Figure()
        for i, hist in enumerate(all_histories):
            fig.add_trace(go.Scatter(
                x=list(range(1, len(hist) + 1)),
                y=hist,
                mode="lines",
                name=f"Run {i}",
                opacity=0.7,
                line=dict(width=2),
            ))
        fig.update_layout(
            xaxis_title="Generacion",
            yaxis_title="Mejor Fitness (Z)",
            template="plotly_white",
            margin=dict(t=20),
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        best_val = max(h[-1] for h in all_histories)
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #27AE60; text-align: center;">
            <h4>Mejor Fitness Encontrado</h4>
            <div class="value" style="color: #27AE60; font-size: 2rem;">${best_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
