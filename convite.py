import flet as ft
import urllib.parse
import smtplib
from email.message import EmailMessage
import json
import os
import asyncio
import threading
from dotenv import load_dotenv

# --- CARREGAR VARIÁVEIS DE AMBIENTE ---
load_dotenv()
MEU_EMAIL = os.getenv("EMAIL_USER")
MINHA_SENHA = os.getenv("EMAIL_PASS")
EMAIL_DOS_NOIVOS = os.getenv("EMAIL_TARGET")

# --- BANCO DE DADOS (JSON) ---
ARQUIVO_DB = "confirmados.json"

def carregar_confirmados():
    if not os.path.exists(ARQUIVO_DB):
        return []
    try:
        with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_confirmacao(nome):
    # =================================================================
    # 🛠️ MODO DE TESTE (BYPASS DO JSON)
    # Se o nome for "Bruno e Ingrid", a gente finge que salva, mas não salva.
    # Assim, vocês podem testar o botão "Aceitar" infinitamente.
    # =================================================================
    if "Bruno e Ingrid" in nome or "Admin" in nome:
        print(f"🔧 [MODO TESTE] Simulação de aceite para '{nome}'. Nada foi salvo no JSON.")
        return  # <--- O código PARA aqui e não grava no arquivo
    # =================================================================

    lista = carregar_confirmados()
    if nome not in lista:
        lista.append(nome)
        try:
            with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=4)
        except:
            pass

# --- FUNÇÃO DE EMAIL (THREAD SEPARADA) ---
def enviar_email_task(nome_padrinho):
    print(f"--- [Background] Iniciando envio para {nome_padrinho}... ---")
    try:
        if not MEU_EMAIL or not MINHA_SENHA:
            print("--- [AVISO] Sem credenciais no .env. Modo Simulação. ---")
            return

        msg = EmailMessage()
        msg.set_content(
            f"Olá Bruno e Ingrid!\n\nO convite foi aceito!\n\n"
            f"Convidado: {nome_padrinho}\nStatus: Confirmado\nData: 10/10/2026\n\n"
            f"Parabéns aos noivos!"
        )
        msg['Subject'] = f"CONFIRMAÇÃO: {nome_padrinho} aceitou!"
        msg['From'] = MEU_EMAIL
        msg['To'] = EMAIL_DOS_NOIVOS

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(MEU_EMAIL, MINHA_SENHA)
            smtp.send_message(msg)
        print(f"--- [SUCESSO] E-mail enviado! ---")

    except Exception as e:
        print(f"--- [ERRO GERAL] Não foi possível enviar o e-mail: {e} ---")


# --- APP PRINCIPAL (ASYNC) ---
async def main(page: ft.Page):
    print("--- App Iniciado ---")

    # Configurações
    page.title = "Convite Padrinhos"
    page.theme_mode = "light"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.scroll = "auto"

    # ADICIONEI "Bruno e Ingrid" AQUI NA LISTA PARA FUNCIONAR O LOGIN
    lista_de_padrinhos = [
        "Karoline Silveira Zavarize", "Vinicius Silveira Zavarize", "Andressa Bonfim Rodrigues",
        "Danrley Lira Ferreira", "Carlos Pereira", "Bruno e Ingrid"
    ]

    # --- ELEMENTOS VISUAIS ---
    # Certifique-se que a pasta 'assets' tem a imagem 'casal.jpeg'
    img_capa = ft.Image(src="casal.jpeg", height=300, fit="contain", border_radius=20)

    txt_feedback = ft.Text("", size=14, text_align="center")

    async def on_submit_nome(e):
        await verificar_convidado(e)

    campo_nome = ft.TextField(
        label="Digite seu Nome Completo",
        width=300,
        text_align="center",
        border_color="indigo",
        on_submit=on_submit_nome
    )

    # --- POPUP / OVERLAY ---
    coluna_popup = ft.Column(
        alignment="center",
        horizontal_alignment="center",
        spacing=20,
        animate_opacity=ft.Animation(500, "easeInOut")
    )

    overlay_fundo = ft.Container(
        content=ft.Container(
            content=coluna_popup,
            bgcolor="white",
            padding=30,
            border_radius=20,
            alignment=ft.Alignment(0, 0),
            width=350,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="black"),
        ),
        bgcolor="black54",
        alignment=ft.Alignment(0, 0),
        visible=False,
        expand=True,
    )

    # --- FUNÇÕES LÓGICAS (ASYNC MISTO) ---
    async def mostrar_tela_final(nome_convidado):
        # Aqui chamamos a função que agora tem o "filtro" de teste
        salvar_confirmacao(nome_convidado)

        overlay_fundo.visible = False
        conteudo_principal.controls.clear()

        titulo_final = ft.Text(f"Parabéns, {nome_convidado}!", size=26, weight="bold", color="indigo",
                               text_align="center")
        texto_confirmacao = ft.Text("Sua presença foi confirmada!\nAvisaremos os noivos.", text_align="center", size=16)

        async def adicionar_agenda(e):
            titulo = "Casamento de Bruno e Ingrid"
            data_inicio = "20261010T160000"
            data_fim = "20261010T220000"
            params = {"action": "TEMPLATE", "text": titulo, "dates": f"{data_inicio}/{data_fim}"}
            url_agenda = f"https://www.google.com/calendar/render?{urllib.parse.urlencode(params)}"
            page.launch_url(url_agenda)

        btn_agenda = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon("calendar_month", color="white"),
                ft.Text("Salvar na Agenda", color="white")
            ], alignment="center"),
            bgcolor="orange", width=220, height=50,
            on_click=adicionar_agenda
        )

        conteudo_principal.controls.extend([
            img_capa,
            titulo_final,
            ft.Icon("mark_email_read", color="green", size=40),
            texto_confirmacao,
            ft.Divider(),
            btn_agenda
        ])

        page.update()

        # Envia e-mail em background (não trava a tela)
        threading.Thread(target=enviar_email_task, args=(nome_convidado,), daemon=True).start()

    async def abrir_carta_magica(nome_formatado):
        coluna_popup.controls.clear()
        coluna_popup.opacity = 0

        async def animar_hover(e):
            e.control.scale = 1.1 if e.data == "true" else 1.0
            e.control.update()

        async def acionar_abertura(e):
            coluna_popup.opacity = 0
            coluna_popup.update()

            await asyncio.sleep(0.3)

            coluna_popup.controls.clear()
            coluna_popup.controls.extend([
                ft.Text(f"Querido(a) {nome_formatado},", size=20, weight="bold", color="indigo", text_align="center"),
                ft.Divider(),
                ft.Text("Temos um convite especial...", size=16, italic=True),
                ft.Container(height=10),
                # AQUI ESTÁ O F-STRING CORRIGIDO COM O NOME
                ft.Text(
                    value=f"Você {nome_formatado} foi escolhido para ser\nPADRINHO/MADRINHA! Com muito carinho e amor, escolhemos você para nos dar apoio, companheirismo e testemunhar o momento mais especial e importante de NOSSAS VIDAS!",
                    text_align="center", size=18, weight="bold"
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("CLIQUE PARA ACEITAR", color="white", weight="bold"),
                    bgcolor="green", width=250, height=50,
                    on_click=lambda e: asyncio.create_task(mostrar_tela_final(nome_formatado))
                )
            ])

            coluna_popup.opacity = 1
            coluna_popup.update()

        # Configuração da Imagem
        container_carta = ft.Container(
            content=ft.Image(
                src="carta.gif",
                width=150, height=150,
                fit="contain",
            ),
            on_hover=animar_hover,
            animate_scale=ft.Animation(600, "elasticOut"),
            on_click=acionar_abertura,
            alignment=ft.Alignment(0, 0),
            ink=True,
            border_radius=20,
            padding=10
        )

        coluna_popup.controls.extend([
            ft.Container(height=20),
            container_carta,
            ft.Text("Você recebeu uma incrível missão!", weight="bold", color="indigo"),
            ft.Text("Toque na carta voadora para abrir", size=12, italic=True, color="grey"),
            ft.Container(height=10),
        ])

        overlay_fundo.visible = True
        coluna_popup.opacity = 1
        page.update()

    async def verificar_convidado(e):
        nome_digitado = campo_nome.value.strip().lower()

        txt_feedback.value = "Verificando..."
        txt_feedback.color = "grey"
        txt_feedback.update()

        await asyncio.sleep(0.5)

        nome_encontrado = None
        for nome_db in lista_de_padrinhos:
            if nome_digitado in nome_db.lower() and len(nome_digitado) > 2:
                nome_encontrado = nome_db
                break

        if nome_encontrado:
            confirmados = carregar_confirmados()
            # Se for teste (Bruno e Ingrid), ele ignora o check de confirmados pq nunca salva no JSON
            if nome_encontrado in confirmados:
                txt_feedback.value = f"{nome_encontrado}, você já confirmou presença!"
                txt_feedback.color = "orange"
                txt_feedback.weight = "bold"
            else:
                txt_feedback.value = ""
                await abrir_carta_magica(nome_encontrado)
        else:
            txt_feedback.value = "Nome não encontrado na lista."
            txt_feedback.color = "red"
            txt_feedback.weight = "normal"

        txt_feedback.update()

    async def mostrar_tela_login(e):
        conteudo_principal.controls.clear()
        conteudo_principal.controls.extend([
            img_capa,
            ft.Text("Identifique-se para o sistema:", size=16),
            campo_nome,
            ft.ElevatedButton(
                content=ft.Text("Verificar Convite", color="white"),
                bgcolor="indigo", width=200, height=45,
                on_click=verificar_convidado
            ),
            txt_feedback
        ])
        page.update()

    # --- MONTAGEM INICIAL ---
    conteudo_principal = ft.Column(
        alignment="center",
        horizontal_alignment="center",
        spacing=20
    )

    conteudo_principal.controls.extend([
        img_capa,
        ft.Text("CASAMENTO DO\nBRUNO E INGRID", text_align="center", size=24, weight="bold", color="indigo"),
        ft.Text("MISSÃO PADRINHOS DE CASAMENTO!!!", size=14, italic=True, color="purple"),
        ft.ElevatedButton(
            content=ft.Text("INICIAR", color="white"),
            width=200, height=45, bgcolor="deeppurple",
            on_click=mostrar_tela_login
        )
    ])

    stack_principal = ft.Stack(
        controls=[
            ft.Container(content=conteudo_principal, alignment=ft.Alignment(0, 0)),
            overlay_fundo
        ],
        expand=True
    )

    page.add(stack_principal)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")