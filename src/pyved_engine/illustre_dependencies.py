from abc import ABC, abstractmethod

from dependencies import DependencyContainer, LazyModule


# Exemple d'interface pour la couche réseau
class NetworkLayerInterface(ABC):
    @abstractmethod
    def send(self, data: bytes) -> None:
        pass

    @abstractmethod
    def receive(self) -> bytes:
        pass


# Implémentation concrète de la couche réseau
class DefaultNetworkLayer(NetworkLayerInterface):
    def send(self, data: bytes) -> None:
        print("Envoi:", data)

    def receive(self) -> bytes:
        print("Réception des données...")
        return b""


# Exemple d'utilisation sans interface pour le plugin
if __name__ == "__main__":
    container = DependencyContainer()

    # Enregistrement d'une dépendance concrète pour la couche réseau
    container.register("network_layer", DefaultNetworkLayer(), interface=NetworkLayerInterface)

    # Enregistrement d'un module plugin en lazy-loading
    # Ici, le module 'mon_module_plugin' doit définir des fonctions ou objets que vous utiliserez
    container.register("plugin", LazyModule("illustrat_plugin"))

    @container.inject
    def run_app(network_layer, plugin):
        network_layer.send(b"Hello, world!")
        # Par exemple, si le module plugin définit une fonction 'execute', on l'appelle :
        if hasattr(plugin, "execute"):
            plugin.execute()
        else:
            print("Le plugin ne fournit pas la fonction 'execute'.")

    run_app()
