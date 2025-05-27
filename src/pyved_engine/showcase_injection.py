"""
The CD-pattern (by Tom) is an elegant solution that enables
sharing components between:
- pyved_engine (current part of the project) and
- pyvm_component

The pattern allows for:
- Retrieving information from the high-level module
- Defining a new class based on that particular information, and
- Injecting the class back into the higher-level module.
Therefore, we facilitate a low coupling between modules,
enabling information sharing in a more "bidirectional" manner.

This is a form of dependency injection that still allows
for retrieving knowledge from the target module ; module into which
new dependencies will be injected.

This pattern can serve as a go-to solution for intricate coding problems:
- Import high-level definitions (such as event defintions) from PYVED
- Declare a custom class that uses HL definitions but at the current level,
- Inject the newly-defined custom class back into PYVED
"""
from abc import ABC, abstractmethod
from cd_patterns import CustomizableCode, inj_dependencies


# ------------------------------
# Abstract Classes
# ------------------------------
class AbstractBumper(ABC):
    @abstractmethod
    def protect(self):
        """
        Method to be implemented by the concrete bumper class.
        It defines how the bumper protects the car.
        """
        pass


class AbstractWindshield(ABC):
    @abstractmethod
    def shield(self):
        """
        Method to be implemented by the concrete windshield class.
        It defines how the windshield shields the car.
        """
        pass


class AbstractCylinder(ABC):
    @abstractmethod
    def fire(self):
        """
        Method to be implemented by the concrete cylinder class.
        It defines how the cylinder fires, typically representing engine combustion.
        """
        pass


class AbstractEngine(ABC):
    @abstractmethod
    def start(self):
        """
        Method to be implemented by the concrete engine class.
        Defines how the engine starts.
        """
        pass

    @abstractmethod
    def overheat(self):
        """
        Method to be implemented by the concrete engine class.
        Defines the behavior when the engine overheats.
        """
        pass


# ------------------------------
# Concrete Classes for Each Component
# ------------------------------
class BumperClass(AbstractBumper):
    def __init__(self, hp):
        """
        Initializes the bumper with its hit points (hp).
        """
        self.hp = hp

    def protect(self):
        """
        Simulates the bumper protecting the car.
        """
        print("Bumper protects the car!")


class WindshieldClass(AbstractWindshield):
    def shield(self):
        """
        Simulates the windshield shielding the car.
        """
        print("Windshield shields the car!")


class CylinderClass(AbstractCylinder):
    def fire(self):
        """
        Simulates the cylinder firing (engine combustion).
        """
        print("Vroum vroum!")


# ------------------------------
# Customizable Pattern Demo: Engine and Car are Defined as Customizable Classes
# ------------------------------
class EngineClass(AbstractEngine, CustomizableCode):
    
    def __init__(self, etype, producer_name):
        """
        Initializes the engine with its type and producer's name.
        Also ensures that dependencies like the cylinder are instantiated.
        """
        self.instantiate_dependencies(
            cylinder_kwargs={}  # Ensure the Cylinder dependency is passed
        )
        print(f"An engine has been built, type: {etype}, produced by: {producer_name}")

    def start(self):
        """
        Starts the engine and fires the cylinder.
        """
        print("Engine starts.")
        print(f"Engine has cylinder: {self.cylinder}")
        self.cylinder.fire()

    def overheat(self):
        """
        Simulates engine overheating.
        """
        print("Engine needs more cooling!")


class Car(CustomizableCode):
    def __init__(self):
        """
        Initializes the car, injecting all necessary dependencies (bumper, windshield, engine).
        """
        self.instantiate_dependencies(
            bumper_kwargs={'hp': 95},
            windshield_kwargs={},
            engine_kwargs={'etype': 6, 'producer_name': 'BMW'}
        )
        print("The car gets out of the factory!")

    def test_car(self):
        """
        Simulates testing the car by activating its components.
        """
        self.bumper.protect()
        self.windshield.shield()
        self.engine.start()


# ------------------------------
# Dependency Injection for Engine and Car Classes
# ------------------------------
# Injecting dependencies for Engine and Car classes to ensure proper instantiation
inj_dependencies(EngineClass, cylinder=CylinderClass)
inj_dependencies(Car, bumper=BumperClass, windshield=WindshieldClass, engine=EngineClass)


# ------------------------------
# Example Usage
# ------------------------------
try:
    # Instantiating Car with all dependencies injected
    car = Car()  # This could raise an error if engine_kwargs is missing or if dependencies are incorrect
    print('-')
    car.test_car()  # Testing the car by calling its methods
    print('+')
    car.engine.overheat()  # Testing the engine's overheat functionality
    print('Bumper status?', car.bumper.hp)  # Printing the bumper's hit points

except RuntimeError as e:
    print(f"Error: {e}")
