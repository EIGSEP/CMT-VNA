# Changelog

## [2.0.0](https://github.com/EIGSEP/CMT-VNA/compare/v1.2.0...v2.0.0) (2026-04-21)


### ⚠ BREAKING CHANGES

* switch_fn callables that previously returned False to signal failure will now be treated as successful. Callers must raise on failure instead.

### Code Refactoring

* switch_fn contract is raises-on-failure, not truthy-return ([7ce30ad](https://github.com/EIGSEP/CMT-VNA/commit/7ce30ad7009403dd17dc33947f3a6e1c61a15535))

## [1.2.0](https://github.com/EIGSEP/CMT-VNA/compare/v1.1.1...v1.2.0) (2026-04-21)


### Features

* enforce switch_fn truthy-return contract in all measure_* methods ([e0e1d2a](https://github.com/EIGSEP/CMT-VNA/commit/e0e1d2aea873d4b9997098a1199c35cab8339dc3))


### Documentation

* align measure_OSL return keys with actual standard states ([94dbafc](https://github.com/EIGSEP/CMT-VNA/commit/94dbafcb014afa01525f916e33bd69f30c4a9546))
* correct measure_OSL and measure_ant return-key docstrings ([3ac650f](https://github.com/EIGSEP/CMT-VNA/commit/3ac650f227b6c8b99a3b17d567f7f5eee7b97762))

## [1.1.1](https://github.com/EIGSEP/CMT-VNA/compare/v1.1.0...v1.1.1) (2026-04-14)


### Bug Fixes

* explicitly set binary byte order and 64-bit precision in SCPI config ([7e817f8](https://github.com/EIGSEP/CMT-VNA/commit/7e817f839f2d282147488c237a4e3c69e1f12b7a))

## [1.1.0](https://github.com/EIGSEP/CMT-VNA/compare/v1.0.0...v1.1.0) (2026-04-14)


### Features

* add a flagger for checking s11 and cal dictionaries in the field ([34c22b4](https://github.com/EIGSEP/CMT-VNA/commit/34c22b426d216bd59f49c4e1b2782ead638bc7bc))


### Bug Fixes

* use picorfswtich in vna scripts ([dc42087](https://github.com/EIGSEP/CMT-VNA/commit/dc420879e240660d4b4649b7658b60c3394853c2))

## [1.0.0](https://github.com/EIGSEP/CMT-VNA/compare/v0.0.2...v1.0.0) (2026-04-14)


### ⚠ BREAKING CHANGES

* `VNA.__init__` parameter renamed `switch_network` -> `switch_fn`, and `VNA.switch_nw` attribute renamed `VNA.switch_fn`. Pass a callable (e.g. `snw.switch` or a lambda) rather than a switch network object.

### Code Refactoring

* replace switch_network object with switch_fn callable ([c65f09f](https://github.com/EIGSEP/CMT-VNA/commit/c65f09f546317f79208c718e34527dd4f0307b9a))

## [0.0.2](https://github.com/EIGSEP/CMT-VNA/compare/v0.0.1...v0.0.2) (2026-03-25)


### Bug Fixes

* numpy array truthiness in S911T.sparams ([#22](https://github.com/EIGSEP/CMT-VNA/issues/22)) ([60561a5](https://github.com/EIGSEP/CMT-VNA/commit/60561a53b93fe0a81edc0b75a4af7f776e77d37e))
