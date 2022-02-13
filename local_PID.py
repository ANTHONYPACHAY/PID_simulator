"""
Library for PID simulation


Created on Sun Jan 30 15:25:39 2022
@author: tonyp

version: 1.0.1
license: GLP
status: developer mode
maintainer: something.uteq@gamil.com
Credits: Brito Geovanny, Carvajal Dúval, Molina Jorge, Pachay Anthony, Toapanta José.

"""

import time


def world():
    print("Hello, World!")


PID_DEFINITIONS_MANUAL = 0
PID_DEFINITIONS_AUTOMATIC = 1

PID_DEFINITIONS_DIRECT = 0
PID_DEFINITIONS_REVERSE = 1

PID_DEFINITIONS_P_ON_M = 0
PID_DEFINITIONS_P_ON_E = 1


class ObjectPID(object):
    """
    Init object PID

    Args:
        Input: La variable que estamos tratando de controlar (doble)
        Output: La variable que será ajustada por el pid (doble)
        Setpoint: el valor que queremos ingresar para mantener (doble)
        Kp, Ki, Kd: Parámetros de sintonización. estos afectan cómo el pid cambiará la salida. (doble>=0)
        Direction: DIRECTA o INVERSA. determina en qué dirección se moverá la salida cuando se enfrente a un error dado. DIRECTO es el más común.
        POn: P_ON_E (predeterminado) o P_ON_M. Permiteespecificar la medida proporcional
    """

    def __init__(self, Setpoint: float, Kp: float, Ki: float, Kd: float, Direction: int, POn: int = None):

        if POn is not None:
            self.PID(Setpoint, Kp, Ki, Kd, Direction, POn)
            print("POn, all fine!")
        else:
            self.PID(Setpoint, Kp, Ki, Kd, Direction, PID_DEFINITIONS_P_ON_E)
            print("POn, no found!")

        return None

    def PID(self, Setpoint: float, Kp: float, Ki: float, Kd: float, Direction: int, POn: int = None):

        
        #################################
        #           Verificar esto!!!
        #################################
        self.outputSum = 0
        self.lastInput = 0
        self.outMin = 0
        self.outMax = 0
        self.controllerDirection = 0
        
        
        self.Input = 0
        self.Output = 0
        self.Setpoint = Setpoint

        self.inAuto = False
        # el límite de salida predeterminado corresponde a los límites de arduino pwm
        self.SetOutputLimits(0, 255)
        # El tiempo de muestra del controlador predeterminado es de 0,1 segundos
        self.SampleTime = 100

        self.SetControllerDirection(Direction)
        self.SetTunings(Kp, Ki, Kd, POn)

        # self.Kp = Kp
        # self.Ki = Ki
        # self.Kd = Kd
        # self.Direction = Direction
        # self.POn = POn

        self.lastTime = int(round(time.time() * 1000)) - self.SampleTime

        return None

    def Compute(self):
        """
        Contiene el algoritmo pid. debe llamarse una vez cada loop(). La mayoría de las veces simplemente regresará sin hacer nada. A una frecuencia especificada por SetSampleTime, calculará una nueva salida.

        Syntax:
            Compute()
        Args:
            Ninguno
        Returns:
            True : cuando se calcula la salida
            False : cuando no se ha hecho nada
        """
        if not self.inAuto:
            return False
        now = int(round(time.time() * 1000))
        timeChange = (now - self.lastTime)
        print(timeChange >= self.SampleTime, timeChange, self.SampleTime)
        if(timeChange >= self.SampleTime):
            # Calcular todas las variables de error de trabajo
            input = self.Input
            error = self.Setpoint - input
            dInput = (input - self.lastInput)
            self.outputSum += (self.ki * error)

            # Agregar proporcional en la medición, si se especifica P_ON_M
            if not self.pOnE:
                self.outputSum -= self.kp * dInput

            if(self.outputSum > self.outMax):
                self.outputSum = self.outMax
            elif(self.outputSum < self.outMin):
                self.outputSum = self.outMin

            # Agregar proporcional en caso de error, si se especifica P_ON_E
            # declaramos output
            output = 0
            if(self.pOnE):
                output = self.kp * error
            else:
                output = 0

            # Calcular el resto de la salida PID
            output += self.Output - self.kd * dInput

            if(output > self.outMax):
                output = self.outMax
            elif(output < self.outMin):
                output = self.outMin
            self.Output = output

            # Recuerda algunas variables para la próxima vez
            self.lastInput = input
            self.lastTime = now

            return True
        else:
            return False

    def SetMode(self, mode: int):
        """
        Especifica si el PID debe estar activado (AUTOMATIC) o desactivado (MANUAL). El PID se establece de manera predeterminada en la posición de desactivado cuando se crea.

        Syntax:
            SetMode(mode)
        Args:
            mode: AUTOMATIC o MANUAL
        Returns:
            Este método no retorna

        """
        newAuto = (mode == PID_DEFINITIONS_AUTOMATIC)
        if(newAuto and not self.inAuto):
            # Pasamos de manual a automático.
            self.Initialize()

        self.inAuto = newAuto
        return None

    def Initialize(self):
        """
        Hace todo lo que debe suceder para garantizar una transferencia sin problemas del modo manual al modo automático.
        Syntax:
            Initialize()
        Returns:
            Este método no retorna
        """

        self.outputSum = self.Output
        self.lastInput = self.Input
        if(self.outputSum > self.outMax):
            self.outputSum = self.outMax
        elif(self.outputSum < self.outMin):
            self.outputSum = self.outMin
        return None

    def SetOutputLimits(self, Min: float, Max: float):
        """
        El controlador PID está diseñado para variar su salida dentro de un rango dado. Por defecto, este rango es 0-255: el rango PWM de arduino. No sirve de nada enviar 300, 400 o 500 al PWM. Sin embargo, dependiendo de la aplicación, se puede desear un rango diferente.

        Syntax:
            SetOutputLimits(Min, Max)
        Args:
            Min: Extremo inferior del rango. debe ser < max (double)
            Max: Gama alta de la gama. debe ser > min (double)
        Returns:
            Este método no retorna
        """
        if(Min >= Max):
            return None
        self.outMin = Min
        self.outMax = Max
        if(self.inAuto):
            if(self.Output > self.outMax):
                self.Output = self.outMax
            elif(self.Output < self.outMin):
                self.Output = self.outMin

        if(self.outputSum > self.outMax):
            self.outputSum = self.outMax
        elif(self.outputSum < self.outMin):
            self.outputSum = self.outMin
        return None

    def SetTunings(self, Kp: float, Ki: float, Kd: float, POn: int = None):
        """
        Los parámetros de sintonización (o "Afinaciones") dictan el comportamiento dinámico del PID. ¿Oscilará o no? ¿Será rápido o lento? Se especifica un conjunto inicial de afinaciones cuando se crea el PID. Para la mayoría de los usuarios esto será suficiente. Sin embargo, a veces es necesario cambiar las afinaciones durante el tiempo de ejecución. En esos momentos se puede llamar a esta función.

        Syntax:
            SetTunings(Kp, Ki, Kd)
            SetTunings(Kp, Ki, Kd, POn)
        Args:
            Kp: determina la agresividad con la que reacciona el PID a la cantidad de error actual (proporcional) (doble >=0)
            Ki: Determina la agresividad con la que el PID reacciona al error a lo largo del tiempo (Integral) (doble>=0)
            Kd: determina la agresividad con la que reacciona el PID al cambio de error (derivado) (doble>=0)
            POn : P_ON_E (predeterminado) o P_ON_M. Permite especificar la medida proporcional.
        Returns:
            Este método no retorna
        """
        if POn is None:
            self.SetTunings(Kp, Ki, Kd, self.pOn)
        else:
            if (Kp < 0 or Ki < 0 or Kd < 0):
                return False

            self.pOn = POn
            self.pOnE = POn == PID_DEFINITIONS_P_ON_E

            SampleTimeInSec = float(self.SampleTime)/1000
            self.kp = Kp
            self.ki = Ki * SampleTimeInSec
            self.kd = Kd / SampleTimeInSec

            if(self.controllerDirection == PID_DEFINITIONS_REVERSE):
                self.kp = (0 - self.kp)
                self.ki = (0 - self.ki)
                self.kd = (0 - self.kd)

        return None

    def SetSampleTime(self, NewSampleTime: int):
        """
        Determina la frecuencia con la que evalúa el algoritmo PID. El valor predeterminado es 200 mS. Para aplicaciones de robótica, es posible que esto deba ser más rápido, pero en su mayor parte, 200 mS es bastante rápido.

        Syntax:
            SetSampleTime(SampleTime)
        Args:
            NewSampleTime: Con qué frecuencia, en milisegundos, se evaluará el PID. (int>0)
        Returns:
            Este método no retorna
        """
        if (NewSampleTime > 0):
            ratio = float(NewSampleTime) / float(self.SampleTime)
            self.ki *= ratio
            self.kd /= ratio
            self.SampleTime = float(NewSampleTime)

        return None

    def SetControllerDirection(self, Direction: int):
        """
        Si mi entrada está por encima del punto de referencia, ¿debería aumentarse o disminuirse la salida? Dependiendo de a qué esté conectado el PID, cualquiera podría ser cierto. Con un automóvil, la salida debe reducirse para reducir la velocidad. Para un refrigerador, lo contrario es cierto. La salida (refrigeración) debe aumentarse para bajar la temperatura. Esta función especifica a qué tipo de proceso está conectado el PID. Esta información también se especifica cuando se construye el PID. Dado que es poco probable que el proceso cambie de directo a inverso, es igualmente poco probable que alguien realmente use esta función
        Syntax:
            SetControllerDirection(Direction);
        Args:
            Direction: DIRECT (como un automóvil) or REVERSE (como un refrigerador)
        Returns:
            Este método no retorna
        """
        if(self.inAuto and Direction !=self.controllerDirection):
            self.kp = (0 - self.kp)
            self.ki = (0 - self.ki)
            self.kd = (0 - self.kd)
            self.controllerDirection = Direction 
        return None
    
    def setSetPoint(self, Setpoint: int):
        """
        Modifica el punto
        Syntax:
            setSetPoint()
        Returns:
            Este método no retorna
        """
        self.Setpoint = Setpoint
        print("change setpoin")
   
    def getSetPoint(self):
        return self.Setpoint
    
    def setInput(self, input: int):
        """
        Envia la señal para que esta sea ajustada
        Syntax:
            setInput()
        Returns:
            Este método no retorna
        """
        self.Input = input
    
    def getOutPut(self):
        """
        devuelve la señal de salida, que ha sido modificada
        Syntax:
            getOutPut()
        Returns:
            Este método retorna el Output
        """
        return self.Output
    
    def setKp(self, Kp: float):
        self.kp = Kp
        if(self.controllerDirection == PID_DEFINITIONS_REVERSE):
            self.kp = (0 - self.kp)
        
    def setKi(self, Ki: float):
        SampleTimeInSec = float(self.SampleTime)/1000
        self.ki = Ki * SampleTimeInSec

        if(self.controllerDirection == PID_DEFINITIONS_REVERSE):
            self.ki = (0 - self.ki)
    
    def setKd(self, Kd: float):
        SampleTimeInSec = float(self.SampleTime)/1000
        self.kd = Kd / SampleTimeInSec

        if(self.controllerDirection == PID_DEFINITIONS_REVERSE):
            self.kd = (0 - self.kd)
            
    #########################################
    #       Funciones de estado 
    #########################################
    # El hecho de que establezca el Kp = -1 no significa que realmente sucedió. estas funciones consultan el estado interno del PID. están aquí para fines de visualización. estas son las funciones que usa el PID Front-end
    def GetKp(self):
        return self.kp

    def GetKi(self):
        return self.ki

    def GetKd(self):
        return self.kd

    def GetMode(self):
        return (self.inAuto if PID_DEFINITIONS_MANUAL else PID_DEFINITIONS_AUTOMATIC)

    def GetDirection(self):
        return self.controllerDirection
        