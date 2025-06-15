# estructuras_datos.py
"""
Estructuras de datos propias para el Traffic Simulator
Implementaciones sin usar list, dict, queue del lenguaje
"""

class Nodo:
    """Nodo genérico para estructuras de datos"""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    """Lista enlazada propia"""
    def __init__(self):
        self.cabeza = None
        self.tamaño = 0
    
    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.tamaño += 1
    
    def eliminar(self, dato):
        if not self.cabeza:
            return False
        
        if self.cabeza.dato == dato:
            self.cabeza = self.cabeza.siguiente
            self.tamaño -= 1
            return True
        
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.dato == dato:
                actual.siguiente = actual.siguiente.siguiente
                self.tamaño -= 1
                return True
            actual = actual.siguiente
        return False
    
    def buscar(self, dato):
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                return True
            actual = actual.siguiente
        return False
    
    def obtener_lista(self):
        """Retorna todos los elementos como lista Python para iteración"""
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos
    
    def es_vacia(self):
        return self.cabeza is None
    
    def obtener_tamaño(self):
        return self.tamaño

class ColaPrioridad:
    """Cola de prioridad usando heap mínimo"""
    def __init__(self):
        self.heap = []
        self.tamaño = 0
    
    def _padre(self, i):
        return (i - 1) // 2
    
    def _hijo_izq(self, i):
        return 2 * i + 1
    
    def _hijo_der(self, i):
        return 2 * i + 2
    
    def _intercambiar(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _heapify_up(self, i):
        while i > 0 and self.heap[self._padre(i)][0] > self.heap[i][0]:
            self._intercambiar(i, self._padre(i))
            i = self._padre(i)
    
    def _heapify_down(self, i):
        while self._hijo_izq(i) < self.tamaño:
            hijo_min = self._hijo_izq(i)
            if (self._hijo_der(i) < self.tamaño and 
                self.heap[self._hijo_der(i)][0] < self.heap[hijo_min][0]):
                hijo_min = self._hijo_der(i)
            
            if self.heap[i][0] <= self.heap[hijo_min][0]:
                break
                
            self._intercambiar(i, hijo_min)
            i = hijo_min
    
    def insertar(self, prioridad, elemento):
        self.heap.append((prioridad, elemento))
        self.tamaño += 1
        self._heapify_up(self.tamaño - 1)
    
    def extraer_min(self):
        if self.tamaño == 0:
            return None
        
        if self.tamaño == 1:
            self.tamaño = 0
            return self.heap.pop()
        
        raiz = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.tamaño -= 1
        self._heapify_down(0)
        return raiz
    
    def es_vacia(self):
        return self.tamaño == 0

class HashTable:
    """Tabla hash propia para mapeos eficientes"""
    def __init__(self, capacidad_inicial=16):
        self.capacidad = capacidad_inicial
        self.tamaño = 0
        self.buckets = [ListaEnlazada() for _ in range(self.capacidad)]
    
    def _hash(self, clave):
        if isinstance(clave, str):
            return sum(ord(c) for c in clave) % self.capacidad
        return hash(clave) % self.capacidad
    
    def _redimensionar(self):
        if self.tamaño >= self.capacidad * 0.75:
            buckets_viejos = self.buckets
            self.capacidad *= 2
            self.tamaño = 0
            self.buckets = [ListaEnlazada() for _ in range(self.capacidad)]
            
            for bucket in buckets_viejos:
                for par in bucket.obtener_lista():
                    self.insertar(par[0], par[1])
    
    def insertar(self, clave, valor):
        indice = self._hash(clave)
        bucket = self.buckets[indice]
        
        # Buscar si ya existe la clave
        for par in bucket.obtener_lista():
            if par[0] == clave:
                par[1] = valor  # Actualizar valor existente
                return
        
        # Insertar nuevo par clave-valor
        bucket.agregar((clave, valor))
        self.tamaño += 1
        self._redimensionar()
    
    def obtener(self, clave):
        indice = self._hash(clave)
        bucket = self.buckets[indice]
        
        for par in bucket.obtener_lista():
            if par[0] == clave:
                return par[1]
        return None
    
    def eliminar(self, clave):
        indice = self._hash(clave)
        bucket = self.buckets[indice]
        
        for par in bucket.obtener_lista():
            if par[0] == clave:
                bucket.eliminar(par)
                self.tamaño -= 1
                return True
        return False
    
    def contiene(self, clave):
        return self.obtener(clave) is not None
    
    def obtener_claves(self):
        claves = []
        for bucket in self.buckets:
            for par in bucket.obtener_lista():
                claves.append(par[0])
        return claves
    
    def obtener_valores(self):
        valores = []
        for bucket in self.buckets:
            for par in bucket.obtener_lista():
                valores.append(par[1])
        return valores