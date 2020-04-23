# Release History

## Unreleased

## 0.7.0 (2020-04-23)

**Features and Improvements**

* Added support for DictField - peterfarrell
* Added support for ListField - peterfarrell

## 0.6.0 (2020-01-03)

**Features and Improvements**

* Added support for Celery - adalekin
* Post process method now called even without a transaction - peterfarrell

## 0.5.0 (2018-08-27)

**Features and Improvements**

* Added ability to defined which database `Service` uses - jackton1
* Changed `Service` into a bona fide Abstract Base Class - jackton1
* Added `CreateServiceView` and `UpdateServiceView` - jackton1

## 0.4.0 (2018-03-30)

**Features and Improvements**

* Add `ModelField` and `MultipleModelField`

## 0.3.1 (2017-12-30)

**Bug fixes**

* Fix `process` not called inside transaction by default

## 0.3.0 (2017-12-14)

**Features and Improvements**

* Add `db_transaction` flag to Service

## 0.2.0 (2017-09-02)

**Features and Improvements**

* Add `ServiceView`
* Add `ModelService`
* Add pt_BR localization

## 0.1.0 (2017-08-13)

* Initial release
