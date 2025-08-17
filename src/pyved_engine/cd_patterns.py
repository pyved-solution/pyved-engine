import re
from abc import ABC


DEP_TABLE_CLS_ATTR = 'declared_dependencies'


def extract_prefix_before_kwargs(kwargs_name):
    # Use regex to capture the part before '_kwargs'
    match = re.match(r"(.+)_kwargs$", kwargs_name)
    if match:
        return match.group(1)
    return None  # Return None if it doesn't match


class CustomizableCode(ABC):  # CustomizableCode base class ; a helper cls for special dependency injection

    def is_vanilla(self):
        if hasattr(self.__class__, DEP_TABLE_CLS_ATTR):
            return False
        return True

    # To be called by classes inheriting CustomizableCode
    def instantiate_dependencies(self, **kwargs):
        if self.is_vanilla():
            return
        deps = getattr(self, DEP_TABLE_CLS_ATTR)
        # Ensure all declared dependencies are provided in kwargs
        missing_dependencies = [dep for dep in deps if f"{dep}_kwargs" not in kwargs]
        if missing_dependencies:
            err_infos = ', '.join(missing_dependencies)
            cls_info = self.__class__
            raise RuntimeError(f"During instantiation of {cls_info}, \
            missing dependencies: {err_infos}. Ensure theyve been passed in kwargs.")

        for dep_name, dep_kwargs in kwargs.items():
            # Dynamically instantiate the dependency
            infotag = extract_prefix_before_kwargs(dep_name)
            if infotag is None:
                raise RuntimeError(f"Dependency name '{dep_name}' is not valid.")

            if infotag not in deps:
                cls_name = self.__class__.__name__
                raise RuntimeError(f"Dependency '{infotag}' not found in '{cls_name}'. Ensure it is injected properly.")
            else:
                # Attempt to get the injected dependency class
                dep_class = deps[infotag]
            # the class is found, therefore we instantiate it
            setattr(self, infotag, dep_class(**dep_kwargs))


# Function to inject dependencies
def inj_dependencies(cls, **dependencies):
    # Class attribute to track declared dependencies, AND at the child class-level
    if not hasattr(cls, DEP_TABLE_CLS_ATTR):
        setattr(cls, DEP_TABLE_CLS_ATTR, {})  # its like setting a flag vanilla=Flase
    for dep_name, dep_class in dependencies.items():
        getattr(cls, DEP_TABLE_CLS_ATTR)[dep_name.lower()] = dep_class
    return cls
