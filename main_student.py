import pygame as py
import random
import time
import json
import os

SCREEN_WIDTH = 1920  # Largeur de la fenêtre
SCREEN_HEIGHT = 1080  # Hauteur de la fenêtre
GRID_SIZE = 50      # Taille d'une cellule de la grille
FPS = 60            # Nombre d'images par seconde

# ci-dessous, des constantes qui représentent des couleurs. Si vous voulez utiliser une couleur non présente dans la liste, vous pouvez utiliser un tuple de 3 nombres compris entre 0 et 255, qui représentent les valeurs de rouge, vert et bleu. (c'est le RGB)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

with open('base.json', 'r+') as f:
    data = json.load(f)

print(data["best_score"])


def load_image(path):
    """
    Une fonction qui charge une image et la retourne.
    Si l'image n'est pas trouvée, une image avec le texte "ERROR" est retournée.
    """
    try:
        return py.image.load(path)
    except:
        font = py.font.Font(None, 36)
        text = font.render("ERROR", True, (0, 0, 0))
        return text


def create_grid():
    """
    Permet de créer une grille de cellules de la taille de la fenêtre.
    """
    grid = []
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):  # Dessin de la grille avec des rectangles
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            grid.append((x, y))
    return grid


class Projectile:
    """
    Classe qui représente un projectile. (lançé par une tour)
    """

    def __init__(self, x, y):
        # Chemin vers l'image du projectile
        self.image_path = "assets/projectile.png"
        # Chargement de l'image
        self.image = load_image(self.image_path)
        # Redimensionnement de l'image
        self.image = py.transform.scale(self.image, (10, 10))
        # Position sur l'axe x du projectile
        self.x = x
        # Position sur l'axe y du projectile
        self.y = y
        self.speed = 5                                          # Vitesse du projectile

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        self.x += self.speed  # On met à jour la position du projectile


class Tower:
    def __init__(self, x, y):
        # Points de vie de la tour
        self.health = 100
        # Chemin vers l'image de la tour
        self.image_path = "assets/tower.png"
        # Chargement de l'image
        self.image = load_image(self.image_path)
        # Redimensionnement de l'image à la taille d'une cellule de la grille
        self.image = py.transform.scale(self.image, (GRID_SIZE, GRID_SIZE))
        # Position sur l'axe x de la tour
        self.x = x
        # Position sur l'axe y de la tour
        self.y = y
        # Temps entre chaque projectile
        self.projectile_cooldown = 60
        # Compteur pour le temps entre chaque projectile
        self.projectile_timer = 0
        # Liste des projectiles
        self.projectiles = []

    def draw(self, screen):
        # On dessine l'image de la tour
        screen.blit(self.image, (self.x, self.y))

        for projectile in self.projectiles:  # On dessine tout les projectiles de la tour
            projectile.draw(screen)

    def shoot(self):
        """
        Permet de faire tirer une projectile par la tour.
        """
        x = self.x + GRID_SIZE  # On place le projectile à la position de la tour, mais décalé de la taille d'une cellule de la grille en x
        # On place le projectile à la position de la tour, mais décalé de la moitié de la taille d'une cellule de la grille en y
        y = self.y + GRID_SIZE // 2
        # On ajoute le projectile à la liste des projectiles
        self.projectiles.append(Projectile(x, y))

    def update(self):
        # Si le compteur est supérieur au temps entre chaque projectile, alors on fait tirer la tour
        if self.projectile_timer >= self.projectile_cooldown:
            self.shoot()
            self.projectile_timer = 0
        else:  # Sinon, on incrémente le compteur
            self.projectile_timer += 1

        for projectile in self.projectiles:  # On met à jour tout les projectiles de la tour
            projectile.update()
            if projectile.x > SCREEN_WIDTH:
                self.projectiles.remove(projectile)

    def delete(self):
        self.towers.remove(self)


class Attacker:
    def __init__(self, x, y):
        # Points de vie du attaquant
        self.health = 100
        # Chemin vers l'image du attaquant
        self.image_path = "assets/zombie.png"
        # Chargement de l'image
        self.image = load_image(self.image_path)
        # Redimensionnement de l'image à la taille d'une cellule de la grille
        self.image = py.transform.scale(self.image, (GRID_SIZE, GRID_SIZE))
        # Position sur l'axe x du attaquant
        self.x = x
        # Position sur l'axe y du attaquant
        self.y = y
        # Vitesse de déplacement du attaquant
        self.speed = 2

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        # On met à jour la position du attaquant en le déplaçant vers la gauche
        self.x -= self.speed


class Tombstone:
    def __init__(self, x, y):
        # Chemin vers l'image de la tombe
        self.image_path = "assets/tombstone.png"
        # Chargement de l'image
        self.image = load_image(self.image_path)
        # Redimensionnement de l'image à la taille d'une cellule de la grille
        self.image = py.transform.scale(self.image, (GRID_SIZE, GRID_SIZE))
        # Position sur l'axe x de la tombe
        self.x = x
        # Position sur l'axe y de la tombe
        self.y = y
        # Durée de vie de la tombe (3 secondes * 60 FPS)
        self.lifetime = 3 * 60

    def draw(self, screen):
        # On dessine l'image de la tombe
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        self.lifetime -= 1


class Game:
    """
    La classe principale du jeu, qui gère les événements, la logique et le rendu.
    """

    def __init__(self):
        """
        Constructeur de la classe Game.
        Cette fonction est appelée lorsqu'on crée un objet de type Game, et elle initialise les attributs de la classe à leur valeur par défaut.
        """
        self.screen = py.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))    # Création de la fenêtre, avec une taille de 500x500 pixels (largeur x hauteur)
        # Définition du titre de la fenêtre
        py.display.set_caption("Plants vs. Zombies")
        # Booléen qui indique si le jeu est en cours d'exécution ou non
        self.running = True
        # Score du joueur au début de la partie
        self.score = 100
        # Liste des tours
        self.towers = []
        # Liste des zombies
        self.attackers = []
        # Cellule sélectionnée par le joueur (pour placer une tour)
        self.selected_cell = None
        # Compteur pour l'apparition des zombies
        self.zombie_spawn_timer = 0
        # Création de la grille
        self.grid = create_grid()
        # Création d'un objet qui permet de gérer les IPS (images par seconde)
        self.fps = py.time.Clock()
        # Chemin vers l'image de la tour
        self.image_path = "assets/gameover.png"
        self.game_over_image = None
        self.kill = 0
        self.tombstones = []

    def events(self):
        """
        Cette fonction gère les événements enrégistrés par Pygame, comme le clic de la souris ou la fermeture de la fenêtre.
        """
        for event in py.event.get():
            if event.type == py.QUIT:  # Si dans les evenements pygame, il y a un événement de type QUIT, alors on arrête le jeu
                self.stop()
            x, y = py.mouse.get_pos()
            if event.type == py.MOUSEBUTTONDOWN:  # Si dans les evenements pygame, il y a un événement de type MOUSEBUTTONDOWN, et que l'on passe tout les checks, alors on place une tour
                for cell in self.grid:
                    # c'est une tuple de 2 nombres, le premier est la position en x, le deuxième est la position en y
                    cell_x, cell_y = cell
                    # print(cell_x, cell_y, x, y)
                    rectangle_cell = py.Rect(
                        cell_x, cell_y, GRID_SIZE, GRID_SIZE)
                    # Ici, on vérifie si les coordonnées de la cellule et les coordonnées de la souris se chevauchent
                    if rectangle_cell.collidepoint(x, y):
                        cell_occupied = False
                        for tower in self.towers:
                            rectangle_tower = py.Rect(
                                tower.x, tower.y, GRID_SIZE, GRID_SIZE)
                            if rectangle_tower.colliderect(rectangle_cell):
                                cell_occupied = True
                        # Placer une tour coûte 10 points et on ne peut pas placer une tour sur une cellule déjà occupée
                        if not cell_occupied and self.score >= 10:
                            self.towers.append(Tower(cell_x, cell_y))
                            print(cell)
                            self.score -= 10

    def update(self):
        """
        Cette fonction met à jour la logique du jeu, comme la position des zombies, des tours, etc.
        """

        for tower in self.towers:  # Mise à jour des tours
            tower.update()

        for attacker in self.attackers:  # Mise à jour des zombies
            attacker.update()

        for attacker in self.attackers:  # Ici l'on gère les collisions naïvement, en vérifiant si les coordonnées de tout les zombies avec toutes les tours
            for tower in self.towers:
                # Ici, on vérifie si les coordonnées de la tour et du attaquant qu'on compare se chevauchent
                if (tower.x == attacker.x and tower.y == attacker.y):
                    tower.health -= 20
                    if tower.health <= 0:
                        tower.delete()

        self.zombie_spawn_timer += 1
        # On fait apparaître un attaquant toutes les 5 secondes (possible grace à la limite de 60 images par seconde)
        if self.zombie_spawn_timer >= 150 and self.score > 0:
            # for valeur in range(5):
            self.attackers.append(Attacker(SCREEN_WIDTH, random.randint(
                0, (SCREEN_HEIGHT / GRID_SIZE) * GRID_SIZE)))
            # time.sleep(1)

            self.zombie_spawn_timer = 0
        for tombstone in self.tombstones:
            tombstone.update()
            if tombstone.lifetime <= 0:
                self.tombstones.remove(tombstone)

        for attacker in self.attackers:
            if attacker.x <= 0:
                print("Attaquant au bout")
                self.attackers.remove(attacker)
                self.score -= 10
            if self.score <= 0:
                self.game_over_image = load_image("assets/gameover.jpg")
                self.game_over_image = py.transform.scale(
                    self.game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.attackers = []
                self.towers = []
                if self.kill > data["best_score"]:
                    data["best_score"] = self.kill
                    with open("base.json", 'w') as jsonfile:
                        json.dump(data, jsonfile, indent=4)
            for tower in self.towers:
                for projectile in tower.projectiles:
                    projectile_rectangle = py.Rect(
                        projectile.x, projectile.y, 10, 10)
                    zombi_rectangle = py.Rect(
                        attacker.x, attacker.y, GRID_SIZE, GRID_SIZE)
                    tower_rectangle = py.Rect(
                        tower.x, tower.y, GRID_SIZE, GRID_SIZE)
                    if projectile_rectangle.colliderect(zombi_rectangle):
                        print("Collision")
                        self.kill += 1
                        self.attackers.remove(attacker)
                        tower.projectiles.remove(projectile)
                        self.tombstones.append(
                            Tombstone(attacker.x, attacker.y))

                    if zombi_rectangle.colliderect(tower_rectangle):
                        print("Collision attaquant et tour")
                        tower.health -= 50
                        print(tower.health)
                        if tower.health == 0:
                            self.towers.remove(tower)

        # Ajouter ici, toute la logique supplémentaire nécessaire pour mettre à jour le jeu et permettre son bon fonctionnement
        # -La collision entre les projectiles et les attaquants
        # -La collision entre tours et attaquants
        # -L'arrivée des attaquants à la fin de l'écran (dans un tower defense, c'est la fin de la partie)
        # -La gestion du score
        # -Quand un attaquant meurt, il doit être retiré de la liste des attaquants idem pour les tours
        # -etc.

    def draw(self):
        """
        Ici l'on dessine tout les éléments du jeu sur la fenêtre.
        L'order dans lequel les éléments sont dessinés est important, car il détermine l'ordre dans lequel les éléments sont affichés : les éléments dessinés en dernier sont affichés au dessus des autres.
        """
        self.screen.fill(WHITE)  # Appelé en premier pour avoir un fond blanc

        # Dessin de la grille avec des rectangles
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                py.draw.rect(self.screen, GREEN,
                             (x, y, GRID_SIZE, GRID_SIZE), 1)

        for tower in self.towers:  # Dessin les tours
            tower.draw(self.screen)

        for attacker in self.attackers:  # Dessin les attaquants
            attacker.draw(self.screen)

        for tombstone in self.tombstones:  # Dessin des tombes
            tombstone.draw(self.screen)

        # Dessin du score
        if self.game_over_image is not None:
            self.screen.blit(self.game_over_image, (0, 0))
        else:
            font = py.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
            self.screen.blit(score_text, (0, 0))
            score_text = font.render(
                f"Nombre kill: {self.kill}", True, (0, 0, 0))
            self.screen.blit(score_text, (0, 30))
            score_text = font.render(
                f"Meilleur score: " + str(data["best_score"]), True, (0, 0, 0))
            self.screen.blit(score_text, (0, 60))

        py.display.flip()

    def stop(self):
        self.running = False


def main():
    py.init()
    game = Game()

    while game.running:
        # On limite le nombre d'images par seconde à 60, pour que la vitesse du jeu soit la même sur tout les ordinateurs et ne soit pas dépendante de la puissance de l'ordinateur
        game.fps.tick(FPS)
        game.events()
        game.update()
        game.draw()

    py.quit()


if __name__ == "__main__":
    main()
