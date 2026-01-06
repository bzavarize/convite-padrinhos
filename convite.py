import flet as ft
import urllib.parse
import unicodedata
import random
import asyncio

# --- PALETA DE CORES ---
CORES = {
    "dourado": "#D4AF37",
    "rosa": "#F8BBD0",
    "cartao": "#EEFFFFFF",
    "botao": "#311B92",
    "titulo": "#1A237E",
    "erro": "#D32F2F",
    "sucesso": "#2E7D32"
}


# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()


# --- ANIMAÇÃO DE PÉTALAS ---
class Petala(ft.Container):
    def __init__(self, page_width, page_height):
        start_left = random.randint(0, 1500)
        self.duration = random.randint(6000, 10000)
        self.page_height = page_height
        super().__init__(
            content=ft.Image(src="petala.png", width=25, height=25),
            top=-50,
            left=start_left,
            animate_position=self.duration,
            animate_opacity=self.duration,
        )

    async def cair(self):
        self.top = self.page_height + 100
        self.opacity = 0
        self.update()
        await asyncio.sleep(self.duration / 1000)
        self.animate_position = 0
        self.animate_opacity = 0
        self.top = -50
        self.opacity = 1
        self.update()
        await asyncio.sleep(0.1)
        self.animate_position = self.duration
        self.animate_opacity = self.duration
        await self.cair()


async def main(page: ft.Page):
    page.title = "Convite Bruno & Ingrid"
    page.padding = 0
    page.margin = 0
    page.bgcolor = "black"  # Fundo externo escuro para destacar o convite
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- SUPORTE A ÁUDIO ---
    audio_player = None
    if hasattr(ft, 'Audio'):
        try:
            audio_player = ft.Audio(src="musica.mp3", autoplay=False, volume=0.5)
            page.overlay.append(audio_player)
        except:
            pass

    lista_padrinhos = ["Karoline Silveira Zavarize", "Vinicius Silveira Zavarize",
                       "Andressa Bonfim Rodrigues", "Danrley Lira Ferreira",
                       "Carlos Pereira", "Bruno e Ingrid"]

    def notificar(texto, cor):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto, color="white"), bgcolor=cor)
        page.snack_bar.open = True
        page.update()

    # --- FUNÇÕES DE TRANSIÇÃO ---
    async def mostrar_final(nome):
        titulo_agenda = urllib.parse.quote("Casamento Bruno e Ingrid")
        link_google = f"https://www.google.com/calendar/render?action=TEMPLATE&text={titulo_agenda}&dates=20261010T190000Z/20261011T010000Z"

        coluna_cartao.controls.clear()
        coluna_cartao.controls.extend([
            ft.Image(src="casal.jpeg", height=250, border_radius=15),
            ft.Text(f"Parabéns, {nome}!", size=26, color=CORES["titulo"], weight="bold", text_align="center"),
            ft.Text("✅ Presença Confirmada!", color=CORES["sucesso"], weight="bold"),
            ft.FilledButton("SALVAR NA AGENDA", bgcolor="orange", url=link_google)
        ])
        page.update()

    async def verificar_nome(e):
        digitado = campo_nome.value
        norm_digitado = normalizar(digitado)
        encontrado = next((p for p in lista_padrinhos if norm_digitado in normalizar(p) and len(digitado) > 2), None)

        if encontrado:
            await mostrar_final(encontrado)
        else:
            notificar("Nome não encontrado!", CORES["erro"])

    campo_nome = ft.TextField(label="Nome Completo", width=280, text_align="center", on_submit=verificar_nome)

    async def tela_login(e):
        if audio_player:
            try:
                await audio_player.play()
            except:
                pass

        coluna_cartao.controls.clear()
        coluna_cartao.controls.extend([
            ft.Image(src="casal.jpeg", height=250, border_radius=15),
            ft.Text("Identifique-se:", size=22, weight="bold", color=CORES["titulo"]),
            campo_nome,
            ft.FilledButton("ENTRAR", bgcolor=CORES["botao"], on_click=verificar_nome, width=200, height=45)
        ])
        page.update()

    # --- CONTEÚDO INICIAL ---
    coluna_cartao = ft.Column([
        ft.Image(src="casal.jpeg", height=300, border_radius=20),
        ft.Text("Casamento de\nBruno & Ingrid", size=45,
                text_align="center", weight="bold", color=CORES["titulo"]),
        ft.FilledButton("INICIAR JORNADA", bgcolor=CORES["botao"],
                        on_click=tela_login, width=250, height=55)
    ], horizontal_alignment="center", spacing=20)

    # --- ESTRUTURA VISUAL RESPONSIVA ---
    # Container centralizado que simula a tela do celular
    convite_central = ft.Container(
        content=ft.Stack([
            # 1. Fundo Gradiente Dourado e Rosa
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[CORES["dourado"], CORES["rosa"]]
                ),
                expand=True
            ),
            # 2. Cartão de Conteúdo Centralizado
            ft.Container(
                content=coluna_cartao,
                alignment=ft.Alignment(0, 0),
                padding=40,
                bgcolor=CORES["cartao"],
                border_radius=30,
                margin=20,
                shadow=ft.BoxShadow(blur_radius=40, color="#66000000")
            )
        ]),
        width=420,  # Largura de celular no PC
        height=800,  # Altura fixa para manter proporção
        border_radius=30,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS
    )

    petalas = [Petala(2000, 1200) for _ in range(25)]

    # Montagem do Stack na página toda para o fundo e as pétalas cobrirem tudo
    page.add(
        ft.Stack([
            # Gradiente que preenche toda a janela do navegador
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[CORES["dourado"], CORES["rosa"]]
                ),
                expand=True
            ),
            *petalas,
            # Centraliza o "celular" no meio da tela do PC
            ft.Container(content=convite_central, alignment=ft.Alignment(0, 0), expand=True)
        ], expand=True)
    )

    for p in petalas:
        asyncio.create_task(p.cair())


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER)