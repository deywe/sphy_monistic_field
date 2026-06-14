import hashlib
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class SPHYPlotlyEmulator:
    def __init__(self, nodes=100, passos=200):
        self.nodes = nodes
        self.passos = passos
        self.dx = 0.1
        self.dt = 0.01
        
        # Parâmetros Fundamentais SPHY
        self.G = 6.6743e-11          
        self.alpha = 0.8            
        self.chi_sphy = 1.5      
        self.omega_res = 3.14    
        
        self.x = np.linspace(0, 10, nodes)
        
        # Matrizes de Armazenamento Contínuo [Espaço x Tempo]
        self.G_history = np.zeros((nodes, passos))
        self.E_history = np.zeros((nodes, passos))
        self.B_history = np.zeros((nodes, passos))
        
        # Métricas de Auditoria
        self.tempo_eixo = np.arange(passos)
        self.resistencia_geometrica = []
        self.erro_bianchi = []
        self.fluxo_poynting_total = []
        
        # Criptografia
        self.ultimo_hash_ancora = "0" * 128
        self.livro_razao_hashes = []

    def processar_todo_o_tempo(self):
        """Calcula estritamente toda a evolução temporal antes de renderizar"""
        # Estado inicial do campo magnético (torção)
        B_atual = np.zeros(self.nodes)
        
        for t in range(self.passos):
            dt_estavel = self.dt * 0.02
            
            # 1. Perturbação do Tecido Gravitacional Fundamental
            G_tissue = np.sin(self.x * 0.5) * np.cos(t * 0.08)
            self.G_history[:, t] = G_tissue
            
            # 2. Derivação do Campo Elétrico (Gradiente)
            E_atual = -np.gradient(G_tissue, self.dx)
            self.E_history[:, t] = E_atual
            
            # 3. Feedback Elástico e Evolução da Torção (Campo Magnético)
            xi_vac = np.sin(np.linspace(0, 2 * np.pi, self.nodes))
            Gamma_fb = self.chi_sphy * self.G * (B_atual * xi_vac) * self.omega_res
            
            rot_alvo = (self.alpha * E_atual) + Gamma_fb
            
            derivada_estavel = np.zeros_like(rot_alvo)
            derivada_estavel[1:-1] = (rot_alvo[2:] - rot_alvo[:-2]) / (2 * self.dx)
            derivada_estavel[0] = (rot_alvo[1] - rot_alvo[-1]) / (2 * self.dx)
            derivada_estavel[-1] = (rot_alvo[0] - rot_alvo[-2]) / (2 * self.dx)
            
            B_atual += derivada_estavel * dt_estavel
            self.B_history[:, t] = B_atual
            
            # 4. Cálculos dos Analisadores Científicos
            fluxo_feedback = np.sum(Gamma_fb ** 2) * 1e20
            perda_ohmica = np.sum(np.abs(E_atual)) / (1.0 + fluxo_feedback)
            div_rot_B = np.mean(np.abs(np.gradient(np.gradient(rot_alvo, self.dx), self.dx)))
            poynting_local = np.sum(np.abs(E_atual * B_atual))
            invariante_topologico = np.mean(E_atual * B_atual)
            
            self.resistencia_geometrica.append(perda_ohmica)
            self.erro_bianchi.append(div_rot_B)
            self.fluxo_poynting_total.append(poynting_local)
            
            # 5. Encadeamento Criptográfico SHA-512
            bloco_dados = G_tissue.tobytes() + B_atual.tobytes() + np.array([div_rot_B, poynting_local, perda_ohmica]).tobytes()
            payload = bloco_dados + self.ultimo_hash_ancora.encode('utf-8')
            hash_atual = hashlib.sha512(payload).hexdigest()
            self.ultimo_hash_ancora = hash_atual
            self.livro_razao_hashes.append(hash_atual)

# --- Execução do Processamento ---
emulador = SPHYPlotlyEmulator(nodes=100, passos=200)
emulador.processar_todo_o_tempo()

# --- Construção do Cenário Contínuo Interativo (Plotly) ---
# Criamos uma malha bidimensional (Espaço x Tempo) para plotar as superfícies 3D
T, X = np.meshgrid(emulador.tempo_eixo, emulador.x)

fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{"type": "surface", "colspan": 2}, None], # Superfície 3D ocupa o topo inteiro
        [{"type": "scatter"}, {"type": "scatter"}]  # Gráficos de auditoria na base
    ],
    subplot_titles=(
        "Evolução Contínua do Espaço-Tempo Monístico (Substância Única SPHY)",
        "Colapso da Resistência por Sincronia",
        "Auditoria de Conservação (Identidade de Bianchi)"
    ),
    vertical_spacing=0.15
)

# 1. Adiciona o Tecido Gravitacional Fundamental como a Superfície Base (Preto/Cinza)
fig.add_trace(
    go.Surface(x=T, y=X, z=emulador.G_history, colorscale='Greys', name='Tecido G', showscale=False),
    row=1, col=1
)

# 2. Adiciona o Campo Elétrico Emergente (Gradiente - Laranja)
fig.add_trace(
    go.Surface(x=T, y=X, z=emulador.E_history, colorscale='YlOrRd', name='Gradiente (E)', opacity=0.7, showscale=False),
    row=1, col=1
)

# 3. Adiciona o Campo Magnético Emergente (Torção - Azul)
fig.add_trace(
    go.Surface(x=T, y=X, z=emulador.B_history, colorscale='Blues', name='Torção (B)', opacity=0.7, showscale=False),
    row=1, col=1
)

# 4. Gráfico de Linha: Queda da Resistência
fig.add_trace(
    go.Scatter(x=emulador.tempo_eixo, y=emulador.resistencia_geometrica, name="Resistência Ôhmica", line=dict(color='crimson', width=2)),
    row=2, col=1
)

# 5. Gráfico de Linha: Erro de Bianchi e Fluxo Poynting
fig.add_trace(
    go.Scatter(x=emulador.tempo_eixo, y=emulador.erro_bianchi, name="Erro Bianchi", line=dict(color='purple', width=2)),
    row=2, col=2
)
fig.add_trace(
    go.Scatter(x=emulador.tempo_eixo, y=emulador.fluxo_poynting_total, name="Fluxo Poynting", line=dict(color='darkblue', width=1.5, dash='dash')),
    row=2, col=2
)

# --- Customização de Layout e Estética Industrial ---
fig.update_layout(
    title=dict(
        text=f"<b>Emulador SPHY Interativo</b><br><sup>Assinatura Raiz Criptográfica: {emulador.ultimo_hash_ancora[:40]}...</sup>",
        x=0.5, font=dict(family="Monospace", size=16)
    ),
    scene=dict(
        xaxis_title='Tempo (Frames)',
        yaxis_title='Espaço (Nodes)',
        zaxis_title='Amplitude do Campo',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)) # Ângulo de visualização isométrica inicial
    ),
    height=850,
    showlegend=True,
    template="plotly_white"
)

# Força os limites dos eixos bidimensionais inferiores para melhor leitura
fig.update_xaxes(title_text="Tempo", row=2, col=1)
fig.update_xaxes(title_text="Tempo", row=2, col=2)
fig.update_yaxes(title_text="Magnitude", row=2, col=1)
fig.update_yaxes(title_text="Métrica Gauge", row=2, col=2)

# Abre automaticamente o painel no navegador local
fig.show()