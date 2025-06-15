# interfaz_pygame.py (versión corregida)
import pygame
import sys
import math
import random
from core.grafo_trafico import GrafoTrafico, NodoGrafo
from core.vehiculos_simulacion import MotorSimulacion, Vehiculo
from core.algoritmos_dijkstra import AnalizadorTrafico

class InterfazTrafficSimulator:
    def __init__(self, ancho=1200, alto=800):
        pygame.init()
        self.ancho = ancho
        self.alto = alto
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Traffic Simulator")
        self.reloj = pygame.time.Clock()
        self.fps = 60

        self.colores = {
            'fondo': (40, 40, 40),
            'nodo': (100, 150, 255),
            'nodo_seleccionado': (255, 255, 100),
            'arista': (200, 200, 200),
            'arista_congestionada': (255, 100, 100),
            'arista_bloqueada': (255, 0, 0),
            'texto': (255, 255, 255),
            'panel': (60, 60, 60),
            'boton': (80, 120, 200),
            'boton_hover': (100, 140, 220),
            'vehiculo': (255, 255, 0),
            'ruta_optima': (0, 255, 0)
        }

        self.fuente_pequena = pygame.font.Font(None, 20)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_grande = pygame.font.Font(None, 32)

        self.grafo = GrafoTrafico()
        self.motor_simulacion = MotorSimulacion(self.grafo)
        self.analizador_trafico = AnalizadorTrafico(self.grafo)

        self.modo = "agregar_nodo"
        self.nodo_seleccionado = None
        self.mouse_pos = (0, 0)
        self.arrastrando = False
        self.offset_drag = (0, 0)

        self.panel_ancho = 250
        self.area_grafo = pygame.Rect(self.panel_ancho, 0, ancho - self.panel_ancho, alto)
        self.botones = self._crear_botones()

        self.ultimo_tiempo = pygame.time.get_ticks()

        self.mostrar_info = True
        self.mostrar_estadisticas = False
        self.ruta_mostrar = None

        self.contador_nodos = 0
        self.contador_vehiculos = 0

    def _crear_botones(self):
        botones = []
        y_pos = 20
        botones_config = [
            ("Agregar Nodo", "agregar_nodo"),
            ("Agregar Arista", "agregar_arista"),
            ("Simular", "simular"),
            ("Pausar/Reanudar", "pausar"),
            ("Reiniciar", "reiniciar"),
            ("Crear Vehículo", "crear_vehiculo"),
            ("Análisis Tráfico", "analizar"),
            ("Info ON/OFF", "toggle_info"),
            ("Limpiar Grafo", "limpiar")
        ]
        for texto, accion in botones_config:
            boton = {
                'rect': pygame.Rect(10, y_pos, self.panel_ancho - 20, 30),
                'texto': texto,
                'accion': accion,
                'hover': False
            }
            botones.append(boton)
            y_pos += 40
        return botones

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            tiempo_actual = pygame.time.get_ticks()
            delta_tiempo = (tiempo_actual - self.ultimo_tiempo) / 1000.0
            self.ultimo_tiempo = tiempo_actual

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False

            self.motor_simulacion.actualizar(delta_tiempo)
            self._renderizar()
            self.reloj.tick(self.fps)

        pygame.quit()
        sys.exit()

    def _renderizar(self):
        self.pantalla.fill(self.colores['fondo'])
        for nodo in self.grafo.nodos.obtener_valores():
            pygame.draw.circle(self.pantalla, self.colores['nodo'], (int(nodo.x), int(nodo.y)), 10)
            label = self.fuente_pequena.render(nodo.nombre, True, self.colores['texto'])
            self.pantalla.blit(label, (nodo.x + 10, nodo.y + 10))

        for arista in self.grafo.obtener_todas_aristas():
            pygame.draw.line(self.pantalla, self.colores['arista'], 
                             (arista.origen.x, arista.origen.y), 
                             (arista.destino.x, arista.destino.y), 2)

        for vehiculo in self.motor_simulacion.gestor_vehiculos.obtener_vehiculos_activos():
            pygame.draw.circle(self.pantalla, self.colores['vehiculo'], 
                               (int(vehiculo.posicion_x), int(vehiculo.posicion_y)), 6)

        pygame.display.flip()

if __name__ == "__main__":
    app = InterfazTrafficSimulator()
    app.ejecutar()