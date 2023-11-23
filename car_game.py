import pygame
from pygame.locals import *
import random

pygame.init()

# Creamos la pantalla principal
width = 500 #dimensiones de nuestra pantalla
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Juego de carreras')

# colores en RGB
gris = (32, 32, 32)
verde = (0, 51, 0)
rojo = (200, 0, 0)
blanco = (255, 255, 255)
amarillo = (255, 232, 0)

# Delcarar variables y tamaños
rodada = 300
ancho_bordes = 10
altura_bordes = 50

# coordenadas declaracion
izquierda = 150
centro = 250
derecha = 350
carriles = [izquierda, centro, derecha]

#bordes de las carreteras
road = (100, 0, rodada, height)
left_edge_marker = (95, 0, ancho_bordes, height)
right_edge_marker = (395, 0, ancho_bordes, height)

# animacion de los carriles con respecto al movimiento en y
lane_marker_move_y = 0

# cordenadas donde empezara el jugo
player_x = 250
player_y = 400

clock = pygame.time.Clock()
fps = 120

# variables del juego
juegofin = False
velocidad = 2
score = 0
class Vehicle(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Reducimos el ancho de la imagen para que no sea mas grande que el carril
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)


#funciones de pygame
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

player = PlayerVehicle(player_x, player_y)
player_group.add(player)

#Cargamos imaenes de los vehculos
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# cargamos imagen del choque
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

avanzar = True
while avanzar:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            avanzar = False
        if event.type == KEYDOWN:

            if event.key == K_LEFT and player.rect.center[0] > izquierda:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < derecha:
                player.rect.x += 100

            # Despues de un choque revisar los carriles
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):

                    juegofin = True

                    #Colocamos el automovil junto a otro al momento del choque y tambien la imagen del choque
                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

    screen.fill(verde)

    pygame.draw.rect(screen, gris, road)
    pygame.draw.rect(screen, amarillo, left_edge_marker)
    pygame.draw.rect(screen, amarillo, right_edge_marker)

    # dibujar lineas de los carriles
    lane_marker_move_y += velocidad * 2
    if lane_marker_move_y >= altura_bordes * 2:
        lane_marker_move_y = 0
    for y in range(altura_bordes * -2, height, altura_bordes * 2):
        pygame.draw.rect(screen, blanco, (izquierda + 45, y + lane_marker_move_y, ancho_bordes, altura_bordes))
        pygame.draw.rect(screen, blanco, (centro + 45, y + lane_marker_move_y, ancho_bordes, altura_bordes))

    player_group.draw(screen)

    if len(vehicle_group) < 2:
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:

            lane = random.choice(carriles)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    # Mover los vehiculos
    for vehicle in vehicle_group:
        vehicle.rect.y += velocidad

        # Si el vehiculo sobre pasa la altura del juego pierde
        if vehicle.rect.top >= height:
            vehicle.kill()

            # Arreglo para aumento de la puntuacion
            score += 1

            # Condicion tras haber pasado 5 vehiculos cambia la velocidad
            if score > 0 and score % 3 == 0:
                velocidad += 3

    #  Se dibujan los vehiculos que estaran saliendo
    vehicle_group.draw(screen)

    # Pantalla de la puntuación
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Puntuación: ' + str(score), True, blanco)
    text_rect = text.get_rect()
    text_rect.center = (50, 400)
    screen.blit(text, text_rect)

    # Condicional si choco el auto o no
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        juegofin = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    # Aqui se hace el "display" cuando se pierde ( cambio de pantalla)
    if juegofin:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, rojo, (0, 50, width, 100))
#tipos de letras y texto que dira
        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        text = font.render('Lastima perdiste, ¿Quieres jugar de nuevo?(Escibe Y para continuar o N para salir)', True, blanco)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

    pygame.display.update()

    # Esperar que el usuario si va a seguir o se va a quedar
    while juegofin:

        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                juegofin = False
                avanzar = False

            # Respuesta optenida S o N
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # Restear el juego nuevamente
                    juegofin = False
                    velocidad = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # Salimos del ciclo de arriba
                    juegofin = False
                    avanzar = False

pygame.quit()
