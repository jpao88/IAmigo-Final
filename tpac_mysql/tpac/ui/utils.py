import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_cabecalho(titulo: str):
    limpar_tela()
    print("=" * 60)
    print(f"{titulo.center(60)}")
    print("=" * 60 + "\n")
    
def exibir_barra_status(usuario):
    print(" ╔══════════════════════════════════════════════════════╗")
    print(f" ║ 👤 Usuário: {usuario:<15}   🤖 IAmigo Online       ║")
    print(" ╚══════════════════════════════════════════════════════╝")
    
def exibir_progresso(tarefas):
    if not tarefas:
        return

    total = len(tarefas)
    concluidas = sum(1 for t in tarefas if t.concluida)

    porcentagem = int((concluidas / total) * 100)

    blocos = int(porcentagem / 10)
    barra = "█" * blocos + "░" * (10 - blocos)

    print("\n📊 PROGRESSO")
    print(f"[{barra}] {porcentagem}%")
    print(f"✅ {concluidas} de {total} atividades concluídas\n")