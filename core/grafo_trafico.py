# grafo_trafico.py
"""
Implementación del grafo para el simulador de tráfico
Usando estructuras de datos propias
"""

from core.estructuras_datos import ListaEnlazada, HashTable
import math

class NodoGrafo:
    """Representa un nodo del grafo (ciudad o punto de interés)"""
    def __init__(self, id_nodo, x, y, nombre=""):
        self.id = id_nodo
        self.x = x
        self.y = y
        self.nombre = nombre if nombre else f"Nodo_{id_nodo}"
        self.activo = True
        self.tipo = "ciudad"  # ciudad, intersección, punto_interés
    
    def __eq__(self, otro):
        return isinstance(otro, NodoGrafo) and self.id == otro.id
    
    def __str__(self):
        return f"Nodo({self.id}, {self.nombre}, ({self.x}, {self.y}))"

class AristaGrafo:
    """Representa una arista del grafo (carretera)"""
    def __init__(self, nodo_origen, nodo_destino, peso=1, bidireccional=True):
        self.origen = nodo_origen
        self.destino = nodo_destino
        self.peso_base = peso
        self.peso_actual = peso
        self.bidireccional = bidireccional
        self.bloqueada = False
        self.carga_trafico = 0  # Número de vehículos actuales
        self.capacidad_maxima = 10  # Capacidad máxima de vehículos
        self.tipo = "carretera"  # carretera, autopista, calle
    
    def calcular_peso_dinamico(self):
        """Calcula el peso dinámico basado en la carga de tráfico"""
        if self.bloqueada:
            return float('inf')
        
        factor_congestion = 1 + (self.carga_trafico / max(self.capacidad_maxima, 1)) * 2
        self.peso_actual = self.peso_base * factor_congestion
        return self.peso_actual
    
    def agregar_vehiculo(self):
        """Incrementa la carga de tráfico"""
        self.carga_trafico += 1
        self.calcular_peso_dinamico()
    
    def remover_vehiculo(self):
        """Decrementa la carga de tráfico"""
        if self.carga_trafico > 0:
            self.carga_trafico -= 1
            self.calcular_peso_dinamico()
    
    def obtener_distancia_euclidiana(self):
        """Calcula la distancia euclidiana entre nodos"""
        dx = self.destino.x - self.origen.x
        dy = self.destino.y - self.origen.y
        return math.sqrt(dx*dx + dy*dy)
    
    def __str__(self):
        direccion = "↔" if self.bidireccional else "→"
        return f"Arista({self.origen.id} {direccion} {self.destino.id}, peso={self.peso_actual:.2f})"

class GrafoTrafico:
    """Clase principal del grafo para el simulador de tráfico"""
    def __init__(self):
        self.nodos = HashTable()  # id_nodo -> NodoGrafo
        self.lista_adyacencia = HashTable()  # id_nodo -> ListaEnlazada de aristas
        self.contador_nodos = 0
        self.aristas_totales = 0
    
    def agregar_nodo(self, x, y, nombre=""):
        """Agrega un nuevo nodo al grafo"""
        self.contador_nodos += 1
        nuevo_nodo = NodoGrafo(self.contador_nodos, x, y, nombre)
        self.nodos.insertar(self.contador_nodos, nuevo_nodo)
        self.lista_adyacencia.insertar(self.contador_nodos, ListaEnlazada())
        return nuevo_nodo
    
    def agregar_arista(self, id_origen, id_destino, peso=1, bidireccional=True):
        """Agrega una arista entre dos nodos"""
        nodo_origen = self.nodos.obtener(id_origen)
        nodo_destino = self.nodos.obtener(id_destino)
        
        if not nodo_origen or not nodo_destino:
            return False
        
        # Calcular peso basado en distancia euclidiana si no se especifica
        if peso == 1:
            dx = nodo_destino.x - nodo_origen.x
            dy = nodo_destino.y - nodo_origen.y
            peso = math.sqrt(dx*dx + dy*dy) / 50  # Normalizar distancia
        
        # Crear arista de origen a destino
        arista = AristaGrafo(nodo_origen, nodo_destino, peso, bidireccional)
        lista_origen = self.lista_adyacencia.obtener(id_origen)
        lista_origen.agregar(arista)
        
        # Si es bidireccional, crear arista inversa
        if bidireccional:
            arista_inversa = AristaGrafo(nodo_destino, nodo_origen, peso, True)
            lista_destino = self.lista_adyacencia.obtener(id_destino)
            lista_destino.agregar(arista_inversa)
        
        self.aristas_totales += 1
        return True
    
    def eliminar_nodo(self, id_nodo):
        """Elimina un nodo y todas sus aristas"""
        if not self.nodos.contiene(id_nodo):
            return False
        
        # Eliminar todas las aristas que llegan a este nodo
        for id_otros in self.nodos.obtener_claves():
            if id_otros != id_nodo:
                self._eliminar_aristas_hacia_nodo(id_otros, id_nodo)
        
        # Eliminar el nodo y su lista de adyacencia
        self.nodos.eliminar(id_nodo)
        self.lista_adyacencia.eliminar(id_nodo)
        return True
    
    def _eliminar_aristas_hacia_nodo(self, id_origen, id_destino):
        """Elimina aristas específicas desde un nodo hacia otro"""
        lista_aristas = self.lista_adyacencia.obtener(id_origen)
        if lista_aristas:
            aristas_a_eliminar = []
            for arista in lista_aristas.obtener_lista():
                if arista.destino.id == id_destino:
                    aristas_a_eliminar.append(arista)
            
            for arista in aristas_a_eliminar:
                lista_aristas.eliminar(arista)
    
    def obtener_vecinos(self, id_nodo):
        """Obtiene los nodos vecinos de un nodo dado"""
        lista_aristas = self.lista_adyacencia.obtener(id_nodo)
        if not lista_aristas:
            return []
        
        vecinos = []
        for arista in lista_aristas.obtener_lista():
            if not arista.bloqueada and arista.destino.activo:
                vecinos.append((arista.destino, arista.peso_actual))
        return vecinos
    
    def obtener_aristas_nodo(self, id_nodo):
        """Obtiene todas las aristas que salen de un nodo"""
        lista_aristas = self.lista_adyacencia.obtener(id_nodo)
        return lista_aristas.obtener_lista() if lista_aristas else []
    
    def bloquear_arista(self, id_origen, id_destino):
        """Bloquea una arista específica"""
        aristas = self.obtener_aristas_nodo(id_origen)
        for arista in aristas:
            if arista.destino.id == id_destino:
                arista.bloqueada = True
                return True
        return False
    
    def desbloquear_arista(self, id_origen, id_destino):
        """Desbloquea una arista específica"""
        aristas = self.obtener_aristas_nodo(id_origen)
        for arista in aristas:
            if arista.destino.id == id_destino:
                arista.bloqueada = False
                return True
        return False
    
    def obtener_nodos_lista(self):
        """Retorna todos los nodos como lista"""
        return self.nodos.obtener_valores()
    
    def obtener_todas_aristas(self):
        """Retorna todas las aristas del grafo"""
        todas_aristas = []
        for id_nodo in self.nodos.obtener_claves():
            aristas = self.obtener_aristas_nodo(id_nodo)
            todas_aristas.extend(aristas)
        return todas_aristas
    
    def obtener_nodo_por_posicion(self, x, y, tolerancia=20):
        """Encuentra un nodo cerca de una posición dada"""
        for nodo in self.nodos.obtener_valores():
            distancia = math.sqrt((nodo.x - x)**2 + (nodo.y - y)**2)
            if distancia <= tolerancia:
                return nodo
        return None
    
    def validar_integridad(self):
        """Valida la integridad del grafo"""
        problemas = []
        
        # Verificar que todos los nodos en aristas existen
        for arista in self.obtener_todas_aristas():
            if not self.nodos.contiene(arista.origen.id):
                problemas.append(f"Nodo origen {arista.origen.id} no existe")
            if not self.nodos.contiene(arista.destino.id):
                problemas.append(f"Nodo destino {arista.destino.id} no existe")
        
        return problemas
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del grafo"""
        nodos_activos = sum(1 for nodo in self.nodos.obtener_valores() if nodo.activo)
        aristas_activas = sum(1 for arista in self.obtener_todas_aristas() if not arista.bloqueada)
        aristas_congestionadas = sum(1 for arista in self.obtener_todas_aristas() 
                                   if arista.carga_trafico > arista.capacidad_maxima * 0.8)
        
        return {
            'total_nodos': len(self.nodos.obtener_claves()),
            'nodos_activos': nodos_activos,
            'total_aristas': len(self.obtener_todas_aristas()),
            'aristas_activas': aristas_activas,
            'aristas_congestionadas': aristas_congestionadas
        }