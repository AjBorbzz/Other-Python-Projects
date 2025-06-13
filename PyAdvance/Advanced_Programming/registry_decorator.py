# ==============================================================================
# REPLICATING DJANGO'S admin.register() DECORATOR
# ==============================================================================

"""
This module demonstrates how Django's admin.register() decorator works
by creating our own implementation that mimics the same functionality.
"""

from typing import Dict, Type, Optional, Any, Callable, Union
from functools import wraps


# ==============================================================================
# 1. BASIC REGISTRY CLASS (Similar to Django's AdminSite)
# ==============================================================================

class CustomRegistry:
    """
    A registry that stores model-admin pairs, similar to Django's AdminSite.
    This is where all registered models and their admin classes are stored.
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        # Dictionary to store model -> admin_class mappings
        self._registry: Dict[Type, Type] = {}
        self._actions: Dict[str, Callable] = {}
    
    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Register a model with an admin class.
        
        This method can be used in three ways:
        1. As a decorator: @registry.register(MyModel)
        2. As a decorator with admin class: @registry.register(MyModel, MyAdmin)
        3. As a regular method: registry.register(MyModel, MyAdmin)
        """
        
        def _model_admin_wrapper(admin_class_inner):
            """Inner wrapper that handles the actual registration"""
            
            # Handle both single model and iterable of models
            if not hasattr(model_or_iterable, '__iter__') or isinstance(model_or_iterable, type):
                models = [model_or_iterable]
            else:
                models = model_or_iterable
            
            for model in models:
                if model in self._registry:
                    raise ValueError(f"Model {model.__name__} is already registered")
                
                # Create admin class with options if provided
                if options:
                    # Create a new class with the provided options
                    attrs = dict(admin_class_inner.__dict__)
                    attrs.update(options)
                    admin_class_with_options = type(
                        admin_class_inner.__name__,
                        (admin_class_inner,),
                        attrs
                    )
                    self._registry[model] = admin_class_with_options
                else:
                    self._registry[model] = admin_class_inner
                
                print(f"✓ Registered {model.__name__} with {admin_class_inner.__name__}")
            
            return admin_class_inner
        
        # If admin_class is provided, this is a direct call (not a decorator)
        if admin_class is not None:
            return _model_admin_wrapper(admin_class)
        
        # Otherwise, this is being used as a decorator
        return _model_admin_wrapper
    
    def unregister(self, model_or_iterable):
        """Unregister a model or models"""
        if not hasattr(model_or_iterable, '__iter__') or isinstance(model_or_iterable, type):
            models = [model_or_iterable]
        else:
            models = model_or_iterable
        
        for model in models:
            if model in self._registry:
                del self._registry[model]
                print(f"✓ Unregistered {model.__name__}")
            else:
                print(f"⚠ Model {model.__name__} was not registered")
    
    def get_registry(self):
        """Get all registered models and their admin classes"""
        return self._registry.copy()
    
    def is_registered(self, model):
        """Check if a model is registered"""
        return model in self._registry
    
    def get_admin_class(self, model):
        """Get the admin class for a specific model"""
        return self._registry.get(model)


# ==============================================================================
# 2. ENHANCED REGISTRY WITH VALIDATION
# ==============================================================================

class ValidatedRegistry(CustomRegistry):
    """
    Enhanced registry with validation, similar to Django's approach
    """
    
    def register(self, model_or_iterable, admin_class=None, **options):
        """Register with validation"""
        
        def _validated_wrapper(admin_class_inner):
            # Validate the model(s)
            if not hasattr(model_or_iterable, '__iter__') or isinstance(model_or_iterable, type):
                models = [model_or_iterable]
            else:
                models = model_or_iterable
            
            for model in models:
                self._validate_model(model)
                self._validate_admin_class(admin_class_inner)
            
            # Call parent's register method
            return super().register(model_or_iterable, admin_class_inner, **options)
        
        if admin_class is not None:
            return _validated_wrapper(admin_class)
        return _validated_wrapper
    
    def _validate_model(self, model):
        """Validate that the model is actually a class"""
        if not isinstance(model, type):
            raise TypeError(f"Expected a class, got {type(model)}")
        
        # You could add more validations here, like checking for specific attributes
        if not hasattr(model, '__name__'):
            raise AttributeError("Model must have a __name__ attribute")
    
    def _validate_admin_class(self, admin_class):
        """Validate the admin class"""
        if not isinstance(admin_class, type):
            raise TypeError(f"Admin class must be a class, got {type(admin_class)}")


# ==============================================================================
# 3. REGISTRY WITH DECORATOR FACTORY (More Django-like)
# ==============================================================================

class AdvancedRegistry:
    """
    Most Django-like implementation with decorator factory support
    """
    
    def __init__(self, name: str = "advanced"):
        self.name = name
        self._registry: Dict[Type, Type] = {}
    
    def register(self, *models, **options):
        """
        The main register method that works as both decorator and direct call
        
        Usage examples:
        @registry.register(Model1, Model2)
        @registry.register(Model1, list_display=['field1', 'field2'])
        registry.register(Model1, Model2, admin_class=MyAdmin)
        """
        
        def decorator(admin_class):
            """The actual decorator function"""
            self._register_models(models, admin_class, **options)
            return admin_class
        
        # If no models provided, raise error
        if not models:
            raise ValueError("At least one model must be provided")
        
        # Check if the first argument is actually an admin class (direct call)
        if len(models) == 1 and hasattr(models[0], '__name__') and 'admin_class' in options:
            admin_class = options.pop('admin_class')
            self._register_models(models, admin_class, **options)
            return admin_class
        
        return decorator
    
    def _register_models(self, models, admin_class, **options):
        """Internal method to register models"""
        for model in models:
            if model in self._registry:
                raise ValueError(f"Model {model.__name__} is already registered")
            
            # Apply options to admin class if any
            if options:
                # Create a new admin class with options
                class_name = f"{admin_class.__name__}WithOptions"
                attrs = dict(admin_class.__dict__)
                attrs.update(options)
                enhanced_admin = type(class_name, (admin_class,), attrs)
                self._registry[model] = enhanced_admin
            else:
                self._registry[model] = admin_class
            
            print(f"✓ Advanced registered {model.__name__} with {admin_class.__name__}")
    
    def get_registry(self):
        return self._registry.copy()


# ==============================================================================
# 4. EXAMPLE USAGE AND TESTING
# ==============================================================================

# Create sample models (like Django models)
class User:
    """Sample User model"""
    def __init__(self, username, email):
        self.username = username
        self.email = email

class Product:
    """Sample Product model"""
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Order:
    """Sample Order model"""
    def __init__(self, user, products):
        self.user = user
        self.products = products


# Create sample admin classes (like Django ModelAdmin)
class BaseAdmin:
    """Base admin class"""
    list_display = []
    search_fields = []
    
    def __init__(self):
        print(f"Initialized {self.__class__.__name__}")

class UserAdmin(BaseAdmin):
    """User admin configuration"""
    list_display = ['username', 'email']
    search_fields = ['username', 'email']

class ProductAdmin(BaseAdmin):
    """Product admin configuration"""
    list_display = ['name', 'price']
    search_fields = ['name']

class OrderAdmin(BaseAdmin):
    """Order admin configuration"""
    list_display = ['user', 'products']


# ==============================================================================
# 5. DEMONSTRATION
# ==============================================================================

def demonstrate_registries():
    """Demonstrate all registry implementations"""
    
    print("=" * 60)
    print("DEMONSTRATING CUSTOM REGISTRY IMPLEMENTATIONS")
    print("=" * 60)
    
    # 1. Basic Registry
    print("\n1. BASIC REGISTRY:")
    print("-" * 20)
    basic_registry = CustomRegistry("basic")
    
    # Register using decorator
    @basic_registry.register(User)
    class UserAdminBasic(BaseAdmin):
        list_display = ['username', 'email']
    
    # Register multiple models
    @basic_registry.register([Product, Order])
    class MultipleAdmin(BaseAdmin):
        list_display = ['name']
    
    print(f"Basic registry has {len(basic_registry.get_registry())} models")
    
    # 2. Validated Registry
    print("\n2. VALIDATED REGISTRY:")
    print("-" * 25)
    validated_registry = ValidatedRegistry("validated")
    
    @validated_registry.register(User)
    class UserAdminValidated(BaseAdmin):
        list_display = ['username', 'email']
    
    print(f"Validated registry has {len(validated_registry.get_registry())} models")
    
    # 3. Advanced Registry
    print("\n3. ADVANCED REGISTRY:")
    print("-" * 22)
    advanced_registry = AdvancedRegistry("advanced")
    
    @advanced_registry.register(User, list_display=['username', 'email', 'date_joined'])
    class UserAdminAdvanced(BaseAdmin):
        search_fields = ['username']
    
    @advanced_registry.register(Product, Order)
    class MultipleAdvancedAdmin(BaseAdmin):
        list_display = ['name', 'created_at']
    
    print(f"Advanced registry has {len(advanced_registry.get_registry())} models")
    
    # 4. Show registry contents
    print("\n4. REGISTRY CONTENTS:")
    print("-" * 21)
    for name, registry in [
        ("Basic", basic_registry),
        ("Validated", validated_registry), 
        ("Advanced", advanced_registry)
    ]:
        print(f"\n{name} Registry:")
        for model, admin in registry.get_registry().items():
            print(f"  {model.__name__} -> {admin.__name__}")


# ==============================================================================
# 6. HOW DECORATORS WORK BREAKDOWN
# ==============================================================================

def explain_decorator_mechanics():
    """Explain how the decorator pattern works step by step"""
    
    print("\n" + "=" * 60)
    print("HOW THE DECORATOR PATTERN WORKS")
    print("=" * 60)
    
    print("""
When you write:

    @registry.register(MyModel)
    class MyAdmin(BaseAdmin):
        pass

Python internally does this:

    class MyAdmin(BaseAdmin):
        pass
    MyAdmin = registry.register(MyModel)(MyAdmin)

Step by step:
1. registry.register(MyModel) returns a decorator function
2. This decorator function receives MyAdmin as an argument
3. The decorator registers the model-admin pair
4. The decorator returns MyAdmin (unchanged)
5. MyAdmin gets assigned back to the original name

This is why the decorator pattern is so powerful - it allows you to
modify or register classes/functions while keeping the original
syntax clean and readable.
    """)


if __name__ == "__main__":
    demonstrate_registries()
    explain_decorator_mechanics()