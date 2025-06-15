# vehiculos_simulacion.py
"""
Sistema de vehículos y motor de simulación para el Traffic Simulator
"""

import math
import random
from core.estructuras_datos import ListaEnlazada, HashTable
from core.algoritmos_dijkstra import AlgoritmoDijkstra

class Vehiculo:
    """Representa un vehículo en la simulación"""
    
    def __init__(self, id_vehiculo, nodo_origen, nodo_destino):
        self.id = id_vehiculo
        self.nodo_origen = nodo_origen
        self.nodo_destino = nodo_destino
        self.posicion_x = nodo_origen.x
        self.posicion_y = nodo_origen.y
        self.velocidad = random.uniform(30, 60)  # Velocidad en píxeles por segundo
        self.estado = "planificando"  # planificando, viajando, arribado, bloqueado
        self.ruta_nodos = []
        self.ruta_aristas = []
        self.indice_ruta_actual = 0
        self.progreso_arista = 0.0  # Progreso en la arista actual (0.0 a 1.0)
        self.tiempo_espera = 0
        self.distancia_total = 0
        self.tiempo_viaje = 0
        self.color = self._generar_color_aleatorio()
        self.tipo = random.choice(["auto", "camion", "bus"])
        self.prioridad = 1  # Para futuros algoritmos de prioridad
    
    def _generar_color_aleatorio(self):
        """Genera un color aleatorio para el vehículo"""
        colores = [
            (255, 0, 0),    # Rojo
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Azul
            (255, 255, 0),  # Amarillo
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 128, 0),  # Naranja
            (128, 0, 255),  # Púrpura
        ]
        return random.choice(colores)
    
    def establecer_ruta(self, ruta_nodos, ruta_aristas, distancia_total):
        """Establece la ruta que seguirá el vehículo"""
        self.ruta_nodos = ruta_nodos
        self.ruta_aristas = ruta_aristas
        self.distancia_total = distancia_total
        self.indice_ruta_actual = 0
        self.progreso_arista = 0.0
        self.estado = "viajando" if ruta_nodos else "bloqueado"
    
    def actualizar_posicion(self, delta_tiempo):
        """Actualiza la posición del vehículo basada en el tiempo transcurrido"""
        if self.estado != "viajando" or not self.ruta_aristas:
            return
        
        # Verificar si hemos llegado al destino
        if self.indice_ruta_actual >= len(self.ruta_aristas):
            self.estado = "arribado"
            self.posicion_x = self.nodo_destino.x
            self.posicion_y = self.nodo_destino.y
            return
        
        # Obtener la arista actual
        arista_actual = self.ruta_aristas[self.indice_ruta_actual]
        
        # Calcular distancia a recorrer en esta actualización
        distancia_movimiento = self.velocidad * delta_tiempo
        distancia_arista = arista_actual.obtener_distancia_euclidiana()
        
        # Calcular cuánto avanzamos en la arista (como proporción)
        progreso_incremento = distancia_movimiento / max(distancia_arista, 1)
        self.progreso_arista += progreso_incremento
        
        # Si completamos la arista actual
        if self.progreso_arista >= 1.0:
            # Remover vehículo de la arista actual
            arista_actual.remover_vehiculo()
            
            # Avanzar a la siguiente arista
            self.indice_ruta_actual += 1
            self.progreso_arista = 0.0
            
            # Si hay más aristas, agregar vehículo a la siguiente
            if self.indice_ruta_actual < len(self.ruta_aristas):
                siguiente_arista = self.ruta_aristas[self.indice_ruta_actual]
                siguiente_arista.agregar_vehiculo()
        
        # Calcular posición interpolada
        if self.indice_ruta_actual < len(self.ruta_aristas):
            arista_actual = self.ruta_aristas[self.indice_ruta_actual]
            self._interpolar_posicion(arista_actual)
        
        self.tiempo_viaje += delta_tiempo
    
    def _interpolar_posicion(self, arista):
        """Interpola la posición del vehículo en una arista"""
        origen = arista.origen
        destino = arista.destino
        
        # Interpolación lineal
        self.posicion_x = origen.x + (destino.x - origen.x) * self.progreso_arista
        self.posicion_y = origen.y + (destino.y - origen.y) * self.progreso_arista
    
    def obtener_estado_detallado(self):
        """Obtiene información detallada del estado del vehículo"""
        return {
            'id': self.id,
            'estado': self.estado,
            'posicion': (self.posicion_x, self.posicion_y),
            'origen': self.nodo_origen.nombre,
            'destino': self.nodo_destino.nombre,
            'progreso_total': self._calcular_progreso_total(),
            'tiempo_viaje': self.tiempo_viaje,
            'velocidad': self.velocidad,
            'tipo': self.tipo
        }
    
    def _calcular_progreso_total(self):
        """Calcula el progreso total del viaje (0.0 a 1.0)"""
        if not self.ruta_aristas:
            return 0.0
        
        if self.estado == "arribado":
            return 1.0
        
        aristas_completadas = self.indice_ruta_actual
        progreso_arista_actual = self.progreso_arista
        total_aristas = len(self.ruta_aristas)
        
        if total_aristas == 0:
            return 0.0
        
        return (aristas_completadas + progreso_arista_actual) / total_aristas

class GestorVehiculos:
    """Gestor para manejar múltiples vehículos en la simulación"""
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.dijkstra = AlgoritmoDijkstra(grafo)
        self.vehiculos = HashTable()  # id_vehiculo -> Vehiculo
        self.contador_vehiculos = 0
        self.vehiculos_activos = ListaEnlazada()
        self.vehiculos_completados = ListaEnlazada()
        self.estadisticas = {
            'total_creados': 0,
            'total_completados': 0,
            'tiempo_promedio_viaje': 0,
            'vehiculos_bloqueados': 0
        }
    
    def crear_vehiculo_aleatorio(self):
        """Crea un vehículo con origen y destino aleatorios"""
        nodos = self.grafo.obtener_nodos_lista()
        if len(nodos) < 2:
            return None
        
        nodo_origen = random.choice(nodos)
        nodo_destino = random.choice(nodos)
        
        # Asegurar que origen y destino sean diferentes
        while nodo_destino.id == nodo_origen.id:
            nodo_destino = random.choice(nodos)
        
        return self.crear_vehiculo(nodo_origen.id, nodo_destino.id)
    
    def crear_vehiculo(self, id_origen, id_destino):
        """Crea un vehículo específico"""
        nodo_origen = self.grafo.nodos.obtener(id_origen)
        nodo_destino = self.grafo.nodos.obtener(id_destino)
        
        if not nodo_origen or not nodo_destino:
            return None
        
        self.contador_vehiculos += 1
        vehiculo = Vehiculo(self.contador_vehiculos, nodo_origen, nodo_destino)
        
        # Calcular ruta
        distancia, ruta_nodos, ruta_aristas = self.dijkstra.encontrar_ruta_mas_corta(
            id_origen, id_destino
        )
        
        if ruta_nodos:
            vehiculo.establecer_ruta(ruta_nodos, ruta_aristas, distancia)
            # Agregar vehículo a la primera arista
            if ruta_aristas:
                ruta_aristas[0].agregar_vehiculo()
        else:
            vehiculo.estado = "bloqueado"
            self.estadisticas['vehiculos_bloqueados'] += 1
        
        # Registrar vehículo
        self.vehiculos.insertar(vehiculo.id, vehiculo)
        self.vehiculos_activos.agregar(vehiculo)
        self.estadisticas['total_creados'] += 1
        
        return vehiculo
    
    def actualizar_simulacion(self, delta_tiempo):
        """Actualiza todos los vehículos en la simulación"""
        vehiculos_a_procesar = self.vehiculos_activos.obtener_lista().copy()
        
        for vehiculo in vehiculos_a_procesar:
            estado_anterior = vehiculo.estado
            vehiculo.actualizar_posicion(delta_tiempo)
            
            # Si el vehículo completó su viaje
            if vehiculo.estado == "arribado" and estado_anterior != "arribado":
                self._procesar_vehiculo_completado(vehiculo)
    
    def _procesar_vehiculo_completado(self, vehiculo):
        """Procesa un vehículo que ha completado su viaje"""
        self.vehiculos_activos.eliminar(vehiculo)
        self.vehiculos_completados.agregar(vehiculo)
        self.estadisticas['total_completados'] += 1
        
        # Actualizar tiempo promedio de viaje
        total_tiempo = 0
        count = 0
        for v_completado in self.vehiculos_completados.obtener_lista():
            total_tiempo += v_completado.tiempo_viaje
            count += 1
        
        if count > 0:
            self.estadisticas['tiempo_promedio_viaje'] = total_tiempo / count
    
    def obtener_vehiculos_activos(self):
        """Obtiene lista de vehículos activos"""
        return self.vehiculos_activos.obtener_lista()
    
    def obtener_vehiculos_en_area(self, x, y, radio):
        """Obtiene vehículos dentro de un área específica"""
        vehiculos_en_area = []
        for vehiculo in self.vehiculos_activos.obtener_lista():
            distancia = math.sqrt(
                (vehiculo.posicion_x - x)**2 + (vehiculo.posicion_y - y)**2
            )
            if distancia <= radio:
                vehiculos_en_area.append(vehiculo)
        return vehiculos_en_area
    
    def eliminar_vehiculo(self, id_vehiculo):
        """Elimina un vehículo de la simulación"""
        vehiculo = self.vehiculos.obtener(id_vehiculo)
        if vehiculo:
            # Remover de arista actual si está viajando
            if (vehiculo.estado == "viajando" and 
                vehiculo.indice_ruta_actual < len(vehiculo.ruta_aristas)):
                arista_actual = vehiculo.ruta_aristas[vehiculo.indice_ruta_actual]
                arista_actual.remover_vehiculo()
            
            # Remover de listas
            self.vehiculos_activos.eliminar(vehiculo)
            self.vehiculos.eliminar(id_vehiculo)
            return True
        return False
    
    def limpiar_vehiculos_completados(self):
        """Limpia vehículos que han completado su viaje"""
        vehiculos_completados = self.vehiculos_completados.obtener_lista()
        for vehiculo in vehiculos_completados:
            self.vehiculos.eliminar(vehiculo.id)
        
        # Crear nueva lista vacía
        self.vehiculos_completados = ListaEnlazada()
    
    def obtener_estadisticas_detalladas(self):
        """Obtiene estadísticas detalladas de la simulación"""
        vehiculos_por_estado = {
            'planificando': 0,
            'viajando': 0,
            'arribado': 0,
            'bloqueado': 0
        }
        
        for vehiculo in self.vehiculos.obtener_valores():
            vehiculos_por_estado[vehiculo.estado] += 1
        
        return {
            **self.estadisticas,
            'vehiculos_por_estado': vehiculos_por_estado,
            'vehiculos_activos_count': self.vehiculos_activos.obtener_tamaño(),
            'vehiculos_completados_count': self.vehiculos_completados.obtener_tamaño()
        }

class MotorSimulacion:
    """Motor principal de la simulación de tráfico"""
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.gestor_vehiculos = GestorVehiculos(grafo)
        self.tiempo_simulacion = 0
        self.velocidad_simulacion = 1.0  # Multiplicador de velocidad
        self.pausado = False
        self.configuracion = {
            'vehiculos_por_minuto': 5,
            'tiempo_entre_vehiculos': 12.0,  # segundos
            'max_vehiculos_simultaneos': 50
        }
        self.tiempo_ultimo_vehiculo = 0
    
    def actualizar(self, delta_tiempo_real):
        """Actualiza la simulación"""
        if self.pausado:
            return
        
        # Aplicar velocidad de simulación
        delta_tiempo = delta_tiempo_real * self.velocidad_simulacion
        self.tiempo_simulacion += delta_tiempo
        
        # Crear nuevos vehículos según configuración
        self._generar_vehiculos_automaticos(delta_tiempo)
        
        # Actualizar todos los vehículos
        self.gestor_vehiculos.actualizar_simulacion(delta_tiempo)
        
        # Actualizar pesos dinámicos de aristas
        self._actualizar_pesos_dinamicos()
    
    def _generar_vehiculos_automaticos(self, delta_tiempo):
        """Genera vehículos automáticamente según la configuración"""
        vehiculos_activos = len(self.gestor_vehiculos.obtener_vehiculos_activos())
        
        if (vehiculos_activos < self.configuracion['max_vehiculos_simultaneos'] and
            self.tiempo_simulacion - self.tiempo_ultimo_vehiculo >= 
            self.configuracion['tiempo_entre_vehiculos']):
            
            vehiculo = self.gestor_vehiculos.crear_vehiculo_aleatorio()
            if vehiculo:
                self.tiempo_ultimo_vehiculo = self.tiempo_simulacion
    
    def _actualizar_pesos_dinamicos(self):
        """Actualiza los pesos dinámicos de todas las aristas"""
        for arista in self.grafo.obtener_todas_aristas():
            arista.calcular_peso_dinamico()
    
    def pausar_reanudar(self):
        """Pausa o reanuda la simulación"""
        self.pausado = not self.pausado
    
    def establecer_velocidad(self, velocidad):
        """Establece la velocidad de simulación"""
        self.velocidad_simulacion = max(0.1, min(10.0, velocidad))
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación"""
        # Limpiar todos los vehículos
        for vehiculo in self.gestor_vehiculos.vehiculos.obtener_valores():
            self.gestor_vehiculos.eliminar_vehiculo(vehiculo.id)
        
        # Resetear aristas
        for arista in self.grafo.obtener_todas_aristas():
            arista.carga_trafico = 0
            arista.calcular_peso_dinamico()
        
        # Resetear tiempos
        self.tiempo_simulacion = 0
        self.tiempo_ultimo_vehiculo = 0
        
        # Resetear estadísticas
        self.gestor_vehiculos.estadisticas = {
            'total_creados': 0,
            'total_completados': 0,
            'tiempo_promedio_viaje': 0,
            'vehiculos_bloqueados': 0
        }
    
    def obtener_estado_completo(self):
        """Obtiene el estado completo de la simulación"""
        return {
            'tiempo_simulacion': self.tiempo_simulacion,
            'velocidad_simulacion': self.velocidad_simulacion,
            'pausado': self.pausado,
            'estadisticas_vehiculos': self.gestor_vehiculos.obtener_estadisticas_detalladas(),
            'estadisticas_grafo': self.grafo.obtener_estadisticas(),
            'vehiculos_activos': len(self.gestor_vehiculos.obtener_vehiculos_activos())
        }