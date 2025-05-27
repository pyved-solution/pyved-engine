from abc import ABC
import re


def extract_prefix_before_kwargs(kwargs_name):
    # Use regex to capture the part before '_kwargs'
    match = re.match(r"(.+)_kwargs$", kwargs_name)
    if match:
        return match.group(1)
    return None  # Return None if it doesn't match


# CustomizableCode base class
class CustomizableCode(ABC):

    # To be called by classes inheriting CustomizableCode
    def instantiate_dependencies(self, **kwargs):
        # Ensure all declared dependencies are provided in kwargs
        missing_dependencies = [dep for dep in self.declared_dependencies if f"{dep}_kwargs" not in kwargs]
        if missing_dependencies:
            err_infos = ', '.join(missing_dependencies)
            cls_info = self.__class__
            raise RuntimeError(f"During instantiation of {cls_info}, missing dependencies: {err_infos}. Ensure theyve been passed in kwargs.")
        
        for dep_name, dep_kwargs in kwargs.items():
            # Dynamically instantiate the dependency
            infotag = extract_prefix_before_kwargs(dep_name)
            if infotag is None:
                raise RuntimeError(f"Dependency name '{dep_name}' is not valid.")
            
            if infotag not in self.declared_dependencies:
                raise RuntimeError(f"Dependency '{infotag}' not found for class '{self.__class__.__name__}'. Ensure it is injected properly.")
            else:
                # Attempt to get the injected dependency class
                dep_class = self.declared_dependencies[infotag]
            
            # If the class is found, instantiate it
            setattr(self, infotag, dep_class(**dep_kwargs))


# Function to inject dependencies
def inj_dependencies(cls, **dependencies):
    # Class attribute to track declared dependencies, AND at the child class-level
    if not hasattr(cls, 'declared_dependencies'):
        setattr(cls, 'declared_dependencies', {})

    for dep_name, dep_class in dependencies.items():
        cls.declared_dependencies[dep_name.lower()] = dep_class
    return cls
