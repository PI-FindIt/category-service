import importlib
import pkgutil


# Get the current package name
package_name = __name__

# Iterate over all modules in the current package
for _, module_name, __ in pkgutil.iter_modules(__path__):
    full_module_name = f"{package_name}.{module_name}"
    importlib.import_module(full_module_name)