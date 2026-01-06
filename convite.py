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
    "sucesso": "#2E7D32"
}


def normalizar(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()


# --- CLASSE PÉTALA (Lírios caindo) ---
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
    page.bgcolor = CORES["rosa"]
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "auto"

    # --- FUNÇÃO DA AGENDA (Link Direto) ---
    def abrir_agenda(e):
        titulo = urllib.parse.quote("Casamento Bruno e Ingrid")
        # Data: 10/10/2026 às 19h UTC
        link = f"https://www.google.com/calendar/render?action=TEMPLATE&text={titulo}&dates=20261010T190000Z/20261011T010000Z"
        page.launch_url(link)

    async def mostrar_final(nome):
        coluna_cartao.controls.clear()
        coluna_cartao.controls.extend([
            ft.Image(src="casal.jpeg", height=200, border_radius=15, fit="cover"),
            ft.Text(f"Parabéns, {nome}!", size=24, color=CORES["titulo"], weight="bold", text_align="center"),
            ft.Text("✅ Presença Confirmada!", color=CORES["sucesso"], weight="bold"),
            ft.FilledButton("SALVAR NA AGENDA", bgcolor="orange", on_click=abrir_agenda)
        ])
        page.update()

    async def verificar_nome(e):
        lista = ["Karoline Silveira Zavarize", "Vinicius Silveira Zavarize", "Andressa Bonfim Rodrigues",
                 "Danrley Lira Ferreira", "Carlos Pereira", "Bruno e Ingrid"]
        digitado = campo_nome.value
        norm_digitado = normalizar(digitado)
        encontrado = next((p for p in lista if norm_digitado in normalizar(p) and len(digitado) > 2), None)

        if encontrado:
            await mostrar_final(encontrado)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Nome não encontrado!"))
            page.snack_bar.open = True
            page.update()

    campo_nome = ft.TextField(label="Nome Completo", width=250, on_submit=verificar_nome)

    async def tela_login(e):
        coluna_cartao.controls.clear()
        coluna_cartao.controls.extend([
            ft.Image(src="casal.jpeg", height=200, border_radius=15, fit="cover"),
            ft.Text("Identifique-se:", size=20, weight="bold", color=CORES["titulo"]),
            campo_nome,
            ft.FilledButton("ENTRAR", bgcolor=CORES["botao"], on_click=verificar_nome, width=180)
        ])
        page.update()

    # --- LAYOUT INICIAL ---
    coluna_cartao = ft.Column([
        ft.Image(src="casal.jpeg", height=220, border_radius=20, fit="cover"),
        ft.Text("Casamento de\nBruno & Ingrid", size=30, text_align="center", weight="bold", color=CORES["titulo"]),
        ft.FilledButton("INICIAR JORNADA", bgcolor=CORES["botao"], on_click=tela_login, width=200, height=50)
    ], horizontal_alignment="center", spacing=15)

    convite_central = ft.Container(
        content=coluna_cartao,
        padding=25,
        bgcolor=CORES["cartao"],
        border_radius=30,
        width=340,
        shadow=ft.BoxShadow(blur_radius=40, color="#66000000"),
    )

    fundo_gradiente = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[CORES["dourado"], CORES["rosa"]]
        ),
        expand=True
    )

    petalas = [Petala(1500, 1000) for _ in range(12)]  # Reduzido para fluidez mobile

    page.add(
        ft.Stack([
            fundo_gradiente,
            *petalas,
            ft.Container(content=convite_central, alignment=ft.Alignment(0, 0), expand=True)
        ], expand=True)
    )

    for p in petalas:
        asyncio.create_task(p.cair())


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER)