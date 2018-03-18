from functools import reduce
from django.db import models



class ModelUpdateDiffMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self.__dict__.copy()


    @property
    def diff(self):
        d1 = self._initial
        d2 = self.__dict__
        diffs = []

        for k, v in d1.items():
            if k in d2 and v != d2[k]:
                diffs.append( (k, (v, d2[k])) )

        return dict(diffs)


    def get_initial_value(self, field_name):
        """
        Get initial value of field when model was instantiated.
        """
        if self._meta.get_field(field_name).get_internal_type() == 'ForeignKey':
            if not field_name.endswith('_id'):
                field_name = field_name+'_id' 
                
        attribute = self.diff.get(field_name, None)

        if not attribute:
            return None

        return attribute[0]


    def has_initial_value_changed(self, field_name):
        """
        Check if a field has changed since the model was instantiated.
        """
        changed = self.diff.keys()

        if self._meta.get_field(field_name).get_internal_type() == 'ForeignKey':
            if not field_name.endswith('_id'):
                field_name = field_name+'_id' 

        if field_name in changed: 
            return True

        return False



def lifecycle(hook: str, ifchanged: str = None, value_prev='*', value_now='*'):
    assert hook in (
        'before_create',
        'after_create',
        'before_update',
        'during_update',
        'after_update',
        'before_delete',
        'after_delete'
    )
    
    if ifchanged is not None:
        assert hook in ('during_update', 'after_update')
        
    def decorator(hooked_method):
        def wrapper(*args, **kwargs):
            hooked_method(*args, **kwargs)
        
        wrapper._hooked = {
            'hook': hook,
            'ifchanged': ifchanged,
            'value_prev': value_prev,
            'value_now': value_now
        }
        
        return wrapper
    return decorator
    


class CoreModel(ModelUpdateDiffMixin, models.Model):

    class Meta:
        abstract = True


    def update(self, **validated_data: dict):
        self._run_hooked_method('before_update')

        for attr, value in validated_data.items():
            setattr(self, attr, value)

        self._run_hooked_method('during_update', is_conditional=True)
        self.save()
        self._run_hooked_method('after_update', is_conditional=True)


    def delete(self, *args, **kwargs):
        self._run_hooked_method('before_delete')
        super().delete(*args, **kwargs)
        self._run_hooked_method('after_delete')
        

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self._run_hooked_method('before_create')
            
        super().save(*args, **kwargs)

        if is_new:
            self._run_hooked_method('after_create')

    
    def _get_potential_methods(self, filter_attr: str):
        methods = []
        skip = ('_get_potential_methods', '_run_hooked_method')
        
        for name in dir(self):
            if name in skip:
                continue
                
            try:
                attr = getattr(self, name)
                if callable(attr) and hasattr(attr, filter_attr):
                    methods.append(attr)
            except AttributeError:
                pass

        return methods

        
    def _run_hooked_method(self, hook: str, is_conditional: bool = False):
        methods = self._get_potential_methods('_hooked')
        
        for method in methods:
            specs = method._hooked
            
            if specs['hook'] != hook:
                continue 
            
            if not is_conditional or specs.get('ifchanged') is None:
                method()
            elif is_conditional and self._check_run_conditions(method._hooked):
                method()
                

    def _check_run_conditions(self, specs: dict):
        field_name = specs['ifchanged']
            
        if not self.has_initial_value_changed(field_name):
            return False

        specs_match = 0

        if specs['value_prev'] in (self.get_initial_value(field_name), '*'):
            specs_match += 1
        
        if specs['value_now'] in (getattr(self, field_name), '*'):
            specs_match += 1

        return specs_match == 2