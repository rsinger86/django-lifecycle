from distutils.version import StrictVersion

import django
from django.db import models
from django.utils.functional import cached_property


class NullType(object):
    pass


def hook(hook: str, when: str = None, was='*', is_now='*', has_changed: bool = None, is_not = NullType):
    assert hook in (
        'before_save',
        'after_save',
        'before_create',
        'after_create',
        'before_update',
        'after_update',
        'before_delete',
        'after_delete'
    )

    def decorator(hooked_method):
        def wrapper(*args, **kwargs):
            hooked_method(*args, **kwargs)
        
        if not hasattr(wrapper, '_hooked'):
            wrapper._hooked = []
            
        wrapper._hooked.append({
            'hook': hook,
            'when': when,
            'was': was,
            'is_now': is_now,
            'has_changed': has_changed,
            'is_not': is_not
        })

        return wrapper
    return decorator
    


class LifecycleModelMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self.__dict__.copy()


    @property
    def _diff_with_initial(self):
        d1 = self._initial
        d2 = self.__dict__
        diffs = []

        for k, v in d1.items():
            if k in d2 and v != d2[k]:
                diffs.append( (k, (v, d2[k])) )

        return dict(diffs)

 
    def initial_value(self, field_name: str = None):
        """
        Get initial value of field when model was instantiated.
        """
        if self._meta.get_field(field_name).get_internal_type() == 'ForeignKey':
            if not field_name.endswith('_id'):
                field_name = field_name+'_id' 
                
        attribute = self._diff_with_initial.get(field_name, None)

        if not attribute:
            return None

        return attribute[0]


    def has_changed(self, field_name: str = None) -> bool:
        """
        Check if a field has changed since the model was instantiated.
        """
        changed = self._diff_with_initial.keys()

        if self._meta.get_field(field_name).get_internal_type() == 'ForeignKey':
            if not field_name.endswith('_id'):
                field_name = field_name+'_id' 

        if field_name in changed: 
            return True

        return False

        
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self._run_hooked_methods('before_create')
        else:
            self._run_hooked_methods('before_update')
        
        self._run_hooked_methods('before_save')

        super().save(*args, **kwargs)

        self._run_hooked_methods('after_save')

        if is_new:
            self._run_hooked_methods('after_create')
        else:
            self._run_hooked_methods('after_update')
            
            
    def update(self, **validated_data: dict):
        for attr, value in validated_data.items():
            setattr(self, attr, value)

        self.save()
        

    def update_field(self, field_name: str, value):
        setattr(self, field_name, value)
        self.save(update_fields=[field_name])


    def delete(self, *args, **kwargs):
        self._run_hooked_methods('before_delete')
        super().delete(*args, **kwargs)
        self._run_hooked_methods('after_delete')

    
    @cached_property
    def _field_names(self):
        return [field.name for field in self._meta.get_fields()]
            
        
    def _get_potentially_hooked_methods(self):
        collected = []
        skip = ('_get_potentially_hooked_methods', '_run_hooked_methods')
        
        for name in dir(self):
            if name in skip or name in self._field_names:
                continue
                
            try:
                attr = getattr(self, name)
                if callable(attr) and hasattr(attr, '_hooked'):
                    collected.append(attr)
            except AttributeError:
                pass

        return collected

        
    def _run_hooked_methods(self, hook: str):
        """
            Iterate through decorated methods to find those that should be 
            triggered by the current hook. If conditions exist, check them before
            running otherwise go ahead and run.
        """
        for method in self._get_potentially_hooked_methods():
            for callback_specs in method._hooked:
                if callback_specs['hook'] != hook:
                    continue

                when = callback_specs.get('when') 

                if when:
                    if self._check_callback_conditions(callback_specs):
                        method()
                else:
                    method()
                

    def _check_callback_conditions(self, specs: dict):
        if not self._check_has_changed(specs):
            return False
        
        if not self._check_value_transition(specs):
            return False 

        if not self._check_is_not_condition(specs):
            return False 

        return True


    def _check_has_changed(self, specs: dict):
        field_name = specs['when']
        has_changed = specs['has_changed']

        if has_changed is None:
            return True 
        
        return has_changed == self.has_changed(field_name)


    def _check_value_transition(self, specs: dict):
        field_name = specs['when']
        specs_match = 0

        if specs['was'] in (self.initial_value(field_name), '*'):
            specs_match += 1
        
        if specs['is_now'] in (getattr(self, field_name), '*'):
            specs_match += 1

        return specs_match == 2


    def _check_is_not_condition(self, specs: dict):
        field_name = specs['when']
        is_not = specs['is_not']
 
        if is_not is NullType:
            return True 
        
        return getattr(self, field_name) != is_not

# For backwards compatibility and Django 1.8
if StrictVersion(django.__version__) >= StrictVersion('1.9'):
    class LifecycleModel(LifecycleModelMixin, models.Model):
        class Meta:
            abstract = True
