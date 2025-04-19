import pygame
import random
import sys
import os

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)  # Inicialização do mixer para garantir que o som funcione

largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Jogo de Nave 2D")
relogio = pygame.time.Clock()

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)

# Fonte
fonte = pygame.font.SysFont(None, 40)

# Sons
tiro_sound = pygame.mixer.Sound(resource_path("assets/tiro.wav"))

# Estados
MENU, JOGANDO, OPCOES, GAMEOVER, VITORIA = "menu", "jogando", "opcoes", "gameover", "vitoria"
estado_jogo = MENU
dificuldade = "normal"

# Jogador com imagem
nave_img = pygame.image.load(resource_path("assets/nave.png")).convert_alpha()
nave_img = pygame.transform.scale(nave_img, (50, 50))
jogador = nave_img.get_rect(midbottom=(400, 550))
vel_jogador = 5
balas = []
movimento_jogador = {"left": False, "right": False}

# Inimigos
inimigos = []
direcoes_inimigos = []
vel_bala = 7
vel_inimigo = 3
balas_inimigas = []

# Vida
vida_jogador = 100
vida_maxima = 100

def spawn_inimigos(qtd):
    inimigos.clear()
    direcoes_inimigos.clear()
    for _ in range(qtd):
        inimigo = pygame.Rect(random.randint(0, largura - 50), random.randint(20, 150), 50, 50)
        inimigos.append(inimigo)
        direcoes_inimigos.append(random.choice([-1, 1]))

def desenhar_menu():
    tela.fill(PRETO)
    titulo = fonte.render("Jogo de Nave 2D", True, BRANCO)
    jogar = fonte.render("Jogar", True, BRANCO)
    opcoes = fonte.render("Opções", True, BRANCO)
    tela.blit(titulo, (largura//2 - titulo.get_width()//2, 100))
    tela.blit(jogar, (largura//2 - jogar.get_width()//2, 200))
    tela.blit(opcoes, (largura//2 - opcoes.get_width()//2, 260))
    pygame.display.flip()

def desenhar_opcoes():
    tela.fill(PRETO)
    txt = fonte.render("Dificuldade:", True, BRANCO)
    normal = fonte.render("1. Normal", True, BRANCO)
    dificil = fonte.render("2. Difícil", True, BRANCO)
    tela.blit(txt, (100, 100))
    tela.blit(normal, (100, 150))
    tela.blit(dificil, (100, 200))
    pygame.display.flip()

def desenhar_gameover():
    tela.fill(PRETO)
    texto = fonte.render("Game Over", True, VERMELHO)
    reiniciar = fonte.render("Pressione R para reiniciar", True, BRANCO)
    tela.blit(texto, (largura//2 - texto.get_width()//2, altura//3))
    tela.blit(reiniciar, (largura//2 - reiniciar.get_width()//2, altura//2))
    pygame.display.flip()

def desenhar_vitoria():
    tela.fill(PRETO)
    texto = fonte.render("Você venceu!", True, VERDE)
    reiniciar = fonte.render("Pressione R para jogar novamente", True, BRANCO)
    tela.blit(texto, (largura//2 - texto.get_width()//2, altura//3))
    tela.blit(reiniciar, (largura//2 - reiniciar.get_width()//2, altura//2))
    pygame.display.flip()

def desenhar_jogo():
    tela.fill(PRETO)
    tela.blit(nave_img, jogador)
    for b in balas:
        pygame.draw.rect(tela, BRANCO, b)
    for inimigo in inimigos:
        pygame.draw.rect(tela, VERMELHO, inimigo)
    for bi in balas_inimigas:
        pygame.draw.rect(tela, VERMELHO, bi['rect'])
    desenhar_barra_de_vida()
    pygame.display.flip()

def desenhar_barra_de_vida():
    barra_largura = 200
    barra_altura = 20
    x = 10
    y = 10
    pygame.draw.rect(tela, (100, 100, 100), (x, y, barra_largura, barra_altura))
    vida_larg = int((vida_jogador / vida_maxima) * barra_largura)
    pygame.draw.rect(tela, VERDE, (x, y, vida_larg, barra_altura))
    pygame.draw.rect(tela, BRANCO, (x, y, barra_largura, barra_altura), 2)

def inimigos_movimentam():
    for i, inimigo in enumerate(inimigos):
        inimigo.x += vel_inimigo * direcoes_inimigos[i]
        if inimigo.left <= 0 or inimigo.right >= largura:
            direcoes_inimigos[i] *= -1
        if random.randint(0, 100) < 2:
            bala = pygame.Rect(inimigo.x + 20, inimigo.y + 50, 5, 10)
            balas_inimigas.append({'rect': bala, 'vel': (0, vel_bala)})

def atualizar_balas():
    for b in list(balas):
        b.y -= vel_bala
        if b.y < 0 and b in balas:
            balas.remove(b)
    for bi in list(balas_inimigas):
        bi['rect'].y += bi['vel'][1]
        if bi['rect'].y > altura and bi in balas_inimigas:
            balas_inimigas.remove(bi)

def checar_colisoes():
    global vida_jogador
    for b in list(balas):
        for inimigo in list(inimigos):
            if b.colliderect(inimigo):
                if b in balas:
                    balas.remove(b)
                if inimigo in inimigos:
                    idx = inimigos.index(inimigo)
                    inimigos.remove(inimigo)
                    direcoes_inimigos.pop(idx)
    for bi in list(balas_inimigas):
        if bi['rect'].colliderect(jogador):
            vida_jogador -= 10
            if bi in balas_inimigas:
                balas_inimigas.remove(bi)

def reiniciar_jogo():
    global vida_jogador, estado_jogo
    vida_jogador = vida_maxima
    spawn_inimigos(5 if dificuldade == "normal" else 10)
    estado_jogo = JOGANDO

# Função de disparo
def disparar_tiro():
    bala = pygame.Rect(jogador.centerx, jogador.y, 5, 10)
    balas.append(bala)
    tiro_sound.play()  # Reproduz o som quando o tiro é disparado

# Início do jogo
rodando = True
spawn_inimigos(5)

while rodando:
    relogio.tick(60)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado_jogo == MENU:
                x, y = pygame.mouse.get_pos()
                if 200 <= y <= 240:
                    estado_jogo = JOGANDO
                    spawn_inimigos(5 if dificuldade == "normal" else 10)
                elif 260 <= y <= 300:
                    estado_jogo = OPCOES
        if evento.type == pygame.KEYDOWN:
            if estado_jogo == OPCOES:
                if evento.key == pygame.K_1:
                    dificuldade = "normal"
                    estado_jogo = MENU
                elif evento.key == pygame.K_2:
                    dificuldade = "dificil"
                    estado_jogo = MENU
            elif estado_jogo == JOGANDO:
                if evento.key == pygame.K_SPACE:
                    disparar_tiro()  # Chama a função de disparo
                if evento.key == pygame.K_LEFT:
                    movimento_jogador["left"] = True
                if evento.key == pygame.K_RIGHT:
                    movimento_jogador["right"] = True
            elif estado_jogo in [GAMEOVER, VITORIA]:
                if evento.key == pygame.K_r:
                    reiniciar_jogo()
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_LEFT:
                movimento_jogador["left"] = False
            if evento.key == pygame.K_RIGHT:
                movimento_jogador["right"] = False

    if estado_jogo == MENU:
        desenhar_menu()
    elif estado_jogo == OPCOES:
        desenhar_opcoes()
    elif estado_jogo == GAMEOVER:
        desenhar_gameover()
    elif estado_jogo == VITORIA:
        desenhar_vitoria()
    elif estado_jogo == JOGANDO:
        if vida_jogador <= 0:
            estado_jogo = GAMEOVER
        elif len(inimigos) == 0:
            estado_jogo = VITORIA

        if movimento_jogador["left"] and jogador.x > 0:
            jogador.x -= vel_jogador
        if movimento_jogador["right"] and jogador.x < largura - jogador.width:
            jogador.x += vel_jogador

        inimigos_movimentam()
        atualizar_balas()
        checar_colisoes()
        desenhar_jogo()

pygame.quit()
