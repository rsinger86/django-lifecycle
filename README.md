## Intro

Stop awkwardly overriding model methods or adding unnecessary indirection via signals. Use lifecyle decorators to declaratively and simply react to model state changes. 

The "core" models that power your business domain are often more than thin SQL table wrappers. Extend a `CoreModel` class to keep these rules encapsulated in your model classes in a way that gracefully handles a range of complex scenarios.
