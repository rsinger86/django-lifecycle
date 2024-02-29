# Changelog

# 1.2.0 (February 2024)

 - Hook condition can be now built using some predefined conditions and/or with custom ones.
 - Fix `has_changed` and `changed_to` when working with mutable data (i.e.: `dict`s). Thanks @AlaaNour94

# 1.1.2 (November 2023)

 - Fix: Hooks were failing if some watched field (those in `when=""` or `when_any=[...]`) was a `GenericForeignKey` 

## 1.1.1 (November 2023)

- Fix: Include missing `django_lifecycle_checks` into python package

## 1.1.0 (November 2023)

- Drop support for Django < 2.2.
- Confirm support for Django 5.0. Thanks @adamchainz!
- Remove urlman from required packages. Thanks @DmytroLitvinov!
- Add an optional Django check to avoid errors by not inheriting from `LifecycleModelMixin` (or `LifecycleModel`) 

## 1.0.2 (September 2023)

- Correct package info to note that Django 4.0, 4.1, and 4.2 are supported.

## 1.0.1 (August 2023)

- Initial state gets reset using `transaction.on_commit()`, fixing the `has_changed()` and `initial_value()` methods for on_commit hooks. Thanks @alb3rto269!


## 1.0.0 (May 2022)

- Drops Python 3.6 support
- Adds `priority` hook kwarg to control the order in which hooked methods fire. Thanks @EnriqueSoria!
- Internal cleanup/refactoring. Thanks @EnriqueSoria!

## 0.9.6 (February 2022)

- Adds missing `packaging` to `install_requires`. Thanks @mikedep333!

## 0.9.5 (February 2022)

- Makes the `has_changed`, `changes_to` conditions depend on whether the field in question was included in the SQL update/insert statement by checking
  the `update_fields` argument passed to save.

## 0.9.4 (February 2022)

- Adds optional @hook `on_commit` argument for executing hooks when the database transaction is committed. Thanks @amcclosky!

## 0.9.3 (October 2021)

- Correct packge info to note that Django 3.2 is supported.

## 0.9.2 (October 2021)

- Run hooked methods inside transactions, just as signals do. Thanks @amirmotlagh!

## 0.9.1 (March 2021)

- Makes hooks work with OneToOneFields. Thanks @bahmdev!

## 0.9.0 (February 2021)

- Prevents calling a hooked method twice with the same state. Thanks @garyd203!

## 0.8.1 (January 2021)

- Added missing return to `delete()` method override. Thanks @oaosman84!

## 0.8.0 (October 2020)

- Significant performance improvements. Thanks @dralley!

## 0.7.7 (August 2020)

- Fixes issue with `GenericForeignKey`. Thanks @bmbouter!

## 0.7.6 (May 2020)

- Updates to use constants for hook names; updates docs to indicate Python 3.8/Django 3.x support. Thanks @thejoeejoee!

## 0.7.5 (April 2020)

- Adds static typed variables for hook names; thanks @Faisal-Manzer!
- Fixes some typos in docs; thanks @tomdyson and @bmispelon!

## 0.7.1 (January 2020)

- Fixes bug in `utils._get_field_names` that could cause recursion bug in some cases.

## 0.7.0 (December 2019)

- Adds `changes_to` condition - thanks @samitnuk! Also some typo fixes in docs.

## 0.6.1 (November 2019)

- Remove variable type annotation for Python 3.5 compatability.

## 0.6.0 (October 2019)

- Adds `when_any` hook parameter to watch multiple fields for state changes

## 0.5.0 (September 2019)

- Adds `was_not` condition
- Allow watching changes to FK model field values, not just FK references

## 0.4.2 (July 2019)

- Fixes missing README.md issue that broke install.

## 0.4.1 (June 2019)

- Fixes [urlman](https://github.com/andrewgodwin/urlman)-compatability.

## 0.4.0 (May 2019)

- Fixes `initial_value(field_name)` behavior - should return value even if no change. Thanks @adamJLev!

## 0.3.2 (February 2019)

- Fixes bug preventing hooks from firing for custom PKs. Thanks @atugushev!

## 0.3.1 (August 2018)

- Fixes m2m field bug, in which accessing auto-generated reverse field in `before_create` causes exception b/c PK does not exist yet. Thanks @garyd203!

## 0.3.0 (April 2018)

- Resets model's comparison state for hook conditions after `save` called.

## 0.2.4 (April 2018)

- Fixed support for adding multiple `@hook` decorators to same method.

## 0.2.3 (April 2018)

- Removes residual mixin methods from earlier implementation.

## 0.2.2 (April 2018)

- Save method now accepts `skip_hooks`, an optional boolean keyword argument that controls whether hooked methods are called.

## 0.2.1 (April 2018)

- Fixed bug in `_potentially_hooked_methods` that caused unwanted side effects by accessing model instance methods decorated with `@cache_property` or `@property`.

## 0.2.0 (April 2018)

- Added Django 1.8 support. Thanks @jtiai!
- Tox testing added for Python 3.4, 3.5, 3.6 and Django 1.8, 1.11 and 2.0. Thanks @jtiai!