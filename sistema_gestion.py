import datetime
import logging
from abc import ABC, abstractmethod

# ==========================================
# 1. CONFIGURACIÓN DEL ARCHIVO DE LOGS
# ==========================================
logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==========================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorSistemaFJ(Exception):
    """Excepción base para el sistema de Software FJ."""
    pass

class ClienteInvalidoError(ErrorSistemaFJ):
    """Excepción lanzada cuando los datos del cliente no son válidos."""
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Excepción lanzada cuando un servicio no existe o no está disponible."""
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    """Excepción lanzada cuando hay un error al intentar procesar una reserva."""
    pass


# ==========================================
# 3. CLASE ABSTRACTA BASE (Abstracción)
# ==========================================
class EntidadBase(ABC):
    def __init__(self, identificador: str):
        self._identificador = identificador

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Método abstracto obligatorio para obtener detalles de la entidad."""
        pass


# ==========================================
# 4. CLASE CLIENTE (Encapsulación y Validación)
# ==========================================
class Cliente(EntidadBase):
    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre        # Valida mediante setter
        self.correo = correo        # Valida mediante setter
        self.telefono = telefono    # Valida mediante setter

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError(f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not valor or "@" not in valor or "." not in valor:
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not valor.isdigit() or len(valor) < 7:
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}'. Debe contener solo números (mínimo 7 dígitos).")
        self._telefono = valor

    def obtener_detalles(self) -> str:
        return f"Cliente [ID: {self.identificador}] - Nombre: {self.nombre}, Correo: {self.correo}, Teléfono: {self.telefono}"


# ==========================================
# 5. CLASE ABSTRACTA SERVICIO Y DERIVADAS (Herencia y Polimorfismo)
# ==========================================
class Servicio(EntidadBase, ABC):
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float):
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base

    @property
    def costo_base(self):
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor):
        if valor < 0:
            raise ValueError("El costo base no puede ser negativo.")
        self._costo_base = float(valor)

    @abstractmethod
    def calcular_costo(self) -> float:
        pass

    @abstractmethod
    def obtener_detalles(self) -> str:
        pass


# Servicio Especializado 1: Alquiler de Equipos
class AlquilerEquipos(Servicio):
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, horas: int):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.horas = horas

    @property
    def horas(self):
        return self._horas

    @horas.setter
    def horas(self, valor):
        if valor <= 0:
            raise ServicioNoDisponibleError("Las horas de alquiler deben ser mayores a cero.")
        self._horas = int(valor)

    # Método con parámetros opcionales (sobrecarga lógica)
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19) -> float:
        try:
            subtotal = self.costo_base * self.horas
            total_con_desc = subtotal * (1 - descuento)
            total_final = total_con_desc * (1 + impuesto)
            return round(total_final, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo en AlquilerEquipos: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Alquiler de Equipos] {self.nombre_servicio} - Horas: {self.horas} - Costo Base/h: ${self.costo_base}"


# Servicio Especializado 2: Reserva de Salas
class ReservaSalas(Servicio):
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, capacidad: int):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if valor <= 0:
            raise ServicioNoDisponibleError("La capacidad de la sala debe ser mayor a cero.")
        self._capacidad = int(valor)

    def calcular_costo(self, tarifa_aseo: float = 20000.0) -> float:
        try:
            return round(self.costo_base + tarifa_aseo, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo en ReservaSalas: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Reserva de Sala] {self.nombre_servicio} - Capacidad: {self.capacidad} personas"


# Servicio Especializado 3: Asesorías Especializadas
class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, nivel_experticia: str):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.nivel_experticia = nivel_experticia

    @property
    def nivel_experticia(self):
        return self._nivel_experticia

    @nivel_experticia.setter
    def nivel_experticia(self, valor):
        niveles_validos = ["Junior", "Senior", "Master"]
        if valor not in niveles_validos:
            raise ServicioNoDisponibleError(f"Nivel de experticia inválido: '{valor}'. Debe ser uno de {niveles_validos}")
        self._nivel_experticia = valor

    def calcular_costo(self, bono_especial: float = 0.0) -> float:
        try:
            multiplicador = 1.5 if self.nivel_experticia == "Senior" else (2.0 if self.nivel_experticia == "Master" else 1.0)
            return round((self.costo_base * multiplicador) + bono_especial, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo en AsesoriaEspecializada: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Asesoría Especializada] {self.nombre_servicio} - Nivel: {self.nivel_experticia}"


# ==========================================
# 6. CLASE RESERVA (Manejo robusto de excepciones: try/except/else/finally)
# ==========================================
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Pendiente"

    def confirmar_reserva(self):
        print(f"\n--- Procesando transacción de reserva: {self.id_reserva} ---")
        costo_total = 0.0
        try:
            # Validación de datos obligatorios en la reserva
            if not self.cliente or not self.servicio:
                raise ReservaInvalidaError("La reserva no cuenta con un cliente o un servicio asignado válidos.")
            
            # Cálculo operativo
            costo_total = self.servicio.calcular_costo()
            
        except ReservaInvalidaError as rie:
            # Manejo de excepción específica con logging
            logging.warning(f"Advertencia en reserva {self.id_reserva}: {rie}")
            print(f"[!] Error controlado de reserva: {rie}")
            self.estado = "Fallida"
            raise
        except Exception as e:
            # Encadenamiento de excepciones para errores críticos inesperados
            logging.error(f"Error crítico en procesamiento de reserva {self.id_reserva}: {e}")
            self.estado = "Error Crítico"
            raise ReservaInvalidaError("Fallo crítico general procesando la reserva.") from e
        else:
            # Se ejecuta únicamente si no se presentaron excepciones
            self.estado = "Confirmada"
            print(f"[✓] ¡Reserva {self.id_reserva} confirmada exitosamente!")
            print(f"    -> Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio}")
            print(f"    -> Costo Total Procesado: ${costo_total}")
            logging.info(f"Reserva {self.id_reserva} confirmada para el cliente {self.cliente.identificador}.")
        finally:
            # Bloque obligatorio de cierre o depuración transaccional
            print(f"[i] Estado final de la transacción [{self.id_reserva}]: {self.estado}")


# ==========================================
# 7. SIMULACIÓN DE 10 OPERACIONES COMPLETAS
# ==========================================
def ejecutar_simulacion():
    print("==================================================")
    print(" INICIO DE SIMULACIÓN - SISTEMA SOFTWARE FJ")
    print("==================================================")

    # Listas internas en memoria para almacenamiento sin bases de datos
    clientes_registrados = []
    servicios_registrados = []
    reservas_registradas = []

    # 1. Registro Válido de Cliente
    print("\n[Operación 1] Registro Válido de Cliente:")
    try:
        c1 = Cliente("C001", "Ruben Bustos", "ruben.bustos@unad.edu.co", "3101234567")
        clientes_registrados.append(c1)
        print(f"    -> {c1.obtener_detalles()}")
        logging.info(f"Cliente registrado: {c1.identificador}")
    except Exception as e:
        print(f"    [X] Error: {e}")

    # 2. Registro Inválido de Cliente (Correo incorrecto)
    print("\n[Operación 2] Registro Inválido de Cliente (Excepción controlada):")
    try:
        c_malo = Cliente("C002", "Maria Perez", "correo_sin_formato", "3209876543")
        clientes_registrados.append(c_malo)
    except ClienteInvalidoError as cie:
        print(f"    [✓ Capturado con éxito]: {cie}")
        logging.info(f"Excepción capturada correctamente: {cie}")

    # 3. Registro Válido de Segundo Cliente
    print("\n[Operación 3] Registro Válido de Segundo Cliente:")
    try:
        c2 = Cliente("C003", "Andres Gomez", "andres.gomez@gmail.com", "3157894561")
        clientes_registrados.append(c2)
        print(f"    -> {c2.obtener_detalles()}")
    except Exception as e:
        print(f"    [X] Error: {e}")

    # 4. Creación Válida de Servicio 1 (Alquiler de Equipos)
    print("\n[Operación 4] Creación Válida de Alquiler de Equipos:")
    try:
        s1 = AlquilerEquipos("S001", "Estación de Desarrollo Grafico", 45000.0, 5)
        servicios_registrados.append(s1)
        print(f"    -> {s1.obtener_detalles()} | Costo Final: ${s1.calcular_costo()}")
    except Exception as e:
        print(f"    [X] Error: {e}")

    # 5. Creación Inválida de Servicio (Nivel de experticia incorrecto)
    print("\n[Operación 5] Creación Inválida de Asesoría (Excepción controlada):")
    try:
        s_malo = AsesoriaEspecializada("S002", "Consultoría Arquitectura", 90000.0, "NivelDios")
        servicios_registrados.append(s_malo)
    except ServicioNoDisponibleError as sne:
        print(f"    [✓ Capturado con éxito]: {sne}")
        logging.info(f"Excepción controlada de servicio: {sne}")

    # 6. Creación Válida de Servicio 2 (Reserva de Sala)
    print("\n[Operación 6] Creación Válida de Reserva de Sala:")
    try:
        s2 = ReservaSalas("S003", "Auditorio Principal FJ", 150000.0, 30)
        servicios_registrados.append(s2)
        print(f"    -> {s2.obtener_detalles()} | Costo Total: ${s2.calcular_costo()}")
    except Exception as e:
        print(f"    [X] Error: {e}")

    # 7. Reserva Exitosa 1
    print("\n[Operación 7] Procesamiento de Reserva Exitosa 1:")
    try:
        res1 = Reserva("R001", clientes_registrados[0], servicios_registrados[0])
        res1.confirmar_reserva()
        reservas_registradas.append(res1)
    except Exception as e:
        print(f"    [X] Error inesperado: {e}")

    # 8. Reserva Exitosa 2
    print("\n[Operación 8] Procesamiento de Reserva Exitosa 2:")
    try:
        res2 = Reserva("R002", clientes_registrados[1], servicios_registrados[1])
        res2.confirmar_reserva()
        reservas_registradas.append(res2)
    except Exception as e:
        print(f"    [X] Error inesperado: {e}")

    # 9. Reserva Fallida Controlada (Falta de servicio asociado)
    print("\n[Operación 9] Intento de Reserva Fallida (Servicio Nulo):")
    try:
        res_fallida = Reserva("R003", clientes_registrados[0], None)
        res_fallida.confirmar_reserva()
    except ReservaInvalidaError:
        print("    [✓] Excepción de reserva inválida procesada y registrada en logs correctamente.")

    # 10. Validación de Datos Erróneos de Teléfono
    print("\n[Operación 10] Validación Estricta de Teléfono con Caracteres Inválidos:")
    try:
        c_error = Cliente("C004", "Lucia Torres", "lucia.torres@mail.com", "310ABC4567")
    except ClienteInvalidoError as cie:
        print(f"    [✓ Capturado con éxito]: {cie}")
        print("    [✓] El sistema continúa operando establemente sin interrupciones.")
        logging.info(f"Operación 10 superada tras excepción: {cie}")

    print("\n==================================================")
    print(" SIMULACIÓN FINALIZADA CON ÉXITO. Sistema estable.")
    print("==================================================")

if __name__ == "__main__":
    ejecutar_simulacion()