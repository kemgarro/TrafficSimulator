# algoritmos_dijkstra.py
"""
Implementación del algoritmo de Dijkstra para encontrar rutas más cortas
Usando estructuras de datos propias
"""

from core.estructuras_datos import ColaPrioridad, HashTable, ListaEnlazada
from core.grafo_trafico import GrafoTrafico

class AlgoritmoDijkstra:
    """Implementación del algoritmo de Dijkstra"""
    
    def __init__(self, grafo):
        self.grafo = grafo
    
    def encontrar_ruta_mas_corta(self, id_origen, id_destino):
        """
        Encuentra la ruta más corta entre dos nodos
        Retorna: (distancia_total, ruta_nodos, ruta_aristas)
        """
        # Validar que los nodos existen
        if (not self.grafo.nodos.contiene(id_origen) or 
            not self.grafo.nodos.contiene(id_destino)):
            return None, [], []
        
        # Inicializar estructuras
        distancias = HashTable()
        predecesores = HashTable()
        visitados = HashTable()
        cola_prioridad = ColaPrioridad()
        
        # Inicializar distancias
        for id_nodo in self.grafo.nodos.obtener_claves():
            distancias.insertar(id_nodo, float('inf'))
            predecesores.insertar(id_nodo, None)
            visitados.insertar(id_nodo, False)
        
        # Distancia al nodo origen es 0
        distancias.insertar(id_origen, 0)
        cola_prioridad.insertar(0, id_origen)
        
        while not cola_prioridad.es_vacia():
            # Extraer nodo con menor distancia
            distancia_actual, nodo_actual = cola_prioridad.extraer_min()
            
            # Si ya fue visitado, continuar
            if visitados.obtener(nodo_actual):
                continue
            
            # Marcar como visitado
            visitados.insertar(nodo_actual, True)
            
            # Si llegamos al destino, terminar
            if nodo_actual == id_destino:
                break
            
            # Examinar vecinos
            vecinos = self.grafo.obtener_vecinos(nodo_actual)
            for nodo_vecino, peso_arista in vecinos:
                id_vecino = nodo_vecino.id
                
                if visitados.obtener(id_vecino):
                    continue
                
                # Calcular nueva distancia
                nueva_distancia = distancia_actual + peso_arista
                
                if nueva_distancia < distancias.obtener(id_vecino):
                    distancias.insertar(id_vecino, nueva_distancia)
                    predecesores.insertar(id_vecino, nodo_actual)
                    cola_prioridad.insertar(nueva_distancia, id_vecino)
        
        # Reconstruir ruta
        ruta_nodos, ruta_aristas = self._reconstruir_ruta(
            predecesores, id_origen, id_destino
        )
        
        distancia_total = distancias.obtener(id_destino)
        if distancia_total == float('inf'):
            return None, [], []
        
        return distancia_total, ruta_nodos, ruta_aristas
    
    def _reconstruir_ruta(self, predecesores, id_origen, id_destino):
        """Reconstruye la ruta desde los predecesores"""
        ruta_nodos = []
        ruta_aristas = []
        
        # Reconstruir desde destino hacia origen
        nodo_actual = id_destino
        while nodo_actual is not None:
            ruta_nodos.append(nodo_actual)
            predecesor = predecesores.obtener(nodo_actual)
            
            if predecesor is not None:
                # Encontrar la arista entre predecesor y nodo actual
                arista = self._encontrar_arista(predecesor, nodo_actual)
                if arista:
                    ruta_aristas.append(arista)
            
            nodo_actual = predecesor
        
        # Invertir para obtener ruta de origen a destino
        ruta_nodos.reverse()
        ruta_aristas.reverse()
        
        return ruta_nodos, ruta_aristas
    
    def _encontrar_arista(self, id_origen, id_destino):
        """Encuentra la arista entre dos nodos"""
        aristas = self.grafo.obtener_aristas_nodo(id_origen)
        for arista in aristas:
            if arista.destino.id == id_destino:
                return arista
        return None
    
    def encontrar_rutas_multiples(self, id_origen, destinos):
        """
        Encuentra rutas más cortas desde un origen hacia múltiples destinos
        Útil para optimizar cuando hay muchos vehículos desde el mismo punto
        """
        rutas = {}
        
        # Ejecutar Dijkstra una vez desde el origen
        distancias = HashTable()
        predecesores = HashTable()
        visitados = HashTable()
        cola_prioridad = ColaPrioridad()
        
        # Inicializar
        for id_nodo in self.grafo.nodos.obtener_claves():
            distancias.insertar(id_nodo, float('inf'))
            predecesores.insertar(id_nodo, None)
            visitados.insertar(id_nodo, False)
        
        distancias.insertar(id_origen, 0)
        cola_prioridad.insertar(0, id_origen)
        
        while not cola_prioridad.es_vacia():
            distancia_actual, nodo_actual = cola_prioridad.extraer_min()
            
            if visitados.obtener(nodo_actual):
                continue
            
            visitados.insertar(nodo_actual, True)
            
            vecinos = self.grafo.obtener_vecinos(nodo_actual)
            for nodo_vecino, peso_arista in vecinos:
                id_vecino = nodo_vecino.id
                
                if visitados.obtener(id_vecino):
                    continue
                
                nueva_distancia = distancia_actual + peso_arista
                
                if nueva_distancia < distancias.obtener(id_vecino):
                    distancias.insertar(id_vecino, nueva_distancia)
                    predecesores.insertar(id_vecino, nodo_actual)
                    cola_prioridad.insertar(nueva_distancia, id_vecino)
        
        # Reconstruir rutas para cada destino
        for id_destino in destinos:
            if distancias.obtener(id_destino) != float('inf'):
                ruta_nodos, ruta_aristas = self._reconstruir_ruta(
                    predecesores, id_origen, id_destino
                )
                rutas[id_destino] = {
                    'distancia': distancias.obtener(id_destino),
                    'ruta_nodos': ruta_nodos,
                    'ruta_aristas': ruta_aristas
                }
        
        return rutas

class AnalizadorTrafico:
    """Analizador para identificar puntos críticos del tráfico"""
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.dijkstra = AlgoritmoDijkstra(grafo)
    
    def identificar_puntos_criticos(self):
        """
        Identifica puntos críticos del tráfico usando varios métodos:
        1. Nodos con mayor centralidad de intermediación
        2. Aristas más congestionadas
        3. Nodos con mayor conectividad
        """
        puntos_criticos = {
            'nodos_centrales': self._calcular_centralidad_intermediacion(),
            'aristas_congestionadas': self._identificar_aristas_congestionadas(),
            'nodos_conectados': self._identificar_nodos_muy_conectados(),
            'cuellos_botella': self._identificar_cuellos_botella()
        }
        
        return puntos_criticos
    
    def _calcular_centralidad_intermediacion(self):
        """Calcula la centralidad de intermediación de cada nodo"""
        centralidad = HashTable()
        nodos = self.grafo.obtener_nodos_lista()
        
        # Inicializar centralidad
        for nodo in nodos:
            centralidad.insertar(nodo.id, 0)
        
        # Para cada par de nodos, calcular rutas más cortas
        for i, nodo_s in enumerate(nodos):
            for j, nodo_t in enumerate(nodos):
                if i != j:
                    _, ruta_nodos, _ = self.dijkstra.encontrar_ruta_mas_corta(
                        nodo_s.id, nodo_t.id
                    )
                    
                    # Incrementar centralidad de nodos intermedios
                    for k in range(1, len(ruta_nodos) - 1):
                        id_intermedio = ruta_nodos[k]
                        valor_actual = centralidad.obtener(id_intermedio)
                        centralidad.insertar(id_intermedio, valor_actual + 1)
        
        # Convertir a lista ordenada
        nodos_centrales = []
        for nodo in nodos:
            valor = centralidad.obtener(nodo.id)
            nodos_centrales.append((nodo, valor))
        
        # Ordenar por centralidad (implementación simple de ordenamiento)
        return self._ordenar_por_valor(nodos_centrales, reverso=True)[:5]
    
    def _identificar_aristas_congestionadas(self):
        """Identifica las aristas más congestionadas"""
        aristas = self.grafo.obtener_todas_aristas()
        aristas_congestionadas = []
        
        for arista in aristas:
            if arista.carga_trafico > 0:
                porcentaje_congestion = (arista.carga_trafico / 
                                       max(arista.capacidad_maxima, 1)) * 100
                aristas_congestionadas.append((arista, porcentaje_congestion))
        
        return self._ordenar_por_valor(aristas_congestionadas, reverso=True)[:5]
    
    def _identificar_nodos_muy_conectados(self):
        """Identifica nodos con mayor número de conexiones"""
        nodos = self.grafo.obtener_nodos_lista()
        nodos_conectados = []
        
        for nodo in nodos:
            aristas = self.grafo.obtener_aristas_nodo(nodo.id)
            num_conexiones = len(aristas)
            nodos_conectados.append((nodo, num_conexiones))
        
        return self._ordenar_por_valor(nodos_conectados, reverso=True)[:5]
    
    def _identificar_cuellos_botella(self):
        """Identifica cuellos de botella eliminando aristas críticas"""
        cuellos_botella = []
        aristas = self.grafo.obtener_todas_aristas()
        
        for arista in aristas:
            # Temporalmente bloquear la arista
            estaba_bloqueada = arista.bloqueada
            arista.bloqueada = True
            
            # Intentar encontrar ruta alternativa
            distancia_sin_arista, _, _ = self.dijkstra.encontrar_ruta_mas_corta(
                arista.origen.id, arista.destino.id
            )
            
            # Restaurar estado de la arista
            arista.bloqueada = estaba_bloqueada
            
            # Si no hay ruta alternativa o es mucho más larga, es cuello de botella
            distancia_con_arista = arista.peso_actual
            if (distancia_sin_arista is None or 
                distancia_sin_arista > distancia_con_arista * 2):
                cuellos_botella.append(arista)
        
        return cuellos_botella[:5]
    
    def _ordenar_por_valor(self, lista, reverso=False):
        """Ordenamiento simple por burbuja basado en el segundo elemento de tuplas"""
        n = len(lista)
        for i in range(n):
            for j in range(0, n - i - 1):
                if reverso:
                    if lista[j][1] < lista[j + 1][1]:
                        lista[j], lista[j + 1] = lista[j + 1], lista[j]
                else:
                    if lista[j][1] > lista[j + 1][1]:
                        lista[j], lista[j + 1] = lista[j + 1], lista[j]
        return lista
    
    def generar_reporte_trafico(self):
        """Genera un reporte completo del estado del tráfico"""
        estadisticas = self.grafo.obtener_estadisticas()
        puntos_criticos = self.identificar_puntos_criticos()
        
        reporte = {
            'estadisticas_generales': estadisticas,
            'puntos_criticos': puntos_criticos,
            'recomendaciones': self._generar_recomendaciones(puntos_criticos)
        }
        
        return reporte
    
    def _generar_recomendaciones(self, puntos_criticos):
        """Genera recomendaciones basadas en el análisis de tráfico"""
        recomendaciones = []
        
        # Recomendaciones para nodos centrales
        if puntos_criticos['nodos_centrales']:
            nodo_mas_central = puntos_criticos['nodos_centrales'][0][0]
            recomendaciones.append(
                f"Considerar ampliar la capacidad del nodo {nodo_mas_central.nombre} "
                f"(ID: {nodo_mas_central.id}) - es un punto de paso crítico"
            )
        
        # Recomendaciones para aristas congestionadas
        if puntos_criticos['aristas_congestionadas']:
            arista_congestionada = puntos_criticos['aristas_congestionadas'][0][0]
            recomendaciones.append(
                f"La carretera entre {arista_congestionada.origen.nombre} y "
                f"{arista_congestionada.destino.nombre} necesita expansión o rutas alternativas"
            )
        
        # Recomendaciones para cuellos de botella
        if puntos_criticos['cuellos_botella']:
            recomendaciones.append(
                "Se detectaron cuellos de botella críticos. Considerar construir "
                "rutas alternativas para mejorar la conectividad"
            )
        
        return recomendaciones